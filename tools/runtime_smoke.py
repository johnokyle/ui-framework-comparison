#!/usr/bin/env python3
"""Development-only stable-ID runtime smoke harness for the comparison applications."""

from __future__ import annotations

import argparse
import json
import math
import os
import queue
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, TextIO

PREFIX = "@UITEST1@"
PRIMARY_IDS = ("primary.browser", "primary.charting", "primary.quantviz")
SECONDARY_BY_PRIMARY = {
    "primary.browser": ("browser.browser1", "browser.browser2", "browser.browser3"),
    "primary.charting": ("chart.analytical", "chart.stock", "chart.pivot"),
    "primary.quantviz": (
        "quant.vol-surface",
        "quant.factor-structure",
        "quant.correlation",
        "quant.frontier",
        "quant.pca",
        "quant.regime",
        "quant.projection",
        "quant.network",
        "quant.knowledge",
        "quant.monte-carlo",
        "quant.order-book",
    ),
}
SECONDARY_IDS = tuple(route for primary in PRIMARY_IDS for route in SECONDARY_BY_PRIMARY[primary])
SECONDARY_OWNER = {
    secondary: primary
    for primary, secondaries in SECONDARY_BY_PRIMARY.items()
    for secondary in secondaries
}
QML_ALIASES = {
    **{route: route for route in PRIMARY_IDS},
    **{route: route for route in SECONDARY_IDS},
    "chart.analytical": "chart.basic",
    "chart.stock": "chart.streaming",
    "chart.pivot": "chart.multiseries",
    "quant.vol-surface": "quant.volsurface",
    "quant.factor-structure": "quant.factorstructure",
    "quant.frontier": "quant.efficientfrontier",
    "quant.pca": "quant.pcamanifold",
    "quant.regime": "quant.regimemap",
    "quant.network": "quant.networkgraph",
    "quant.knowledge": "quant.advanced",
    "quant.monte-carlo": "quant.distribution",
    "quant.order-book": "quant.heatmap",
}
QML_CANONICAL_IDS = {alias: canonical for canonical, alias in QML_ALIASES.items()}
ADAPTER_ENV = {
    "slint": ("SLINTUITEST_AUTOMATION", ("SLINTUITEST_METRICS",)),
    "qml": ("QMLUITEST_AUTOMATION", ("QMLUITEST_METRICS",)),
    "bevy-egui": ("BEVY_EGUI_AUTOMATION", ()),
}
IMPLEMENTATION_ORDER = tuple(ADAPTER_ENV)


class SmokeFailure(RuntimeError):
    """A protocol, assertion, or child-process failure."""


@dataclass(frozen=True)
class Route:
    primary: str
    secondary: str


@dataclass(frozen=True)
class Reply:
    command: str
    status: str
    requested: str | None = None
    primary: str | None = None
    secondary: str | None = None

    @property
    def route(self) -> Route:
        if self.primary is None or self.secondary is None:
            raise SmokeFailure(f"{self.command} reply has no active route")
        return Route(self.primary, self.secondary)


@dataclass(frozen=True)
class Adapter:
    implementation: str
    executable: str
    asset_root: str | None = None
    environment: tuple[tuple[str, str], ...] = ()

    @property
    def automation_variable(self) -> str:
        return ADAPTER_ENV[self.implementation][0]


class JsonlRecorder:
    """Immediately flushed, explicitly non-controlled development evidence."""

    def __init__(self, path: str | None):
        self.handle: TextIO | None = open(path, "w", encoding="utf-8") if path else None

    def write(self, implementation: str, event: str, **fields: object) -> None:
        if self.handle is None:
            return
        record = {
            "evidence": "development-runtime-smoke",
            "implementation": implementation,
            "event": event,
            **fields,
        }
        self.handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        self.handle.flush()

    def close(self) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def canonical_route(primary: str, secondary: str, implementation: str) -> Route:
    if implementation == "qml":
        primary = QML_CANONICAL_IDS.get(primary, primary)
        secondary = QML_CANONICAL_IDS.get(secondary, secondary)
    if primary not in PRIMARY_IDS:
        raise SmokeFailure(f"unknown actual primary ID: {primary!r}")
    if secondary not in SECONDARY_IDS:
        raise SmokeFailure(f"unknown actual secondary ID: {secondary!r}")
    if SECONDARY_OWNER[secondary] != primary:
        raise SmokeFailure(f"actual route {primary}/{secondary} violates primary ownership")
    return Route(primary, secondary)


