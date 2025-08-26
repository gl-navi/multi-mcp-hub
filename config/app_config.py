"""Application configuration."""
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
    SCALEKIT_RESOURCE_METADATA_URL: str = os.environ.get("SCALEKIT_RESOURCE_METADATA_URL", "")
    SCALEKIT_AUTHORIZATION_SERVERS: str = os.environ.get("SCALEKIT_AUTHORIZATION_SERVERS", "")
    SCALEKIT_AUDIENCE_NAME: str = os.environ.get("SCALEKIT_AUDIENCE_NAME", "")
    SCALEKIT_RESOURCE_NAME: str = os.environ.get("SCALEKIT_RESOURCE_NAME", "")
    SCALEKIT_RESOURCE_DOCS_URL: str = os.environ.get("SCALEKIT_RESOURCE_DOCS_URL", "")
    CLIENT_ID: str = os.environ.get("CLIENT_ID", "")
    CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET", "")
    
    
    METADATA_JSON_URL: str = os.environ.get("METADATA_JSON_URL", "")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"
    
    def __post_init__(self):
        if not self.SCALEKIT_RESOURCE_IDENTIFIER:
            raise ValueError("SCALEKIT_RESOURCE_IDENTIFIER environment variable not set")
        if not self.SCALEKIT_CLIENT_ID:
            raise ValueError("SCALEKIT_CLIENT_ID environment variable not set")
        if not self.SCALEKIT_CLIENT_SECRET:
            raise ValueError("SCALEKIT_CLIENT_SECRET environment variable not set")
        if not self.SCALEKIT_RESOURCE_DOCS_URL:
            raise ValueError("SCALEKIT_RESOURCE_DOCS_URL environment variable not set")
        if not self.SCALEKIT_ENVIRONMENT_URL:
            raise ValueError("SCALEKIT_ENVIRONMENT_URL environment variable not set")
        if not self.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY environment variable not set")
        if not self.SCALEKIT_RESOURCE_METADATA_URL:
            raise ValueError("SCALEKIT_RESOURCE_METADATA_URL environment variable not set")
        if not self.SCALEKIT_AUTHORIZATION_SERVERS:
            raise ValueError("SCALEKIT_AUTHORIZATION_SERVERS environment variable not set")
        if not self.SCALEKIT_AUDIENCE_NAME:
            raise ValueError("SCALEKIT_AUDIENCE_NAME environment variable not set")


settings = Settings()
