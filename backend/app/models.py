from datetime import date, datetime, timezone

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
    is_admin: bool = False  # Phase J: may open /admin; granted with `scripts/labbox admin grant <name>`


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


class ChapterProgress(SQLModel, table=True):
    # one row per (user, lab, chapter)
    __tablename__ = "chapter_progress"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    lab_id: str = Field(primary_key=True)
    chapter_id: str = Field(primary_key=True)
    current_step: int = 0
    setup_done: bool = False
    started_at: datetime | None = None  # first opened on a running machine; incident timers count from here
    completed_at: datetime | None = None
    updated_at: datetime = Field(default_factory=utcnow)


class TaskProgress(SQLModel, table=True):
    # one row per (user, lab, task); task ids are unique within a lab
    __tablename__ = "task_progress"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    lab_id: str = Field(primary_key=True)
    task_id: str = Field(primary_key=True)
    chapter_id: str
    passed: bool = False
    hints_used: int = 0
    first_passed_at: datetime | None = None


class PredictAnswer(SQLModel, table=True):
    # one row per attempt, so "right first time" can be worked out later
    __tablename__ = "predict_answer"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    chapter_id: str
    step_index: int
    choice: int
    correct: bool
    created_at: datetime = Field(default_factory=utcnow)


class UserProfile(SQLModel, table=True):
    # Totals here are a cache: they are always recalculated from the xp_event ledger.
    __tablename__ = "user_profile"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    display_name: str | None = None
    timezone: str | None = None  # IANA name, e.g. Asia/Kolkata; None until the browser sends it
    goal: str | None = None
    placement_level: str | None = None
    onboarded_at: datetime | None = None
    level: int = 1
    xp_total: int = 0
    streak_current: int = 0
    streak_best: int = 0
    last_active_day: date | None = None
    # Set once progress made before the ledger existed has been turned into XP.
    backfilled_at: datetime | None = None
    created_at: datetime = Field(default_factory=utcnow)


class XpEvent(SQLModel, table=True):
    # Append-only ledger. ref makes every award happen at most once per user.
    __tablename__ = "xp_event"
    __table_args__ = (UniqueConstraint("user_id", "ref"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    kind: str  # task | predict | chapter | lab | drill
    amount: int
    ref: str  # e.g. task:python-basics:greet
    day: date  # the learner's local day when it was earned (streaks use this)
    lab_id: str | None = None
    chapter_id: str | None = None
    task_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class DrillAnswer(SQLModel, table=True):
    __tablename__ = "drill_answer"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    day: date
    drill_id: str
    choice: int
    correct: bool
    created_at: datetime = Field(default_factory=utcnow)


class LlmRequest(SQLModel, table=True):
    # Every call through the LLM gateway (labs and the tutor): budgets are summed from here, and
    # `lab requests` shows the learner their own rows.
    __tablename__ = "llm_request"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    endpoint: str  # chat | embeddings | messages | tutor | review
    alias: str  # what the lab asked for, e.g. lab-chat
    model: str  # provider/model it went to
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    status: int = 200
    error: str | None = None
    request_json: str = ""  # capped
    response_json: str = ""  # capped
    created_at: datetime = Field(default_factory=utcnow, index=True)


class DesignAnswer(SQLModel, table=True):
    # One graded attempt at a design step (system design labs): the answers and the rubric scores.
    __tablename__ = "design_answer"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    chapter_id: str
    step_index: int
    answers_json: str  # {question id: text}
    result_json: str  # see design.DesignResult
    score: int
    max_score: int
    created_at: datetime = Field(default_factory=utcnow)


class AnalyticsEvent(SQLModel, table=True):
    # Phase J: what the other tables cannot tell. Today: "step" (a learner moved to a lesson step), which
    # gives the time spent on each step. Append-only; kind names what happened.
    __tablename__ = "analytics_event"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    kind: str = Field(index=True)
    lab_id: str | None = Field(default=None, index=True)
    chapter_id: str | None = None
    step_index: int | None = None
    data_json: str = ""
    created_at: datetime = Field(default_factory=utcnow, index=True)


class LibraryItem(SQLModel, table=True):
    """One entry of the Library (owner, 24 November): a book, a research paper or a tech blog worth reading.
    Seeded once from library/seed.yaml by migration 0009; after that admins edit the list in the app."""
    __tablename__ = "library_item"

    id: int | None = Field(default=None, primary_key=True)
    kind: str = Field(index=True)  # book | paper | blog
    title: str
    authors: str = ""
    year: int | None = None
    url: str = ""
    note: str = ""  # why it is worth reading, in plain words
    topic: str = ""  # a short label for the filter, like "AI" or "Databases"
    lab: str = ""  # the LabBox lab where you practise it (a lab id), or empty
    practice: str = ""  # where in that lab, like "chapter 6, the HNSW index"
    level: str = ""  # beginner | intermediate | advanced, or empty
    free: bool = False  # free to read online
    featured: bool = False  # the "Start here" card of its section (at most one per kind)
    image: str = ""  # a picture stored with LabBox: library/images/ (the starting list) or LIBRARY_UPLOADS_DIR
    position: int = 0  # order within its kind, smallest first
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
