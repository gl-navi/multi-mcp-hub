from fastmcp import FastMCP
from mcp_config import  aws_mcp_instructions
from tools.aws_tools import aws_tools
from authentication_config import auth


def create_gl_aws_mcp_server():
    return FastMCP(
        name="gl_aws_mcp_server",
        auth=auth,
        stateless_http=True,
        tools=aws_tools,
        instructions=aws_mcp_instructions
    )

