from mcp.server.fastmcp import FastMCP
from mcp_config import  github_mcp_instructions
from tools.github_tools import github_tools

def create_gl_github_mcp_server():
    return FastMCP(
        name="gl_github_mcp_server",
        stateless_http=True,
        tools=github_tools,
        instructions=github_mcp_instructions
    )

