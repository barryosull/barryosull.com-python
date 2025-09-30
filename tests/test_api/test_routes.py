"""Tests for API routes."""

from fastapi.testclient import TestClient
from my_app.web import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to My App"}


def test_greet():
    """Test greet endpoint."""
    response = client.post("/greet", json={"name": "World"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}