"""Lostdesk, chapter 13: create, read, update and delete, with separate models for each direction."""
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlmodel import Field, Session, SQLModel, col, create_engine, select


class ItemBase(SQLModel):
    title: str = Field(min_length=3, max_length=60, index=True)
    category: str
    station: str = Field(index=True)


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = "held"


class ItemCreate(ItemBase):
    pass


class ItemPublic(ItemBase):
    id: int
    status: str


class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=3, max_length=60)
    category: str | None = None
    station: str | None = None
    status: str | None = None


engine = create_engine("sqlite:///lostdesk.db", connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def find(session: Session, item_id: int) -> Item:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No item with that id")
    return item


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep) -> ItemPublic:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.get("/items")
def list_items(
    session: SessionDep,
    station: str | None = None,
    q: Annotated[str | None, Query(min_length=3)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[ItemPublic]:
    # TODO (task filter_db): when station is given, keep only that station's items; when q is given, only items whose
    # title contains q. Let the database do it: add .where(...) to the query.
    query = select(Item)
    return session.exec(query.order_by(Item.id).offset(offset).limit(limit)).all()


@app.get("/items/{item_id}")
def read_item(item_id: int, session: SessionDep) -> ItemPublic:
    return find(session, item_id)


# TODO (task update_db): PATCH /items/{item_id} takes an ItemUpdate, changes only the fields that were sent, saves the
# row (add, commit, refresh) and gives back the ItemPublic; an unknown id gives 404.


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: SessionDep):
    session.delete(find(session, item_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
