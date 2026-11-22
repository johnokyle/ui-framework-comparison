#!/usr/bin/env python3
"""Development-only OS keyboard smoke through the RemoteDesktop portal."""

from __future__ import annotations

import argparse
import os
import sys
import time
from types import TracebackType

import runtime_smoke as core

CONTROL_L = 0xFFE3
SHIFT_L = 0xFFE1
TAB = 0xFF09
INITIAL_ROUTE = core.Route("primary.browser", "browser.browser1")
CHARTING_ROUTE = core.Route("primary.charting", "chart.analytical")
QUANT_DEFAULT_BY_IMPLEMENTATION = {
    "qml": core.Route("primary.quantviz", "quant.order-book"),
}
DEFAULT_QUANT_ROUTE = core.Route("primary.quantviz", "quant.vol-surface")


def cycling_routes(implementation: str) -> tuple[core.Route, core.Route, core.Route]:
    quant = QUANT_DEFAULT_BY_IMPLEMENTATION.get(implementation, DEFAULT_QUANT_ROUTE)
    return CHARTING_ROUTE, quant, INITIAL_ROUTE


def reverse_cycling_routes(implementation: str) -> tuple[core.Route, core.Route, core.Route]:
    quant = QUANT_DEFAULT_BY_IMPLEMENTATION.get(implementation, DEFAULT_QUANT_ROUTE)
    return quant, CHARTING_ROUTE, INITIAL_ROUTE


def request_path(unique_name: str, token: str) -> str:
    sender = unique_name.removeprefix(":").replace(".", "_")
    return f"/org/freedesktop/portal/desktop/request/{sender}/{token}"


def run_keyboard_sequence(session: core.ProcessSession, keyboard, *, settle: float = 1.0) -> None:
    """Require forward and reverse primary cycling, then exit through the adapter."""
    core.require_route(session.request("state"), INITIAL_ROUTE, "OS keyboard initial state")
    time.sleep(settle)
    for expected in cycling_routes(session.adapter.implementation):
        keyboard.ctrl_tab()
        time.sleep(settle)
        core.require_route(session.request("state"), expected, "state after OS Ctrl+Tab")
    for expected in reverse_cycling_routes(session.adapter.implementation):
        keyboard.ctrl_shift_tab()
        time.sleep(settle)
        core.require_route(session.request("state"), expected, "state after OS Ctrl+Shift+Tab")
    reply = session.request("quit")
    if reply.status != "ok":
        raise core.SmokeFailure("OS keyboard smoke quit was not acknowledged")
    session.finish_quit()


class RemoteDesktopKeyboard:
    """XDG RemoteDesktop keyboard session using the host's PyGObject bindings."""

    def __init__(self, timeout: float):
        try:
            import gi

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio, GLib
        except (ImportError, ValueError) as error:
            raise core.SmokeFailure(
                "OS keyboard smoke requires PyGObject with Gio and GLib"
            ) from error
        self.Gio = Gio
        self.GLib = GLib
        self.timeout = timeout
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.session: str | None = None
        self._counter = 0

    def _token(self, kind: str) -> str:
        self._counter += 1
        return f"uicompare_{kind}_{os.getpid()}_{self._counter}"

    def _request(self, method: str, signature: str, args: tuple) -> dict:
        token = self._token("request")
        expected = request_path(self.bus.get_unique_name(), token)
        args = (
            *args[:-1],
            {**args[-1], "handle_token": self.GLib.Variant("s", token)},
        )
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
                "org.freedesktop.portal.RemoteDesktop",
                method,
                self.GLib.Variant(signature, args),
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
            raise core.SmokeFailure(f"portal {method} timed out")
        if outcome.get("response") != 0:
            raise core.SmokeFailure(f"portal {method} failed: {outcome!r}")
        return outcome["results"]

    def __enter__(self):
        try:
            results = self._request(
                "CreateSession",
                "(a{sv})",
                ({"session_handle_token": self.GLib.Variant("s", self._token("session"))},),
            )
            self.session = results["session_handle"]
            self._request(
                "SelectDevices",
                "(oa{sv})",
                (self.session, {"types": self.GLib.Variant("u", 1)}),
            )
            self._request("Start", "(osa{sv})", (self.session, "", {}))
            return self
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        if self.session is None:
            return
        try:
            self.bus.call_sync(
                "org.freedesktop.portal.Desktop",
                self.session,
                "org.freedesktop.portal.Session",
                "Close",
                None,
                None,
                self.Gio.DBusCallFlags.NONE,
                int(self.timeout * 1000),
                None,
            )
        except Exception as error:
            print(f"remote-desktop session close warning: {error}", file=sys.stderr)
        finally:
            self.session = None

    def __exit__(
        self,
        _type: type[BaseException] | None,
        _value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()

    def keysym(self, keysym: int, state: int) -> None:
        if self.session is None:
            raise core.SmokeFailure("remote-desktop keyboard session is not active")
        self.bus.call_sync(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.RemoteDesktop",
            "NotifyKeyboardKeysym",
            self.GLib.Variant("(oa{sv}iu)", (self.session, {}, keysym, state)),
            None,
            self.Gio.DBusCallFlags.NONE,
            int(self.timeout * 1000),
            None,
        )

    def ctrl_tab(self) -> None:
        self.keysym(CONTROL_L, 1)
        time.sleep(0.05)
        self.keysym(TAB, 1)
        time.sleep(0.05)
        self.keysym(TAB, 0)
        time.sleep(0.05)
        self.keysym(CONTROL_L, 0)
        time.sleep(0.05)

    def ctrl_shift_tab(self) -> None:
        self.keysym(CONTROL_L, 1)
        self.keysym(SHIFT_L, 1)
        time.sleep(0.05)
        self.keysym(TAB, 1)
        time.sleep(0.05)
        self.keysym(TAB, 0)
        time.sleep(0.05)
        self.keysym(SHIFT_L, 0)
        self.keysym(CONTROL_L, 0)
        time.sleep(0.05)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Development OS-level primary-keyboard smoke; not a performance or rendering test."
    )
    result.add_argument("--slint")
    result.add_argument("--qml")
    result.add_argument("--bevy-egui")
    result.add_argument("--bevy-asset-root")
    result.add_argument("--timeout", type=float, default=30.0)
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

    try:
        with RemoteDesktopKeyboard(args.timeout) as keyboard:
            for adapter in adapters:
                session = core.ProcessSession(adapter, args.timeout)
                try:
                    run_keyboard_sequence(session, keyboard)
                except Exception as error:
                    print(f"FAIL {adapter.implementation}: {error}", file=sys.stderr)
                    tail = session.diagnostic_tail()
                    if tail:
                        print(tail, file=sys.stderr)
                    return 1
                finally:
                    session.close()
                print(
                    f"PASS {adapter.implementation}: "
                    "three OS Ctrl+Tab and three Ctrl+Shift+Tab transitions and clean exit"
                )
    except Exception as error:
        print(f"FAIL OS runtime smoke: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
