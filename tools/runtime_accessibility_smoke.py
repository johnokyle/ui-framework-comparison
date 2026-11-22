#!/usr/bin/env python3
"""Development AT-SPI and focused-tab OS keyboard evidence, not screen-reader acceptance."""

from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
import math
from pathlib import Path
import sys
import time

import runtime_os_smoke as os_smoke
import runtime_screenshot as screenshots
import runtime_smoke as core

RIGHT = 0xFF53
LEFT = 0xFF51
RETURN = 0xFF0D
INITIAL_ROUTE = core.Route("primary.browser", "browser.browser1")
BROWSER2_ROUTE = core.Route("primary.browser", "browser.browser2")
MAX_NODES = 4000


def walk_tree(root, *, max_nodes: int = MAX_NODES):
    """Iterate one already process-scoped accessible tree in stable child order."""
    stack = [root]
    count = 0
    while stack:
        node = stack.pop()
        if node is None:
            continue
        count += 1
        if count > max_nodes:
            raise core.SmokeFailure(f"accessible tree exceeds {max_nodes} nodes")
        yield node
        children = [node.get_child_at_index(index) for index in range(node.get_child_count())]
        stack.extend(reversed(children))


def visible_tab(bridge, nodes, name: str):
    matches = [
        node
        for node in nodes
        if node.get_name() == name
        and node.get_role_name() == "page tab"
        and bridge.has_state(node, "SHOWING")
    ]
    if len(matches) != 1:
        raise core.SmokeFailure(f"expected one visible {name!r} page tab, found {len(matches)}")
    return matches[0]


def tree_summary(bridge, root) -> tuple[dict[str, object], list]:
    nodes = list(walk_tree(root))
    showing = [node for node in nodes if bridge.has_state(node, "SHOWING")]
    names = {node.get_name() for node in showing}
    required = {
        "Browser",
        "Charting",
        "Quantitative Visualization",
        "Browser #1",
        "Browser #2",
        "Browser #3",
        "Symbol",
        "Change %",
    }
    missing = sorted(required - names)
    if missing:
        raise core.SmokeFailure(f"visible Browser 1 accessibility names are missing: {missing}")
    route_labels = sorted(
        node.get_name()
        for node in showing
        if node.get_role_name() == "label"
        and "(primary.browser)" in node.get_name()
        and "(browser.browser" in node.get_name()
    )
    tabs = [
        {
            "name": node.get_name(),
            "focused": bridge.has_state(node, "FOCUSED"),
            "checked": bridge.has_state(node, "CHECKED"),
        }
        for node in showing
        if node.get_role_name() == "page tab"
    ]
    summary = {
        "node_count": len(nodes),
        "showing_node_count": len(showing),
        "application_name": root.get_name(),
        "frame_names": sorted(
            node.get_name() for node in showing if node.get_role_name() == "frame"
        ),
        "route_labels": route_labels,
        "visible_page_tabs": tabs,
    }
    return summary, nodes


def tap(keyboard, keysym: int) -> None:
    keyboard.keysym(keysym, 1)
    time.sleep(0.05)
    keyboard.keysym(keysym, 0)
    time.sleep(0.05)


def set_focus(bridge, node) -> None:
    actions = [node.get_action_name(index) for index in range(node.get_n_actions())]
    if "SetFocus" not in actions:
        raise core.SmokeFailure(f"{node.get_name()!r} has no AT-SPI SetFocus action: {actions}")
    if not node.do_action(actions.index("SetFocus")):
        raise core.SmokeFailure(f"AT-SPI SetFocus failed for {node.get_name()!r}")


def require_focus(bridge, node, expected: bool = True) -> None:
    if bridge.has_state(node, "FOCUSED") != expected:
        raise core.SmokeFailure(
            f"unexpected AT-SPI focus for {node.get_name()!r}: expected {expected}"
        )


def finish_cleanly(session: core.ProcessSession) -> None:
    reply = session.request("quit")
    if reply.status != "ok":
        raise core.SmokeFailure("accessibility smoke quit was not acknowledged")
    session.finish_quit()


