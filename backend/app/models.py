from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    # SQLite drops tzinfo, so store naive UTC everywhere.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=utcnow)


class Workspace(SQLModel, table=True):
    # one row per (user, lab)
    __table_args__ = (UniqueConstraint("user_id", "lab_id"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    container_name: str = Field(unique=True)  # lab-u{user_id}-{lab_id}
    volume_path: str  # host path
    seeded: bool = False  # starter files copied?
    last_active_at: datetime = Field(default_factory=utcnow)
    created_at: datetime = Field(default_factory=utcnow)


class CheckRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str = Field(index=True)
    chapter_id: str
    passed_count: int
    total_count: int
    results_json: str  # list of {task, passed, message}
    output_tail: str
    duration_ms: int
    created_at: datetime = Field(default_factory=utcnow)
