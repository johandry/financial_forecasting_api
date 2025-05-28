import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_users_initially_empty():
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    user_data = {"email": "testuser@example.com", "password": "testpass123"}
    response = client.post("/users", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_create_user_duplicate_email():
    user_data = {"email": "duplicate@example.com", "password": "testpass123"}
    # First creation should succeed
    response1 = client.post("/users", json=user_data)
    assert response1.status_code == 200
    # Second creation should fail
    response2 = client.post("/users", json=user_data)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"

def test_list_users_after_creation():
    # Create a user
    user_data = {"email": "anotheruser@example.com", "password": "testpass123"}
    client.post("/users", json=user_data)
    # List users
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert any(u["email"] == "anotheruser@example.com" for u in users)