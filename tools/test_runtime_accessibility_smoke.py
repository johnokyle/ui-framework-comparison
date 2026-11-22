#!/usr/bin/env python3

from types import SimpleNamespace
import unittest
from unittest import mock

import runtime_accessibility_smoke as accessibility
import runtime_os_smoke as os_smoke
import runtime_smoke as core


class FakeNode:
    def __init__(self, name, role="label", *, showing=True, checked=False, children=()):
        self.name = name
        self.role = role
        self.states = {"SHOWING"} if showing else set()
        if checked:
            self.states.add("CHECKED")
        self.children = list(children)
        self.focusable = role == "page tab"
        self.tree = None

    def get_name(self):
        return self.name

    def get_role_name(self):
        return self.role

    def get_child_count(self):
        return len(self.children)

    def get_child_at_index(self, index):
        return self.children[index]

    def get_n_actions(self):
        return 1 if self.focusable else 0

    def get_action_name(self, index):
        if index == 0 and self.focusable:
            return "SetFocus"
        raise IndexError(index)

    def do_action(self, index):
        if self.get_action_name(index) != "SetFocus":
            return False
        for node in self.tree:
            node.states.discard("FOCUSED")
        self.states.add("FOCUSED")
        return True


class FakeBridge:
    def __init__(self, root):
        self.root = root
        self.nodes = list(accessibility.walk_tree(root))
        for node in self.nodes:
            node.tree = self.nodes

    def application_for_pid(self, pid):
        return self.root if pid == 42 else None

    def has_state(self, node, name):
        return name in node.states


class FakeKeyboard:
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.keys = []

    def keysym(self, keysym, state):
        if state:
            self.keys.append(keysym)
            return
        if keysym in (accessibility.RIGHT, accessibility.LEFT):
            source, target = (
                (self.first, self.second)
                if keysym == accessibility.RIGHT
                else (self.second, self.first)
            )
            if "FOCUSED" in source.states:
                source.states.discard("FOCUSED")
                target.states.add("FOCUSED")
        elif keysym == accessibility.RETURN:
            selected = self.second if "FOCUSED" in self.second.states else self.first
            other = self.first if selected is self.second else self.second
            selected.states.add("CHECKED")
            other.states.discard("CHECKED")


class RecordingKeyboard:
    def __init__(self):
        self.keys = []

    def keysym(self, keysym, state):
        if state:
            self.keys.append(keysym)


class FakeSession:
    def __init__(self, routes, implementation="qml"):
        self.adapter = core.Adapter(implementation, "unused")
        self.process = SimpleNamespace(pid=42)
        self.routes = list(routes)
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


def browser_tree():
    first = FakeNode("Browser #1", "page tab", checked=True)
    second = FakeNode("Browser #2", "page tab")
    labels = [
        FakeNode("Browser", "page tab", checked=True),
        FakeNode("Charting", "page tab"),
        FakeNode("Quantitative Visualization", "page tab"),
        first,
        second,
        FakeNode("Browser #3", "page tab"),
        FakeNode("Symbol"),
        FakeNode("Change %"),
        FakeNode(
            "Primary: Browser (primary.browser) Secondary: Browser #1 (browser.browser1)"
        ),
    ]
    frame = FakeNode("UI Framework Test Application", "frame", children=labels)
    return FakeNode("appQmlUITest", "application", children=[frame]), first, second


