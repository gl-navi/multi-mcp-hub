"""MCP Tool Server with OAuth2 Authorization.

This module implements a FastAPI-based MCP tool server that provides simple tools
for testing MCP implementation with OAuth2 authorization. Each tool requires a valid
access token obtained from the OAuth2 authorization server.

Features:
* Secure tool access through OAuth2 tokens
* Standard MCP response formatting
* Token expiration management
* Detailed error responses
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional
import httpx

app = FastAPI(
    title="MCP Tool Server",
    description="A simple MCP tool server with OAuth2 authorization"
)


# OAuth server URL for token validation
AUTH_SERVER = "http://127.0.0.1:8000"


class ToolRequest(BaseModel):
    """
    Model for tool invocation requests.
    
    Attributes:
        tool (str): The name of the tool to invoke
        parameters (dict): Parameters to pass to the tool
    """
    tool: str
    parameters: Dict = {}


async def validate_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Validate the access token with the OAuth server.
    
    Args:
        authorization (str): The Authorization header containing the bearer token
        
    Returns:
        dict: The decoded token information if valid
        
    Raises:
        HTTPException: If the token is missing, invalid, or expired
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
            headers={
                "WWW-Authenticate": 'Bearer error="missing_token"',
                "error": "missing_token",
                "error_description": "Missing or malformed token"
            }
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVER}/api/mcp/validate_token",
                headers={"Authorization": authorization}
            )
            
            if response.status_code == 401:
                error_info = response.json()
                error = error_info.get("error", "invalid_token")
                error_description = error_info.get("error_description", "Token validation failed")
                
                # Handle different token error cases
                if "expired" in error_description.lower():
                    # Token is expired - client should refresh
                    raise HTTPException(
                        status_code=401,
                        detail="Token has expired",
                        headers={
                            "WWW-Authenticate": 'Bearer error="invalid_token", error_description="Token expired"',
                            "error": "token_expired",
                            "error_description": "Access token has expired. Please refresh your token.",
                        }
                    )
                else:
                    # Token is invalid for other reasons
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid token",
                        headers={
                            "WWW-Authenticate": f'Bearer error="{error}"',
                            "error": error,
                            "error_description": error_description
                        }
                    )
            
            elif response.status_code != 200:
                # Unexpected error from auth server
                raise HTTPException(
                    status_code=500,
                    detail="Token validation failed",
                    headers={
                        "error": "validation_failed",
                        "error_description": "Unable to validate token with authorization server"
                    }
                )
            
            token_data = response.json()
            
            # Check if token will expire soon (within 5 minutes)
            if token_data.get("exp"):
                exp_time = datetime.fromtimestamp(token_data["exp"])
                time_to_expire = exp_time - datetime.now()
                
                if time_to_expire.total_seconds() < 300:  # 5 minutes
                    # Add warning header but still process request
                    headers = {
                        "Warning": "199 - Token will expire soon. Consider refreshing.",
                        "X-Token-Expires-In": str(int(time_to_expire.total_seconds()))
                    }
                    token_data["_warning"] = "Token will expire soon"
                    token_data["_expires_in"] = int(time_to_expire.total_seconds())
            
            return token_data
            
        except httpx.RequestError as e:
            # Network or connection error
            raise HTTPException(
                status_code=503,
                detail="Authorization service unavailable",
                headers={
                    "error": "service_unavailable",
                    "error_description": "Unable to reach authorization server"
                }
            )


@app.get("/api/mcp/tools")
async def list_tools(token_data: Dict = Depends(validate_token)) -> Dict:
    """
    List all available MCP tools.
    
    Args:
        token_data (dict): The validated token data from the authorization middleware
        
    Returns:
        dict: Information about available tools and the token data
    """
    return {
        "tools": [
            {
                "name": "echo",
                "description": "Echo back the input text",
                "parameters": ["text"]
            },
            {
                "name": "add_numbers",
                "description": "Add two numbers together",
                "parameters": ["a", "b"]
            },
            {
                "name": "get_time",
                "description": "Get current server time",
                "parameters": []
            }
        ],
        "token_info": token_data
    }


@app.post("/api/mcp/tools/invoke")
async def invoke_tool(
    request: ToolRequest, 
    token_data: Dict = Depends(validate_token)
) -> Dict:
    """
    Execute an MCP tool with the given parameters.
    
    Args:
        request (ToolRequest): The tool invocation request
        token_data (dict): The validated token data from the authorization middleware
        
    Returns:
        dict: The tool execution result in standard MCP format
        
    Raises:
        HTTPException: If the tool doesn't exist or parameters are invalid
    """
    tool_name = request.tool
    params = request.parameters
    
    try:
        if tool_name == "echo":
            if "text" not in params:
                raise ValueError("Missing required parameter: text")
            result = f"Echo: {params['text']}"
        
        elif tool_name == "add_numbers":
            if "a" not in params or "b" not in params:
                raise ValueError("Missing required parameters: a, b")
            try:
                result = float(params["a"]) + float(params["b"])
            except (ValueError, TypeError):
                raise ValueError("Parameters 'a' and 'b' must be numbers")
        
        elif tool_name == "get_time":
            result = f"Current server time: {datetime.now().isoformat()}"
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            "status": "success",
            "result": result,
            "tool": tool_name,
            "token_info": token_data
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )
