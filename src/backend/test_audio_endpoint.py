"""
Test script for the audio prediction endpoint.
"""
import os
import sys
import requests
import wave
import numpy as np
import soundfile as sf
import io

def generate_test_audio(output_path: str = "test_audio.wav", duration: float = 1.0, sample_rate: int = 16000):
    """Generate a simple sine wave audio file for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Generate a 440 Hz sine wave
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    
    # Convert to 16-bit PCM
    audio = (audio * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)   # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    
    print(f"Generated test audio file: {os.path.abspath(output_path)}")
    return output_path

def test_audio_prediction(server_url: str = "http://localhost:8000", audio_file: str = None):
    """Test the audio prediction endpoint."""
    if audio_file is None or not os.path.exists(audio_file):
        print("No valid audio file provided, generating a test tone...")
        audio_file = generate_test_audio()
    
    url = f"{server_url.rstrip('/')}/ai/predict"
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': (os.path.basename(audio_file), f, 'audio/wav')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("\nPrediction successful!")
            print(f"Status: {response.status_code}")
            print(f"Predicted class: {result['predictions'][0]['class_name']}")
            print(f"Confidence: {result['predictions'][0]['confidence']:.2%}")
            return result
        else:
            print(f"\nPrediction failed with status code: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"\nError testing audio prediction: {e}")
        return None

if __name__ == "__main__":
    # If an audio file path is provided as a command-line argument, use it
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    test_audio_prediction(audio_file=audio_file)
