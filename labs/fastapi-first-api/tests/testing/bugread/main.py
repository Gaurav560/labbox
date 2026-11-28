"""Lostdesk, chapter 15: the finished chapter 13 app. Your tests prove that it works."""
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
    query = select(Item)
    if station:
        query = query.where(Item.station == station)
    if q:
        query = query.where(col(Item.title).contains(q))
    return session.exec(query.order_by(Item.id).offset(offset).limit(limit)).all()


@app.get("/items/{item_id}")
def read_item(item_id: int, session: SessionDep) -> ItemPublic:
    item = find(session, item_id)
    return ItemPublic(id=item.id, title=item.title, category=item.category, station=item.station, status="returned")


@app.patch("/items/{item_id}")
def update_item(item_id: int, changes: ItemUpdate, session: SessionDep) -> ItemPublic:
    db_item = find(session, item_id)
    db_item.sqlmodel_update(changes.model_dump(exclude_unset=True))
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: SessionDep):
    session.delete(find(session, item_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
