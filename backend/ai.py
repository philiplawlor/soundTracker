import os
import tempfile
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import soundfile as sf
import librosa
import io
from typing import Dict, List, Tuple, Optional

# Constants for audio processing
SAMPLE_RATE = 16000  # YamNet expects 16kHz audio
DURATION = 0.975  # Duration in seconds for each audio chunk (YamNet's window size)
HOP_LENGTH = 128  # Hop length for YamNet's spectrogram
N_MELS = 64  # Number of mel bands

# Load the YamNet model from TensorFlow Hub
YAMNET_MODEL_URI = 'https://tfhub.dev/google/yamnet/1'

class SoundClassifier:
    def __init__(self):
        """Initialize the sound classifier with YamNet model."""
        self.model = hub.load(YAMNET_MODEL_URI)
        self.class_names = self._load_class_names()
    
    def _load_class_names(self) -> List[str]:
        """Load the class names for YamNet."""
        class_map_path = self.model.class_map_path().numpy()
        class_names = {}
        with open(class_map_path) as f:
            for line in f:
                idx, _, name = line.strip().split('\t')
                class_names[int(idx)] = name
        return [class_names[i] for i in range(len(class_names))]
    
    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio data for YamNet.
        
        Args:
            audio_data: Raw audio data in bytes
            
        Returns:
            np.ndarray: Preprocessed audio waveform
        """
        # Load audio using soundfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_data)
            tmp_filename = tmp.name
        
        try:
            # Load audio and resample to 16kHz
            waveform, sample_rate = sf.read(tmp_filename, dtype=np.float32)
            
            # Convert to mono if stereo
            if len(waveform.shape) > 1:
                waveform = np.mean(waveform, axis=1)
                
            # Resample if needed
            if sample_rate != SAMPLE_RATE:
                waveform = librosa.resample(
                    waveform, 
                    orig_sr=sample_rate, 
                    target_sr=SAMPLE_RATE
                )
                
            # Ensure the waveform is between -1.0 and 1.0
            waveform = np.clip(waveform, -1.0, 1.0)
            
            return waveform
            
        except Exception as e:
            raise ValueError(f"Error processing audio: {str(e)}")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_filename)
            except:
                pass
    
    def classify_sound(self, audio_data: bytes, top_k: int = 5) -> List[Dict[str, float]]:
        """
        Classify sound from raw audio data.
        
        Args:
            audio_data: Raw audio data in bytes (WAV format)
            top_k: Number of top predictions to return
            
        Returns:
            List of dicts with 'label' and 'score' for each prediction
        """
        try:
            # Preprocess audio
            waveform = self.preprocess_audio(audio_data)
            
            # Ensure waveform is the correct length (YamNet expects 15600 samples for 0.975s at 16kHz)
            target_length = int(SAMPLE_RATE * DURATION)
            if len(waveform) < target_length:
                # Pad with zeros if too short
                pad_length = target_length - len(waveform)
                waveform = np.pad(waveform, (0, pad_length), mode='constant')
            else:
                # Truncate if too long
                waveform = waveform[:target_length]
            
            # Add batch dimension
            waveform = waveform[np.newaxis, :]
            
            # Run inference
            scores, embeddings, spectrogram = self.model(waveform)
            scores_np = scores.numpy()
            
            # Get top-k predictions
            top_k_indices = np.argsort(scores_np[0])[-top_k:][::-1]
            top_k_scores = scores_np[0][top_k_indices]
            
            # Convert to list of dicts
            predictions = []
            for i, (idx, score) in enumerate(zip(top_k_indices, top_k_scores)):
                predictions.append({
                    'label': self.class_names[idx],
                    'score': float(score)
                })
            
            return predictions
            
        except Exception as e:
            raise ValueError(f"Error during sound classification: {str(e)}")

# Initialize the global classifier instance
sound_classifier = SoundClassifier()

def identify_sound(audio_data: bytes) -> str:
    """
    Identify the type of sound in the given audio data using YamNet.
    
    Args:
        audio_data (bytes): Raw audio data in WAV format
        
    Returns:
        str: The most likely sound class
    """
    try:
        # Get top prediction
        predictions = sound_classifier.classify_sound(audio_data, top_k=1)
        return predictions[0]['label']
    except Exception as e:
        return f"error: {str(e)}"
