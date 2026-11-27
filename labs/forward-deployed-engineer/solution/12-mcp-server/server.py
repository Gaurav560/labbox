"""Claimdesk as an MCP server: Deccan Shield's own AI assistant (or Claude Desktop, or any MCP client) can look up
policies and check claims through it. Run it with: python server.py   (it speaks MCP over stdin and stdout)
Try it from Python with: python try_server.py"""
import sqlite3

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("claimdesk")


def _policy(policy_no, path="data/claimdesk.db"):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM policies WHERE policy_no = ?", (policy_no,)).fetchone()
    con.close()
    return dict(row) if row else None


@mcp.tool()
def get_policy(policy_no: str) -> dict:
    """Looks up a Deccan Shield motor policy by number (like DS-POL-40185): holder, vehicle_reg, vehicle, start_date,
    end_date, sum_insured and deductible in rupees."""
    policy = _policy(policy_no)
    if policy is None:
        raise ToolError(f"No policy {policy_no}")
    return policy


@mcp.tool()
def in_force(policy_no: str, on: str) -> bool:
    """True when the policy covers the date `on` (YYYY-MM-DD): on or after start_date and on or before end_date."""
    policy = _policy(policy_no)
    if policy is None:
        raise ToolError(f"No policy {policy_no}")
    return policy["start_date"] <= on <= policy["end_date"]


if __name__ == "__main__":
    mcp.run()
