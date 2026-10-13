"""Bundled, explicitly synthetic demonstration inputs."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

from ._support import json_object
from .engine import analyze

DEMO_AT = "2026-10-13T12:00:00Z"
SCENARIOS = ("healthy", "broken", "unknown")


def demo(scenario: str = "broken") -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Scenario must be one of: {', '.join(SCENARIOS)}.")
    root = files("dataqmonitor").joinpath("fixtures")
    report = analyze(
        root.joinpath(f"{scenario}.csv").read_text(encoding="utf-8"),
        json_object(root.joinpath("config.json").read_text(encoding="utf-8")),
        attempts_csv=root.joinpath(f"{scenario}_attempts.csv").read_text(encoding="utf-8"),
        at=DEMO_AT,
    )
    report["synthetic"] = True
    report["scenario"] = scenario
    return report
