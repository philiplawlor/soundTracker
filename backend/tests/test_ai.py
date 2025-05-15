import io
from fastapi.testclient import TestClient
from backend.main import app

def test_identify_endpoint():
    client = TestClient(app)
    # Generate fake WAV header (44 bytes) + silence
    wav_header = b'RIFF' + b'\x00' * 40
    audio_data = wav_header + b'\x00' * 1000
    files = {"file": ("test.wav", io.BytesIO(audio_data), "audio/wav")}
    response = client.post("/ai/identify", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert isinstance(data["label"], str)
