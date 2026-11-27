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


# TODO (task mcp_tools): two tools, each a function with @mcp.tool() above it, type hints and a docstring (the docstring
# is the description clients show and models read):
#   get_policy(policy_no: str) -> dict: the policy as a dict, from _policy
#   in_force(policy_no: str, on: str) -> bool: True when the date `on` (YYYY-MM-DD) is between start_date and end_date
# TODO (task tool_errors): for an unknown policy both raise ToolError(f"No policy {policy_no}"): MCP sends the client an
# error result with that message. (Any other exception reaches the client only as "Error executing tool ...".)


if __name__ == "__main__":
    mcp.run()
