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
    # How many labs this learner may have unlocked at once (owner, 26 November). None: the site's setting
    # (site_setting "lab_limit"); 0: every lab; N: N labs. Set by an admin on the learner's row.
    lab_limit: int | None = None
    # A verified email address, from Google or GitHub sign-in (owner, 27 November); None for username-only accounts.
    email: str | None = Field(default=None, unique=True, index=True)
    email_verified_at: datetime | None = None
    # "free" or "pro" (owner, 28 November). Set by an admin by hand until payments exist; Jarvis's voice is for Pro.
    plan: str = "free"
    # Jarvis, as this learner set him (owner, 28 November, step 4): "tap" (he offers, a tap starts the talk), "first" (Pro:
    # he starts talking himself when he has something to say, if the browser allows it), or "off" (no offers, no orb).
    jarvis_mode: str = "tap"
    jarvis_note_seen: bool = False  # read "What Jarvis can see" (shown once, before the first conversation)


class UserIdentity(SQLModel, table=True):
    """A Google or GitHub account that signs into a LabBox account (owner, 27 November). One row per provider account;
    a LabBox account may have several (Google and GitHub with the same verified email end up in the same account)."""
    __tablename__ = "user_identity"
    __table_args__ = (UniqueConstraint("provider", "subject"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    provider: str  # "google" or "github"
    subject: str  # the provider's stable id for the person (Google "sub", GitHub numeric id)
    email: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    last_login_at: datetime = Field(default_factory=utcnow)


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
    certificate_name: str | None = None  # the full name for certificates, typed when the first one is claimed
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


class SiteSetting(SQLModel, table=True):
    """Settings an admin changes in the app, one row per key (owner, 26 November). Today: "lab_limit", how many
    labs a learner may have unlocked at once ("0" or no row: every lab is open)."""
    __tablename__ = "site_setting"

    key: str = Field(primary_key=True)
    value: str = ""
    updated_at: datetime = Field(default_factory=utcnow)
    updated_by: int | None = None  # the admin's user id


class Certificate(SQLModel, table=True):
    """A lab completed (owner, 27 November: 80% of its tasks passed, the same moment its slot frees), with a public
    page at /c/<id> to share on LinkedIn, X and elsewhere. One per (user, lab). The name is the one the learner typed
    for certificates (user_profile.certificate_name), copied here so later changes never alter an issued one, except
    the single correction the learner may make."""
    __tablename__ = "certificate"
    __table_args__ = (UniqueConstraint("user_id", "lab_id"),)

    id: str = Field(primary_key=True)  # 8 characters, easy to read aloud: no 0, 1, I, L, O or U
    user_id: int = Field(foreign_key="user.id", index=True)
    lab_id: str
    name: str
    tasks_passed: int
    tasks_total: int
    chapters_total: int
    issued_at: datetime = Field(default_factory=utcnow)
    hidden: bool = False  # the learner may hide it: its page then says it is not available
    name_corrected: bool = False  # one correction of the name, then it is final


class LabSlot(SQLModel, table=True):
    """A lab a learner unlocked (owner, 26 November: at most a few labs at a time, so learners focus). One row per
    (user, lab); a Monday swap sets released_at, and unlocking the lab again clears it."""
    __tablename__ = "lab_slot"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    lab_id: str = Field(primary_key=True)
    unlocked_at: datetime = Field(default_factory=utcnow)
    released_at: datetime | None = None
    released_reason: str | None = None  # "swapped"


class JarvisSession(SQLModel, table=True):
    """One voice conversation with Jarvis (owner, 28 November): who, where, how long, and what it cost, from the usage
    OpenAI reports after each reply. kind is "pro" or "trial" (a free learner's one-time taste)."""
    __tablename__ = "jarvis_session"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    kind: str = "pro"
    lab_id: str | None = None
    chapter_id: str | None = None
    started_at: datetime = Field(default_factory=utcnow, index=True)
    last_seen_at: datetime = Field(default_factory=utcnow)
    ended_at: datetime | None = None
    seconds: int = 0
    max_seconds: int = 0
    audio_in_tokens: int = 0
    audio_cached_tokens: int = 0
    text_in_tokens: int = 0
    text_cached_tokens: int = 0
    audio_out_tokens: int = 0
    text_out_tokens: int = 0
    cost_usd: float = 0.0
    call_id: str | None = None
    # What Jarvis keeps from this conversation for the next ones (step 3, Pro): two or three sentences he writes
    # himself at the end. None when the conversation ended before he could.
    summary: str | None = None
