import io
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import requests
import os
import csv

# YAMNet TF Hub URL and class map URL
YAMNET_MODEL_URL = "https://tfhub.dev/google/yamnet/1"
YAMNET_LABELS_URL = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
LABELS_PATH = "yamnet_class_map.csv"

# Download class map if not present
def download_labels():
    if not os.path.exists(LABELS_PATH):
        print("Downloading YAMNet class map...")
        r = requests.get(YAMNET_LABELS_URL)
        with open(LABELS_PATH, "wb") as f:
            f.write(r.content)
download_labels()

def load_labels(path):
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row["display_name"] for row in reader]

CLASS_LABELS = load_labels(LABELS_PATH)

# Load YAMNet model from TensorFlow Hub
yamnet_model = hub.load(YAMNET_MODEL_URL)

# YAMNet expects mono, 16kHz, float32 waveform
def preprocess_audio(audio_bytes: bytes) -> np.ndarray:
    # Load audio from bytes
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
    return y.astype(np.float32)

def identify_sound(audio_data: bytes) -> str:
    """
    Identify the type of sound in the given audio data using YAMNet (TF Hub).
    Args:
        audio_data (bytes): Raw audio data (WAV/PCM bytes)
    Returns:
        str: Predicted label (e.g., 'Speech', 'Music', ...)
    """
    waveform = preprocess_audio(audio_data)
    # YAMNet expects a 1D float32 Tensor of waveform samples
    # Add batch dimension for inference
    scores, embeddings, spectrogram = yamnet_model(waveform)
    mean_scores = np.mean(scores.numpy(), axis=0)
    top_idx = np.argmax(mean_scores)
    label = CLASS_LABELS[top_idx]
    return label
