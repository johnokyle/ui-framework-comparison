#!/usr/bin/env python3
"""Development-only OS pointer smoke through a RemoteDesktop pointer session."""

from __future__ import annotations

import argparse
from contextlib import nullcontext
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
import time

import runtime_os_smoke as os_smoke
import runtime_screenshot as screenshots
import runtime_smoke as core

INITIAL_ROUTE = core.Route("primary.browser", "browser.browser1")
BROWSER2_ROUTE = core.Route("primary.browser", "browser.browser2")
BROWSER3_ROUTE = core.Route("primary.browser", "browser.browser3")
CHARTING_ROUTE = core.Route("primary.charting", "chart.analytical")
STOCK_ROUTE = core.Route("primary.charting", "chart.stock")
PIVOT_ROUTE = core.Route("primary.charting", "chart.pivot")
QUANT_DEFAULT_ROUTE = core.Route("primary.quantviz", "quant.vol-surface")
QML_QUANT_DEFAULT_ROUTE = core.Route("primary.quantviz", "quant.order-book")
LEFT_BUTTON = 0x110
ORIGIN_DELTA = -100000.0


@dataclass(frozen=True)
class ClickStep:
    target_id: str
    expected: core.Route
    description: str


@dataclass(frozen=True)
class DisabledRouteCase:
    target_id: str
    selected: core.Route
    fallback: core.Route
    disabled_status: str


DISABLED_ROUTE_CASES = {
    "slint": DisabledRouteCase(
        "quant.order-book",
        core.Route("primary.quantviz", "quant.order-book"),
        core.Route("primary.quantviz", "quant.monte-carlo"),
        "ok",
    ),
    "qml": DisabledRouteCase(
        "quant.knowledge",
        core.Route("primary.quantviz", "quant.knowledge"),
        core.Route("primary.quantviz", "quant.vol-surface"),
        "rejected",
    ),
    "bevy-egui": DisabledRouteCase(
        "quant.order-book",
        core.Route("primary.quantviz", "quant.order-book"),
        core.Route("primary.quantviz", "quant.monte-carlo"),
        "ok",
    ),
}
CONTROL_TARGET_IDS = ("advanced", "show-diagnostics")


CLICK_SEQUENCE = (
    ClickStep("browser.browser2", BROWSER2_ROUTE, "pointer selects Browser 2"),
    ClickStep("browser.browser3", BROWSER3_ROUTE, "pointer selects Browser 3"),
    ClickStep("primary.charting", CHARTING_ROUTE, "pointer selects Charting"),
    ClickStep("chart.stock", STOCK_ROUTE, "pointer selects Stock"),
    ClickStep("chart.pivot", PIVOT_ROUTE, "pointer selects Pivot"),
    ClickStep("chart.analytical", CHARTING_ROUTE, "pointer restores Analytical"),
    ClickStep("primary.browser", BROWSER3_ROUTE, "pointer restores Browser with retained Browser 3"),
    ClickStep("browser.browser1", INITIAL_ROUTE, "pointer restores Browser 1"),
    ClickStep("primary.quantviz", QUANT_DEFAULT_ROUTE, "pointer selects Quantitative"),
    ClickStep("quant.factor-structure", core.Route("primary.quantviz", "quant.factor-structure"), "pointer selects Factor Structure"),
    ClickStep("quant.correlation", core.Route("primary.quantviz", "quant.correlation"), "pointer selects Correlation"),
    ClickStep("quant.frontier", core.Route("primary.quantviz", "quant.frontier"), "pointer selects Efficient Frontier"),
    ClickStep("quant.pca", core.Route("primary.quantviz", "quant.pca"), "pointer selects PCA Manifold"),
    ClickStep("quant.regime", core.Route("primary.quantviz", "quant.regime"), "pointer selects Regime Map"),
    ClickStep("quant.projection", core.Route("primary.quantviz", "quant.projection"), "pointer selects High-Dimensional Projection"),
    ClickStep("quant.knowledge", core.Route("primary.quantviz", "quant.knowledge"), "pointer selects Knowledge Graph"),
    ClickStep("quant.monte-carlo", core.Route("primary.quantviz", "quant.monte-carlo"), "pointer selects Monte Carlo"),
    ClickStep("quant.vol-surface", QUANT_DEFAULT_ROUTE, "pointer selects Volatility Surface"),
    ClickStep("primary.browser", INITIAL_ROUTE, "pointer restores Browser with retained Browser 1"),
)
TARGET_IDS = tuple(step.target_id for step in CLICK_SEQUENCE)
IMPLEMENTATIONS = ("slint", "qml", "bevy-egui")


