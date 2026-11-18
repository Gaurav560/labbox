from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 720
    LABS_DIR: Path = Path("../labs")
    VOLUMES_DIR: Path = Path("/srv/labbox/volumes")
    CHECKS_DIR: Path = Path("/srv/labbox/checks")
    DATABASE_URL: str = "sqlite:///./data/labbox.db"
    CONTAINER_RUNTIME: str = ""
    IDLE_STOP_MINUTES: float = 15
    REAPER_INTERVAL_SECONDS: float = 60
    MAX_FILE_BYTES: int = 1_000_000
    CORS_ORIGINS: str = "http://localhost:5173"
    ALLOW_SIGNUP: bool = True

    @field_validator("JWT_SECRET")
    @classmethod
    def secret_long_enough(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters")
        return v

    @field_validator("LABS_DIR", "VOLUMES_DIR", "CHECKS_DIR")
    @classmethod
    def relative_to_backend(cls, v: Path) -> Path:
        # Relative paths are relative to backend/, not to wherever uvicorn was started.
        return v if v.is_absolute() else (BACKEND_DIR / v).resolve()

    @field_validator("DATABASE_URL")
    @classmethod
    def sqlite_relative_to_backend(cls, v: str) -> str:
        prefix = "sqlite:///"
        if v.startswith(prefix) and not v.startswith(prefix + "/"):
            return prefix + str((BACKEND_DIR / v[len(prefix):]).resolve())
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
