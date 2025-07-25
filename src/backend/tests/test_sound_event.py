import pytest
from fastapi.testclient import TestClient
from backend.main import app
from sqlmodel import SQLModel, create_engine, Session
from backend.database import get_session
import os

import backend.database

import os
import backend.database

@pytest.fixture(name="client")
def client_fixture():
    # Use a temporary SQLite file for testing
    test_db_path = "./test.db"
    db_url = f"sqlite:///{test_db_path}"
    engine = create_engine(db_url)

    # Patch the backend.database.engine to use the test engine
    backend.database.engine = engine

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    # Create tables on the test engine
    SQLModel.metadata.create_all(engine)

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    if os.path.exists(test_db_path):
        engine.dispose()  # Ensure all connections are closed
        os.remove(test_db_path)

def test_create_and_read_sound_event(client):
    payload = {
        "timestamp": "2025-05-15T12:00:00",
        "noise_level": 42.5,
        "sound_type": "speech",
        "description": "Talking"
    }
    response = client.post("/sound-events/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["noise_level"] == 42.5
    assert data["sound_type"] == "speech"
    assert data["description"] == "Talking"

    # Test read all
    response = client.get("/sound-events/")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["id"] == 1

    # Test read by id
    response = client.get(f"/sound-events/1")
    assert response.status_code == 200
    event = response.json()
    assert event["id"] == 1
