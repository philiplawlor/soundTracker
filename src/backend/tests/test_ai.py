import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os

# Import the router from the application, but NOT the global ai_model
from ..routers.ai import router as ai_router
from ..database import get_session
from ..models import SoundEvent

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def get_session_override() -> Generator[Session, None, None]:
    """Override the get_session dependency for tests."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

# Create a new FastAPI app instance for testing
app = FastAPI()
# The prefix must match how it's included in the main app
app.include_router(ai_router, prefix="/api/v1/ai")

# Override the database dependency for the entire app
app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

# A minimal, silent WAV file for testing
# This is a valid 16-bit PCM, 16kHz, mono WAV file of silence
SILENT_WAV_CONTENT = (
    b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00\xfa\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
)
TEST_AUDIO_PATH = "test_audio.wav"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_module():
    """Create the test audio file before tests run, and clean up after."""
    with open(TEST_AUDIO_PATH, "wb") as f:
        f.write(SILENT_WAV_CONTENT)
    yield
    if os.path.exists(TEST_AUDIO_PATH):
        os.remove(TEST_AUDIO_PATH)

def test_identify_sound_and_save_to_db():
    """
    Test the /api/v1/ai/identify endpoint.
    It should process an audio file, return a classification,
    and save the event to the database.
    The AI model is initialized on first use by the `get_ai_model` dependency.
    """
    with open(TEST_AUDIO_PATH, "rb") as audio_file:
        response = client.post(
            "/api/v1/ai/identify",
            files={"file": (TEST_AUDIO_PATH, audio_file, "audio/wav")}
        )
    
    assert response.status_code == 200, f"API call failed with {response.status_code}: {response.text}"
    data = response.json()
    assert "label" in data
    # The dummy audio is silent, so it will likely be classified as "Silence"
    # Note: YAMNet can sometimes classify silence as other low-energy sounds.
    # If this fails, we may need a more robust check.
    assert data["label"] == "Silence"

    # Verify that the event was saved to the database
    # We need a separate session to query the DB after the request-response cycle is complete
    with Session(engine) as session:
        events = session.query(SoundEvent).all()
        assert len(events) >= 1, "No events were saved to the database"
        latest_event = events[-1]
        assert latest_event.sound_type == "Silence"
        assert latest_event.confidence is not None
