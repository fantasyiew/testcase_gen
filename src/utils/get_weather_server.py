# Weather server (streamable HTTP transport)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "早上下雨，晚上雪下得很大"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")