import re
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
    # Shared state between workers (Phase H2, app/shared.py): redis://... from scripts/devdb.sh url.
    # Empty: in this process's memory, so run one worker.
    REDIS_URL: str = ""
    # Background worker (Phase H3, app/worker.py): nightly database backups, newest BACKUP_KEEP kept.
    BACKUP_DIR: Path = Path("/srv/labbox/backups")
    LIBRARY_UPLOADS_DIR: Path = Path("/srv/labbox/library")  # pictures admins upload for Library items
    BACKUP_KEEP: int = 14
    BACKUP_HOUR_UTC: int = 21  # 21:00 UTC is 02:30 in India, the quietest hour
    # Safety limits (Phase H5, app/limits.py). 0 turns a limit off.
    DISK_QUOTA_MB: int = 500  # a learner's own files, all labs together
    SERVICE_DATA_MAX_MB: int = 1024  # one lab's databases (seeded data included)
    MAX_RUNNING_LABS: int = 2  # per learner; starting a third stops the least recently used one
    SESSION_HOURS: float = 4  # a machine running this long is stopped (files kept; start it again)
    CPU_STUCK_MINUTES: float = 10  # a machine using all its CPU this long is stopped (an endless loop)
    SIGNUPS_PER_IP_HOUR: int = 60  # generous: a whole classroom can share one address
    LOGIN_FAILS_PER_IP_MINUTE: int = 30
    LOGIN_FAILS_PER_USER_MINUTE: int = 10
    CHECKS_PER_IP_MINUTE: int = 120
    # Operations (Phase H6). LOG_FORMAT: "text" (people) or "json" (one JSON object a line, for log tools).
    LOG_FORMAT: str = "text"
    METRICS_TOKEN: str = ""  # /metrics answers the machine itself, or a request with "Authorization: Bearer <this>"
    SENTRY_DSN: str = ""  # error reports to Sentry; empty: off (nothing is sent anywhere)
    SENTRY_ENVIRONMENT: str = "development"
    CONTAINER_RUNTIME: str = ""
    # A second LabBox on the same Docker (the live site on the owner's laptop, 27 November) sets its own name, e.g.
    # "prod": its lab machines, check containers and lab networks are then named lab-prod-u1-..., carry the label
    # labbox.instance=prod, and each instance's cleanup touches only its own. Empty (the default): the names and
    # labels of before, so existing machines keep working.
    INSTANCE: str = ""
    # The commit being served (the release script sets it); /api/health reports it so a deploy can wait for it.
    RELEASE: str = ""
    # The site's public address, e.g. https://labbox.gauravships.systems: certificate QR codes point at its /verify
    # page. Empty: the address of the request (fine in development).
    PUBLIC_URL: str = ""
    # Per-user lab networks get a /28 each from this range (4,096 networks); empty: Docker's own pool.
    LAB_SUBNET_POOL: str = "10.88.0.0/16"
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
    # OpenAI for every alias (owner, 23 November: "use open ai" for the tutor; Ollama no longer runs on this
    # laptop). ai-chat and ai-embed are the Spring AI course's; lab-chat-smart is the tutor and the design grader.
    # Every call still goes through the gateway's budget and log. lab-code (editor ghost text) needs a
    # fill-in-the-middle model, which gpt-4o-mini is not, so it is left out: completion stays off until the owner
    # picks a model (an Ollama coder model, or another provider).
    LLM_MODELS: str = (
        "lab-chat=openai/gpt-4o-mini,lab-chat-smart=openai/gpt-4o-mini,lab-embed=openai/text-embedding-3-small,"
        "ai-chat=openai/gpt-4o-mini,ai-embed=openai/text-embedding-3-small"
    )
    OLLAMA_URL: str = "http://127.0.0.1:11434"
    LLM_DAILY_TOKENS: int = 50_000  # per user, per UTC day, all labs and the tutor together
    LLM_RPM: int = 20  # requests per minute per user
    LLM_MAX_TOKENS: int = 1024  # cap on the reply length of one request
    LLM_TIMEOUT_SECONDS: float = 120
    # VS Code in the lab (openvscode-server, downloaded once by scripts/openvscode.sh and mounted
    # read-only into every lab machine). Off, or not downloaded: labs use the classic editor.
    IDE_ENABLED: bool = True
    IDE_DIR: Path = Path("/srv/labbox/openvscode")
    IDE_EXTRA_MEMORY_MB: int = 512  # added to a lab machine's memory while VS Code runs in it
    AI_COMPLETION: bool = True  # ghost-text code completion in the editor (alias lab-code)
    LLM_COMPLETION_RPM: int = 30  # editor completions have their own limits
    LLM_COMPLETION_DAILY_TOKENS: int = 200_000
    LLM_EMBED_RPM: int = 300  # embeddings have their own limits: a vector store embeds one document per request
    LLM_EMBED_DAILY_TOKENS: int = 500_000  # about 1 US cent of text-embedding-3-small

    @field_validator("JWT_SECRET")
    @classmethod
    def secret_long_enough(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters")
        return v

    @field_validator("INSTANCE")
    @classmethod
    def instance_name(cls, v: str) -> str:
        if v and not re.fullmatch(r"[a-z][a-z0-9]{0,11}", v):
            raise ValueError("INSTANCE must be lowercase letters and digits, starting with a letter, at most 12")
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
