from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Authentication
    API_KEY: str  # Coolify provides this
    API_KEY_NAME: str = "x-api-key"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    TZ: str = "UTC"

    # Coolify specific variables
    SOURCE_COMMIT: Optional[str] = None
    COOLIFY_URL: Optional[str] = None
    COOLIFY_FQDN: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "extra": "allow"  # Allow extra fields from Coolify
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure PORT is an integer
        if isinstance(self.PORT, str):
            self.PORT = int(self.PORT)

    @property
    def api_key(self) -> str:
        """Get the API key from API_KEYS."""
        return self.API_KEYS

settings = Settings() 