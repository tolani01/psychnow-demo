"""
Application Configuration Settings
Loads environment variables and provides typed settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "PsychNow"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False  # Default to False, override with environment variable
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./psychnow.db"
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 2000
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = "http://localhost:5173,http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:5173,https://psychnow-demo.web.app,https://psychnow-demo.firebaseapp.com"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Provider Invite
    PROVIDER_INVITE_CODE: str = "PSYCHNOW-PROVIDER-2024"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    PDF_DIR: str = "./pdfs"
    
    # Email Settings (Optional - for demo notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ADMIN_EMAIL: str = "admin@psychnow.com"
    FROM_EMAIL: str = "noreply@psychnow.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",  # Handle BOM
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields
    )


# Create global settings instance
settings = Settings()

