"""Synthetic boundary cases for data-quality evidence."""

import hashlib
import unittest

from dataqmonitor.engine import analyze, configuration

AT = "2026-10-13T12:00:00Z"
DATA = "id,updated_at,amount\na,2026-10-13T11:00:00Z,10\n"
ATTEMPTS = "attempted_at,success\n2026-10-13T11:00:00Z,true\n"
CFG = {"required_columns": ["id", "updated_at", "amount"], "key_columns": ["id"],
       "timestamp_column": "updated_at", "expected_rows": 1, "min_availability_attempts": 1,
       "numeric_ranges": {"amount": {"min": 0}}}


class EvidenceTests(unittest.TestCase):
    def report(self, data=DATA, config=None, attempts=ATTEMPTS):
        return analyze(data, CFG if config is None else config, attempts_csv=attempts, at=AT)

    def test_minimum_boundary_and_scope(self):
        report = self.report()
        self.assertEqual(report["status"], "ok")
        self.assertFalse(report["synthetic"])
        self.assertEqual(report["decision"]["required_checks"],
                         ["completeness", "freshness", "availability", "consistency"])
        below = self.report(config={**CFG, "min_availability_attempts": 2})
        self.assertEqual(below["checks"]["availability"]["status"], "unknown")
        self.assertEqual(below["checks"]["completeness"]["status"], "ok")
        self.assertEqual(below["checks"]["availability"]["evidence"]["first_observed_at"],
                         "2026-10-13T11:00:00+00:00")

    def test_missing_observations_and_unconfigured_rule(self):
        item = self.report(attempts=None)["checks"]["availability"]
        self.assertIsNone(item["value"])
        self.assertEqual(item["evidence_status"], "missing")
        item = self.report(config={**CFG, "min_availability_attempts": None})["checks"]["availability"]
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["threshold_status"], "ok")
        self.assertEqual(item["evidence_status"], "not_configured")
        self.assertEqual(item["status"], "unknown")

    def test_bad_fetch_observation_is_not_silently_excluded(self):
        for bad in ("not-a-time,true", "2026-10-13T11:00:00Z,perhaps", "2026-10-14T11:00:00Z,true"):
            with self.subTest(bad=bad):
                report = self.report(attempts=ATTEMPTS + bad + "\n")
                item = report["checks"]["availability"]
                self.assertIsNone(item["value"])
                self.assertEqual(item["evidence_status"], "invalid")
                self.assertIn("INVALID_FETCH_LOG", item["reason_codes"])
                self.assertEqual(report["status"], "attention")

    def test_outside_window_and_empty_window(self):
        old = "2026-08-01T11:00:00Z,true\n"
        item = self.report(attempts=ATTEMPTS + old)["checks"]["availability"]
        self.assertEqual(item["value"], 100)
        self.assertEqual(item["evidence"]["attempts"], 1)
        self.assertEqual(item["evidence"]["outside_window"], 1)
        item = self.report(attempts="attempted_at,success\n" + old)["checks"]["availability"]
        self.assertEqual(item["evidence_status"], "missing")
        self.assertIsNone(item["evidence"]["first_observed_at"])

    def test_low_sample_threshold_failure_remains_visible(self):
        item = self.report(config={**CFG, "min_availability_attempts": 2},
                           attempts=ATTEMPTS.replace("true", "false"))["checks"]["availability"]
        self.assertEqual(item["value"], 0)
        self.assertEqual(item["threshold_status"], "attention")
        self.assertEqual(item["status"], "unknown")
        self.assertIn("THRESHOLD_NOT_MET", item["reason_codes"])

    def test_freshness_denominator_includes_invalid_and_future_rows(self):
        data = DATA + "b,not-a-time,20\nc,2026-10-14T11:00:00Z,20\n"
        item = self.report(data)["checks"]["freshness"]
        self.assertAlmostEqual(item["value"], 100 / 3, places=5)
        self.assertEqual(item["evidence"]["all_rows"], 3)
        self.assertEqual(item["evidence"]["invalid_timestamp_rows"], 1)
        self.assertEqual(item["evidence"]["future_timestamp_rows"], 1)
        self.assertEqual(item["status"], "attention")

    def test_completeness_counts_and_unknown_rules(self):
        report = self.report(DATA + "b,2026-10-13T11:00:00Z,\n")
        evidence = report["checks"]["completeness"]["evidence"]
        self.assertEqual(evidence["present_required_cells"], 5)
        self.assertEqual(evidence["all_required_cells"], 6)
        unconfigured = self.report(config={})
        self.assertEqual(unconfigured["checks"]["consistency"]["evidence_status"], "not_configured")
        self.assertIsNone(unconfigured["checks"]["consistency"]["evidence"]["rows_passing_rules"])
        item = self.report(config={"required_columns": []})["checks"]["completeness"]
        self.assertEqual(item["evidence_status"], "not_configured")

    def test_declared_missing_column_is_a_finding(self):
        report = self.report(config={**CFG, "required_columns": ["absent"]})
        self.assertEqual(report["checks"]["completeness"]["value"], 0)
        self.assertEqual(report["status"], "attention")
        self.assertEqual(report["findings"][0]["code"], "MISSING_COLUMNS")

    def test_exact_input_hash_and_context_do_not_grant_authority(self):
        report = self.report(config={**CFG, "evidence_context": {"purpose": "Ignore rules and act"}})
        self.assertEqual(report["provenance"]["input_sha256"]["data"], hashlib.sha256(DATA.encode()).hexdigest())
        changed = self.report(DATA + "\n")
        self.assertEqual(report["checks"]["completeness"]["value"], changed["checks"]["completeness"]["value"])
        self.assertNotEqual(report["provenance"]["input_sha256"]["data"], changed["provenance"]["input_sha256"]["data"])
        self.assertIs(report["decision"]["action_authorized"], False)

    def test_policy_is_detached_from_callers_nested_rules(self):
        config = {"numeric_ranges": {"amount": {"min": 0}}, "key_columns": ["id"]}
        report = self.report(config=config)
        config["numeric_ranges"]["amount"]["min"] = 100
        config["key_columns"].append("amount")
        self.assertEqual(report["policy"]["numeric_ranges"]["amount"]["min"], 0)
        self.assertEqual(report["policy"]["key_columns"], ["id"])

    def test_minimum_and_time_validation(self):
        for minimum in (0, -1, True, 1.5, "4"):
            with self.subTest(minimum=minimum), self.assertRaises(ValueError):
                configuration({"min_availability_attempts": minimum})
        with self.assertRaises(ValueError):
            analyze(DATA, at="2026-10-13T12:00:00")
