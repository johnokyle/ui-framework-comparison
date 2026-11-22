#!/usr/bin/env python3

import argparse
import unittest
from unittest import mock

import runtime_pointer_smoke as pointer_smoke
import runtime_smoke as core


ROUTES = [
    pointer_smoke.INITIAL_ROUTE,
    pointer_smoke.INITIAL_ROUTE,
    pointer_smoke.BROWSER2_ROUTE,
    pointer_smoke.BROWSER3_ROUTE,
    pointer_smoke.CHARTING_ROUTE,
    pointer_smoke.STOCK_ROUTE,
    pointer_smoke.PIVOT_ROUTE,
    pointer_smoke.CHARTING_ROUTE,
    pointer_smoke.BROWSER3_ROUTE,
    pointer_smoke.INITIAL_ROUTE,
    pointer_smoke.QUANT_DEFAULT_ROUTE,
    core.Route("primary.quantviz", "quant.factor-structure"),
    core.Route("primary.quantviz", "quant.correlation"),
    core.Route("primary.quantviz", "quant.frontier"),
    core.Route("primary.quantviz", "quant.pca"),
    core.Route("primary.quantviz", "quant.regime"),
    core.Route("primary.quantviz", "quant.projection"),
    core.Route("primary.quantviz", "quant.knowledge"),
    core.Route("primary.quantviz", "quant.monte-carlo"),
    pointer_smoke.QUANT_DEFAULT_ROUTE,
    pointer_smoke.INITIAL_ROUTE,
]


def routes_for(implementation):
    return [
        pointer_smoke.QML_QUANT_DEFAULT_ROUTE
        if implementation == "qml" and index == 10
        else route
        for index, route in enumerate(ROUTES)
    ]


def complete_quant_routes_for(implementation):
    return (
        routes_for(implementation)[:-1]
        + [
            core.Route("primary.quantviz", "quant.network"),
            core.Route("primary.quantviz", "quant.order-book"),
        ]
        + routes_for(implementation)[-1:]
    )


class FakeSession:
    def __init__(self, routes=None, implementation="slint", select_replies=None):
        self.adapter = core.Adapter(implementation, "unused")
        self.routes = list(routes_for(implementation) if routes is None else routes)
        self.select_replies = list(select_replies or [])
        self.selection_requests = []
        self.state_count = 0
        self.quit_acknowledged = False
        self.finished = False

    def request(self, command):
        if command == "state":
            route = self.routes[self.state_count]
            self.state_count += 1
            return core.Reply(
                "state", "ok", primary=route.primary, secondary=route.secondary
            )
        if command.startswith("select-route "):
            self.selection_requests.append(command.removeprefix("select-route "))
            if not self.select_replies:
                raise AssertionError(command)
            return self.select_replies.pop(0)
        if command == "quit":
            self.quit_acknowledged = True
            return core.Reply("quit", "ok")
        raise AssertionError(command)

    def finish_quit(self):
        self.finished = self.quit_acknowledged


class FakePointer:
    def __init__(self):
        self.clicks = []
        self.normalizations = 0

    def normalize_origin(self):
        self.normalizations += 1

    def click(self, x, y):
        self.normalize_origin()
        self.clicks.append((x, y))


class FakeVariant:
    def __init__(self, signature, args):
        self.signature = signature
        self.args = args


class FakeDBusFlags:
    NONE = 0


class FakeBus:
    def __init__(self):
        self.calls = []

    def call_sync(self, *args):
        self.calls.append(args)


def complete_targets(implementation="slint"):
    return {
        (implementation, stable_id): (100.0 + 20 * index, 300.0)
        for index, stable_id in enumerate(pointer_smoke.TARGET_IDS)
    }


def complete_disabled_targets(implementation="slint"):
    targets = complete_targets(implementation)
    targets[(implementation, "advanced")] = (700.0, 100.0)
    if implementation == "slint":
        targets[(implementation, "show-diagnostics")] = (800.0, 100.0)
    return targets


def select_reply(target_id, route, status="ok"):
    return core.Reply(
        "select",
        status,
        requested=target_id,
        primary=route.primary,
        secondary=route.secondary,
    )


def disabled_select_replies(implementation):
    case = pointer_smoke.DISABLED_ROUTE_CASES[implementation]
    return [
        select_reply(case.target_id, case.selected),
        select_reply(case.target_id, case.fallback, case.disabled_status),
        select_reply(case.target_id, case.selected),
    ]


