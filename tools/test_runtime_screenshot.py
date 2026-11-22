#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

import runtime_screenshot as capture
import runtime_smoke as core


def png_header(width=640, height=480):
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"test-image-data"
    )


class FakePortal:
    def __init__(self, source: Path):
        self.source = source
        self.capture_count = 0

    def capture(self):
        self.capture_count += 1
        return self.source.as_uri()


class FakeSession:
    def __init__(self, executable="unused", initial=core.Route("primary.browser", "browser.browser1")):
        self.adapter = core.Adapter("slint", executable)
        self.initial = initial
        self.state_count = 0
        self.quit_acknowledged = False
        self.finished = False

    def request(self, command):
        if command == "state":
            self.state_count += 1
            return core.Reply(
                "state",
                "ok",
                primary=self.initial.primary,
                secondary=self.initial.secondary,
            )
        if command == "quit":
            self.quit_acknowledged = True
            return core.Reply("quit", "ok")
        raise AssertionError(command)

    def finish_quit(self):
        self.finished = self.quit_acknowledged

    def close(self):
        pass

    def diagnostic_tail(self):
        return ""


class RuntimeScreenshotTests(unittest.TestCase):
    def test_request_path_uses_portal_sender_rules(self):
        self.assertEqual(
            capture.request_path(":1.234", "token"),
            "/org/freedesktop/portal/desktop/request/1_234/token",
        )

    def test_file_uri_decodes_escaped_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture with spaces.png"
            self.assertEqual(capture.file_uri_path(path.as_uri()), str(path))

    def test_non_file_uri_is_rejected(self):
        with self.assertRaises(core.SmokeFailure):
            capture.file_uri_path("https://example.invalid/capture.png")

    def test_copy_capture_records_png_metadata_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.png"
            content = png_header(1920, 1080)
            source.write_bytes(content)
            destination = root / "destination.png"
            record = capture.copy_capture(source.as_uri(), destination)
            self.assertEqual(record["width"], 1920)
            self.assertEqual(record["height"], 1080)
            self.assertEqual(record["bytes"], len(content))
            self.assertEqual(record["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(destination.read_bytes(), content)
            with self.assertRaises(FileExistsError):
                capture.copy_capture(source.as_uri(), destination)

    def test_capture_sequence_preserves_route_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "portal result.png"
            source.write_bytes(png_header())
            output = root / "output"
            output.mkdir()
            portal = FakePortal(source)
            session = FakeSession()
            with mock.patch.object(
                capture, "executable_sha256", return_value="executable-hash"
            ):
                record = capture.run_capture(session, portal, output, settle=0)
            self.assertEqual(portal.capture_count, 1)
            self.assertEqual(session.state_count, 2)
            self.assertTrue(session.quit_acknowledged)
            self.assertTrue(session.finished)
            self.assertEqual(record["scope"], "full-desktop")
            self.assertFalse(record["equivalence_established"])
            self.assertTrue(record["clean_exit"])
            self.assertEqual(record["executable_sha256"], "executable-hash")
            self.assertEqual(record["requested_theme"], "default")
            self.assertEqual(record["requested_scale_percent"], "native")
            self.assertEqual(record["requested_size"], "native")
            saved = Path(record["capture"]["path"])
            self.assertEqual(saved.parent, output)
            self.assertEqual(saved.name, "slint-browser1-desktop.png")
            self.assertEqual(saved.read_bytes(), source.read_bytes())
            json.dumps(record)

    def test_variant_environment_and_qml_host_normalization(self):
        self.assertEqual(
            capture.variant_environment("slint", "dark", "200", "native", None),
            (
                ("SLINTUITEST_CAPTURE_THEME", "dark"),
                ("SLINT_SCALE_FACTOR", "2"),
            ),
        )
        self.assertEqual(
            capture.variant_environment("qml", "light", "100", "native", 5 / 3),
            (
                ("QMLUITEST_CAPTURE_THEME", "light"),
                ("QT_SCALE_FACTOR", "0.6"),
            ),
        )
        self.assertEqual(
            capture.variant_environment("qml", "dark", "200", "native", 5 / 3),
            (
                ("QMLUITEST_CAPTURE_THEME", "dark"),
                ("QT_SCALE_FACTOR", "1.2"),
            ),
        )
        self.assertEqual(
            capture.variant_environment("bevy-egui", "system", "200", "native", None),
            (
                ("BEVY_EGUI_CAPTURE_THEME", "system"),
                ("BEVY_EGUI_CAPTURE_SCALE_PERCENT", "200"),
            ),
        )
        self.assertEqual(capture.variant_environment("slint", "default", "native", "native", None), ())
        for invalid in (None, 0, -1, float("nan"), float("inf")):
            with self.subTest(invalid=invalid), self.assertRaises(core.SmokeFailure):
                capture.variant_environment("qml", "default", "100", "native", invalid)
        for implementation, variable in (
            ("slint", "SLINTUITEST_CAPTURE_SIZE"),
            ("qml", "QMLUITEST_CAPTURE_SIZE"),
            ("bevy-egui", "BEVY_EGUI_CAPTURE_SIZE"),
        ):
            self.assertEqual(
                capture.variant_environment(implementation, "default", "native", "660x750", None),
                ((variable, "660x750"),),
            )

    def test_variant_capture_metadata_and_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "portal.png"
            source.write_bytes(png_header())
            session = FakeSession()
            session.adapter = core.Adapter("qml", "unused")
            with mock.patch.object(capture, "executable_sha256", return_value="hash"):
                record = capture.run_capture(
                    session,
                    FakePortal(source),
                    root,
                    settle=0,
                    theme="dark",
                    scale="200",
                    size="660x750",
                    qml_host_scale=5 / 3,
                )
            self.assertEqual(record["requested_theme"], "dark")
            self.assertEqual(record["requested_scale_percent"], "200")
            self.assertEqual(record["requested_size"], "660x750")
            self.assertAlmostEqual(record["qml_host_scale"], 5 / 3)
            self.assertAlmostEqual(record["qml_scale_factor"], 1.2)
            self.assertEqual(
                Path(record["capture"]["path"]).name,
                "qml-browser1-dark-200pct-660x750-desktop.png",
            )

    def test_main_runs_twelve_fresh_variant_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "portal.png"
            source.write_bytes(png_header())
            output = root / "output"
            portal = FakePortal(source)
            sessions = []

            def factory(adapter, timeout):
                session = FakeSession(adapter.executable)
                session.adapter = adapter
                sessions.append(session)
                return session

            arguments = [
                "--slint", "slint",
                "--qml", "qml",
                "--bevy-egui", "bevy",
                "--bevy-asset-root", "assets",
                "--output-dir", str(output),
                "--settle", "0",
                "--themes", "light", "dark",
                "--scales", "100", "200",
                "--qml-host-scale", str(5 / 3),
            ]
            with (
                mock.patch.object(capture, "ScreenshotPortal", return_value=portal),
                mock.patch.object(capture.core, "ProcessSession", side_effect=factory),
                mock.patch.object(capture, "executable_sha256", return_value="hash"),
            ):
                self.assertEqual(capture.main(arguments), 0)
            self.assertEqual(len(sessions), 12)
            self.assertEqual(portal.capture_count, 12)
            self.assertTrue(all(session.finished for session in sessions))
            self.assertEqual(
                [(session.adapter.implementation, session.adapter.environment) for session in sessions[:2]],
                [
                    ("slint", (("SLINTUITEST_CAPTURE_THEME", "light"), ("SLINT_SCALE_FACTOR", "1"))),
                    ("slint", (("SLINTUITEST_CAPTURE_THEME", "light"), ("SLINT_SCALE_FACTOR", "2"))),
                ],
            )
            records = [json.loads(line) for line in (output / "manifest.jsonl").read_text().splitlines()]
            self.assertEqual(len(records), 12)
            self.assertEqual(len({record["capture"]["path"] for record in records}), 12)
            self.assertTrue(all(record["clean_exit"] for record in records))
            self.assertTrue(all(not record["equivalence_established"] for record in records))

    def test_main_runs_six_fresh_constrained_size_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "portal.png"
            source.write_bytes(png_header())
            output = root / "output"
            portal = FakePortal(source)
            sessions = []

            def factory(adapter, timeout):
                session = FakeSession(adapter.executable)
                session.adapter = adapter
                sessions.append(session)
                return session

            arguments = [
                "--slint", "slint",
                "--qml", "qml",
                "--bevy-egui", "bevy",
                "--bevy-asset-root", "assets",
                "--output-dir", str(output),
                "--settle", "0",
                "--themes", "light",
                "--scales", "100",
                "--sizes", "1200x750", "660x750",
                "--qml-host-scale", str(5 / 3),
            ]
            with (
                mock.patch.object(capture, "ScreenshotPortal", return_value=portal),
                mock.patch.object(capture.core, "ProcessSession", side_effect=factory),
                mock.patch.object(capture, "executable_sha256", return_value="hash"),
            ):
                self.assertEqual(capture.main(arguments), 0)
            self.assertEqual(len(sessions), 6)
            self.assertEqual(portal.capture_count, 6)
            self.assertTrue(all(session.finished for session in sessions))
            self.assertEqual(
                [(session.adapter.implementation, session.adapter.environment) for session in sessions],
                [
                    ("slint", (("SLINTUITEST_CAPTURE_THEME", "light"), ("SLINT_SCALE_FACTOR", "1"), ("SLINTUITEST_CAPTURE_SIZE", "1200x750"))),
                    ("slint", (("SLINTUITEST_CAPTURE_THEME", "light"), ("SLINT_SCALE_FACTOR", "1"), ("SLINTUITEST_CAPTURE_SIZE", "660x750"))),
                    ("qml", (("QMLUITEST_CAPTURE_THEME", "light"), ("QT_SCALE_FACTOR", "0.6"), ("QMLUITEST_CAPTURE_SIZE", "1200x750"))),
                    ("qml", (("QMLUITEST_CAPTURE_THEME", "light"), ("QT_SCALE_FACTOR", "0.6"), ("QMLUITEST_CAPTURE_SIZE", "660x750"))),
                    ("bevy-egui", (("BEVY_EGUI_CAPTURE_THEME", "light"), ("BEVY_EGUI_CAPTURE_SCALE_PERCENT", "100"), ("BEVY_EGUI_CAPTURE_SIZE", "1200x750"))),
                    ("bevy-egui", (("BEVY_EGUI_CAPTURE_THEME", "light"), ("BEVY_EGUI_CAPTURE_SCALE_PERCENT", "100"), ("BEVY_EGUI_CAPTURE_SIZE", "660x750"))),
                ],
            )
            records = [json.loads(line) for line in (output / "manifest.jsonl").read_text().splitlines()]
            self.assertEqual(
                [(record["implementation"], record["requested_size"]) for record in records],
                [(implementation, size) for implementation in ("slint", "qml", "bevy-egui") for size in ("1200x750", "660x750")],
            )
            self.assertEqual(len({record["capture"]["path"] for record in records}), 6)
            self.assertTrue(all(record["clean_exit"] for record in records))

    def test_wrong_initial_route_is_rejected_without_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "portal.png"
            source.write_bytes(png_header())
            portal = FakePortal(source)
            session = FakeSession(
                initial=core.Route("primary.quantviz", "quant.monte-carlo")
            )
            with self.assertRaises(core.SmokeFailure):
                capture.run_capture(session, portal, root, settle=0)
            self.assertEqual(portal.capture_count, 0)
            self.assertFalse(session.quit_acknowledged)


if __name__ == "__main__":
    unittest.main()
