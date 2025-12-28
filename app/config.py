from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "flags"
    
    # API configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # API Keys (comma-separated for multiple keys)
    API_KEYS: str = "dev-api-key-12345"
    
    @property
    def database_url(self) -> str:
        """Construct database URL from components."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
