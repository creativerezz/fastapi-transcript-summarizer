import os
from functools import lru_cache
from typing import Optional
from pydantic import AnyUrl, Field, model_validator

# Ensure .env file is loaded
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for pydantic v1
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # Pydantic V2 syntax - use validation_alias with string for environment variable names
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    redis_url: AnyUrl | str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    openai_chunk_model: str = "gpt-4.1-mini"
    openai_reduce_model: str = "gpt-4.1"
    
    # Webshare proxy (optional) - supports both naming conventions
    webshare_username: Optional[str] = Field(default=None)
    webshare_password: Optional[str] = Field(default=None)
    
    @model_validator(mode='after')
    def set_webshare_credentials(self):
        """Set Webshare credentials from environment variables if not already set."""
        if self.webshare_username is None:
            self.webshare_username = os.getenv("WEBSHARE_PROXY_USERNAME") or os.getenv("WEBSHARE_USERNAME")
        if self.webshare_password is None:
            self.webshare_password = os.getenv("WEBSHARE_PROXY_PASSWORD") or os.getenv("WEBSHARE_PASSWORD")
        return self
    
    cache_ttl_transcript_seconds: int = 60 * 60 * 24 * 7   # 7 days
    cache_ttl_summary_seconds: int = 60 * 60 * 24 * 30     # 30 days
    max_chars_per_chunk: int = 12000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