def run_qml_sequence(
    session: core.ProcessSession,
    bridge,
    keyboard,
    *,
    settle: float = 1.0,
) -> dict[str, object]:
    """Exercise focus-only arrow navigation and Return selection through real OS keys."""
    core.require_route(session.request("state"), INITIAL_ROUTE, "AT-SPI initial state")
    time.sleep(settle)
    root = bridge.application_for_pid(session.process.pid)
    if root is None:
        raise core.SmokeFailure("QML exposed no populated process-scoped AT-SPI application")
    initial_summary, nodes = tree_summary(bridge, root)
    first = visible_tab(bridge, nodes, "Browser #1")
    second = visible_tab(bridge, nodes, "Browser #2")
    if not bridge.has_state(first, "CHECKED") or bridge.has_state(second, "CHECKED"):
        raise core.SmokeFailure("initial AT-SPI Browser tab checked states do not match Browser 1")

    set_focus(bridge, first)
    time.sleep(0.2)
    require_focus(bridge, first)

    tap(keyboard, RIGHT)
    time.sleep(settle)
    require_focus(bridge, second)
    require_focus(bridge, first, False)
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "Right must move focus without selection"
    )

    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), BROWSER2_ROUTE, "Return selects focused Browser 2")
    if not bridge.has_state(second, "CHECKED") or bridge.has_state(first, "CHECKED"):
        raise core.SmokeFailure("AT-SPI checked states did not follow Browser 2 selection")

    tap(keyboard, LEFT)
    time.sleep(settle)
    require_focus(bridge, first)
    require_focus(bridge, second, False)
    core.require_route(
        session.request("state"), BROWSER2_ROUTE, "Left must move focus without selection"
    )

    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), INITIAL_ROUTE, "Return restores Browser 1")
    if not bridge.has_state(first, "CHECKED") or bridge.has_state(second, "CHECKED"):
        raise core.SmokeFailure("AT-SPI checked states did not follow Browser 1 restoration")
    final_summary, _ = tree_summary(bridge, root)
    finish_cleanly(session)
    return {
        "evidence": "development-atspi-os-keyboard",
        "implementation": "qml",
        "status": "passed",
        "outcome": "focused-tab-keyboard-selection",
        "initial_tree": initial_summary,
        "final_tree": final_summary,
        "focus_action": "AT-SPI SetFocus",
        "os_key_sequence": ["Right", "Return", "Left", "Return"],
        "route_sequence": [
            "browser.browser1",
            "browser.browser1",
            "browser.browser2",
            "browser.browser2",
            "browser.browser1",
        ],
        "focus_without_selection_verified": True,
        "pointer_input": False,
        "clean_exit": True,
    }


def observe_application(session: core.ProcessSession, bridge) -> dict[str, object]:
    """Record process-scoped AT-SPI presence independently of keyboard evidence."""
    root = bridge.application_for_pid(session.process.pid)
    if root is None:
        outcome = "no-process-accessible"
        summary = None
    else:
        outcome = "tree-observed-no-input-assertion"
        summary = tree_summary(bridge, root)[0]
    return {
        "evidence": "development-atspi-observation",
        "implementation": session.adapter.implementation,
        "status": "gap" if root is None else "observed",
        "outcome": outcome,
        "tree": summary,
    }


def run_slint_sequence(
    session: core.ProcessSession,
    bridge,
    keyboard,
    *,
    settle: float = 1.0,
) -> dict[str, object]:
    """Use the Browser secondary bar's ordinary startup focus and real OS keys."""
    core.require_route(session.request("state"), INITIAL_ROUTE, "OS keyboard initial state")
    time.sleep(settle)
    accessibility = observe_application(session, bridge)

    tap(keyboard, RIGHT)
    time.sleep(settle)
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "Right must move focus without selection"
    )
    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), BROWSER2_ROUTE, "Return selects focused Browser 2")
    tap(keyboard, LEFT)
    time.sleep(settle)
    core.require_route(
        session.request("state"), BROWSER2_ROUTE, "Left must move focus without selection"
    )
    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), INITIAL_ROUTE, "Return restores Browser 1")
    finish_cleanly(session)
    return {
        "evidence": "development-os-keyboard",
        "implementation": "slint",
        "status": "passed",
        "outcome": "focused-tab-keyboard-selection",
        "focus_action": "ordinary startup focus on Browser secondary tab bar",
        "os_key_sequence": ["Right", "Return", "Left", "Return"],
        "route_sequence": [
            "browser.browser1",
            "browser.browser1",
            "browser.browser2",
            "browser.browser2",
            "browser.browser1",
        ],
        "focus_without_selection_verified": True,
        "accessibility": accessibility,
        "pointer_input": False,
        "clean_exit": True,
    }


