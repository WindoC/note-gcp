import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    username: str = os.getenv("USERNAME", "admin")
    password_hash: str = os.getenv("PASSWORD_HASH", "")
    firestore_project: str = os.getenv("FIRESTORE_PROJECT", "")
    firestore_emulator_host: Optional[str] = os.getenv("FIRESTORE_EMULATOR_HOST", None)
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    environment: str = os.getenv("ENVIRONMENT", "development")
    aes_key: str = os.getenv("AES_KEY", "")
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def cookie_secure(self) -> bool:
        return self.is_production
    
    @property
    def cookie_samesite(self) -> str:
        return "strict" if self.is_production else "lax"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()