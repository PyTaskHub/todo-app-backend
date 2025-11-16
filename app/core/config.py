"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All required settings must be provided via .env file or environment variables.
    """
    # Application
    APP_NAME: str = Field(
        default="PyTaskHub",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug mode"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment name (development, staging, production)"
    )

    # Server
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    PORT: int = Field(
        default=8000,
        description="Server port"
    )

    # Database
    DATABASE_URL: str = Field(
        description="PostgreSQL database URL (postgresql+asyncpg://...)"
    )

    # Security
    SECRET_KEY: str = Field(
        description="Secret key for JWT (min 32 characters)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )

    # CORS
    BACKEND_CORS_ORIGINS: str = ""

    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """
        Parse CORS origins from comma-separated string.
        """
        if not v or v == "":
            return []
        # Разделить по запятой и убрать пробелы
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        env_nested_delimiter="__"
    )

    # Computed properties
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


# Create global settings instance
settings = Settings()