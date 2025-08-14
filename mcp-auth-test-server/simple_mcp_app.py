"""
Simple MCP Application - FastAPI app that serves the simple MCP server
Follows the same pattern as the main app.py
"""
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from simple_mcp_server import create_simple_mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleMCPManager:
    """Manager for the simple MCP server."""
    
    def __init__(self):
        self.simple_mcp = create_simple_mcp_server()
    
    @asynccontextmanager
    async def lifespan_manager(self):
        """Manage simple MCP server lifecycle."""
        logger.info("Starting Simple MCP server...")
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(self.simple_mcp.session_manager.run())
            logger.info("Simple MCP server started successfully")
            yield
        logger.info("Simple MCP server stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application for simple MCP server."""
    mcp_manager = SimpleMCPManager()
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp_manager.lifespan_manager():
            yield
    
    app = FastAPI(
        title="Simple MCP Test Server",
        description="A simple MCP server for testing authorization flows",
        version="1.0.0",
        debug=True,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for testing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/", include_in_schema=False, tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "message": "Simple MCP Test Server is running",
            "version": "1.0.0"
        }

    # Info endpoint
    @app.get("/info", tags=["info"])
    async def get_info():
        """Returns basic info about the Simple MCP Server."""
        return {
            "name": "Simple MCP Test Server",
            "version": "1.0.0",
            "description": "A simple MCP server for testing authorization flows",
            "tools": [
                "echo", "add_numbers", "get_time", 
                "square", "greet", "server_info"
            ]
        }
    
    # Mount simple MCP application
    app.mount("/mcp", mcp_manager.simple_mcp.streamable_http_app())
    
    logger.info("Simple MCP Application created")
    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