def expected_route(step: ClickStep, implementation: str) -> core.Route:
    if step.target_id == "primary.quantviz" and implementation == "qml":
        return QML_QUANT_DEFAULT_ROUTE
    return step.expected


def parse_target(text: str) -> tuple[tuple[str, str], tuple[float, float]]:
    try:
        owner, coordinates = text.split("=", 1)
        implementation, stable_id = owner.split(":", 1)
        x_text, y_text = coordinates.split(",", 1)
        point = float(x_text), float(y_text)
    except (ValueError, TypeError) as error:
        raise argparse.ArgumentTypeError(
            "target must be implementation:stable-id=X,Y"
        ) from error
    if implementation not in IMPLEMENTATIONS or stable_id not in TARGET_IDS:
        raise argparse.ArgumentTypeError("target names an unknown implementation or click target")
    if not all(math.isfinite(value) and value >= 0 for value in point):
        raise argparse.ArgumentTypeError("target coordinates must be finite and nonnegative")
    return (implementation, stable_id), point


def parse_control_target(text: str) -> tuple[tuple[str, str], tuple[float, float]]:
    try:
        owner, coordinates = text.split("=", 1)
        implementation, control_id = owner.split(":", 1)
        x_text, y_text = coordinates.split(",", 1)
        point = float(x_text), float(y_text)
    except (ValueError, TypeError) as error:
        raise argparse.ArgumentTypeError(
            "control target must be implementation:control-id=X,Y"
        ) from error
    if implementation not in IMPLEMENTATIONS or control_id not in CONTROL_TARGET_IDS:
        raise argparse.ArgumentTypeError(
            "control target names an unknown implementation or control"
        )
    if not all(math.isfinite(value) and value >= 0 for value in point):
        raise argparse.ArgumentTypeError(
            "control target coordinates must be finite and nonnegative"
        )
    return (implementation, control_id), point


def target_map(entries) -> dict[tuple[str, str], tuple[float, float]]:
    result = {}
    for key, point in entries:
        if key in result:
            raise core.SmokeFailure(f"duplicate pointer target: {key[0]}:{key[1]}")
        result[key] = point
    return result


def require_targets(targets, implementations, *, disabled_controls=False) -> None:
    missing = [
        f"{implementation}:{stable_id}"
        for implementation in implementations
        for stable_id in TARGET_IDS
        if (implementation, stable_id) not in targets
    ]
    if disabled_controls:
        missing.extend(
            f"{implementation}:{control_id}"
            for implementation in implementations
            for control_id in (
                ("advanced", "show-diagnostics")
                if implementation == "slint"
                else ("advanced",)
            )
            if (implementation, control_id) not in targets
        )
    if missing:
        raise core.SmokeFailure(f"missing pointer targets: {', '.join(missing)}")


def finish_cleanly(session: core.ProcessSession) -> None:
    reply = session.request("quit")
    if reply.status != "ok":
        raise core.SmokeFailure("OS pointer smoke quit was not acknowledged")
    session.finish_quit()


