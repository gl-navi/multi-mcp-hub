"""Unified MCP server combining AWS and GitHub tools with scope-based access control."""
from mcp.server.fastmcp import FastMCP
from fastapi import Request
from mcp_servers.config.mcp_config import aws_mcp_instructions, github_mcp_instructions
from tools.aws_tools import aws_tools
from tools.github_tools import github_tools
import logging
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

class ScopeBasedToolProvider:
    """
    A provider that filters tools based on user scopes from the request.
    """
    def __init__(self):
        # Map each scope to the corresponding tools
        self.scope_to_tools = {
            "mcp:aws": aws_tools,
            "mcp:github": github_tools
        }
        
        # Store instructions by scope for context
        self.scope_to_instructions = {
            "mcp:aws": aws_mcp_instructions,
            "mcp:github": github_mcp_instructions
        }
        
    def get_tools_for_scopes(self, scopes: List[str]) -> Dict[str, Callable]:
        """Get tools available for the given scopes."""
        available_tools = {}
        
        # Add tools based on user scopes
        for scope, tools in self.scope_to_tools.items():
            if scope in scopes:
                logger.info(f"Adding tools for scope: {scope}")
                available_tools.update(tools)
                
        return available_tools
        
    def get_instructions_for_scopes(self, scopes: List[str]) -> str:
        """Get instructions for the given scopes."""
        instructions = []
        
        for scope, scope_instructions in self.scope_to_instructions.items():
            if scope in scopes:
                instructions.append(scope_instructions)
                
        if not instructions:
            return "No tools are available with your current permissions."
            
        return "\n\n".join(instructions)


def create_unified_mcp_server():
    """
    Create a unified MCP server that provides access to tools based on user scopes.
    """
    # Create a base MCP server
    unified_mcp = FastMCP(
        name="unified_mcp_server",
        stateless_http=True,
        instructions="Tools will be available based on your authentication scopes.",
    )
    
    # Create the tool provider
    tool_provider = ScopeBasedToolProvider()
    
    # Override the method that handles incoming requests
    original_handle = unified_mcp._handle_request
    
    async def scope_based_handle_request(request: Request):
        """Custom request handler that applies scope-based restrictions."""
        # Get user scopes from auth middleware
        user_scopes = getattr(request.state, "user_scopes", [])
        
        if not user_scopes:
            logger.warning("No scopes found in request, using default empty list")
        
        # Get tools for these scopes
        available_tools = tool_provider.get_tools_for_scopes(user_scopes)
        
        # Register tools dynamically for this request
        for tool_name, tool_function in available_tools.items():
            unified_mcp.register_tool(tool_name, tool_function)
            
        # Update instructions based on scopes
        unified_mcp.instructions = tool_provider.get_instructions_for_scopes(user_scopes)
        
        # Process the request with the original handler
        return await original_handle(request)
    
    # Replace the handler
    unified_mcp._handle_request = scope_based_handle_request
    
    return unified_mcp
