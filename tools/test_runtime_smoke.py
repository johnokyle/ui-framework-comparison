#!/usr/bin/env python3
"""Stdlib tests for the development stable-ID runtime smoke harness."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from runtime_smoke import (
    ADAPTER_ENV,
    IMPLEMENTATION_ORDER,
    PREFIX,
    PRIMARY_IDS,
    QML_ALIASES,
    QML_CANONICAL_IDS,
    SECONDARY_BY_PRIMARY,
    SECONDARY_IDS,
    SECONDARY_OWNER,
    Adapter,
    JsonlRecorder,
    ProcessSession,
    Reply,
    Route,
    SmokeFailure,
    canonical_route,
    child_environment,
    main,
    parse_args,
    parse_reply,
    require_selection,
    run_adapters,
    run_default_sequence,
)


def line(command: str, status: str, *fields: str) -> str:
    return "\t".join((PREFIX, command, status, *fields)) + "\n"


class FakeStdin(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.flushes = 0

    def flush(self) -> None:
        self.flushes += 1
        super().flush()


class BlockingStdout:
    def __init__(self, release: threading.Event):
        self.release = release

    def __iter__(self):
        return self

    def __next__(self):
        self.release.wait(2)
        raise StopIteration


class FakeProcess:
    def __init__(
        self,
        output: str = "",
        *,
        returncode: int | None = None,
        exit_status: int | None = None,
        exit_on_stdin_close: bool = False,
        exit_on_terminate: bool = True,
        blocking: bool = False,
    ) -> None:
        self.returncode = returncode
        self.exit_status = exit_status
        self.exit_on_stdin_close = exit_on_stdin_close
        self.exit_on_terminate = exit_on_terminate
        self.stdin = FakeStdin()
        self.release = threading.Event()
        self.stdout = BlockingStdout(self.release) if blocking else io.StringIO(output)
        self.terminate_calls = 0
        self.kill_calls = 0

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is not None:
            return self.returncode
        if self.exit_on_stdin_close and self.stdin.closed:
            self.returncode = 0 if self.exit_status is None else self.exit_status
            self.release.set()
            return self.returncode
        if self.exit_status is not None:
            self.returncode = self.exit_status
            self.release.set()
            return self.returncode
        raise subprocess.TimeoutExpired("fake", timeout)

    def terminate(self) -> None:
        self.terminate_calls += 1
        if self.exit_on_terminate:
            self.returncode = -15
            self.release.set()

    def kill(self) -> None:
        self.kill_calls += 1
        self.returncode = -9
        self.release.set()


class InMemorySession:
    def __init__(self, adapter: Adapter, timeout: float):
        self.adapter = adapter
        self.timeout = timeout
        self.route = Route("primary.browser", "browser.browser1")
        self.retained = {
            "primary.browser": "browser.browser1",
            "primary.charting": "chart.analytical",
            "primary.quantviz": "quant.vol-surface",
        }
        self.commands: list[str] = []
        self.closed = 0
        self.finish_calls = 0
        self.exit_status = 0
        self.failure_command: str | None = None

    def request(self, command: str) -> Reply:
        self.commands.append(command)
        if command == self.failure_command:
            raise SmokeFailure(f"{self.adapter.implementation}: injected failure")
        if command == "state":
            return Reply("state", "ok", primary=self.route.primary, secondary=self.route.secondary)
        if command == "quit":
            return Reply("quit", "ok")
        assert command.startswith("select-route ")
        stable_id = command.removeprefix("select-route ")
        if stable_id not in PRIMARY_IDS and stable_id not in SECONDARY_IDS:
            return Reply(
                "select",
                "unknown-id",
                requested=stable_id,
                primary=self.route.primary,
                secondary=self.route.secondary,
            )
        if stable_id in PRIMARY_IDS:
            primary = stable_id
        else:
            primary = SECONDARY_OWNER[stable_id]
            self.retained[primary] = stable_id
        self.route = Route(primary, self.retained[primary])
        return Reply(
            "select",
            "ok",
            requested=stable_id,
            primary=self.route.primary,
            secondary=self.route.secondary,
        )

    def finish_quit(self) -> None:
        self.finish_calls += 1
        if self.exit_status != 0:
            raise SmokeFailure(f"child exited with status {self.exit_status} after quit")

    def close(self) -> None:
        self.closed += 1

    def diagnostic_tail(self) -> str:
        return ""


class RegistryTests(unittest.TestCase):
    def test_exact_registry_and_ownership(self) -> None:
        self.assertEqual(PRIMARY_IDS, ("primary.browser", "primary.charting", "primary.quantviz"))
        self.assertEqual(len(SECONDARY_IDS), 17)
        self.assertEqual(len(set(SECONDARY_IDS)), 17)
        self.assertEqual(
            SECONDARY_BY_PRIMARY["primary.browser"],
            ("browser.browser1", "browser.browser2", "browser.browser3"),
        )
        self.assertEqual(
            SECONDARY_BY_PRIMARY["primary.charting"],
            ("chart.analytical", "chart.stock", "chart.pivot"),
        )
        self.assertEqual(
            SECONDARY_BY_PRIMARY["primary.quantviz"],
            (
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
        )
        for primary, secondaries in SECONDARY_BY_PRIMARY.items():
            for secondary in secondaries:
                self.assertEqual(SECONDARY_OWNER[secondary], primary)

    def test_exact_qml_aliases_and_unambiguous_inverse(self) -> None:
        nonidentity = {
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
        expected_aliases = {
            **{primary: primary for primary in PRIMARY_IDS},
            "browser.browser1": "browser.browser1",
            "browser.browser2": "browser.browser2",
            "browser.browser3": "browser.browser3",
            "quant.correlation": "quant.correlation",
            "quant.projection": "quant.projection",
            **nonidentity,
        }
        self.assertEqual(QML_ALIASES, expected_aliases)
        self.assertEqual(
            QML_CANONICAL_IDS,
            {alias: canonical for canonical, alias in expected_aliases.items()},
        )
        for canonical, alias in nonidentity.items():
            self.assertEqual(QML_ALIASES[canonical], alias)
            self.assertEqual(QML_CANONICAL_IDS[alias], canonical)
        for canonical in set(QML_ALIASES) - set(nonidentity):
            self.assertEqual(QML_ALIASES[canonical], canonical)
        self.assertNotIn("browser.browser4", QML_CANONICAL_IDS)
        self.assertNotIn("chart.layout", QML_CANONICAL_IDS)


class ReplyTests(unittest.TestCase):
    def test_response_grammar(self) -> None:
        self.assertEqual(
            parse_reply(line("state", "ok", "primary.browser", "browser.browser1"), "slint"),
            Reply("state", "ok", primary="primary.browser", secondary="browser.browser1"),
        )
        for status in ("ok", "unknown-id", "rejected"):
            reply = parse_reply(
                line(
                    "select",
                    status,
                    "browser.browser2",
                    "primary.browser",
                    "browser.browser1",
                ),
                "slint",
            )
            self.assertEqual(reply.status, status)
            self.assertEqual(reply.requested, "browser.browser2")
        self.assertEqual(parse_reply(line("quit", "ok"), "bevy-egui"), Reply("quit", "ok"))
        self.assertEqual(
            parse_reply(line("error", "bad-request"), "qml"), Reply("error", "bad-request")
        )

    def test_malformed_records_are_rejected(self) -> None:
        malformed = (
            "state\tok\n",
            PREFIX + "\n",
            PREFIX + "\tstate\n",
            line("state", "ok", "primary.browser"),
            line("state", "rejected", "primary.browser", "browser.browser1"),
            line("select", "ok", "browser.browser2", "primary.browser"),
            line("select", "maybe", "x", "primary.browser", "browser.browser1"),
            line("select", "ok", "", "primary.browser", "browser.browser1"),
            line("quit", "ok", "extra"),
            line("error", "bad-request", "extra"),
        )
        for record in malformed:
            with self.subTest(record=record), self.assertRaises(SmokeFailure):
                parse_reply(record, "slint")

    def test_qml_requests_and_responses_use_canonical_oracle(self) -> None:
        reply = parse_reply(
            line(
                "select",
                "ok",
                "quant.distribution",
                "primary.quantviz",
                "quant.distribution",
            ),
            "qml",
        )
        self.assertEqual(reply.requested, "quant.monte-carlo")
        self.assertEqual(reply.route, Route("primary.quantviz", "quant.monte-carlo"))
        state = parse_reply(
            line("state", "ok", "primary.charting", "chart.basic"), "qml"
        )
        self.assertEqual(state.route, Route("primary.charting", "chart.analytical"))
        self.assertEqual(
            canonical_route("primary.charting", "chart.multiseries", "qml").secondary,
            "chart.pivot",
        )

    def test_unknown_actual_ids_and_qml_placeholders_are_rejected(self) -> None:
        for primary, secondary in (
            ("primary.unknown", "browser.browser1"),
            ("primary.browser", "browser.browser4"),
            ("primary.charting", "chart.layout"),
        ):
            with self.subTest(primary=primary, secondary=secondary), self.assertRaises(SmokeFailure):
                canonical_route(primary, secondary, "qml")
        with self.assertRaises(SmokeFailure):
            canonical_route("primary.browser", "chart.stock", "slint")

    def test_unknown_rejected_and_fallback_selection_are_not_success_assertions(self) -> None:
        expected = Route("primary.quantviz", "quant.order-book")
        rejected = Reply(
            "select",
            "rejected",
            requested="quant.order-book",
            primary="primary.quantviz",
            secondary="quant.vol-surface",
        )
        with self.assertRaises(SmokeFailure):
            require_selection(rejected, "quant.order-book", expected)
        fallback = Reply(
            "select",
            "ok",
            requested="quant.order-book",
            primary="primary.quantviz",
            secondary="quant.monte-carlo",
        )
        with self.assertRaises(SmokeFailure):
            require_selection(fallback, "quant.order-book", expected)


class DefaultSequenceTests(unittest.TestCase):
    def test_complete_default_sequence_and_clean_quit(self) -> None:
        session = InMemorySession(Adapter("slint", "/fake/slint"), 1)
        run_default_sequence(session)
        self.assertEqual(
            session.commands,
            [
                "state",
                "select-route browser.browser2",
                "select-route chart.stock",
                "select-route quant.monte-carlo",
                "select-route primary.browser",
                "select-route primary.charting",
                "select-route primary.quantviz",
                "select-route quant.monte-carlo",
                "select-route not.a-route",
                "state",
                "select-route browser.browser1",
                "quit",
            ],
        )
        self.assertEqual(session.finish_calls, 1)

    def test_assertion_failure_stops_sequence(self) -> None:
        session = InMemorySession(Adapter("slint", "/fake/slint"), 1)
        original = session.request

        def wrong_stock(command: str) -> Reply:
            reply = original(command)
            if command == "select-route chart.stock":
                return Reply(
                    "select",
                    "ok",
                    requested="chart.stock",
                    primary="primary.charting",
                    secondary="chart.analytical",
                )
            return reply

        session.request = wrong_stock
        with self.assertRaisesRegex(SmokeFailure, "select chart.stock"):
            run_default_sequence(session)
        self.assertNotIn("quit", session.commands)

    def test_unknown_id_must_preserve_both_reply_and_follow_up_state(self) -> None:
        for mutation in ("status", "requested", "reply-route", "follow-up-state"):
            with self.subTest(mutation=mutation):
                session = InMemorySession(Adapter("slint", "/fake/slint"), 1)
                original = session.request
                state_requests = 0

                def broken(command: str) -> Reply:
                    nonlocal state_requests
                    reply = original(command)
                    if command == "select-route not.a-route":
                        if mutation == "status":
                            return Reply(
                                "select",
                                "ok",
                                requested=reply.requested,
                                primary=reply.primary,
                                secondary=reply.secondary,
                            )
                        if mutation == "requested":
                            return Reply(
                                "select",
                                reply.status,
                                requested="different.route",
                                primary=reply.primary,
                                secondary=reply.secondary,
                            )
                        if mutation == "reply-route":
                            return Reply(
                                "select",
                                reply.status,
                                requested=reply.requested,
                                primary="primary.browser",
                                secondary="browser.browser2",
                            )
                    if command == "state":
                        state_requests += 1
                        if mutation == "follow-up-state" and state_requests == 2:
                            return Reply(
                                "state",
                                "ok",
                                primary="primary.charting",
                                secondary="chart.stock",
                            )
                    return reply

                session.request = broken
                with self.assertRaises(SmokeFailure):
                    run_default_sequence(session)

    def test_jsonl_is_optional_flushed_and_development_labeled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "smoke.jsonl"
            recorder = JsonlRecorder(str(path))
            session = InMemorySession(Adapter("qml", "/fake/qml"), 1)
            run_default_sequence(session, recorder)
            with path.open(encoding="utf-8") as handle:
                records = [json.loads(item) for item in handle]
            recorder.close()
            self.assertTrue(records)
            self.assertTrue(all(item["evidence"] == "development-runtime-smoke" for item in records))
            self.assertEqual(records[-1]["event"], "pass")
            self.assertNotIn("startup_ms", path.read_text(encoding="utf-8"))
            empty = JsonlRecorder(None)
            empty.write("slint", "start")
            empty.close()


class ProcessSessionTests(unittest.TestCase):
    def session(self, process: FakeProcess, implementation: str = "slint", timeout: float = 0.2):
        return ProcessSession(
            Adapter(implementation, "/fake/executable", "/fake/assets" if implementation == "bevy-egui" else None),
            timeout,
            process=process,
            eof_grace=0.01,
        )

    def test_diagnostic_noise_is_not_a_reply_and_tail_is_bounded(self) -> None:
        noise = "".join(f"NAV diagnostic {index}\n" for index in range(8))
        process = FakeProcess(
            noise + line("state", "ok", "primary.browser", "browser.browser1")
        )
        session = self.session(process)
        try:
            reply = session.request("state")
            self.assertEqual(reply.status, "ok")
            self.assertIn("state\n", process.stdin.getvalue())
            self.assertNotIn(PREFIX, session.diagnostic_tail())
            self.assertIn("NAV diagnostic 0", session.diagnostic_tail())
        finally:
            session.close()

        process = FakeProcess(
            "".join(f"noise {index}\n" for index in range(120))
            + line("state", "ok", "primary.browser", "browser.browser1")
        )
        session = self.session(process)
        try:
            session.request("state")
            self.assertLessEqual(len(session.diagnostics), 100)
        finally:
            session.close()

    def test_qml_outgoing_aliases_and_unknown_literal(self) -> None:
        process = FakeProcess(
            line(
                "select",
                "unknown-id",
                "not.a-route",
                "primary.browser",
                "browser.browser1",
            ),
            exit_on_stdin_close=True,
        )
        session = self.session(process, "qml")
        try:
            reply = session.request("select-route not.a-route")
            self.assertEqual(reply.requested, "not.a-route")
            self.assertIn("select-route not.a-route\n", process.stdin.getvalue())
        finally:
            session.close()

        process = FakeProcess(
            line(
                "select",
                "ok",
                "chart.streaming",
                "primary.charting",
                "chart.streaming",
            ),
            exit_on_stdin_close=True,
        )
        session = self.session(process, "qml")
        try:
            reply = session.request("select-route chart.stock")
            self.assertEqual(reply.route, Route("primary.charting", "chart.stock"))
            self.assertIn("select-route chart.streaming\n", process.stdin.getvalue())
        finally:
            session.close()

    def test_malformed_prefixed_record_and_wrong_command_fail(self) -> None:
        for output in (PREFIX + "\tstate\tok\n", line("quit", "ok")):
            process = FakeProcess(output, exit_on_stdin_close=True)
            session = self.session(process)
            try:
                with self.assertRaises(SmokeFailure):
                    session.request("state")
            finally:
                session.close()

    def test_timeout_makes_session_unusable_and_cleans_up(self) -> None:
        process = FakeProcess(blocking=True, exit_on_terminate=False)
        session = self.session(process, timeout=0.01)
        with self.assertRaisesRegex(SmokeFailure, "timed out"):
            session.request("state")
        with self.assertRaisesRegex(SmokeFailure, "no longer usable"):
            session.request("state")
        session.close()
        self.assertEqual(process.terminate_calls, 1)
        self.assertEqual(process.kill_calls, 1)

    def test_startup_eof_and_early_nonzero_exit_fail(self) -> None:
        process = FakeProcess("", returncode=None, exit_on_stdin_close=True)
        session = self.session(process)
        try:
            with self.assertRaisesRegex(SmokeFailure, "closed output"):
                session.request("state")
        finally:
            session.close()

        process = FakeProcess(returncode=7)
        session = self.session(process)
        try:
            with self.assertRaisesRegex(SmokeFailure, "exited early with status 7"):
                session.request("state")
        finally:
            session.close()

    def test_clean_quit_acknowledgement_requires_zero_exit(self) -> None:
        process = FakeProcess(line("quit", "ok"), exit_status=0)
        session = self.session(process)
        try:
            self.assertEqual(session.request("quit"), Reply("quit", "ok"))
            session.finish_quit()
            self.assertEqual(process.returncode, 0)
        finally:
            session.close()

        for status in (None, 3):
            process = FakeProcess(line("quit", "ok"), exit_status=status)
            session = self.session(process, timeout=0.01)
            try:
                session.request("quit")
                with self.assertRaises(SmokeFailure):
                    session.finish_quit()
            finally:
                session.close()


class EnvironmentAndCliTests(unittest.TestCase):
    def test_environment_scrubbing_opt_in_and_asset_root(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "SLINTUITEST_METRICS": "1",
                "QMLUITEST_METRICS": "1",
                "KEEP_ME": "yes",
            },
            clear=False,
        ):
            slint = child_environment(Adapter("slint", "/fake/slint"))
            self.assertNotIn("SLINTUITEST_METRICS", slint)
            self.assertEqual(slint["SLINTUITEST_AUTOMATION"], "1")
            self.assertEqual(slint["KEEP_ME"], "yes")
            qml = child_environment(Adapter("qml", "/fake/qml"))
            self.assertNotIn("QMLUITEST_METRICS", qml)
            self.assertEqual(qml["QMLUITEST_AUTOMATION"], "1")
            bevy = child_environment(Adapter("bevy-egui", "/fake/bevy", "/assets"))
            self.assertEqual(bevy["BEVY_EGUI_AUTOMATION"], "1")
            self.assertEqual(bevy["BEVY_ASSET_ROOT"], "/assets")
        with self.assertRaises(SmokeFailure):
            child_environment(Adapter("bevy-egui", "/fake/bevy"))

    def test_popen_is_direct_merges_stderr_and_applies_environment(self) -> None:
        process = FakeProcess(
            line("state", "ok", "primary.browser", "browser.browser1"),
            exit_on_stdin_close=True,
        )
        with mock.patch("runtime_smoke.subprocess.Popen", return_value=process) as popen:
            session = ProcessSession(Adapter("slint", "/fake/slint"), 0.2)
            try:
                session.request("state")
            finally:
                session.close()
        kwargs = popen.call_args.kwargs
        self.assertEqual(popen.call_args.args[0], ["/fake/slint"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(kwargs["stderr"], subprocess.STDOUT)
        self.assertNotIn("SLINTUITEST_METRICS", kwargs["env"])
        self.assertEqual(kwargs["env"]["SLINTUITEST_AUTOMATION"], "1")

    def test_cli_requires_an_executable_and_bevy_asset_root(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args([])
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(["--bevy-egui", "/fake/bevy"])
        with tempfile.TemporaryDirectory() as directory:
            args = parse_args(
                [
                    "--bevy-egui",
                    "/fake/bevy",
                    "--bevy-asset-root",
                    directory,
                    "--timeout",
                    "2",
                ]
            )
            self.assertEqual(args.timeout, 2)
        for timeout in ("0", "nan", "inf", "-inf"):
            with self.subTest(timeout=timeout), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parse_args(["--slint", "/fake/slint", "--timeout", timeout])

    def test_main_orders_supplied_implementations(self) -> None:
        with tempfile.TemporaryDirectory() as directory, mock.patch(
            "runtime_smoke.run_adapters", return_value=[]
        ) as run:
            result = main(
                [
                    "--bevy-egui",
                    "/fake/bevy",
                    "--bevy-asset-root",
                    directory,
                    "--qml",
                    "/fake/qml",
                    "--slint",
                    "/fake/slint",
                ]
            )
        self.assertEqual(result, 0)
        adapters = run.call_args.args[0]
        self.assertEqual([item.implementation for item in adapters], list(IMPLEMENTATION_ORDER))
        self.assertEqual(tuple(ADAPTER_ENV), IMPLEMENTATION_ORDER)


class CoordinatorTests(unittest.TestCase):
    def test_sequential_execution_and_failure_cleanup_preserve_original_error(self) -> None:
        sessions: list[InMemorySession] = []

        def factory(adapter: Adapter, timeout: float) -> InMemorySession:
            session = InMemorySession(adapter, timeout)
            sessions.append(session)
            return session

        adapters = [Adapter(name, f"/fake/{name}") for name in IMPLEMENTATION_ORDER]
        outcomes = run_adapters(adapters, 1, session_factory=factory)
        self.assertTrue(all(passed for _, passed, _ in outcomes))
        self.assertEqual([item.adapter.implementation for item in sessions], list(IMPLEMENTATION_ORDER))
        self.assertTrue(all(item.closed == 1 for item in sessions))

        sessions.clear()
        original_factory = factory

        def failing_factory(adapter: Adapter, timeout: float) -> InMemorySession:
            session = original_factory(adapter, timeout)
            if adapter.implementation == "qml":
                session.failure_command = "select-route chart.stock"
            return session

        outcomes = run_adapters(adapters, 1, session_factory=failing_factory)
        self.assertEqual([passed for _, passed, _ in outcomes], [True, False, True])
        self.assertIn("injected failure", outcomes[1][2])
        self.assertTrue(all(item.closed == 1 for item in sessions))


if __name__ == "__main__":
    unittest.main()
