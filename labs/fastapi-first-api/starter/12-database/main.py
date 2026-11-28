"""Lostdesk, chapter 12: a real database. Found items now live in SQLite, through SQLModel."""
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select


class ItemCreate(SQLModel):
    """What staff send."""

    title: str = Field(min_length=3, max_length=60)
    station: str


class Item(SQLModel, table=True):
    """A row in the item table."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    station: str
    status: str = "held"


engine = create_engine("sqlite:///lostdesk.db", connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)  # create the tables, once, when the server starts
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/items")
def list_items(session: SessionDep) -> list[Item]:
    return session.exec(select(Item)).all()


# TODO (task create_found): POST /items takes an ItemCreate, saves it as an Item row (add, commit, refresh) and gives
# back the Item with its new id, status 201.


# TODO (task read_found): GET /items/{item_id} gives back one Item from the database (session.get), or 404.
