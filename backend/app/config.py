"""
Configuration settings for the OpenForge backend

All sensitive information (MongoDB credentials, API keys) must be provided
via environment variables or .env file. Never hardcode credentials in source code.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings
    
    Sensitive fields must be set in .env file:
    - MONGODB_URL: MongoDB connection string (required)
    - MONGODB_DB_NAME: Database name (optional, defaults based on environment)
    - CLERK_SECRET_KEY: Clerk authentication secret (optional)
    - ENVIRONMENT: Environment name (dev, prod, default: dev)
    - FRONTEND_URL: Frontend URL for CORS (required in production)
    """
    
    # Environment
    environment: str = Field(
        default="dev",
        description="Environment name: 'dev' or 'prod'. Set as ENVIRONMENT in .env"
    )
    
    # MongoDB - Read from environment variables only (sensitive, required)
    mongodb_url: str = Field(
        ...,
        description="MongoDB connection string. Must be set in .env file as MONGODB_URL"
    )
    mongodb_db_name: Optional[str] = Field(
        default=None,
        description="MongoDB database name. If not set, defaults to 'openforge-dev' or 'openforge-prod' based on ENVIRONMENT"
    )
    
    # Clerk Authentication - Read from environment variables only (sensitive, optional)
    clerk_secret_key: Optional[str] = Field(
        default=None,
        description="Clerk secret key. Set as CLERK_SECRET_KEY in .env"
    )
    
    # GitHub API - Read from environment variables only (sensitive, optional)
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub personal access token for authenticated API requests. Set as GITHUB_TOKEN in .env. Optional but recommended for higher rate limits."
    )
    
    # API & CORS
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="API base URL for frontend"
    )
    frontend_url: Optional[str] = Field(
        default=None,
        description="Frontend URL for CORS. Set as FRONTEND_URL in .env. Required in production."
    )
    
    @model_validator(mode='after')
    def set_default_database_name(self):
        """Auto-set database name based on environment if not explicitly provided or incorrectly set"""
        env_suffix = "prod" if self.environment.lower() == "prod" else "dev"
        expected_db_name = f"openforge-{env_suffix}"
        
        # If not set, or if set to a value without the correct suffix, update it
        if self.mongodb_db_name is None or not self.mongodb_db_name.endswith(f"-{env_suffix}"):
            self.mongodb_db_name = expected_db_name
        return self
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "prod"
    
    @property
    def allowed_origins(self) -> list[str]:
        """Get allowed CORS origins based on environment"""
        origins = ["http://localhost:3000", "http://localhost:3001"]
        if self.frontend_url:
            frontend_url = self.frontend_url.rstrip("/")
            origins.append(frontend_url)
            # Normalize and add variations (with/without trailing slash, with/without www)
            if frontend_url.startswith("https://"):
                base_url = frontend_url.replace("https://", "").replace("www.", "")
                # Add variations for Vercel deployments (preview deployments use different subdomains)
                origins.append(f"https://{base_url}")
                if not frontend_url.startswith("https://www."):
                    origins.append(f"https://www.{base_url}")
        
        return origins
    
    @field_validator('mongodb_url')
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Ensure MongoDB URL is provided and not empty"""
        if not v or not v.strip():
            raise ValueError(
                "MONGODB_URL must be set in environment variables or .env file. "
                "This contains sensitive credentials and should never be hardcoded."
            )
        return v.strip()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Extra fields are ignored for security
        extra = "ignore"


settings = Settings()

