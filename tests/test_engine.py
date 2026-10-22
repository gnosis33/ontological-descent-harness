"""Unit and fixture tests, with no network or model access."""
import json
import unittest

from odh.engine import ResponseFormatError, ask, extract_json_object, run_experiment
from odh.providers import FixtureProvider
from odh.report import markdown_report
from odh.prompts import OPERATORS


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.provider = FixtureProvider()

    def test_json_object_parsing(self):
        parsed = extract_json_object('Prefix:\n```json\n{"key": 2}\n```')
        self.assertEqual(parsed, {"key": 2})

    def test_malformed_json_fails(self):
        with self.assertRaises(ResponseFormatError):
            extract_json_object("this is not JSON")

    def test_stage_validation(self):
        result = ask(self.provider, "audit", {"problem": "test"})
        self.assertIn("invariants", result)

    def test_rejects_non_integer_scores(self):
        from odh.engine import validate
        candidate = json.loads(self.provider.complete("ODH_ROLE=evaluate"))
        candidate["scores"]["coherence"] = 6
        with self.assertRaises(ResponseFormatError):
            validate("evaluate", candidate)

    def test_runs_bounded_search(self):
        run = run_experiment("Evaluate adaptive routing.", self.provider, 3)
        self.assertEqual(len(run["trials"]), 3)
        self.assertEqual(run["trials"][1]["operator"], OPERATORS[1])
        self.assertEqual(len(run["provisional_ranking"]), 3)
        self.assertIn("UNVERIFIED", markdown_report(run))

    def test_rejects_invalid_budget(self):
        with self.assertRaises(ValueError):
            run_experiment("test", self.provider, 13)

    def test_fixture_outputs_are_synthetic(self):
        run = run_experiment("test", self.provider, 1)
        self.assertEqual(run["provider"], "fixture")
        self.assertIn("Synthetic", run["trials"][0]["candidate"]["name"])


if __name__ == "__main__":
    unittest.main()
