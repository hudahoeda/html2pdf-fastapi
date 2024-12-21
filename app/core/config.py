from typing import List
import json
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    API_KEY_NAME: str
    HOST: str
    PORT: int = 8000
    TZ: str = "UTC"

    model_config = {
        "env_file": ".env"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure PORT is an integer
        if isinstance(self.PORT, str):
            self.PORT = int(self.PORT)

settings = Settings() 