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
# Using a specific version of the model that's known to work
YAMNET_MODEL_URL = "https://tfhub.dev/google/yamnet/1"  # Using the standard version instead of tf2/1
YAMNET_LABELS_URL = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
LABELS_PATH = "yamnet_class_map.csv"

# Set TF Hub cache directory to a local path
tf_hub_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "tfhub_modules")
os.makedirs(tf_hub_cache_dir, exist_ok=True)
os.environ["TFHUB_CACHE_DIR"] = tf_hub_cache_dir

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
        logger.info("Downloading YAMNet labels...")
        download_labels()
        CLASS_LABELS = load_labels(LABELS_PATH)
        logger.info(f"Loaded {len(CLASS_LABELS)} YAMNet class labels")
        
        # Load model with explicit error handling
        logger.info(f"Loading YAMNet model from {YAMNET_MODEL_URL}...")
        
        # Clear any existing TF session and set memory growth
        tf.keras.backend.clear_session()
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices:
            try:
                tf.config.experimental.set_memory_growth(physical_devices[0], True)
                logger.info("Enabled memory growth on GPU")
            except Exception as e:
                logger.warning(f"Could not enable memory growth on GPU: {e}")
        
        # Load model with custom options
        yamnet_model = hub.load(YAMNET_MODEL_URL)
        logger.info("Successfully loaded YAMNet model")
        
        # Test model with dummy data
        logger.info("Running test inference...")
        test_waveform = np.zeros((16000,), dtype=np.float32)
        scores, embeddings, spectrogram = yamnet_model(test_waveform)
        logger.info(f"YAMNet model test inference successful. Output shapes - scores: {scores.shape}, embeddings: {embeddings.shape}, spectrogram: {spectrogram.shape}")
        
    except Exception as e:
        logger.error(f"Error loading YAMNet model: {str(e)}", exc_info=True)
        logger.error(f"TF Hub URL: {YAMNET_MODEL_URL}")
        logger.error("Make sure you have a stable internet connection and the model URL is accessible.")
        logger.error("If the issue persists, try clearing the TF Hub cache at %LOCALAPPDATA%\temp\tfhub_modules")
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