class RuntimeAccessibilitySmokeTests(unittest.TestCase):
    def test_walk_tree_is_ordered_and_bounded(self):
        root, _, _ = browser_tree()
        nodes = list(accessibility.walk_tree(root))
        self.assertEqual(nodes[0], root)
        self.assertEqual(nodes[2], root.children[0].children[0])
        with self.assertRaises(core.SmokeFailure):
            list(accessibility.walk_tree(root, max_nodes=2))

    def test_visible_tab_rejects_hidden_or_duplicate_matches(self):
        root, first, _ = browser_tree()
        bridge = FakeBridge(root)
        self.assertIs(accessibility.visible_tab(bridge, bridge.nodes, "Browser #1"), first)
        first.states.discard("SHOWING")
        with self.assertRaises(core.SmokeFailure):
            accessibility.visible_tab(bridge, bridge.nodes, "Browser #1")

    def test_qml_focus_arrows_return_and_clean_restoration(self):
        root, first, second = browser_tree()
        bridge = FakeBridge(root)
        keyboard = FakeKeyboard(first, second)
        session = FakeSession(
            [
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.INITIAL_ROUTE,
            ]
        )
        with mock.patch.object(accessibility.time, "sleep"):
            record = accessibility.run_qml_sequence(session, bridge, keyboard, settle=0)
        self.assertEqual(
            keyboard.keys,
            [accessibility.RIGHT, accessibility.RETURN, accessibility.LEFT, accessibility.RETURN],
        )
        self.assertEqual(session.state_count, 5)
        self.assertTrue(record["focus_without_selection_verified"])
        self.assertFalse(record["pointer_input"])
        self.assertTrue(record["clean_exit"])
        self.assertTrue(session.finished)

    def test_qml_rejects_selection_change_from_arrow(self):
        root, first, second = browser_tree()
        session = FakeSession(
            [accessibility.INITIAL_ROUTE, accessibility.BROWSER2_ROUTE]
        )
        keyboard = FakeKeyboard(first, second)
        with mock.patch.object(accessibility.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                accessibility.run_qml_sequence(session, FakeBridge(root), keyboard, settle=0)
        self.assertEqual(keyboard.keys, [accessibility.RIGHT])
        self.assertFalse(session.quit_acknowledged)

    def test_qml_requires_focus_to_follow_right(self):
        root, first, second = browser_tree()
        session = FakeSession([accessibility.INITIAL_ROUTE])
        keyboard = FakeKeyboard(first, second)
        keyboard.keysym = lambda keysym, state: (
            keyboard.keys.append(keysym) if state else None
        )
        with mock.patch.object(accessibility.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                accessibility.run_qml_sequence(session, FakeBridge(root), keyboard, settle=0)
        self.assertFalse(session.quit_acknowledged)

    def test_qml_requires_set_focus_action(self):
        root, first, second = browser_tree()
        first.focusable = False
        session = FakeSession([accessibility.INITIAL_ROUTE])
        with mock.patch.object(accessibility.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                accessibility.run_qml_sequence(
                    session, FakeBridge(root), FakeKeyboard(first, second), settle=0
                )
        self.assertFalse(session.quit_acknowledged)

    def test_slint_startup_focus_arrows_return_and_clean_restoration(self):
        root, _, _ = browser_tree()
        bridge = FakeBridge(root)
        bridge.root = None
        keyboard = RecordingKeyboard()
        session = FakeSession(
            [
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.INITIAL_ROUTE,
            ],
            implementation="slint",
        )
        with mock.patch.object(accessibility.time, "sleep"):
            record = accessibility.run_slint_sequence(
                session, bridge, keyboard, settle=0
            )
        self.assertEqual(
            keyboard.keys,
            [accessibility.RIGHT, accessibility.RETURN, accessibility.LEFT, accessibility.RETURN],
        )
        self.assertEqual(record["status"], "passed")
        self.assertEqual(record["accessibility"]["status"], "gap")
        self.assertTrue(record["focus_without_selection_verified"])
        self.assertTrue(session.finished)

    def test_slint_rejects_selection_change_from_focus_only_arrow(self):
        root, _, _ = browser_tree()
        bridge = FakeBridge(root)
        bridge.root = None
        session = FakeSession(
            [accessibility.INITIAL_ROUTE, accessibility.BROWSER2_ROUTE],
            implementation="slint",
        )
        with mock.patch.object(accessibility.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                accessibility.run_slint_sequence(
                    session, bridge, RecordingKeyboard(), settle=0
                )
        self.assertFalse(session.quit_acknowledged)

    def test_bevy_tab_traversal_arrows_return_and_clean_restoration(self):
        root, _, _ = browser_tree()
        bridge = FakeBridge(root)
        bridge.root = None
        keyboard = RecordingKeyboard()
        session = FakeSession(
            [
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.INITIAL_ROUTE,
            ],
            implementation="bevy-egui",
        )
        with mock.patch.object(accessibility.time, "sleep"):
            record = accessibility.run_bevy_sequence(
                session, bridge, keyboard, settle=0
            )
        self.assertEqual(
            keyboard.keys,
            [os_smoke.TAB] * 11
            + [
                accessibility.RIGHT,
                accessibility.RETURN,
                accessibility.LEFT,
                accessibility.RETURN,
            ],
        )
        self.assertEqual(record["status"], "passed")
        self.assertEqual(record["accessibility"]["status"], "gap")
        self.assertEqual(record["os_key_sequence"][0], "Tab x11")
        self.assertTrue(session.finished)

    def test_bevy_rejects_selection_change_from_left(self):
        root, _, _ = browser_tree()
        bridge = FakeBridge(root)
        bridge.root = None
        session = FakeSession(
            [
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.INITIAL_ROUTE,
                accessibility.BROWSER2_ROUTE,
                accessibility.INITIAL_ROUTE,
            ],
            implementation="bevy-egui",
        )
        with mock.patch.object(accessibility.time, "sleep"):
            with self.assertRaises(core.SmokeFailure):
                accessibility.run_bevy_sequence(
                    session, bridge, RecordingKeyboard(), settle=0
                )
        self.assertFalse(session.quit_acknowledged)

    def test_missing_non_qml_tree_is_gap_with_clean_exit(self):
        root, _, _ = browser_tree()
        bridge = FakeBridge(root)
        bridge.root = None
        session = FakeSession([accessibility.INITIAL_ROUTE], implementation="slint")
        with mock.patch.object(accessibility.time, "sleep"):
            record = accessibility.run_observation(session, bridge, settle=0)
        self.assertEqual(record["status"], "gap")
        self.assertEqual(record["outcome"], "no-process-accessible")
        self.assertIsNone(record["tree"])
        self.assertTrue(session.finished)

    def test_observed_non_qml_tree_is_not_an_input_pass(self):
        root, _, _ = browser_tree()
        session = FakeSession([accessibility.INITIAL_ROUTE], implementation="bevy-egui")
        with mock.patch.object(accessibility.time, "sleep"):
            record = accessibility.run_observation(session, FakeBridge(root), settle=0)
        self.assertEqual(record["status"], "observed")
        self.assertEqual(record["outcome"], "tree-observed-no-input-assertion")
        self.assertFalse(record["pointer_input"])
        self.assertTrue(session.finished)

    def test_capture_variants_and_qml_activation_are_child_only(self):
        qml = accessibility.configured_adapter(core.Adapter("qml", "qml"), 5 / 3)
        environment = dict(qml.environment)
        self.assertEqual(environment["QT_SCALE_FACTOR"], "0.6")
        self.assertEqual(environment["QMLUITEST_CAPTURE_SIZE"], "1200x750")
        self.assertEqual(environment["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"], "1")
        slint = accessibility.configured_adapter(core.Adapter("slint", "slint"), None)
        self.assertNotIn("QT_LINUX_ACCESSIBILITY_ALWAYS_ON", dict(slint.environment))
        self.assertIn(("SLINT_SCALE_FACTOR", "1"), slint.environment)


if __name__ == "__main__":
    unittest.main()
