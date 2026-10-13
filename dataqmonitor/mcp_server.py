"""An optional local adapter over the same public calculation functions."""

from __future__ import annotations

from typing import Any, Literal

from .demo import demo
from .engine import analyze


def serve() -> None:
    try:
        from mcp.server import MCPServer
        from mcp.types import ToolAnnotations
    except ImportError as exc:
        raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

    server = MCPServer("dataqmonitor")
    annotations = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)

    @server.tool(annotations=annotations)
    def inspect_data(csv_text: str, config: dict[str, Any] | None = None,
                     attempts_csv: str | None = None, at: str | None = None) -> dict[str, Any]:
        """Check supplied CSV text and optional fetch observations. Does not read files or call models."""
        return analyze(csv_text, config, attempts_csv=attempts_csv, at=at)

    @server.tool(annotations=annotations)
    def demonstrate_data_quality(scenario: Literal["healthy", "broken", "unknown"] = "broken") -> dict[str, Any]:
        """Return calculations over bundled synthetic data with a fixed reference time."""
        return demo(scenario)

    server.run(transport="stdio")
