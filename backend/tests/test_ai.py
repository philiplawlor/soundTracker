import io
from fastapi.testclient import TestClient
from backend.main import app

def test_identify_endpoint():
    client = TestClient(app)
    # Generate a minimal valid WAV file (PCM, mono, 16kHz, silence)
    import wave
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(b'\x00' * 32000)  # 1 second silence
        tmp.seek(0)
        files = {"file": ("test.wav", tmp.read(), "audio/wav")}
    response = client.post("/ai/identify", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert isinstance(data["label"], str)
    # For CI: consider mocking identify_sound for speed/determinism
