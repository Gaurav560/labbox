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


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep) -> Item:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.get("/items/{item_id}")
def read_item(item_id: int, session: SessionDep) -> Item:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No item with that id")
    return item
