"""Lostdesk, chapter 21: the capstone. A found item meets its owner's report, and goes home."""
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOSTDESK_")
    database_url: str = "sqlite:///lostdesk.db"
    desk_key: str = "riverside-desk-7"


settings = Settings()


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    station: str
    status: str = "held"  # held, claimed, returned


class Report(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    contact: str
    status: str = "open"  # open, matched


class Claim(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    report_id: int = Field(foreign_key="report.id")
    collected_on: date | None = None


class ClaimIn(SQLModel):
    item_id: int
    report_id: int


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def require_desk(x_desk_key: Annotated[str | None, Header()] = None) -> None:
    if x_desk_key != settings.desk_key:
        raise HTTPException(status_code=401, detail="Only staff at a desk can do this")


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Lostdesk", version="1.0.0", lifespan=lifespan, dependencies=[Depends(require_desk)])


@app.post("/items", status_code=status.HTTP_201_CREATED)
def log_item(item: Item, session: SessionDep) -> Item:
    item.id, item.status = None, "held"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.post("/reports", status_code=status.HTTP_201_CREATED)
def file_report(report: Report, session: SessionDep) -> Report:
    report.id, report.status = None, "open"
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


@app.get("/claims")
def list_claims(session: SessionDep) -> list[Claim]:
    return session.exec(select(Claim).order_by(Claim.id)).all()


@app.post("/claims", status_code=status.HTTP_201_CREATED)
def create_claim(claim: ClaimIn, session: SessionDep) -> Claim:
    item = session.get(Item, claim.item_id)
    report = session.get(Report, claim.report_id)
    if item is None or report is None:
        raise HTTPException(status_code=404, detail="No such item or report")
    if item.status != "held":
        raise HTTPException(status_code=409, detail=f"Item {item.id} is already {item.status}")
    if report.status != "open":
        raise HTTPException(status_code=409, detail=f"Report {report.id} is already {report.status}")
    item.status, report.status = "claimed", "matched"
    db_claim = Claim(item_id=item.id, report_id=report.id)
    session.add_all([item, report, db_claim])
    session.commit()
    session.refresh(db_claim)
    return db_claim


@app.post("/claims/{claim_id}/collect")
def collect(claim_id: int, session: SessionDep) -> Claim:
    claim = session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="No claim with that id")
    if claim.collected_on is not None:
        raise HTTPException(status_code=409, detail=f"Claim {claim.id} was collected on {claim.collected_on}")
    item = session.get(Item, claim.item_id)
    item.status = "returned"
    claim.collected_on = date.today()
    session.add_all([item, claim])
    session.commit()
    session.refresh(claim)
    return claim
