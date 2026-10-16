"""An optional local adapter over the same public calculation functions."""

from __future__ import annotations

from typing import Any, Literal

try:
    from ._mcp_contract import Report
except ImportError as exc:
    raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

from .demo import demo
from .engine import analyze


def create_server() -> Any:
    try:
        from mcp.server import MCPServer
        from mcp.server.mcpserver.exceptions import ToolError
        from mcp.types import ToolAnnotations
    except ImportError as exc:
        raise ImportError("MCP support requires: python -m pip install '.[mcp]'") from exc

    server = MCPServer("dataqmonitor")
    annotations = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)

    @server.tool(annotations=annotations, structured_output=True)
    def inspect_data(csv_text: str, config: dict[str, Any] | None = None,
                     attempts_csv: str | None = None, at: str | None = None) -> Report:
        """Check supplied CSV text and optional fetch observations. Does not read files or call models."""
        try:
            return analyze(csv_text, config, attempts_csv=attempts_csv, at=at)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc

    @server.tool(annotations=annotations, structured_output=True)
    def demonstrate_data_quality(scenario: Literal["healthy", "broken", "unknown", "small_sample"] = "broken") -> Report:
        """Return calculations over bundled synthetic data with a fixed reference time."""
        return demo(scenario)

    return server


def serve() -> None:
    create_server().run(transport="stdio")
