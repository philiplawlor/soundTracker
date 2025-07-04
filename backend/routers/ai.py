"""
AI Router for SoundTracker

This module provides endpoints for sound classification using the YAMNet model.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
import os
import io
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import requests
import csv
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])

# Response models
class AudioPredictionResult(BaseModel):
    class_name: str
    confidence: float
    class_id: int

class AudioPredictionResponse(BaseModel):
    success: bool
    predictions: List[AudioPredictionResult]
    error: Optional[str] = None

class SoundClass(BaseModel):
    id: int
    name: str

class SoundClassesResponse(BaseModel):
    count: int
    classes: List[SoundClass]

# AI Model Configuration
class AIModelConfig:
    def __init__(self):
        self.yamnet_model_url = "https://tfhub.dev/google/yamnet/1"
        self.yamnet_labels_url = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
        self.labels_path = "yamnet_class_map.csv"
        self.tf_hub_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "tfhub_modules")

class AIModel:
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.model = None
        self.class_labels = None
        self.initialized = False
        self.error = None
        
    def initialize(self):
        try:
            logger.info("Initializing AI model...")
            os.makedirs(self.config.tf_hub_cache_dir, exist_ok=True)
            os.environ["TFHUB_CACHE_DIR"] = self.config.tf_hub_cache_dir
            
            # Download labels if they don't exist
            self._download_labels()
            self.class_labels = self._load_labels()
            
            # Load the model
            logger.info("Loading YAMNet model...")
            self.model = hub.load(self.config.yamnet_model_url)
            logger.info("YAMNet model loaded successfully")
            self.initialized = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to initialize AI model: {e}", exc_info=True)
            return False
    
    def _download_labels(self):
        if not os.path.exists(self.config.labels_path):
            logger.info(f"Downloading YAMNet labels from {self.config.yamnet_labels_url}")
            response = requests.get(self.config.yamnet_labels_url)
            with open(self.config.labels_path, 'w') as f:
                f.write(response.text)
    
    def _load_labels(self) -> list:
        with open(self.config.labels_path, 'r') as f:
            reader = csv.reader(f)
            return [row[2] for row in reader if len(row) > 2]
    
    def preprocess_audio(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        try:
            # Convert bytes to numpy array
            audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000, mono=True)
            return audio
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            return None
    
    def predict(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        if not self.initialized or self.model is None:
            return {"error": "Model not initialized", "details": self.error}
        
        try:
            # Preprocess audio
            waveform = self.preprocess_audio(audio_data)
            if waveform is None:
                return {"error": "Failed to preprocess audio data"}
            
            # Run inference
            scores, embeddings, spectrogram = self.model(waveform)
            predicted_class = tf.argmax(scores, axis=-1).numpy()[0]
            confidence = tf.reduce_max(scores, axis=-1).numpy()[0]
            
            return {
                "class": self.class_labels[predicted_class],
                "confidence": float(confidence),
                "class_id": int(predicted_class)
            }
        except Exception as e:
            logger.error(f"Error during prediction: {e}", exc_info=True)
            return {"error": "Prediction failed", "details": str(e)}

# Initialize the AI model
ai_config = AIModelConfig()
ai_model = AIModel(ai_config)

@router.on_event("startup")
async def startup_event():
    # Initialize the AI model when the application starts
    if not ai_model.initialize():
        logger.error("Failed to initialize AI model. Some features may not work.")

@router.get("/status")
async def ai_status():
    """Check the status of the AI model."""
    return {
        "initialized": ai_model.initialized,
        "model_loaded": ai_model.model is not None,
        "error": ai_model.error,
        "config": {
            "model_url": ai_model.config.yamnet_model_url,
            "cache_dir": ai_model.config.tf_hub_cache_dir
        }
    }

@router.get("/classes", response_model=SoundClassesResponse)
async def list_sound_classes():
    """List all available sound classes that the model can recognize."""
    if not ai_model.initialized or not ai_model.class_labels:
        raise HTTPException(
            status_code=503,
            detail="AI model is not initialized or class labels are not loaded."
        )
    
    return {
        "count": len(ai_model.class_labels),
        "classes": [{"id": i, "name": name} for i, name in enumerate(ai_model.class_labels)]
    }

@router.post("/predict", response_model=AudioPredictionResponse)
async def predict_audio(file: UploadFile = File(...)):
    """
    Process an audio file and return sound classification predictions.
    
    Accepts WAV audio files (16kHz, mono, 16-bit PCM recommended).
    """
    if not ai_model.initialized:
        raise HTTPException(
            status_code=503,
            detail="AI model is not initialized. Please check the /ai/status endpoint."
        )
    
    # Check file type
    if not file.filename.lower().endswith(('.wav', '.wave')):
        raise HTTPException(
            status_code=400,
            detail="Only WAV audio files are supported"
        )
    
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Make prediction
        result = ai_model.predict(contents)
        
        if "error" in result:
            return AudioPredictionResponse(
                success=False,
                predictions=[],
                error=result.get("details", "Prediction failed")
            )
        
        # Format the response
        prediction_result = AudioPredictionResult(
            class_name=result["class"],
            confidence=result["confidence"],
            class_id=result["class_id"]
        )
        
        return AudioPredictionResponse(
            success=True,
            predictions=[prediction_result]
        )
        
    except Exception as e:
        logger.error(f"Error processing audio file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio file: {str(e)}"
        )

# For backward compatibility
@router.post("/identify")
async def identify_endpoint(file: UploadFile = File(...)):
    """Legacy endpoint for backward compatibility."""
    response = await predict_audio(file)
    if response.success and response.predictions:
        return {"label": response.predictions[0].class_name}
    return {"error": response.error or "Failed to identify sound"}
