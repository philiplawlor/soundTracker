import logging
import os
import io
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import requests
import csv
from typing import List, Optional, Dict, Any
from functools import lru_cache

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel

from ..database import get_session
from ..models import (
    SoundEvent,
    SoundEventCreate,
    SoundType,
    Prediction,
    AudioPredictionResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# --- AI Model and Configuration ---

class AIModelConfig:
    """Configuration for the AI model."""
    def __init__(self):
        self.yamnet_model_url = "https://tfhub.dev/google/yamnet/1"
        self.yamnet_labels_url = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
        self.labels_path = "yamnet_class_map.csv"
        self.tf_hub_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "tfhub_modules")

class AIModel:
    """Handles loading the YAMNet model and making predictions."""
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.model = None
        self.class_labels = None
        self.initialized = False
        self.error = None

    def initialize(self) -> bool:
        """Loads the model and labels into memory."""
        try:
            logger.info("Initializing AI model...")
            os.makedirs(self.config.tf_hub_cache_dir, exist_ok=True)
            os.environ["TFHUB_CACHE_DIR"] = self.config.tf_hub_cache_dir
            self._download_labels()
            self.class_labels = self._load_labels()
            logger.info("Loading YAMNet model from TensorFlow Hub...")
            self.model = hub.load(self.config.yamnet_model_url)
            logger.info("YAMNet model loaded successfully.")
            self.initialized = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to initialize AI model: {e}", exc_info=True)
            return False

    def _download_labels(self):
        """Downloads the class labels CSV if it doesn't exist locally."""
        if not os.path.exists(self.config.labels_path):
            logger.info(f"Downloading YAMNet labels from {self.config.yamnet_labels_url}")
            response = requests.get(self.config.yamnet_labels_url)
            response.raise_for_status()
            with open(self.config.labels_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

    def _load_labels(self) -> list:
        """Loads the class labels from the CSV file."""
        with open(self.config.labels_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            return [row[2] for row in reader if row]

    def preprocess_audio(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """Converts audio bytes into a waveform suitable for the model."""
        try:
            audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
            return audio
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}", exc_info=True)
            return None

    def predict(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """Runs inference on the preprocessed audio data."""
        if not self.initialized or self.model is None:
            return {"error": "Model not initialized", "details": self.error}
        
        try:
            waveform = self.preprocess_audio(audio_data)
            if waveform is None:
                return {"error": "Failed to preprocess audio data"}
            
            scores, embeddings, spectrogram = self.model(waveform)
            scores_np = scores.numpy()
            top_class_index = scores_np.mean(axis=0).argmax()
            inferred_class = self.class_labels[top_class_index]
            top_score = scores_np.mean(axis=0)[top_class_index]

            return {
                "class": inferred_class,
                "confidence": float(top_score),
                "class_id": int(top_class_index)
            }
        except Exception as e:
            logger.error(f"Error during prediction: {e}", exc_info=True)
            return {"error": "Prediction failed", "details": str(e)}



# --- Dependency Injection ---

@lru_cache(maxsize=1)
def get_ai_model() -> AIModel:
    """Dependency to get a singleton instance of the AI model."""
    logger.info("Attempting to get AI model instance...")
    config = AIModelConfig()
    model = AIModel(config)
    if not model.initialize():
        raise RuntimeError("Could not initialize AI model")
    logger.info("AI model instance ready.")
    return model

# --- API Endpoints ---

@router.on_event("startup")
async def startup_event():
    """Pre-load the AI model on application startup."""
    try:
        logger.info("Startup event: Initializing AI model...")
        get_ai_model()
        logger.info("Startup event: AI model initialized successfully.")
    except Exception as e:
        # Log the error but do not re-raise it to prevent the app from crashing.
        # The endpoints will handle the uninitialized model gracefully.
        logger.error(f"CRITICAL: AI model failed to initialize on startup: {e}", exc_info=True)

@router.post("/predict", response_model=AudioPredictionResponse)
async def predict_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    model: AIModel = Depends(get_ai_model)
):
    """Process an audio file, return predictions, and save the event."""
    try:
        contents = await file.read()
        result = model.predict(contents)

        if not result or "error" in result:
            error_detail = result.get("details", "Prediction failed.") if result else "Prediction failed."
            raise HTTPException(status_code=400, detail=error_detail)

        prediction_result = Prediction(
            class_name=result["class"],
            confidence=result["confidence"],
            class_id=result["class_id"]
        )

        event_in = SoundEventCreate(
            sound_type=result["class"],
            confidence=result["confidence"],
            event_metadata=result
        )
        db_event = SoundEvent.from_orm(event_in)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        logger.info(f"Saved sound event {db_event.id} to the database.")

        return AudioPredictionResponse(
            success=True,
            predictions=[prediction_result]
        )

    except Exception as e:
        logger.error(f"Error processing audio file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identify")
async def identify_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_session),
    model: AIModel = Depends(get_ai_model)
):
    """Legacy endpoint for backward compatibility. Saves event to DB."""
    try:
        contents = await file.read()
        result = model.predict(contents)

        if not result or "error" in result:
            error_detail = result.get("details", "Failed to identify sound") if result else "Failed to identify sound"
            return {"error": error_detail}

        # Manually create the metadata dict to ensure JSON compatibility
        metadata = {
            "class": result["class"],
            "confidence": float(result["confidence"]),
            "class_id": int(result["class_id"])
        }

        # Convert the string label to the SoundType enum member
        try:
            sound_type_enum = SoundType(result["class"].lower())
        except ValueError:
            logger.warning(f"Unknown sound type '{result['class']}' received from model. Defaulting to UNKNOWN.")
            sound_type_enum = SoundType.UNKNOWN

        event_in = SoundEventCreate(
            sound_type=sound_type_enum,
            confidence=result["confidence"],
            event_metadata=metadata
        )
        db_event = SoundEvent.from_orm(event_in)
        db.add(db_event)
        db.commit()

        return {"label": result["class"]}

    except Exception as e:
        logger.error(f"Error in /identify endpoint: {e}", exc_info=True)
        return {"error": f"Failed to identify sound: {e}"}
