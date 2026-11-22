#!/usr/bin/env python3

import unittest

import runtime_os_smoke as os_smoke
import runtime_smoke as core


class FakeKeyboard:
    def __init__(self):
        self.ctrl_tab_count = 0

    def ctrl_tab(self):
        self.ctrl_tab_count += 1


class FakeSession:
    def __init__(self, routes=None, implementation="slint"):
        self.adapter = core.Adapter(implementation, "unused")
        self.routes = list(
            routes
            or (
                os_smoke.INITIAL_ROUTE,
                *os_smoke.cycling_routes(implementation),
            )
        )
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
        if command == "quit":
            self.quit_acknowledged = True
            return core.Reply("quit", "ok")
        raise AssertionError(command)

    def finish_quit(self):
        self.finished = self.quit_acknowledged


class RuntimeOsSmokeTests(unittest.TestCase):
    def test_request_path_uses_portal_sender_rules(self):
        self.assertEqual(
            os_smoke.request_path(":1.234", "token"),
            "/org/freedesktop/portal/desktop/request/1_234/token",
        )

    def test_three_ctrl_tab_cycles_and_clean_quit(self):
        session = FakeSession()
        keyboard = FakeKeyboard()
        os_smoke.run_keyboard_sequence(session, keyboard, settle=0)
        self.assertEqual(keyboard.ctrl_tab_count, 3)
        self.assertEqual(session.state_count, 4)
        self.assertTrue(session.quit_acknowledged)
        self.assertTrue(session.finished)

    def test_qml_uses_its_canonical_order_book_default(self):
        session = FakeSession(implementation="qml")
        keyboard = FakeKeyboard()
        os_smoke.run_keyboard_sequence(session, keyboard, settle=0)
        self.assertEqual(keyboard.ctrl_tab_count, 3)
        self.assertTrue(session.finished)

    def test_wrong_initial_route_is_rejected_without_input(self):
        session = FakeSession(
            [core.Route("primary.quantviz", "quant.monte-carlo")]
        )
        keyboard = FakeKeyboard()
        with self.assertRaises(core.SmokeFailure):
            os_smoke.run_keyboard_sequence(session, keyboard, settle=0)
        self.assertEqual(keyboard.ctrl_tab_count, 0)
        self.assertFalse(session.quit_acknowledged)

    def test_wrong_post_input_route_is_rejected_without_quit(self):
        session = FakeSession(
            [os_smoke.INITIAL_ROUTE, os_smoke.INITIAL_ROUTE]
        )
        keyboard = FakeKeyboard()
        with self.assertRaises(core.SmokeFailure):
            os_smoke.run_keyboard_sequence(session, keyboard, settle=0)
        self.assertEqual(keyboard.ctrl_tab_count, 1)
        self.assertFalse(session.quit_acknowledged)


if __name__ == "__main__":
    unittest.main()
