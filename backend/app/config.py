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
    PEXELS_API_KEY: str = ""  # only for `labbox cover` (stock photos for lab cards); free at pexels.com/api
    # Only for `labbox cover --generate` (AI cover art). Never used by the running app.
    # OpenAI is used when its key is set, otherwise Gemini.
    OPENAI_API_KEY: str = ""
    OPENAI_IMAGE_MODEL: str = "gpt-image-2"
    GEMINI_API_KEY: str = ""
    GEMINI_IMAGE_MODEL: str = "gemini-nano-banana-2.1"

    # LLM gateway (Phase E). Labs call model aliases; this maps each alias to provider/model.
    # Providers: ollama (free, local: scripts/ollama.sh), openai, gemini, fake (tests). Paid providers
    # use the keys above, so pointing an alias at one needs the owner's approval.
    LLM_GATEWAY_ENABLED: bool = True
    LLM_GATEWAY_HOST: str = ""  # empty: the Docker bridge address, so lab relays can reach it
    LLM_GATEWAY_PORT: int = 9000
    LLM_MODELS: str = (
        "lab-chat=ollama/qwen2.5:0.5b,lab-chat-smart=ollama/qwen2.5:1.5b,lab-embed=ollama/nomic-embed-text,"
        "lab-code=ollama/qwen2.5-coder:1.5b"
    )
    OLLAMA_URL: str = "http://127.0.0.1:11434"
    LLM_DAILY_TOKENS: int = 50_000  # per user, per UTC day, all labs and the tutor together
    LLM_RPM: int = 20  # requests per minute per user
    LLM_MAX_TOKENS: int = 1024  # cap on the reply length of one request
    LLM_TIMEOUT_SECONDS: float = 120
    AI_COMPLETION: bool = True  # ghost-text code completion in the editor (alias lab-code)
    LLM_COMPLETION_RPM: int = 30  # editor completions have their own limits
    LLM_COMPLETION_DAILY_TOKENS: int = 200_000

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
    def llm_models(self) -> dict[str, tuple[str, str]]:
        """alias -> (provider, model), from LLM_MODELS ("alias=provider/model,...")."""
        out: dict[str, tuple[str, str]] = {}
        for part in self.LLM_MODELS.split(","):
            if "=" not in part:
                continue
            alias, target = (x.strip() for x in part.split("=", 1))
            provider, _, model = target.partition("/")
            if alias and provider and model:
                out[alias] = (provider, model)
        return out

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
