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


# TODO (task claim_flow): POST /claims takes a ClaimIn. An unknown item or report gives 404; an item that is not "held",
# or a report that is not "open", gives 409. Otherwise the item becomes "claimed", the report "matched", and a new Claim
# row is saved, all in one commit; give back the Claim with status 201.


# TODO (task collect_item): POST /claims/{claim_id}/collect marks the owner's visit: the item becomes "returned" and the
# claim's collected_on becomes today's date. An unknown claim gives 404; collecting twice gives 409.
