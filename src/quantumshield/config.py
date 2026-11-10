"""Central application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings with safe development defaults."""

    model_config = SettingsConfigDict(
        env_prefix="QUANTUMSHIELD_",
        env_file=".env",
        extra="ignore",
    )

    env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    data_dir: Path = Path("./data")
    master_key: str = ""
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024)
    allowed_origins: str = "http://localhost:3000"

    @property
    def vault_dir(self) -> Path:
        path = self.data_dir / "vault"
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
