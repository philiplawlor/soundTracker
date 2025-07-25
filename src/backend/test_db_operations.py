"""Test database operations for the SoundEvent model."""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from models import SoundEvent, SoundEventCreate, SoundType
from database import engine, create_db_and_tables

def test_create_sound_event():
    """Test creating a sound event in the database."""
    # Create test data
    test_event = SoundEventCreate(
        audio_file_path="/test/audio/file.wav",
        sound_type=SoundType.SPEECH,
        confidence=0.95,
        noise_level_db=42.5,
        duration_seconds=10.5,
        sample_rate=44100,
        channels=2,
        event_metadata={
            "speaker_id": "spk_123",
            "language": "en-US",
            "transcription": "This is a test transcription"
        }
    )
    
    # Create database session
    with Session(engine) as session:
        # Create and add the event
        db_event = SoundEvent.model_validate(test_event)
        session.add(db_event)
        session.commit()
        session.refresh(db_event)
        
        print(f"Created event with ID: {db_event.id}")
        
        # Query the event back
        statement = select(SoundEvent).where(SoundEvent.id == db_event.id)
        result = session.exec(statement).first()
        
        if result:
            print("Successfully retrieved event:")
            print(f"  ID: {result.id}")
            print(f"  Timestamp: {result.timestamp}")
            print(f"  Sound Type: {result.sound_type}")
            print(f"  Confidence: {result.confidence}")
            print(f"  Metadata: {result.event_metadata}")
            return True
        return False

def test_query_events():
    """Test querying sound events from the database."""
    with Session(engine) as session:
        # Get all events
        statement = select(SoundEvent).order_by(SoundEvent.timestamp.desc())
        results = session.exec(statement).all()
        
        print(f"\nFound {len(results)} events in the database:")
        for event in results:
            print(f"- ID: {event.id}, Type: {event.sound_type}, "
                  f"Timestamp: {event.timestamp}, "
                  f"File: {event.audio_file_path}")
        
        return len(results) > 0

if __name__ == "__main__":
    print("Setting up database...")
    create_db_and_tables()
    
    print("\n=== Testing SoundEvent Creation ===")
    create_success = test_create_sound_event()
    
    print("\n=== Testing Query ===")
    query_success = test_query_events()
    
    if create_success and query_success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
