"""Smoke test for pipeline."""
from __future__ import annotations

import unittest

from run import orchestrate


class SmokeTest(unittest.TestCase):
    def test_pipeline_pass(self) -> None:
        result = orchestrate(demo_failure=False)
        self.assertEqual(result["validation"]["status"], "pass")
        self.assertTrue(result["scoreboard"]["invariant_ok"])


if __name__ == "__main__":
    unittest.main()
