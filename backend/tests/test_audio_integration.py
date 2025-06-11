"""
Integration tests for audio capture functionality.
"""
import pytest
import asyncio
import websockets
import json
from fastapi.testclient import TestClient
from ..main import app

# Test client
client = TestClient(app)

# Test WebSocket connection
@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection and message format."""
    # Skip if sounddevice is not available
    pytest.importorskip("sounddevice")
    
    # Connect to WebSocket
    async with websockets.connect("ws://localhost:8000/audio/ws") as websocket:
        # Wait for a message
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        data = json.loads(message)
        
        # Check message format
        assert "timestamp" in data
        assert "rms" in data
        assert "db" in data
        assert "sample_rate" in data
        
        # Check data types
        assert isinstance(data["rms"], (int, float))
        assert isinstance(data["db"], (int, float))
        assert isinstance(data["sample_rate"], int)

# Test REST API endpoints
def test_audio_status():
    """Test /audio/status endpoint."""
    response = client.get("/audio/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "is_running" in data
    assert "sample_rate" in data
    assert "channels" in data
    assert "active_connections" in data

def test_audio_level():
    """Test /audio/level endpoint."""
    response = client.get("/audio/level")
    assert response.status_code == 200
    data = response.json()
    
    assert "level_db" in data
    assert isinstance(data["level_db"], (int, float))
    
    # Level should be between -100 and 0 dBFS
    assert -100 <= data["level_db"] <= 0
