"""Every model of Lostdesk, in one place: tables, and what goes in and out of the API."""
from sqlmodel import Field, SQLModel


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


class ReportBase(SQLModel):
    title: str = Field(min_length=3, max_length=60)
    station: str


class Report(ReportBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    contact: str
    status: str = "open"


class ReportCreate(ReportBase):
    contact: str = Field(min_length=6, max_length=40)


class ReportPublic(ReportBase):
    id: int
    status: str
