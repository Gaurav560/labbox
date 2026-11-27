"""Claimdesk's settings, read from the environment, so the same code runs on a laptop, in CI and in production."""
from dataclasses import dataclass, field


class ConfigError(Exception):
    """Every setting that is missing or wrong, in one message."""


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str = field(repr=False)  # never printed, never logged
    pilot_limit_rs: int = 50000
    prompt_version: str = "v1"
    db_path: str = "data/claimdesk.db"


REQUIRED = ["OPENAI_BASE_URL", "OPENAI_API_KEY"]


def settings_from_env(env):
    """Settings from a dict of environment variables (os.environ in real use). Required: OPENAI_BASE_URL, OPENAI_API_KEY.
    Optional: PILOT_LIMIT_RS (a positive whole number, default 50000), PROMPT_VERSION (default "v1"), CLAIMDESK_DB
    (default "data/claimdesk.db"). Raises ConfigError naming every problem, joined by "; ":
    "<NAME> is not set" for each missing (or empty) required variable, in the order of REQUIRED, then
    "PILOT_LIMIT_RS must be a positive whole number of rupees" when it is given but wrong. Never puts a value in a message."""
    problems = [f"{name} is not set" for name in REQUIRED if not env.get(name)]
    limit = env.get("PILOT_LIMIT_RS", "50000")
    if not (limit.isdigit() and int(limit) > 0):
        problems.append("PILOT_LIMIT_RS must be a positive whole number of rupees")
    if problems:
        raise ConfigError("; ".join(problems))
    return Settings(
        base_url=env["OPENAI_BASE_URL"],
        api_key=env["OPENAI_API_KEY"],
        pilot_limit_rs=int(limit),
        prompt_version=env.get("PROMPT_VERSION", "v1"),
        db_path=env.get("CLAIMDESK_DB", "data/claimdesk.db"),
    )
