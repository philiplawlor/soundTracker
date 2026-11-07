import io
import numpy as np
import tensorflow as tf
import librosa
import os
import csv
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define base directory for the project
# This assumes ai.py is in the 'backend' subdirectory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths for the local model and labels
YAMNET_MODEL_PATH = os.path.join(BASE_DIR, "yamnet.h5")
LABELS_PATH = os.path.join(BASE_DIR, "yamnet_class_map.csv")

# Global variables for model and labels
yamnet_model = None
CLASS_LABELS = None

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
    """Load YAMNet model from local .h5 file."""
    global yamnet_model, CLASS_LABELS
    
    try:
        # Check if model and label files exist
        if not os.path.exists(YAMNET_MODEL_PATH):
            raise FileNotFoundError(f"YAMNet model not found at {YAMNET_MODEL_PATH}")
        if not os.path.exists(LABELS_PATH):
            raise FileNotFoundError(f"YAMNet class map not found at {LABELS_PATH}")

        # Load labels
        CLASS_LABELS = load_labels(LABELS_PATH)
        logger.info(f"Loaded {len(CLASS_LABELS)} YAMNet class labels")
        
        # Load model
        logger.info(f"Loading YAMNet model from local path: {YAMNET_MODEL_PATH}...")
        yamnet_model = tf.keras.models.load_model(YAMNET_MODEL_PATH)
        logger.info("Successfully loaded YAMNet model")
        
        # Test model with dummy data
        logger.info("Running test inference...")
        test_waveform = np.zeros((1, 16000), dtype=np.float32)
        scores, embeddings, spectrogram = yamnet_model(test_waveform)
        logger.info(f"YAMNet model test inference successful. Output shapes - scores: {scores.shape}, embeddings: {embeddings.shape}, spectrogram: {spectrogram.shape}")
        
    except Exception as e:
        logger.error(f"Error loading local YAMNet model: {str(e)}", exc_info=True)
        raise

# Initialize model and labels on import
try:
    load_model()
except Exception as e:
    logger.error(f"Failed to initialize YAMNet model: {e}")
    # Allow the app to start, but model won't be available

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
        mean_scores = np.mean(scores, axis=0)
        top_idx = np.argmax(mean_scores)
        label = CLASS_LABELS[top_idx]
        
        logger.debug(f"Predicted sound label: {label}")
        return label
        
    except Exception as e:
        logger.error(f"Error during sound identification: {e}")
        return None