def parse_reply(line: str, implementation: str) -> Reply:
    line = line.rstrip("\r\n")
    fields = line.split("\t")
    if not fields or fields[0] != PREFIX:
        raise SmokeFailure(f"malformed protocol record: {line!r}")
    command = fields[1] if len(fields) > 1 else ""
    if command == "state" and len(fields) == 5 and fields[2] == "ok":
        route = canonical_route(fields[3], fields[4], implementation)
        return Reply("state", "ok", primary=route.primary, secondary=route.secondary)
    if command == "select" and len(fields) == 6 and fields[2] in {
        "ok",
        "unknown-id",
        "rejected",
    }:
        requested = fields[3]
        if not requested:
            raise SmokeFailure("select reply has an empty requested ID")
        if implementation == "qml":
            requested = QML_CANONICAL_IDS.get(requested, requested)
        route = canonical_route(fields[4], fields[5], implementation)
        return Reply(
            "select",
            fields[2],
            requested=requested,
            primary=route.primary,
            secondary=route.secondary,
        )
    if command == "quit" and fields == [PREFIX, "quit", "ok"]:
        return Reply("quit", "ok")
    if command == "error" and fields == [PREFIX, "error", "bad-request"]:
        return Reply("error", "bad-request")
    raise SmokeFailure(f"malformed protocol record: {line!r}")


def child_environment(adapter: Adapter) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(adapter.environment)
    automation_variable, metrics_variables = ADAPTER_ENV[adapter.implementation]
    for variable in metrics_variables:
        environment.pop(variable, None)
    environment[automation_variable] = "1"
    if adapter.implementation == "bevy-egui":
        if adapter.asset_root is None:
            raise SmokeFailure("Bevy requires an asset root")
        environment["BEVY_ASSET_ROOT"] = adapter.asset_root
    return environment


