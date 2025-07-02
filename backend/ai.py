import io
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import requests
import os
import csv
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YAMNet TF Hub URL and class map URL
YAMNET_MODEL_URL = "https://tfhub.dev/google/yamnet/1"
YAMNET_LABELS_URL = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
LABELS_PATH = "yamnet_class_map.csv"

# Global variables for model and labels
yamnet_model = None
CLASS_LABELS = None

# Download class map if not present
def download_labels() -> None:
    """Download YAMNet class map if it doesn't exist."""
    try:
        if not os.path.exists(LABELS_PATH):
            logger.info("Downloading YAMNet class map...")
            r = requests.get(YAMNET_LABELS_URL, timeout=10)
            r.raise_for_status()
            with open(LABELS_PATH, "wb") as f:
                f.write(r.content)
            logger.info("Successfully downloaded YAMNet class map")
    except Exception as e:
        logger.error(f"Error downloading YAMNet class map: {e}")
        raise

def load_labels(path: str) -> list[str]:
    """Load class labels from CSV file."""
    try:
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            return [row["display_name"] for row in reader]
    except Exception as e:
        logger.error(f"Error loading labels from {path}: {e}")
        raise

def load_model() -> None:
    """Load YAMNet model from TensorFlow Hub."""
    global yamnet_model, CLASS_LABELS
    
    try:
        # Download labels first
        download_labels()
        CLASS_LABELS = load_labels(LABELS_PATH)
        
        # Load model with explicit error handling
        logger.info("Loading YAMNet model from TensorFlow Hub...")
        yamnet_model = hub.load(YAMNET_MODEL_URL)
        logger.info("Successfully loaded YAMNet model")
        
        # Test model with dummy data
        test_waveform = np.zeros((16000,), dtype=np.float32)
        _ = yamnet_model(test_waveform)
        logger.info("YAMNet model test inference successful")
        
    except Exception as e:
        logger.error(f"Error loading YAMNet model: {e}")
        raise

# Initialize model and labels on import
try:
    load_model()
except Exception as e:
    logger.error(f"Failed to initialize YAMNet model: {e}")
    # Allow the app to start but model won't be available

# YAMNet expects mono, 16kHz, float32 waveform
def preprocess_audio(audio_bytes: bytes) -> np.ndarray:
    """
    Preprocess audio data for YAMNet model.
    
    Args:
        audio_bytes: Raw audio data as bytes
        
    Returns:
        np.ndarray: Preprocessed audio waveform
    """
    try:
        # Load audio from bytes
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
        return y.astype(np.float32)
    except Exception as e:
        logger.error(f"Error preprocessing audio: {e}")
        raise

def identify_sound(audio_data: bytes) -> Optional[str]:
    """
    Identify the type of sound in the given audio data using YAMNet.
    
    Args:
        audio_data: Raw audio data (WAV/PCM bytes)
        
    Returns:
        str: Predicted label (e.g., 'Speech', 'Music', ...)
        None: If model is not loaded or an error occurs
    """
    if yamnet_model is None or CLASS_LABELS is None:
        logger.error("YAMNet model or labels not loaded")
        return None
        
    try:
        # Preprocess audio
        waveform = preprocess_audio(audio_data)
        
        # Ensure waveform has the correct shape (1D array)
        if len(waveform.shape) > 1:
            waveform = np.mean(waveform, axis=0)  # Convert to mono if needed
            
        # Add batch dimension for inference
        waveform = np.expand_dims(waveform, 0)
        
        # Run inference
        scores, embeddings, spectrogram = yamnet_model(waveform)
        mean_scores = np.mean(scores.numpy(), axis=0)
        top_idx = np.argmax(mean_scores)
        label = CLASS_LABELS[top_idx]
        
        logger.debug(f"Predicted sound label: {label}")
        return label
        
    except Exception as e:
        logger.error(f"Error during sound identification: {e}")
        return None
