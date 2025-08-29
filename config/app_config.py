"""Application configuration."""
import json
import os


class Settings:
    """Application settings."""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    TITLE: str = "GL MCP Hub"
    DESCRIPTION: str = "MCP Hub"
    VERSION: str = "1.0.0"
    
    # Environment
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    
    # Health check
    HEALTH_CHECK_PATH: str = "/health"
    
    # CORS
    CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    # ScaleKit Configuration
    SCALEKIT_ENVIRONMENT_URL: str = os.environ.get("SCALEKIT_ENVIRONMENT_URL", "")
    SCALEKIT_CLIENT_ID: str = os.environ.get("SCALEKIT_CLIENT_ID", "")
    SCALEKIT_CLIENT_SECRET: str = os.environ.get("SCALEKIT_CLIENT_SECRET", "")
    SCALEKIT_RESOURCE_IDENTIFIER: str = os.environ.get("SCALEKIT_RESOURCE_IDENTIFIER", "")
    SCALEKIT_BASE_RESOURCE_METADATA_URL: str = os.environ.get("SCALEKIT_BASE_RESOURCE_METADATA_URL", "")
    
    SCALEKIT_AUTHORIZATION_SERVERS: str = os.environ.get("SCALEKIT_AUTHORIZATION_SERVERS", "")
    SCALEKIT_AUDIENCE_NAME: str = os.environ.get("SCALEKIT_AUDIENCE_NAME", "")
    SCALEKIT_RESOURCE_NAME: str = os.environ.get("SCALEKIT_RESOURCE_NAME", "")
    SCALEKIT_RESOURCE_DOCS_URL: str = os.environ.get("SCALEKIT_RESOURCE_DOCS_URL", "")
    CLIENT_ID: str = os.environ.get("CLIENT_ID", "")
    CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET", "")
    METADATA_GITHUB_MCP_JSON_URL: str = os.environ.get("METADATA_GITHUB_MCP_JSON_URL", "")
    METADATA_AWS_MCP_JSON_URL: str = os.environ.get("METADATA_AWS_MCP_JSON_URL", "")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    import json

    def get_server_metadata(self, server_name: str) -> dict:
        """Get server-specific metadata for OAuth discovery."""
        if server_name == "github":
            return json.loads(self.METADATA_GITHUB_MCP_JSON_URL)
        elif server_name == "aws":
            return json.loads(self.METADATA_AWS_MCP_JSON_URL)
        else:
            raise ValueError(f"Unknown server name in get_server_metadata: {server_name}")
        
settings = Settings()
