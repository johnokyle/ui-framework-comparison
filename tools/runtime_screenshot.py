#!/usr/bin/env python3
"""Development-only external desktop captures through the Screenshot portal."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import time
from urllib.parse import urlparse
from urllib.request import url2pathname

import runtime_smoke as core

INITIAL_ROUTE = core.Route("primary.browser", "browser.browser1")


def request_path(unique_name: str, token: str) -> str:
    sender = unique_name.removeprefix(":").replace(".", "_")
    return f"/org/freedesktop/portal/desktop/request/{sender}/{token}"


def file_uri_path(uri: str) -> str:
    parsed = urlparse(uri)
    if (
        parsed.scheme != "file"
        or parsed.netloc not in ("", "localhost")
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise core.SmokeFailure(f"screenshot portal returned an invalid file URI: {uri!r}")
    path = url2pathname(parsed.path)
    if not path:
        raise core.SmokeFailure("screenshot portal returned an empty file URI")
    return path


def copy_capture(uri: str, destination: Path) -> dict[str, object]:
    """Copy one portal result without overwriting and record basic PNG metadata."""
    source = Path(file_uri_path(uri))
    digest = hashlib.sha256()
    header = bytearray()
    size = 0
    with source.open("rb") as source_file, destination.open("xb") as destination_file:
        while chunk := source_file.read(1024 * 1024):
            if len(header) < 24:
                header.extend(chunk[: 24 - len(header)])
            digest.update(chunk)
            destination_file.write(chunk)
            size += len(chunk)
    if (
        len(header) < 24
        or header[:8] != b"\x89PNG\r\n\x1a\n"
        or header[12:16] != b"IHDR"
    ):
        raise core.SmokeFailure(f"screenshot capture is not a PNG: {source}")
    width, height = struct.unpack(">II", header[16:24])
    return {
        "path": str(destination),
        "sha256": digest.hexdigest(),
        "bytes": size,
        "width": width,
        "height": height,
    }


def executable_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as executable:
        while chunk := executable.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def run_capture(
    session: core.ProcessSession,
    portal,
    output_dir: Path,
    *,
    settle: float = 2.0,
) -> dict[str, object]:
    """Capture Browser 1 externally; the stable-ID adapter only observes and quits."""
    implementation = session.adapter.implementation
    core.require_route(session.request("state"), INITIAL_ROUTE, "screenshot initial state")
    time.sleep(settle)
    uri = portal.capture()
    capture = copy_capture(
        uri, output_dir / f"{implementation}-browser1-desktop.png"
    )
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "state after external screenshot"
    )
    reply = session.request("quit")
    if reply.status != "ok":
        raise core.SmokeFailure("screenshot smoke quit was not acknowledged")
    session.finish_quit()
    return {
        "evidence": "development-external-screenshot",
        "status": "passed",
        "implementation": implementation,
        "primary": INITIAL_ROUTE.primary,
        "secondary": INITIAL_ROUTE.secondary,
        "scope": "full-desktop",
        "interactive": False,
        "capture": capture,
        "executable_sha256": executable_sha256(session.adapter.executable),
        "clean_exit": True,
        "equivalence_established": False,
    }


class ScreenshotPortal:
    """XDG Screenshot portal requests using the host's PyGObject bindings."""

    def __init__(self, timeout: float):
        try:
            import gi

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio, GLib
        except (ImportError, ValueError) as error:
            raise core.SmokeFailure(
                "external screenshot smoke requires PyGObject with Gio and GLib"
            ) from error
        self.Gio = Gio
        self.GLib = GLib
        self.timeout = timeout
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self._counter = 0

    def capture(self) -> str:
        self._counter += 1
        token = f"uicompare_screenshot_{os.getpid()}_{self._counter}"
        expected = request_path(self.bus.get_unique_name(), token)
        loop = self.GLib.MainLoop()
        outcome = {}

        def response(_connection, _sender, _path, _interface, _signal, parameters):
            outcome["response"], outcome["results"] = parameters.unpack()
            loop.quit()

        subscription = self.bus.signal_subscribe(
            None,
            "org.freedesktop.portal.Request",
            "Response",
            expected,
            None,
            self.Gio.DBusSignalFlags.NONE,
            response,
        )

        def expire():
            outcome["timeout"] = True
            loop.quit()
            return self.GLib.SOURCE_REMOVE

        timer = self.GLib.timeout_add(int(self.timeout * 1000), expire)
        try:
            actual = self.bus.call_sync(
                "org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Screenshot",
                "Screenshot",
                self.GLib.Variant(
                    "(sa{sv})",
                    (
                        "",
                        {
                            "handle_token": self.GLib.Variant("s", token),
                            "interactive": self.GLib.Variant("b", False),
                        },
                    ),
                ),
                None,
                self.Gio.DBusCallFlags.NONE,
                int(self.timeout * 1000),
                None,
            ).unpack()[0]
            if actual != expected:
                raise core.SmokeFailure(
                    f"portal returned request path {actual!r}, expected {expected!r}"
                )
            loop.run()
        finally:
            self.GLib.source_remove(timer)
            self.bus.signal_unsubscribe(subscription)
        if outcome.get("timeout"):
            raise core.SmokeFailure("portal Screenshot timed out")
        if outcome.get("response") != 0:
            raise core.SmokeFailure(f"portal Screenshot failed: {outcome!r}")
        try:
            return outcome["results"]["uri"]
        except KeyError as error:
            raise core.SmokeFailure(
                f"portal Screenshot omitted its URI: {outcome!r}"
            ) from error


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Development full-desktop captures; not equivalence or performance evidence."
    )
    result.add_argument("--slint")
    result.add_argument("--qml")
    result.add_argument("--bevy-egui")
    result.add_argument("--bevy-asset-root")
    result.add_argument("--output-dir", required=True)
    result.add_argument("--timeout", type=float, default=30.0)
    result.add_argument("--settle", type=float, default=2.0)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    adapters = []
    if args.slint:
        adapters.append(core.Adapter("slint", args.slint))
    if args.qml:
        adapters.append(core.Adapter("qml", args.qml))
    if args.bevy_egui:
        if not args.bevy_asset_root:
            parser().error("--bevy-asset-root is required with --bevy-egui")
        adapters.append(
            core.Adapter("bevy-egui", args.bevy_egui, args.bevy_asset_root)
        )
    if not adapters:
        parser().error("at least one implementation executable is required")

    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
        portal = ScreenshotPortal(args.timeout)
        with (output_dir / "manifest.jsonl").open("x", encoding="utf-8") as manifest:
            for adapter in adapters:
                session = core.ProcessSession(adapter, args.timeout)
                try:
                    record = run_capture(session, portal, output_dir, settle=args.settle)
                except Exception as error:
                    failure = {
                        "evidence": "development-external-screenshot",
                        "status": "failed",
                        "implementation": adapter.implementation,
                        "error": str(error),
                    }
                    manifest.write(json.dumps(failure, sort_keys=True) + "\n")
                    manifest.flush()
                    print(f"FAIL {adapter.implementation}: {error}", file=sys.stderr)
                    tail = session.diagnostic_tail()
                    if tail:
                        print(tail, file=sys.stderr)
                    return 1
                finally:
                    session.close()
                manifest.write(json.dumps(record, sort_keys=True) + "\n")
                manifest.flush()
                print(f"PASS {adapter.implementation}: {record['capture']['path']}")
    except Exception as error:
        print(f"FAIL external screenshot smoke: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
