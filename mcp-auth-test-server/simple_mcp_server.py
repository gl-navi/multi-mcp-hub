"""
Simple MCP Server for testing MCP authorization flow
Uses the same FastMCP pattern as your existing AWS/GitHub servers
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
from typing import List, Dict, Union

# Create the FastMCP server instance
mcp = FastMCP(name="simple_test_tools", stateless_http=True)

@mcp.tool(description="Echo back the input text")
def echo(text: str) -> str:
    """Echo back the provided text"""
    return f"Echo: {text}"

@mcp.tool(description="Add two numbers together")
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result"""
    return a + b

@mcp.tool(description="Get current server time")
def get_time() -> str:
    """Get the current server time in ISO format"""
    return f"Current server time: {datetime.now().isoformat()}"

@mcp.tool(description="Calculate the square of a number")
def square(number: float) -> float:
    """Calculate the square of the given number"""
    return number * number

@mcp.tool(description="Generate a simple greeting")
def greet(name: str = "World") -> str:
    """Generate a greeting for the given name"""
    return f"Hello, {name}! Welcome to the Simple MCP Server."

@mcp.tool(description="Get basic server information")
def server_info() -> Dict[str, Union[str, int]]:
    """Return basic information about this MCP server"""
    return {
        "name": "Simple MCP Test Server",
        "version": "1.0.0",
        "tools_count": 6,
        "description": "A simple MCP server for testing authorization flow"
    }

# Extract tools for use in other modules
simple_tools = list(mcp._tool_manager._tools.values())

# Instructions for the simple MCP server
simple_mcp_instructions = """
This is a simple MCP server for testing authentication and authorization flows.

SIMPLE TOOLS

- echo(text):
    Echoes back the provided text string.

- add_numbers(a, b):
    Adds two numbers together and returns the result.

- get_time():
    Returns the current server time in ISO format.

- square(number):
    Calculates and returns the square of the given number.

- greet(name="World"):
    Generates a greeting message for the given name (defaults to "World").

- server_info():
    Returns basic information about this MCP server including name, version, and tool count.
"""

def create_simple_mcp_server():
    """Create and return a simple MCP server instance"""
    return FastMCP(
        name="simple_test_mcp_server",
        stateless_http=True,
        tools=simple_tools,
        instructions=simple_mcp_instructions
    )