def run_bevy_sequence(
    session: core.ProcessSession,
    bridge,
    keyboard,
    *,
    settle: float = 1.0,
) -> dict[str, object]:
    """Use ordinary egui focus traversal and tab-bar arrows, with Return activation."""
    core.require_route(session.request("state"), INITIAL_ROUTE, "OS keyboard initial state")
    time.sleep(settle)
    accessibility = observe_application(session, bridge)

    for _ in range(11):
        tap(keyboard, os_smoke.TAB)
    time.sleep(settle)
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "Tab traversal must focus Browser 1 without selection"
    )
    tap(keyboard, RIGHT)
    time.sleep(settle)
    core.require_route(
        session.request("state"), INITIAL_ROUTE, "Right must focus Browser 2 without selection"
    )
    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), BROWSER2_ROUTE, "Return selects focused Browser 2")
    tap(keyboard, LEFT)
    time.sleep(settle)
    core.require_route(
        session.request("state"), BROWSER2_ROUTE, "Left must focus Browser 1 without selection"
    )
    tap(keyboard, RETURN)
    time.sleep(settle)
    core.require_route(session.request("state"), INITIAL_ROUTE, "Return restores Browser 1")
    finish_cleanly(session)
    return {
        "evidence": "development-os-keyboard",
        "implementation": "bevy-egui",
        "status": "passed",
        "outcome": "focused-tab-keyboard-selection",
        "focus_action": "ordinary egui Tab traversal to Browser 1",
        "os_key_sequence": ["Tab x11", "Right", "Return", "Left", "Return"],
        "route_sequence": [
            "browser.browser1",
            "browser.browser1",
            "browser.browser1",
            "browser.browser2",
            "browser.browser2",
            "browser.browser1",
        ],
        "focus_without_selection_verified": True,
        "accessibility": accessibility,
        "pointer_input": False,
        "clean_exit": True,
    }


def run_observation(
    session: core.ProcessSession,
    bridge,
    *,
    settle: float = 1.0,
) -> dict[str, object]:
    """Record only whether a non-QML process has an AT-SPI tree, then exit."""
    core.require_route(session.request("state"), INITIAL_ROUTE, "AT-SPI initial state")
    time.sleep(settle)
    record = observe_application(session, bridge)
    finish_cleanly(session)
    record.update({"pointer_input": False, "clean_exit": True})
    return record


class AtspiBridge:
    """Lazy host AT-SPI bindings; desktop traversal is always filtered by child PID."""

    def __init__(self, timeout: float):
        try:
            import gi

            gi.require_version("Atspi", "2.0")
            gi.require_version("Gio", "2.0")
            from gi.repository import Atspi, Gio, GLib
        except (ImportError, ValueError) as error:
            raise core.SmokeFailure("AT-SPI smoke requires PyGObject with Atspi and Gio") from error
        self.Atspi = Atspi
        self.Gio = Gio
        self.GLib = GLib
        self.timeout = timeout
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def host_enabled(self) -> bool:
        value = self.bus.call_sync(
            "org.a11y.Bus",
            "/org/a11y/bus",
            "org.freedesktop.DBus.Properties",
            "Get",
            self.GLib.Variant("(ss)", ("org.a11y.Status", "IsEnabled")),
            None,
            self.Gio.DBusCallFlags.NONE,
            int(self.timeout * 1000),
            None,
        )
        return bool(value.unpack()[0])

    def application_for_pid(self, pid: int):
        desktop = self.Atspi.get_desktop(0)
        matches = []
        for index in range(desktop.get_child_count()):
            application = desktop.get_child_at_index(index)
            if (
                application is not None
                and application.get_process_id() == pid
                and application.get_child_count() > 0
            ):
                matches.append(application)
        if len(matches) > 1:
            raise core.SmokeFailure(f"multiple populated AT-SPI applications match child PID {pid}")
        return matches[0] if matches else None

    def has_state(self, node, name: str) -> bool:
        state = getattr(self.Atspi.StateType, name)
        states = node.get_state_set()
        return states is not None and state in states.get_states()


