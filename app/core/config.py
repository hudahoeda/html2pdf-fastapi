from typing import List
import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEYS: List[str]
    API_KEY_NAME: str
    HOST: str
    PORT: int = 8000
    TZ: str = "UTC"

    model_config = {
        "env_file": ".env"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle string input for API_KEYS
        if isinstance(self.API_KEYS, str):
            try:
                # First try parsing as JSON
                self.API_KEYS = json.loads(self.API_KEYS)
            except json.JSONDecodeError:
                # If JSON parsing fails, try simple string splitting
                clean_str = self.API_KEYS.strip('[]').replace('"', '').replace("'", '')
                self.API_KEYS = [key.strip() for key in clean_str.split(',') if key.strip()]
        
        # Ensure PORT is an integer
        if isinstance(self.PORT, str):
            self.PORT = int(self.PORT)

settings = Settings() 