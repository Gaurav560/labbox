"""Tests for Lostdesk. Run them with: python -m pytest -q (from the 15-testing folder)."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()


UMBRELLA = {"title": "black umbrella", "category": "umbrella", "station": "Riverside"}
PHONE = {"title": "silver phone", "category": "phone", "station": "Tech Park"}


def test_unknown_item_is_404(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No item with that id"}


def test_create_gives_201_and_the_new_item(client):
    response = client.post("/items", json=UMBRELLA)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "black umbrella"
    assert data["status"] == "held"
    assert isinstance(data["id"], int)


def test_created_item_can_be_read_back(client):
    created = client.post("/items", json=UMBRELLA).json()
    response = client.get(f"/items/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_station_filter(client):
    client.post("/items", json=UMBRELLA)
    client.post("/items", json=PHONE)
    response = client.get("/items", params={"station": "Tech Park"})
    assert [item["title"] for item in response.json()] == ["silver phone"]