class ProcessSession:
    """One non-reusable child process with a single outstanding request."""

    def __init__(
        self,
        adapter: Adapter,
        timeout: float,
        *,
        process: subprocess.Popen[str] | None = None,
        diagnostic_capacity: int = 100,
        eof_grace: float = 2.0,
    ):
        self.adapter = adapter
        self.timeout = timeout
        self.eof_grace = eof_grace
        self.diagnostics: deque[str] = deque(maxlen=diagnostic_capacity)
        self._events: queue.Queue[tuple[str, object]] = queue.Queue()
        self._failed = False
        self._finished = False
        self._quit_acknowledged = False
        self.process = process or subprocess.Popen(
            [adapter.executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="strict",
            bufsize=1,
            shell=False,
            env=child_environment(adapter),
        )
        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()

    def _read_output(self) -> None:
        try:
            assert self.process.stdout is not None
            for line in self.process.stdout:
                if line.startswith(PREFIX):
                    self._events.put(("reply", line))
                else:
                    self.diagnostics.append(line.rstrip("\r\n"))
        except Exception as error:  # Propagate reader/UTF-8 failures to the requester.
            self._events.put(("error", error))
        finally:
            self._events.put(("eof", None))

    def _failure(self, message: str) -> SmokeFailure:
        self._failed = True
        return SmokeFailure(f"{self.adapter.implementation}: {message}")

    def request(self, command: str) -> Reply:
        if self._failed or self._finished:
            raise self._failure("session is no longer usable")
        status = self.process.poll()
        if status is not None:
            raise self._failure(f"child exited early with status {status}")
        wire_command = command
        if self.adapter.implementation == "qml" and command.startswith("select-route "):
            stable_id = command.removeprefix("select-route ")
            wire_command = f"select-route {QML_ALIASES.get(stable_id, stable_id)}"
        try:
            assert self.process.stdin is not None
            self.process.stdin.write(wire_command + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError, ValueError) as error:
            raise self._failure(f"could not send {command!r}: {error}") from error

        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise self._failure(f"timed out waiting for {command!r}")
            try:
                kind, payload = self._events.get(timeout=remaining)
            except queue.Empty as error:
                raise self._failure(f"timed out waiting for {command!r}") from error
            if kind == "eof":
                status = self.process.poll()
                suffix = "" if status is None else f" with status {status}"
                raise self._failure(f"child closed output while awaiting {command!r}{suffix}")
            if kind == "error":
                raise self._failure(f"output reader failed: {payload}")
            try:
                reply = parse_reply(str(payload), self.adapter.implementation)
            except SmokeFailure as error:
                raise self._failure(str(error)) from error
            expected_command = "select" if command.startswith("select-route ") else command
            if reply.command != expected_command:
                raise self._failure(
                    f"wrong reply command {reply.command!r} for request {command!r}"
                )
            if command == "quit":
                self._quit_acknowledged = True
            return reply

    def finish_quit(self) -> None:
        if self._failed or self._finished or not self._quit_acknowledged:
            raise self._failure("quit completion requested without a valid quit acknowledgement")
        try:
            status = self.process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired as error:
            raise self._failure("child acknowledged quit but did not exit") from error
        if status != 0:
            raise self._failure(f"child exited with status {status} after quit")
        self._finished = True

    def close(self) -> None:
        """Best-effort cleanup that never replaces the triggering failure."""
        if self.process.poll() is not None:
            self._finished = True
            return
        try:
            if self.process.stdin is not None and not self.process.stdin.closed:
                self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=self.eof_grace)
            self._finished = True
            return
        except subprocess.TimeoutExpired:
            pass
        try:
            self.process.terminate()
            self.process.wait(timeout=self.eof_grace)
        except (OSError, subprocess.TimeoutExpired):
            try:
                self.process.kill()
                self.process.wait(timeout=self.eof_grace)
            except (OSError, subprocess.TimeoutExpired):
                pass
        self._finished = True

    def diagnostic_tail(self) -> str:
        return "\n".join(self.diagnostics)


def require_route(reply: Reply, expected: Route, context: str) -> None:
    if reply.status != "ok":
        raise SmokeFailure(f"{context}: expected ok, received {reply.status}")
    if reply.route != expected:
        raise SmokeFailure(
            f"{context}: expected {expected.primary}/{expected.secondary}, "
            f"received {reply.primary}/{reply.secondary}"
        )


def require_selection(reply: Reply, requested: str, expected: Route) -> None:
    if reply.requested != requested:
        raise SmokeFailure(
            f"select {requested}: reply identified {reply.requested!r} as the request"
        )
    require_route(reply, expected, f"select {requested}")


