import os
import secrets
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "ALIST-IMAGE-API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server & Ports
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "5235"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/alist_images.db")
    
    # Rate Limiting & Anti-leech
    DEFAULT_RATE_LIMIT_QPM: int = int(os.getenv("DEFAULT_RATE_LIMIT_QPM", "120"))
    ANTI_REPEAT_WINDOW_SIZE: int = int(os.getenv("ANTI_REPEAT_WINDOW_SIZE", "20"))
    
    # Default Admin
    DEFAULT_ADMIN_USER: str = os.getenv("ADMIN_USER", "admin")
    DEFAULT_ADMIN_PASS: str = os.getenv("ADMIN_PASS", "admin123")

settings = Settings()