def run_disabled_control_phase(
    session: core.ProcessSession,
    pointer,
    targets,
    *,
    settle: float,
) -> dict[str, object]:
    """Toggle Advanced with real pointer input; use stable IDs for target requests."""
    implementation = session.adapter.implementation
    case = DISABLED_ROUTE_CASES[implementation]
    route_sequence = [case.selected.secondary]
    click_records = []

    def click(target_id: str, purpose: str) -> None:
        logical_point = targets[(implementation, target_id)]
        pointer.click(*logical_point)
        time.sleep(settle)
        click_records.append(
            {
                "target_id": target_id,
                "logical_point": logical_point,
                "purpose": purpose,
            }
        )

    enabled = session.request(f"select-route {case.target_id}")
    core.require_selection(enabled, case.target_id, case.selected)

    if implementation == "slint":
        click("show-diagnostics", "reveal Advanced control")
        core.require_route(
            session.request("state"),
            case.selected,
            "Show Diagnostics preserves the enabled target",
        )

    click("advanced", "disable Advanced")
    core.require_route(
        session.request("state"),
        case.fallback,
        "disabling Advanced selects the nearest enabled route",
    )
    route_sequence.append(case.fallback.secondary)

    disabled = session.request(f"select-route {case.target_id}")
    if disabled.requested != case.target_id:
        raise core.SmokeFailure(
            f"disabled select {case.target_id}: reply identified "
            f"{disabled.requested!r} as the request"
        )
    if disabled.status != case.disabled_status or disabled.route != case.fallback:
        raise core.SmokeFailure(
            f"disabled select {case.target_id}: expected {case.disabled_status} at "
            f"{case.fallback.primary}/{case.fallback.secondary}, received "
            f"{disabled.status} at {disabled.primary}/{disabled.secondary}"
        )
    core.require_route(
        session.request("state"),
        case.fallback,
        "disabled target request preserves the fallback route",
    )

    click("advanced", "re-enable Advanced")
    core.require_route(
        session.request("state"),
        case.fallback,
        "re-enabling Advanced retains the fallback route",
    )
    reenabled = session.request(f"select-route {case.target_id}")
    core.require_selection(reenabled, case.target_id, case.selected)
    route_sequence.append(case.selected.secondary)

    click("primary.browser", "restore Browser 1 after disabled-control checks")
    core.require_route(
        session.request("state"),
        INITIAL_ROUTE,
        "disabled-control phase restores Browser 1",
    )
    route_sequence.append(INITIAL_ROUTE.secondary)
    return {
        "target_id": case.target_id,
        "fallback_id": case.fallback.secondary,
        "disabled_request_status": disabled.status,
        "route_sequence": route_sequence,
        "click_sequence": click_records,
    }


def run_pointer_sequence(
    session: core.ProcessSession,
    pointer,
    targets,
    *,
    settle: float,
    disabled_controls: bool = False,
) -> dict[str, object]:
    """Activate common tabs through real pointer input and semantic readback only."""
    implementation = session.adapter.implementation
    core.require_route(session.request("state"), INITIAL_ROUTE, "OS pointer initial state")
    time.sleep(settle)
    focus_point = targets[(implementation, "primary.browser")]
    pointer.click(*focus_point)
    time.sleep(settle)
    core.require_route(
        session.request("state"),
        INITIAL_ROUTE,
        "OS pointer initial focus click is a no-op",
    )
    route_sequence = [INITIAL_ROUTE.secondary]
    click_records = [
        {
            "target_id": "primary.browser",
            "logical_point": focus_point,
            "purpose": "initial-focus-no-op",
        }
    ]
    for step in CLICK_SEQUENCE:
        expected = expected_route(step, implementation)
        logical_point = targets[(implementation, step.target_id)]
        pointer.click(*logical_point)
        time.sleep(settle)
        core.require_route(session.request("state"), expected, step.description)
        route_sequence.append(expected.secondary)
        click_records.append(
            {
                "target_id": step.target_id,
                "logical_point": logical_point,
            }
        )
    disabled_record = None
    if disabled_controls:
        disabled_record = run_disabled_control_phase(
            session, pointer, targets, settle=settle
        )
        route_sequence.extend(disabled_record["route_sequence"])
        click_records.extend(disabled_record["click_sequence"])
    finish_cleanly(session)
    record = {
        "evidence": "development-os-pointer",
        "implementation": implementation,
        "status": "passed",
        "outcome": (
            "pointer-tab-selection-and-disabled-controls"
            if disabled_record is not None
            else "pointer-tab-selection"
        ),
        "route_sequence": route_sequence,
        "click_sequence": click_records,
        "pointer_input": True,
        "pointer_motion": "relative-with-top-left-normalization",
        "keyboard_input": False,
        "programmatic_route_selection": disabled_record is not None,
        "retained_secondary_verified": True,
        "charting_secondary_verified": True,
        "quantitative_secondary_verified": True,
        "clean_exit": True,
        "rendered_frame_verified": False,
    }
    if disabled_record is not None:
        record["disabled_control"] = {
            key: value
            for key, value in disabled_record.items()
            if key not in {"route_sequence", "click_sequence"}
        }
        record["advanced_pointer_toggle_verified"] = True
    return record