def run_default_sequence(session: ProcessSession, recorder: JsonlRecorder | None = None) -> None:
    """Execute semantic navigation assertions; no input/frame/performance claims."""

    implementation = session.adapter.implementation

    def request(command: str) -> Reply:
        try:
            reply = session.request(command)
        except SmokeFailure as error:
            if recorder is not None:
                recorder.write(implementation, "failure", command=command, error=str(error))
            raise
        if recorder is not None:
            recorder.write(
                implementation,
                "reply",
                command=command,
                status=reply.status,
                requested_id=reply.requested,
                actual_primary=reply.primary,
                actual_secondary=reply.secondary,
            )
        return reply

    initial = Route("primary.browser", "browser.browser1")
    require_route(request("state"), initial, "initial state")

    selections = (
        ("browser.browser2", Route("primary.browser", "browser.browser2")),
        ("chart.stock", Route("primary.charting", "chart.stock")),
        ("quant.monte-carlo", Route("primary.quantviz", "quant.monte-carlo")),
        ("primary.browser", Route("primary.browser", "browser.browser2")),
        ("primary.charting", Route("primary.charting", "chart.stock")),
        ("primary.quantviz", Route("primary.quantviz", "quant.monte-carlo")),
        ("quant.monte-carlo", Route("primary.quantviz", "quant.monte-carlo")),
    )
    for stable_id, expected in selections:
        require_selection(request(f"select-route {stable_id}"), stable_id, expected)

    before_unknown = Route("primary.quantviz", "quant.monte-carlo")
    unknown = request("select-route not.a-route")
    if unknown.status != "unknown-id" or unknown.requested != "not.a-route":
        raise SmokeFailure(
            "select not.a-route: expected unknown-id for the requested unknown stable ID"
        )
    if unknown.route != before_unknown:
        raise SmokeFailure("select not.a-route: unknown request changed active selection")
    require_route(request("state"), before_unknown, "state after unknown ID")

    require_selection(
        request("select-route browser.browser1"),
        "browser.browser1",
        Route("primary.browser", "browser.browser1"),
    )
    quit_reply = request("quit")
    if quit_reply.status != "ok":
        raise SmokeFailure("quit was not acknowledged")
    try:
        session.finish_quit()
    except SmokeFailure as error:
        if recorder is not None:
            recorder.write(implementation, "failure", command="wait-for-exit", error=str(error))
        raise
    if recorder is not None:
        recorder.write(implementation, "pass", clean_exit=True)


SessionFactory = Callable[[Adapter, float], ProcessSession]


def run_adapters(
    adapters: Iterable[Adapter],
    timeout: float,
    recorder: JsonlRecorder | None = None,
    session_factory: SessionFactory = ProcessSession,
) -> list[tuple[str, bool, str]]:
    outcomes: list[tuple[str, bool, str]] = []
    for adapter in adapters:
        session: ProcessSession | None = None
        try:
            if recorder is not None:
                recorder.write(adapter.implementation, "start")
            session = session_factory(adapter, timeout)
            run_default_sequence(session, recorder)
            outcomes.append((adapter.implementation, True, "passed"))
        except (OSError, SmokeFailure) as error:
            message = str(error)
            if session is not None and session.diagnostic_tail():
                message += "\nDiagnostic tail:\n" + session.diagnostic_tail()
            outcomes.append((adapter.implementation, False, message))
            if recorder is not None:
                recorder.write(adapter.implementation, "fail", error=message)
        finally:
            if session is not None:
                session.close()
    return outcomes


def positive_timeout(value: str) -> float:
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be a finite positive number")
    return timeout


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slint", help="absolute path to the Slint Release executable")
    parser.add_argument("--qml", help="absolute path to the QML Release executable")
    parser.add_argument("--bevy-egui", help="absolute path to the Bevy + egui Release executable")
    parser.add_argument("--bevy-asset-root", help="Bevy project root containing assets/")
    parser.add_argument("--timeout", type=positive_timeout, default=30.0)
    parser.add_argument("--jsonl", help="optional development-only JSONL output path")
    args = parser.parse_args(argv)
    if not any((args.slint, args.qml, args.bevy_egui)):
        parser.error("at least one implementation executable is required")
    if args.bevy_egui and not args.bevy_asset_root:
        parser.error("--bevy-asset-root is required with --bevy-egui")
    if args.bevy_asset_root and not Path(args.bevy_asset_root).is_dir():
        parser.error("--bevy-asset-root must name an existing directory")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = {"slint": args.slint, "qml": args.qml, "bevy-egui": args.bevy_egui}
    adapters = [
        Adapter(name, paths[name], args.bevy_asset_root if name == "bevy-egui" else None)
        for name in IMPLEMENTATION_ORDER
        if paths[name]
    ]
    recorder = JsonlRecorder(args.jsonl)
    try:
        outcomes = run_adapters(adapters, args.timeout, recorder)
    finally:
        recorder.close()
    for implementation, passed, message in outcomes:
        print(f"{'PASS' if passed else 'FAIL'} {implementation}: {message}")
    return 0 if all(passed for _, passed, _ in outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
