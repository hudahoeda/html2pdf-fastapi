from typing import List
import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEYS: List[str]
    API_KEY_NAME: str
    HOST: str
    PORT: int = 8000
    TZ: str = "UTC"

    @property
    def model_config(self):
        return {"env_file": ".env"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Handle string input for API_KEYS
        if isinstance(self.API_KEYS, str):
            try:
                self.API_KEYS = json.loads(self.API_KEYS)
            except json.JSONDecodeError:
                # Try removing quotes and brackets if present
                clean_str = self.API_KEYS.strip('[]').replace('"', '').replace("'", '')
                self.API_KEYS = [key.strip() for key in clean_str.split(',')]

settings = Settings() 