class RemoteDesktopPointer(os_smoke.RemoteDesktopKeyboard):
    """Pointer-only RemoteDesktop session using compositor-logical relative motion."""

    def __init__(self, timeout: float):
        super().__init__(timeout, device_types=2)

    def _notify(self, method: str, signature: str, args: tuple) -> None:
        if self.session is None:
            raise core.SmokeFailure("remote-desktop pointer session is not active")
        self.bus.call_sync(
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.RemoteDesktop",
            method,
            self.GLib.Variant(signature, args),
            None,
            self.Gio.DBusCallFlags.NONE,
            int(self.timeout * 1000),
            None,
        )

    def move_relative(self, dx: float, dy: float) -> None:
        self._notify(
            "NotifyPointerMotion",
            "(oa{sv}dd)",
            (self.session, {}, dx, dy),
        )

    def normalize_origin(self) -> None:
        # Large negative deltas clamp at the desktop's top-left independently of
        # the prior pointer location; repeating covers compositor-specific clamps.
        for _ in range(2):
            self.move_relative(ORIGIN_DELTA, ORIGIN_DELTA)
            time.sleep(0.05)

    def click(self, x: float, y: float) -> None:
        self.normalize_origin()
        self.move_relative(x, y)
        time.sleep(0.2)
        self.button(1)
        time.sleep(0.12)
        self.button(0)
        time.sleep(0.1)

    def button(self, state: int) -> None:
        self._notify(
            "NotifyPointerButton",
            "(oa{sv}iu)",
            (self.session, {}, LEFT_BUTTON, state),
        )


def configured_adapter(base: core.Adapter, qml_host_scale: float | None) -> core.Adapter:
    return screenshots.variant_adapter(base, "light", "100", "1200x750", qml_host_scale)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Development OS-pointer tab smoke; not visual or performance acceptance."
    )
    result.add_argument("--slint")
    result.add_argument("--qml")
    result.add_argument("--bevy-egui")
    result.add_argument("--bevy-asset-root")
    result.add_argument("--qml-host-scale", type=float)
    result.add_argument(
        "--target",
        action="append",
        default=[],
        type=parse_target,
        metavar="IMPLEMENTATION:STABLE-ID=X,Y",
        help="target center in compositor-logical desktop coordinates; repeat for every selected application",
    )
    result.add_argument(
        "--disabled-controls",
        action="store_true",
        help="also toggle Advanced and check the implementation-specific disabled route",
    )
    result.add_argument(
        "--control-target",
        action="append",
        default=[],
        type=parse_control_target,
        metavar="IMPLEMENTATION:CONTROL-ID=X,Y",
        help="Advanced or Slint Show Diagnostics center; required with --disabled-controls",
    )
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
        adapters.append(
            core.Adapter("bevy-egui", args.bevy_egui, args.bevy_asset_root)
        )
    if not adapters:
        parser().error("at least one implementation executable is required")

    try:
        targets = target_map([*args.target, *args.control_target])
        require_targets(
            targets,
            [adapter.implementation for adapter in adapters],
            disabled_controls=args.disabled_controls,
        )
        with (
            Path(args.jsonl).open("x", encoding="utf-8") if args.jsonl else nullcontext()
        ) as manifest, RemoteDesktopPointer(args.timeout) as pointer:
            for base in adapters:
                adapter = configured_adapter(base, args.qml_host_scale)
                session = core.ProcessSession(adapter, args.timeout)
                try:
                    record = run_pointer_sequence(
                        session,
                        pointer,
                        targets,
                        settle=args.settle,
                        disabled_controls=args.disabled_controls,
                    )
                except Exception as error:
                    record = {
                        "evidence": "development-os-pointer",
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
                        "requested_theme": "light",
                        "requested_scale_percent": "100",
                        "requested_size": "1200x750",
                        "executable_sha256": screenshots.executable_sha256(adapter.executable),
                    }
                )
                if manifest is not None:
                    manifest.write(json.dumps(record, sort_keys=True) + "\n")
                    manifest.flush()
                print(f"PASS {adapter.implementation}: {record['outcome']} and clean exit")
    except Exception as error:
        print(f"FAIL OS pointer runtime smoke: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
