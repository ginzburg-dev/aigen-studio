import tempfile
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AigenConfig(BaseSettings):
    """Configuration for Aigen Studio."""

    model_config = SettingsConfigDict()
    cache_dir: str = Field(alias="AIGEN_CACHE_DIR", default="")
    openai_api_key: str = Field(alias="OPENAI_API_KEY", default="")

    def get_cache_dir(self) -> Path:
        """Returns the cache directory path, using a temporary directory if not set."""
        if self.cache_dir:
            return Path(self.cache_dir)
        else:
            temp_dir = Path(tempfile.gettempdir())
            return temp_dir / "aigen_cache"
