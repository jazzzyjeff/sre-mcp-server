from fastmcp import FastMCP
from azure_devops.tools import register_tools as azure_tools

mcp = FastMCP("sre-mcp-server")

azure_tools(mcp)

if __name__ == "__main__":
    mcp.run()