def disabled_state_routes(implementation):
    case = pointer_smoke.DISABLED_ROUTE_CASES[implementation]
    routes = routes_for(implementation)
    if implementation == "slint":
        routes.append(case.selected)
    routes.extend([case.fallback, case.fallback, case.fallback, pointer_smoke.INITIAL_ROUTE])
    return routes


def bare_pointer():
    pointer = pointer_smoke.RemoteDesktopPointer.__new__(
        pointer_smoke.RemoteDesktopPointer
    )
    pointer.session = "/session"
    pointer.timeout = 30.0
    pointer.bus = FakeBus()
    pointer.GLib = mock.Mock()
    pointer.GLib.Variant = FakeVariant
    pointer.Gio = mock.Mock()
    pointer.Gio.DBusCallFlags = FakeDBusFlags
    return pointer


class RuntimePointerSmokeTests(unittest.TestCase):
    def test_target_parser(self):
        key, point = pointer_smoke.parse_target("qml:browser.browser2=123.5,456")
        self.assertEqual(key, ("qml", "browser.browser2"))
        self.assertEqual(point, (123.5, 456.0))
        for invalid in (
            "qml:browser.browser4=1,2",
            "other:browser.browser2=1,2",
            "qml:browser.browser2=-1,2",
            "qml:browser.browser2=nan,2",
            "qml:browser.browser2=1",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(argparse.ArgumentTypeError):
                pointer_smoke.parse_target(invalid)

    def test_control_target_parser(self):
        key, point = pointer_smoke.parse_control_target("slint:advanced=123.5,456")
        self.assertEqual(key, ("slint", "advanced"))
        self.assertEqual(point, (123.5, 456.0))
        for invalid in (
            "qml:unknown=1,2",
            "other:advanced=1,2",
            "qml:advanced=-1,2",
            "qml:advanced=nan,2",
            "qml:advanced=1",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(argparse.ArgumentTypeError):
                pointer_smoke.parse_control_target(invalid)

    def test_duplicate_and_missing_targets_are_rejected(self):
        entries = [
            (("slint", "browser.browser2"), (1.0, 2.0)),
            (("slint", "browser.browser2"), (3.0, 4.0)),
        ]
        with self.assertRaises(core.SmokeFailure):
            pointer_smoke.target_map(entries)
        with self.assertRaises(core.SmokeFailure) as caught:
            pointer_smoke.require_targets({}, ["slint"])
        self.assertIn("slint:browser.browser1", str(caught.exception))
        pointer_smoke.require_targets(complete_targets("slint"), ["slint"])
        with self.assertRaises(core.SmokeFailure) as caught:
            pointer_smoke.require_targets(
                complete_targets("slint"), ["slint"], disabled_controls=True
            )
        self.assertIn("slint:advanced", str(caught.exception))
        self.assertIn("slint:show-diagnostics", str(caught.exception))
        pointer_smoke.require_targets(
            complete_disabled_targets("slint"), ["slint"], disabled_controls=True
        )
        base_targets = {
            key: point
            for key, point in complete_targets("slint").items()
            if key[1] in pointer_smoke.BASE_TARGET_IDS
        }
        pointer_smoke.require_targets(base_targets, ["slint"])
        with self.assertRaises(core.SmokeFailure) as caught:
            pointer_smoke.require_targets(
                base_targets, ["slint"], complete_quantitative=True
            )
        self.assertIn("slint:quant.network", str(caught.exception))
        self.assertIn("slint:quant.order-book", str(caught.exception))

    def test_complete_pointer_sequence_and_clean_quit(self):
        for implementation in pointer_smoke.IMPLEMENTATIONS:
            with self.subTest(implementation=implementation):
                session = FakeSession(implementation=implementation)
                pointer = FakePointer()
                with mock.patch.object(pointer_smoke.time, "sleep"):
                    record = pointer_smoke.run_pointer_sequence(
                        session,
                        pointer,
                        complete_targets(implementation),
                        settle=0,
                    )
                self.assertEqual(session.state_count, len(routes_for(implementation)))
                self.assertTrue(session.quit_acknowledged)
                self.assertTrue(session.finished)
                self.assertEqual(
                    record["route_sequence"],
                    [
                        route.secondary
                        for index, route in enumerate(routes_for(implementation))
                        if index != 1
                    ],
                )
                self.assertEqual(len(pointer.clicks), len(pointer_smoke.CLICK_SEQUENCE) + 1)
                self.assertEqual(pointer.normalizations, len(pointer.clicks))
                self.assertEqual(pointer.clicks[0], (460.0, 300.0))
                self.assertEqual(pointer.clicks[1], (100.0, 300.0))
                self.assertEqual(record["click_sequence"][0]["logical_point"], (460.0, 300.0))
                self.assertEqual(record["click_sequence"][0]["purpose"], "initial-focus-no-op")
                self.assertTrue(record["pointer_input"])
                self.assertFalse(record["keyboard_input"])
                self.assertFalse(record["programmatic_route_selection"])
                self.assertTrue(record["retained_secondary_verified"])
                self.assertTrue(record["charting_secondary_verified"])
                self.assertTrue(record["quantitative_secondary_verified"])
                self.assertFalse(record["rendered_frame_verified"])
                self.assertNotIn("complete_quantitative_pointer_verified", record)

    def test_complete_quantitative_sequence_and_clean_quit(self):
        for implementation in pointer_smoke.IMPLEMENTATIONS:
            with self.subTest(implementation=implementation):
                routes = complete_quant_routes_for(implementation)
                session = FakeSession(routes, implementation)
                pointer = FakePointer()
                with mock.patch.object(pointer_smoke.time, "sleep"):
                    record = pointer_smoke.run_pointer_sequence(
                        session,
                        pointer,
                        complete_targets(implementation),
                        settle=0,
                        complete_quantitative=True,
                    )
                self.assertEqual(session.state_count, len(routes))
                self.assertTrue(session.quit_acknowledged)
                self.assertTrue(session.finished)
                self.assertEqual(
                    record["route_sequence"],
                    [
                        route.secondary
                        for index, route in enumerate(routes)
                        if index != 1
                    ],
                )
                self.assertEqual(
                    record["route_sequence"][-3:],
                    ["quant.network", "quant.order-book", "browser.browser1"],
                )
                self.assertEqual(
                    len(pointer.clicks), len(pointer_smoke.CLICK_SEQUENCE) + 3
                )
                self.assertEqual(pointer.normalizations, len(pointer.clicks))
                self.assertEqual(
                    [
                        click["target_id"]
                        for click in record["click_sequence"][-3:]
                    ],
                    ["quant.network", "quant.order-book", "primary.browser"],
                )
                self.assertTrue(record["complete_quantitative_pointer_verified"])
                self.assertFalse(record["programmatic_route_selection"])
                self.assertEqual(
                    record["outcome"], "complete-quantitative-pointer-tab-selection"
                )

    def test_native_adapter_omits_only_the_fixed_size_override(self):
        size_variables = {
            "slint": "SLINTUITEST_CAPTURE_SIZE",
            "qml": "QMLUITEST_CAPTURE_SIZE",
            "bevy-egui": "BEVY_EGUI_CAPTURE_SIZE",
        }
        for implementation in pointer_smoke.IMPLEMENTATIONS:
            with self.subTest(implementation=implementation):
                base = core.Adapter(implementation, "unused")
                default = pointer_smoke.configured_adapter(base, 1.5)
                native = pointer_smoke.configured_adapter(base, 1.5, size="native")
                self.assertIn(
                    (size_variables[implementation], "1200x750"), default.environment
                )
                self.assertNotIn(size_variables[implementation], dict(native.environment))
                self.assertEqual(
                    native.environment,
                    tuple(
                        (name, value)
                        for name, value in default.environment
                        if name != size_variables[implementation]
                    ),
                )

    def test_disabled_control_sequence_and_clean_quit(self):
        for implementation in pointer_smoke.IMPLEMENTATIONS:
            with self.subTest(implementation=implementation):
                case = pointer_smoke.DISABLED_ROUTE_CASES[implementation]
                session = FakeSession(
                    disabled_state_routes(implementation),
                    implementation,
                    disabled_select_replies(implementation),
                )
                pointer = FakePointer()
                with mock.patch.object(pointer_smoke.time, "sleep"):
                    record = pointer_smoke.run_pointer_sequence(
                        session,
                        pointer,
                        complete_disabled_targets(implementation),
                        settle=0,
                        disabled_controls=True,
                    )
                self.assertEqual(session.state_count, len(disabled_state_routes(implementation)))
                self.assertEqual(session.selection_requests, [case.target_id] * 3)
                self.assertEqual(session.select_replies, [])
                self.assertTrue(session.quit_acknowledged)
                self.assertTrue(session.finished)
                self.assertEqual(
                    record["route_sequence"],
                    [
                        route.secondary
                        for index, route in enumerate(routes_for(implementation))
                        if index != 1
                    ]
                    + [
                        case.selected.secondary,
                        case.fallback.secondary,
                        case.selected.secondary,
                        pointer_smoke.INITIAL_ROUTE.secondary,
                    ],
                )
                phase_clicks = 4 if implementation == "slint" else 3
                self.assertEqual(
                    len(pointer.clicks), len(pointer_smoke.CLICK_SEQUENCE) + 1 + phase_clicks
                )
                self.assertEqual(pointer.normalizations, len(pointer.clicks))
                purposes = [
                    click["purpose"] for click in record["click_sequence"][-phase_clicks:]
                ]
                expected_purposes = [
                    "disable Advanced",
                    "re-enable Advanced",
                    "restore Browser 1 after disabled-control checks",
                ]
                if implementation == "slint":
                    expected_purposes.insert(0, "reveal Advanced control")
                self.assertEqual(purposes, expected_purposes)
                self.assertTrue(record["programmatic_route_selection"])
                self.assertTrue(record["advanced_pointer_toggle_verified"])
                self.assertEqual(
                    record["disabled_control"],
                    {
                        "target_id": case.target_id,
                        "fallback_id": case.fallback.secondary,
                        "disabled_request_status": case.disabled_status,
                    },
                )
                self.assertEqual(
                    record["outcome"], "pointer-tab-selection-and-disabled-controls"
                )
                self.assertTrue(record["clean_exit"])

    def test_qml_disabled_target_must_be_rejected_without_mutation(self):
        case = pointer_smoke.DISABLED_ROUTE_CASES["qml"]
        session = FakeSession(
            [case.fallback, case.fallback],
            "qml",
            [
                select_reply(case.target_id, case.selected),
                select_reply(case.target_id, case.fallback),
            ],
        )
        with mock.patch.object(pointer_smoke.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                pointer_smoke.run_disabled_control_phase(
                    session,
                    FakePointer(),
                    complete_disabled_targets("qml"),
                    settle=0,
                )
        self.assertEqual(session.selection_requests, [case.target_id] * 2)
        self.assertFalse(session.quit_acknowledged)

    def test_wrong_route_stops_without_quit(self):
        session = FakeSession(
            [
                pointer_smoke.INITIAL_ROUTE,
                pointer_smoke.INITIAL_ROUTE,
                pointer_smoke.INITIAL_ROUTE,
            ]
        )
        pointer = FakePointer()
        with mock.patch.object(pointer_smoke.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                pointer_smoke.run_pointer_sequence(
                    session,
                    pointer,
                    complete_targets(),
                    settle=0,
                )
        self.assertEqual(len(pointer.clicks), 2)
        self.assertFalse(session.quit_acknowledged)

    def test_session_requests_pointer_device_only(self):
        with mock.patch.object(
            pointer_smoke.os_smoke.RemoteDesktopKeyboard,
            "__init__",
            return_value=None,
        ) as initialize:
            pointer_smoke.RemoteDesktopPointer(12.5)
        initialize.assert_called_once_with(12.5, device_types=2)

    def test_relative_motion_uses_pointer_only_coordinates(self):
        pointer = bare_pointer()
        pointer.move_relative(123.5, -456.0)
        call = pointer.bus.calls[0]
        self.assertEqual(call[2], "org.freedesktop.portal.RemoteDesktop")
        self.assertEqual(call[3], "NotifyPointerMotion")
        self.assertEqual(call[4].signature, "(oa{sv}dd)")
        self.assertEqual(call[4].args, ("/session", {}, 123.5, -456.0))

    def test_click_normalizes_origin_before_target_motion(self):
        pointer = bare_pointer()
        with (
            mock.patch.object(pointer, "move_relative") as motion,
            mock.patch.object(pointer, "button") as button,
            mock.patch.object(pointer_smoke.time, "sleep"),
        ):
            pointer.click(123.5, 456.0)
        self.assertEqual(
            motion.call_args_list,
            [
                mock.call(pointer_smoke.ORIGIN_DELTA, pointer_smoke.ORIGIN_DELTA),
                mock.call(pointer_smoke.ORIGIN_DELTA, pointer_smoke.ORIGIN_DELTA),
                mock.call(123.5, 456.0),
            ],
        )
        self.assertEqual(button.call_args_list, [mock.call(1), mock.call(0)])

    def test_button_uses_left_evdev_code_and_requested_state(self):
        pointer = bare_pointer()
        pointer.button(1)
        call = pointer.bus.calls[0]
        self.assertEqual(call[3], "NotifyPointerButton")
        self.assertEqual(call[4].signature, "(oa{sv}iu)")
        self.assertEqual(call[4].args, ("/session", {}, 0x110, 1))

    def test_inactive_pointer_rejects_input(self):
        pointer = bare_pointer()
        pointer.session = None
        with self.assertRaises(core.SmokeFailure):
            pointer.move_relative(1, 2)


if __name__ == "__main__":
    unittest.main()
