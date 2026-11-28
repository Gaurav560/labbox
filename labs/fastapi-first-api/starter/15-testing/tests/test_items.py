"""Tests for Lostdesk. Run them with: python -m pytest -q (from the 15-testing folder)."""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:  # "with" runs the app's lifespan, which creates the tables
        yield test_client


def test_unknown_item_is_404(client):
    response = client.get("/items/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No item with that id"}


# TODO (task override_db): these tests use the real database file, lostdesk.db. Add a pytest fixture that gives the
# app a fresh in-memory database instead (app.dependency_overrides[get_session]), and use it in every test.


# TODO (task write_tests): add tests that prove: POST /items answers 201 with the new item and its id; the new item
# can be read back with GET /items/{id}; GET /items?station=... gives only that station's items.
