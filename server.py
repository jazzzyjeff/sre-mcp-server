"""SRE MCP server entry point."""

from fastmcp import FastMCP
from azure_devops.tools import register_tools as azure_tools
from k8s.tools import register_tools as k8s_tools

mcp = FastMCP("sre-mcp-server")

azure_tools(mcp)
k8s_tools(mcp)

if __name__ == "__main__":
    mcp.run()
