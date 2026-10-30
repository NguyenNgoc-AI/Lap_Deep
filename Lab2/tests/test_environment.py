import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torch
from src.phases import phase_01_environment as phase


class EnvironmentTests(unittest.TestCase):
    def execute(self, available, effects):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(phase.torch.xpu, "is_available", return_value=available):
                with patch.object(phase, "benchmark", side_effect=effects) as mocked:
                    result = phase.run(directory)
            saved = json.loads((Path(result["directory"]) / "report.json").read_text())
            self.assertEqual(saved["status"], result["status"])
            return result, mocked.call_args_list

    def test_unavailable_xpu_is_skipped(self):
        result, calls = self.execute(False, [{"status": "PASSED"}])
        self.assertEqual(result["status"], "PASSED")
        self.assertEqual(result["attempts"][0]["devices"]["xpu"]["status"], "SKIPPED")
        self.assertEqual(len(calls), 1)

    def test_oom_retries_both_devices_at_same_batch(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
            {"status": "PASSED"}, {"status": "PASSED"},
        ])
        self.assertEqual(result["status"], "PASSED")
        self.assertEqual([(c.args[0], c.args[1]) for c in calls],
                         [("cpu", 8), ("xpu", 8), ("cpu", 4), ("xpu", 4)])
        self.assertTrue(result["attempts"][0]["devices"]["xpu"]["oom"])

    def test_oom_at_batch_four_stops(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
        ])
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(calls), 4)

    def test_runtime_error_is_not_hidden_or_retried(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, RuntimeError("fixture"),
        ])
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(calls), 2)
        self.assertIn("RuntimeError", result["attempts"][0]["devices"]["xpu"]["traceback"])

    def test_invalid_batch_creates_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                phase.run(directory, batch=0)
            self.assertEqual(list(Path(directory).iterdir()), [])
