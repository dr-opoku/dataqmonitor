"""Deterministic data checks; no model, database, or platform dependency."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ._support import (
    check, finite_number, numeric_cell, overall, read_csv, reference_time,
    string_list, timestamp,
)

DEFAULTS: dict[str, Any] = {
    "dataset_name": "Local dataset",
    "expected_rows": None,
    "required_columns": None,
    "key_columns": [],
    "timestamp_column": None,
    "max_age_hours": 24,
    "future_tolerance_minutes": 5,
    "availability_window_hours": 720,
    "numeric_ranges": {},
    "allowed_values": {},
    "thresholds": {
        "completeness": 95, "freshness": 95,
        "availability": 95, "consistency": 95,
    },
}


def configuration(supplied: dict[str, Any] | None) -> dict[str, Any]:
    supplied = {} if supplied is None else supplied
    if not isinstance(supplied, dict):
        raise ValueError("Configuration must be an object.")
    extra = set(supplied) - set(DEFAULTS)
    if extra:
        raise ValueError(f"Unknown configuration keys: {', '.join(sorted(extra))}")
    cfg = {**DEFAULTS, **supplied}
    if not isinstance(cfg["dataset_name"], str) or not cfg["dataset_name"].strip():
        raise ValueError("dataset_name must be a nonempty string.")
    expected = cfg["expected_rows"]
    if expected is not None and (isinstance(expected, bool) or not isinstance(expected, int) or expected < 1):
        raise ValueError("expected_rows must be a positive integer, or null.")
    if cfg["required_columns"] is not None:
        string_list(cfg["required_columns"], "required_columns")
    string_list(cfg["key_columns"], "key_columns")
    column = cfg["timestamp_column"]
    if column is not None and (not isinstance(column, str) or not column.strip()):
        raise ValueError("timestamp_column must be a nonempty string, or null.")
    for key in ("max_age_hours", "availability_window_hours"):
        if finite_number(cfg[key], key, 0) == 0:
            raise ValueError(f"{key} must be greater than zero.")
    finite_number(cfg["future_tolerance_minutes"], "future_tolerance_minutes", 0)
    for name in ("numeric_ranges", "allowed_values", "thresholds"):
        if not isinstance(cfg[name], dict):
            raise ValueError(f"{name} must be an object.")
    for name, bounds in cfg["numeric_ranges"].items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("numeric_ranges column names must be nonempty strings.")
        if not isinstance(bounds, dict) or not bounds or set(bounds) - {"min", "max"}:
            raise ValueError(f"numeric_ranges.{name} accepts min and/or max.")
        for limit, value in bounds.items():
            finite_number(value, f"numeric_ranges.{name}.{limit}")
        if "min" in bounds and "max" in bounds and bounds["min"] > bounds["max"]:
            raise ValueError(f"numeric_ranges.{name}: min exceeds max.")
    for name, values in cfg["allowed_values"].items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("allowed_values column names must be nonempty strings.")
        string_list(values, f"allowed_values.{name}", allow_empty=False)
    if set(cfg["thresholds"]) - set(DEFAULTS["thresholds"]):
        raise ValueError("Unknown quality threshold.")
    cfg["thresholds"] = {**DEFAULTS["thresholds"], **cfg["thresholds"]}
    for key, value in cfg["thresholds"].items():
        if finite_number(value, f"thresholds.{key}", 0) > 100:
            raise ValueError(f"thresholds.{key} must be between 0 and 100.")
    return cfg


def analyze(csv_text: str, config: dict[str, Any] | None = None, *,
            attempts_csv: str | None = None, at: str | datetime | None = None) -> dict[str, Any]:
    """Measure supplied rows and optional fetch attempts without retaining raw data."""
    cfg = configuration(config)
    now = reference_time(at)
    header, rows = read_csv(csv_text)
    count = len(rows)
    findings: list[dict[str, Any]] = []
    checks: dict[str, dict[str, Any]] = {}

    required = header if cfg["required_columns"] is None else cfg["required_columns"]
    rule_columns = set(required) | set(cfg["key_columns"]) | set(cfg["numeric_ranges"]) | set(cfg["allowed_values"])
    if cfg["timestamp_column"]:
        rule_columns.add(cfg["timestamp_column"])
    missing_columns = sorted(rule_columns - set(header))
    if missing_columns:
        findings.append({
            "code": "MISSING_COLUMNS", "message": "Configured columns are absent from the CSV header.",
            "columns": missing_columns,
        })

    seen: set[tuple[str, ...]] = set()
    duplicate_rows: set[int] = set()
    incomplete_key_rows: set[int] = set()
    keys = cfg["key_columns"]
    for index, row in enumerate(rows):
        if not keys:
            continue
        key = tuple(row.get(name, "") for name in keys)
        if any(not value for value in key):
            incomplete_key_rows.add(index)
        elif key in seen:
            duplicate_rows.add(index)
        else:
            seen.add(key)
    observed_records = len(seen) if keys else count
    cell_total = count * len(required)
    cell_present = sum(bool(row.get(name, "")) for row in rows for name in required)
    cell_pct = 100 * cell_present / cell_total if cell_total else None
    expected = cfg["expected_rows"]
    row_pct = min(100, 100 * observed_records / expected) if expected is not None and count else None
    components = [value for value in (cell_pct, row_pct) if value is not None]
    checks["completeness"] = check(
        "Completeness", min(components) if components else None, "%",
        {"rows": count, "observed_records": observed_records, "expected_rows": expected,
         "row_coverage_pct": row_pct, "required_cell_coverage_pct": cell_pct,
         "missing_required_cells": cell_total - cell_present},
        "The weaker of expected-record coverage and required-cell coverage; no rows means unknown.",
        minimum=cfg["thresholds"]["completeness"],
    )

    recent = invalid = future = stale = 0
    ages: list[float] = []
    column = cfg["timestamp_column"]
    if column:
        for row in rows:
            try:
                age = (now - timestamp(row.get(column, ""))).total_seconds() / 3600
            except (ValueError, OverflowError):
                invalid += 1
                continue
            if age < -cfg["future_tolerance_minutes"] / 60:
                future += 1
            else:
                ages.append(age)
                if age > cfg["max_age_hours"]:
                    stale += 1
                else:
                    recent += 1
    checks["freshness"] = check(
        "Freshness", 100 * recent / count if column and count else None, "%",
        {"timestamp_column": column, "max_age_hours": cfg["max_age_hours"],
         "fresh_rows": recent, "stale_rows": stale, "invalid_timestamp_rows": invalid,
         "future_timestamp_rows": future,
         "oldest_age_hours": max(ages) if ages else None},
        "Share of rows with a valid, recent timestamp; unconfigured timestamps or no rows means unknown.",
        minimum=cfg["thresholds"]["freshness"],
    )

    attempt_count = successes = invalid_attempts = outside_window = 0
    if attempts_csv is not None:
        attempt_header, attempts = read_csv(attempts_csv)
        if not {"attempted_at", "success"} <= set(attempt_header):
            raise ValueError("Fetch-attempt CSV requires attempted_at and success columns.")
        for row in attempts:
            try:
                age = (now - timestamp(row["attempted_at"])).total_seconds() / 3600
                success = row["success"].lower()
                if age < -cfg["future_tolerance_minutes"] / 60:
                    raise ValueError("Future fetch attempt.")
                if success not in {"true", "false", "1", "0"}:
                    raise ValueError("Invalid success flag.")
            except (ValueError, OverflowError):
                invalid_attempts += 1
                continue
            if age > cfg["availability_window_hours"]:
                outside_window += 1
                continue
            attempt_count += 1
            successes += success in {"true", "1"}
    if invalid_attempts:
        findings.append({
            "code": "INVALID_FETCH_LOG", "count": invalid_attempts,
            "message": "Invalid fetch observations prevent a reliable availability score.",
        })
    checks["availability"] = check(
        "Availability", 100 * successes / attempt_count if attempt_count and not invalid_attempts else None, "%",
        {"attempts": attempt_count, "successful_attempts": successes,
         "invalid_attempts": invalid_attempts, "outside_window": outside_window,
         "window_hours": cfg["availability_window_hours"]},
        "Successful fetch attempts divided by valid attempts in the lookback window; no attempts means unknown.",
        minimum=cfg["thresholds"]["availability"],
    )

    invalid_rows = duplicate_rows | incomplete_key_rows
    violations: dict[str, int] = {
        "duplicate_keys": len(duplicate_rows), "incomplete_keys": len(incomplete_key_rows),
    }
    for name, bounds in cfg["numeric_ranges"].items():
        bad = 0
        for index, row in enumerate(rows):
            value = numeric_cell(row.get(name, ""))
            if value is None or ("min" in bounds and value < bounds["min"]) or ("max" in bounds and value > bounds["max"]):
                invalid_rows.add(index)
                bad += 1
        violations[f"numeric_range:{name}"] = bad
    for name, allowed in cfg["allowed_values"].items():
        bad = 0
        for index, row in enumerate(rows):
            if row.get(name, "") not in allowed:
                invalid_rows.add(index)
                bad += 1
        violations[f"allowed_values:{name}"] = bad
    has_rules = bool(keys or cfg["numeric_ranges"] or cfg["allowed_values"])
    checks["consistency"] = check(
        "Consistency", 100 * (count - len(invalid_rows)) / count if count and has_rules else None, "%",
        {"rows_failing_rules": len(invalid_rows), "violations": violations,
         "sample_record_numbers": [index + 1 for index in sorted(invalid_rows)[:10]]},
        "Share of rows satisfying every configured rule; no rows or no rules means unknown.",
        minimum=cfg["thresholds"]["consistency"],
    )
    for name, result in checks.items():
        if result["status"] == "attention":
            findings.append({
                "code": f"LOW_{name.upper()}",
                "message": f"{result['label']} is below its configured minimum.",
                "threshold_pct": cfg["thresholds"][name],
            })
    return {
        "schema_version": "1.0", "tool": "dataqmonitor",
        "dataset": cfg["dataset_name"], "evaluated_at": now.isoformat(),
        "synthetic": False, "status": overall(list(checks.values()), findings),
        "summary": {"rows": count, "columns": len(header), "observed_records": observed_records},
        "checks": checks, "findings": findings,
        "notes": [
            "Thresholds express expectations; they do not prove that data represents reality.",
            "Expected rows refer to this supplied extract. Filter the intended period before analysis.",
            "Availability measures supplied fetch observations, not time-based service uptime.",
            "Reports include aggregate evidence, column names and record numbers, not raw row values.",
        ],
    }
