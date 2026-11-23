"""The co-op's tools as an MCP server: any MCP client (an AI app, an IDE, another agent) can use them."""
from fastmcp import FastMCP

mcp = FastMCP("pimpalgaon-coop")
RATES = {"onion": 1850, "tomato": 1200, "grapes": 4600}


@mcp.tool
def mandi_price(crop: str) -> int:
    """Today's mandi rate in rupees per quintal. crop is onion, tomato or grapes."""
    return RATES[crop.strip().lower()]


@mcp.tool
def storage_cost(crates: int, days: int) -> int:
    """The cold storage charge in rupees for some crates kept some days (Rs 2 per crate per day)."""
    return crates * days * 2


if __name__ == "__main__":
    mcp.run()  # stdio: the client starts this file and talks over its standard input and output
