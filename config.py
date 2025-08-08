"""Application configuration."""
import os
from typing import Optional


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
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT == "production"


settings = Settings()
