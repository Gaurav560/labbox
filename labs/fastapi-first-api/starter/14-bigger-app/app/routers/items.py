"""Every route about found items. main.py includes this router under /items."""
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from ..database import SessionDep
from ..models import Item, ItemCreate, ItemPublic

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: SessionDep) -> ItemPublic:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("")
def list_items(session: SessionDep) -> list[ItemPublic]:
    return session.exec(select(Item).order_by(Item.id)).all()


@router.get("/{item_id}")
def read_item(item_id: int, session: SessionDep) -> ItemPublic:
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="No item with that id")
    return item
