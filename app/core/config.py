from typing import Set
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEYS: Set[str] = {"your-secret-api-key-1", "your-secret-api-key-2"}  # Replace with your actual API keys
    API_KEY_NAME: str = "x-api-key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 