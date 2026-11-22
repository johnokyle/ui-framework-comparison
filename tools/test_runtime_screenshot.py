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
            saved = Path(record["capture"]["path"])
            self.assertEqual(saved.parent, output)
            self.assertEqual(saved.read_bytes(), source.read_bytes())
            json.dumps(record)

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
