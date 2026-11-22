#!/usr/bin/env python3
"""Development-only external desktop captures through the Screenshot portal."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def variant_environment(
    implementation: str,
    theme: str,
    scale: str,
    size: str,
    qml_host_scale: float | None,
) -> tuple[tuple[str, str], ...]:
    """Translate requested capture variants into narrow, child-only overrides."""
    variables: list[tuple[str, str]] = []
    if theme != "default":
        variable = {
            "slint": "SLINTUITEST_CAPTURE_THEME",
            "qml": "QMLUITEST_CAPTURE_THEME",
            "bevy-egui": "BEVY_EGUI_CAPTURE_THEME",
        }[implementation]
        variables.append((variable, theme))
    if scale != "native":
        if implementation == "slint":
            variables.append(("SLINT_SCALE_FACTOR", str(int(scale) // 100)))
        elif implementation == "bevy-egui":
            variables.append(("BEVY_EGUI_CAPTURE_SCALE_PERCENT", scale))
        else:
            if qml_host_scale is None or not math.isfinite(qml_host_scale) or qml_host_scale <= 0:
                raise core.SmokeFailure(
                    "explicit QML scales require a finite positive --qml-host-scale"
                )
            factor = int(scale) / 100 / qml_host_scale
            variables.append(("QT_SCALE_FACTOR", format(factor, ".12g")))
    if size != "native":
        variable = {
            "slint": "SLINTUITEST_CAPTURE_SIZE",
            "qml": "QMLUITEST_CAPTURE_SIZE",
            "bevy-egui": "BEVY_EGUI_CAPTURE_SIZE",
        }[implementation]
        variables.append((variable, size))
    return tuple(variables)


def variant_adapter(
    adapter: core.Adapter,
    theme: str,
    scale: str,
    size: str,
    qml_host_scale: float | None,
) -> core.Adapter:
    return core.Adapter(
        adapter.implementation,
        adapter.executable,
        adapter.asset_root,
        variant_environment(adapter.implementation, theme, scale, size, qml_host_scale),
    )


def capture_name(implementation: str, theme: str, scale: str, size: str) -> str:
    stem = f"{implementation}-browser1"
    if theme != "default" or scale != "native":
        stem += f"-{theme}-{scale}pct"
    if size != "native":
        stem += f"-{size}"
    return f"{stem}-desktop.png"


def run_capture(
    session: core.ProcessSession,
    portal,
    output_dir: Path,
    *,
    settle: float = 2.0,
    theme: str = "default",
    scale: str = "native",
    size: str = "native",
    qml_host_scale: float | None = None,
) -> dict[str, object]:
    """Capture Browser 1 externally; the stable-ID adapter only observes and quits."""
    implementation = session.adapter.implementation
    core.require_route(session.request("state"), INITIAL_ROUTE, "screenshot initial state")
    time.sleep(settle)
    uri = portal.capture()
    capture = copy_capture(uri, output_dir / capture_name(implementation, theme, scale, size))
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "state after external screenshot"
    )
    reply = session.request("quit")
    if reply.status != "ok":
        raise core.SmokeFailure("screenshot smoke quit was not acknowledged")
    session.finish_quit()
    record = {
        "evidence": "development-external-screenshot",
        "status": "passed",
        "implementation": implementation,
        "requested_theme": theme,
        "requested_scale_percent": scale,
        "requested_size": size,
        "primary": INITIAL_ROUTE.primary,
        "secondary": INITIAL_ROUTE.secondary,
        "scope": "full-desktop",
        "interactive": False,
        "capture": capture,
        "executable_sha256": executable_sha256(session.adapter.executable),
        "clean_exit": True,
        "equivalence_established": False,
    }
    if implementation == "qml" and scale != "native":
        record["qml_host_scale"] = qml_host_scale
        record["qml_scale_factor"] = int(scale) / 100 / qml_host_scale
    return record


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
    result.add_argument(
        "--themes",
        nargs="+",
        choices=("default", "light", "dark", "system"),
        default=["default"],
    )
    result.add_argument(
        "--scales",
        nargs="+",
        choices=("native", "100", "200"),
        default=["native"],
    )
    result.add_argument(
        "--sizes",
        nargs="+",
        choices=("native", "1200x750", "660x750"),
        default=["native"],
        help="logical client sizes requested through startup-only overrides",
    )
    result.add_argument(
        "--qml-host-scale",
        type=float,
        help="absolute host scale used to normalize explicit QML scale requests",
    )
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
    if (
        args.qml
        and any(scale != "native" for scale in args.scales)
        and (
            args.qml_host_scale is None
            or not math.isfinite(args.qml_host_scale)
            or args.qml_host_scale <= 0
        )
    ):
        parser().error("explicit QML scales require a finite positive --qml-host-scale")

    output_dir = Path(args.output_dir)
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
        portal = ScreenshotPortal(args.timeout)
        with (output_dir / "manifest.jsonl").open("x", encoding="utf-8") as manifest:
            for base_adapter in adapters:
                for theme in args.themes:
                    for scale in args.scales:
                        for size in args.sizes:
                            adapter = variant_adapter(
                                base_adapter, theme, scale, size, args.qml_host_scale
                            )
                            label = f"{adapter.implementation} {theme} {scale} {size}"
                            session = core.ProcessSession(adapter, args.timeout)
                            try:
                                record = run_capture(
                                    session,
                                    portal,
                                    output_dir,
                                    settle=args.settle,
                                    theme=theme,
                                    scale=scale,
                                    size=size,
                                    qml_host_scale=args.qml_host_scale,
                                )
                            except Exception as error:
                                failure = {
                                    "evidence": "development-external-screenshot",
                                    "status": "failed",
                                    "implementation": adapter.implementation,
                                    "requested_theme": theme,
                                    "requested_scale_percent": scale,
                                    "requested_size": size,
                                    "error": str(error),
                                }
                                manifest.write(json.dumps(failure, sort_keys=True) + "\n")
                                manifest.flush()
                                print(f"FAIL {label}: {error}", file=sys.stderr)
                                tail = session.diagnostic_tail()
                                if tail:
                                    print(tail, file=sys.stderr)
                                return 1
                            finally:
                                session.close()
                            manifest.write(json.dumps(record, sort_keys=True) + "\n")
                            manifest.flush()
                            print(f"PASS {label}: {record['capture']['path']}")
    except Exception as error:
        print(f"FAIL external screenshot smoke: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
