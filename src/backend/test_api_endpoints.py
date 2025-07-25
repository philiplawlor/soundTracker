"""Test script for the SoundEvent API endpoints."""
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
BACKEND_DIR = Path(__file__).parent.absolute()
sys.path.append(str(BACKEND_DIR))

# Test configuration
BASE_URL = "http://localhost:8000/api/v1"
SOUNDS_ENDPOINT = f"{BASE_URL}/sounds"

# Print API base URL for debugging
print(f"🔍 Testing API at: {BASE_URL}")
print(f"🔍 Sounds endpoint: {SOUNDS_ENDPOINT}")

class TestData:
    """Test data for the API tests."""
    @staticmethod
    def create_sound_event_data() -> Dict[str, Any]:
        """Create test data for a sound event."""
        return {
            "audio_file_path": "/test/audio/sample.wav",
            "sound_type": "speech",
            "confidence": 0.95,
            "noise_level_db": 42.5,
            "duration_seconds": 10.5,
            "sample_rate": 44100,
            "channels": 2,
            "event_metadata": {
                "speaker_id": "spk_123",
                "language": "en-US",
                "transcription": "This is a test transcription"
            }
        }

class TestClient:
    """Test client for the API."""
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = None
        self.created_event_ids = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensure client is closed."""
        if self.client:
            await self.client.aclose()
    
    async def create_test_event(self) -> Dict[str, Any]:
        """Create a test event and return its data."""
        data = TestData.create_sound_event_data()
        url = f"{self.base_url}/sounds"
        logger.info(f"Creating test event with data: {json.dumps(data, indent=2)}")
        logger.info(f"POST {url}")
        
        try:
            response = await self.client.post(url, json=data)
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response body: {response.text}")
            
            if response.status_code != 201:
                logger.error(f"Failed to create test event: {response.status_code} - {response.text}")
                
            assert response.status_code == 201, f"Failed to create test event: {response.status_code} - {response.text}"
            
            event = response.json()
            logger.info(f"Created event with ID: {event.get('id')}")
            self.created_event_ids.append(event["id"])
            return event
            
        except Exception as e:
            logger.error(f"Error creating test event: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up any test data."""
        for event_id in self.created_event_ids:
            try:
                await self.client.delete(f"{self.base_url}/sounds/{event_id}")
            except Exception as e:
                print(f"Warning: Failed to clean up event {event_id}: {e}")
        self.created_event_ids = []

async def test_create_event():
    """Test creating a sound event."""
    async with TestClient() as client:
        data = TestData.create_sound_event_data()
        response = await client.client.post(
            f"{SOUNDS_ENDPOINT}",
            json=data
        )
        assert response.status_code == 201, f"Failed to create event: {response.text}"
        event = response.json()
        assert event["id"] is not None
        assert event["timestamp"] is not None
        assert event["sound_type"] == data["sound_type"]
        assert event["confidence"] == data["confidence"]
        assert event["event_metadata"] == data["event_metadata"]
        print("✅ Create event test passed")
        return event["id"]

async def test_get_event():
    """Test getting a sound event by ID."""
    async with TestClient() as client:
        # First create a test event
        event_id = await test_create_event()
        
        # Now try to get it
        response = await client.client.get(f"{SOUNDS_ENDPOINT}/{event_id}")
        assert response.status_code == 200, f"Failed to get event: {response.text}"
        event = response.json()
        assert event["id"] == event_id
        print("✅ Get event test passed")

async def test_list_events():
    """Test listing sound events with filters."""
    async with TestClient() as client:
        # Create a couple of test events
        event1_id = await test_create_event()
        event2_id = await test_create_event()
        
        # Test basic listing
        response = await client.client.get(f"{SOUNDS_ENDPOINT}")
        assert response.status_code == 200, f"Failed to list events: {response.text}"
        events = response.json()
        assert len(events) >= 2, "Expected at least 2 events"
        
        # Test filtering by sound_type
        response = await client.client.get(
            f"{SOUNDS_ENDPOINT}?sound_type=speech"
        )
        assert response.status_code == 200
        events = response.json()
        assert all(e["sound_type"] == "speech" for e in events)
        
        print("✅ List events test passed")

async def test_delete_event():
    """Test deleting a sound event."""
    async with TestClient() as client:
        # First create a test event
        event_id = await test_create_event()
        
        # Now delete it
        response = await client.client.delete(f"{SOUNDS_ENDPOINT}/{event_id}")
        assert response.status_code == 204, f"Failed to delete event: {response.text}"
        
        # Verify it's gone
        response = await client.client.get(f"{SOUNDS_ENDPOINT}/{event_id}")
        assert response.status_code == 404, "Event should be deleted but still exists"
        
        print("✅ Delete event test passed")

async def run_tests():
    """Run all API tests."""
    print("🚀 Starting API tests...\n")
    
    tests = [
        ("Create Event", test_create_event),
        ("Get Event", test_get_event),
        ("List Events", test_list_events),
        ("Delete Event", test_delete_event)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"🧪 Running test: {name}...")
            await test_func()
            print(f"✅ {name} test passed\n")
            passed += 1
        except Exception as e:
            print(f"❌ {name} test failed: {str(e)}\n")
            import traceback
            traceback.print_exc()
            print()
            failed += 1
    
    print("\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🏆 Total: {passed + failed}")
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