def configured_adapter(base: core.Adapter, qml_host_scale: float | None) -> core.Adapter:
    adapter = screenshots.variant_adapter(base, "light", "100", "1200x750", qml_host_scale)
    environment = adapter.environment
    if adapter.implementation == "qml":
        environment = (*environment, ("QT_LINUX_ACCESSIBILITY_ALWAYS_ON", "1"))
    return core.Adapter(adapter.implementation, adapter.executable, adapter.asset_root, environment)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Development AT-SPI/focused-keyboard evidence; not pointer or screen-reader acceptance."
    )
    result.add_argument("--slint")
    result.add_argument("--qml")
    result.add_argument("--bevy-egui")
    result.add_argument("--bevy-asset-root")
    result.add_argument("--qml-host-scale", type=float)
    result.add_argument("--timeout", type=float, default=30.0)
    result.add_argument("--settle", type=float, default=1.0)
    result.add_argument("--jsonl")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    adapters = []
    if args.slint:
        adapters.append(core.Adapter("slint", args.slint))
    if args.qml:
        if (
            args.qml_host_scale is None
            or not math.isfinite(args.qml_host_scale)
            or args.qml_host_scale <= 0
        ):
            parser().error("QML requires a finite positive --qml-host-scale")
        adapters.append(core.Adapter("qml", args.qml))
    if args.bevy_egui:
        if not args.bevy_asset_root:
            parser().error("--bevy-asset-root is required with --bevy-egui")
        adapters.append(core.Adapter("bevy-egui", args.bevy_egui, args.bevy_asset_root))
    if not adapters:
        parser().error("at least one implementation executable is required")

    try:
        with (
            Path(args.jsonl).open("x", encoding="utf-8") if args.jsonl else nullcontext()
        ) as manifest, os_smoke.RemoteDesktopKeyboard(args.timeout) as keyboard:
            bridge = AtspiBridge(args.timeout)
            host_enabled = bridge.host_enabled()
            for base in adapters:
                adapter = configured_adapter(base, args.qml_host_scale)
                session = core.ProcessSession(adapter, args.timeout)
                try:
                    if adapter.implementation == "qml":
                        record = run_qml_sequence(
                            session, bridge, keyboard, settle=args.settle
                        )
                    elif adapter.implementation == "slint":
                        record = run_slint_sequence(
                            session, bridge, keyboard, settle=args.settle
                        )
                    else:
                        record = run_bevy_sequence(
                            session, bridge, keyboard, settle=args.settle
                        )
                except Exception as error:
                    record = {
                        "evidence": "development-atspi-smoke",
                        "implementation": adapter.implementation,
                        "status": "failed",
                        "error": str(error),
                    }
                    print(f"FAIL {adapter.implementation}: {error}", file=sys.stderr)
                    tail = session.diagnostic_tail()
                    if tail:
                        print(tail, file=sys.stderr)
                    if manifest is not None:
                        manifest.write(json.dumps(record, sort_keys=True) + "\n")
                        manifest.flush()
                    return 1
                finally:
                    session.close()
                record.update(
                    {
                        "host_atspi_enabled": host_enabled,
                        "requested_theme": "light",
                        "requested_scale_percent": "100",
                        "requested_size": "1200x750",
                        "executable_sha256": screenshots.executable_sha256(adapter.executable),
                        "screen_reader_acceptance_established": False,
                    }
                )
                if manifest is not None:
                    manifest.write(json.dumps(record, sort_keys=True) + "\n")
                    manifest.flush()
                label = "PASS" if record["status"] == "passed" else "GAP"
                print(f"{label} {adapter.implementation}: {record['outcome']} and clean exit")
                accessibility = record.get("accessibility")
                if accessibility is not None:
                    label = "GAP" if accessibility["status"] == "gap" else "OBSERVED"
                    print(f"{label} {adapter.implementation}: {accessibility['outcome']}")
    except Exception as error:
        print(f"FAIL AT-SPI runtime smoke: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
