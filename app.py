"""Application factory and configuration."""
import contextlib
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp_servers.aws_mcp_server import create_gl_aws_mcp_server

from dotenv import load_dotenv
load_dotenv()
from config.app_config import settings
from mcp_servers.github_mcp_server import create_gl_github_mcp_server
from middleware.middleware import setup_middleware

from starlette.middleware import Middleware


# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPManager:
    """Manager for MCP servers."""
    
    def __init__(self):
        self.github_mcp = create_gl_github_mcp_server()
        self.aws_mcp = create_gl_aws_mcp_server()
    
    @asynccontextmanager
    async def lifespan_manager(self):
        """Manage MCP server lifecycles."""
        logger.info("Starting MCP servers...")
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(self.github_mcp.session_manager.run())
            await stack.enter_async_context(self.aws_mcp.session_manager.run())
            logger.info("MCP servers started successfully")
            yield
        logger.info("MCP servers stopped")


def create_FASTAPI_app() -> FastAPI:
    """Create and configure FastAPI application."""
    mcp_manager = MCPManager()
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with mcp_manager.lifespan_manager():
            yield
    
    app = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )
        
    # Setup custom middleware
    setup_middleware(app)
    
    
    # MCP well-known endpoint
    @app.get("/.well-known/oauth-protected-resource/mcp")
    async def oauth_protected_resource_metadata():
        """
        OAuth 2.0 Protected Resource Metadata endpoint for MCP client discovery.
        Required by the MCP specification for authorization server discovery.
        """
        response = json.loads(settings.METADATA_JSON_URL)
        return response

    # Health check endpoint
    @app.get(settings.HEALTH_CHECK_PATH, include_in_schema=False, tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION
        }

    # Info endpoint for OpenAPI docs
    @app.get("/info", tags=["info"])
    async def get_info():
        """Returns basic info about the MCP Hub."""
        return {
            "name": settings.TITLE,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "environment": settings.ENVIRONMENT
        }
    
    # Mount MCP applications
    app.mount("/github", mcp_manager.github_mcp.streamable_http_app())
    app.mount("/aws", mcp_manager.aws_mcp.streamable_http_app())
    
    logger.info(f"Application created - Environment: {settings.ENVIRONMENT}")
    return app


# Create the FAST API app instance
app = create_FASTAPI_app()
