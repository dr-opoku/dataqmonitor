"""Command line for people, scripts, and coding agents."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from ._support import json_object, read_file
from .demo import SCENARIOS, demo
from .engine import analyze
from .report import as_html, as_json, as_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect local CSV data without a model or account.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    demo_parser = commands.add_parser("demo", help="Use bundled synthetic data at a fixed reference time.")
    demo_parser.add_argument("--scenario", choices=SCENARIOS, default="broken")
    inspect_parser = commands.add_parser("check", help="Check a supplied CSV extract.")
    inspect_parser.add_argument("csv", type=Path)
    inspect_parser.add_argument("--config", type=Path)
    inspect_parser.add_argument("--attempts", type=Path, help="CSV with attempted_at and success.")
    inspect_parser.add_argument("--at", help="Timezone-aware ISO reference time; defaults to current UTC.")
    for command in (demo_parser, inspect_parser):
        command.add_argument("--format", choices=("text", "json", "html"), default="text")
        command.add_argument("--output", type=Path, help="Write this file instead of stdout.")
        command.add_argument("--require-ok", action="store_true", help="Exit 1 for attention or unknown.")
    commands.add_parser("serve", help="Run the optional MCP server over stdio.")
    args = parser.parse_args(argv)
    try:
        if args.command == "serve":
            from .mcp_server import serve
            serve()
            return 0
        if args.command == "demo":
            report = demo(args.scenario)
        else:
            config = json_object(read_file(args.config)) if args.config else None
            report = analyze(
                read_file(args.csv), config,
                attempts_csv=read_file(args.attempts) if args.attempts else None,
                at=args.at,
            )
        output = {"text": as_text, "json": as_json, "html": as_html}[args.format](report)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
        return 1 if args.require_ok and report["status"] != "ok" else 0
    except (OSError, ValueError, ImportError, OverflowError) as exc:
        if getattr(args, "format", None) == "json":
            sys.stdout.write(as_json({
                "schema_version": "2.0", "tool": "dataqmonitor", "status": "error",
                "error": {"code": "INVALID_INPUT", "message": str(exc)},
            }))
        else:
            print(f"dataqmonitor: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
