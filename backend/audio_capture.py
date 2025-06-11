"""
Audio capture and noise level analysis module for SoundTracker.

This module provides functionality to capture audio from the default microphone
and calculate noise levels in real-time using RMS (Root Mean Square).
"""

import queue
import threading
import time
import numpy as np
import sounddevice as sd
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Audio capture settings
DEFAULT_SAMPLE_RATE = 44100  # Hz
DEFAULT_CHANNELS = 1  # Mono
DEFAULT_BLOCK_SIZE = 1024  # Samples per block

class AudioDeviceError(Exception):
    """Exception raised for audio device related errors."""
    pass

def list_audio_devices() -> List[Dict[str, Any]]:
    """List all available audio devices."""
    try:
        devices = sd.query_devices()
        return [
            {
                'id': i,
                'name': device['name'],
                'max_input_channels': device['max_input_channels'],
                'default_samplerate': device.get('default_samplerate', 44100)
            }
            for i, device in enumerate(devices)
            if device['max_input_channels'] > 0
        ]
    except Exception as e:
        logger.error(f"Error listing audio devices: {e}")
        raise AudioDeviceError(f"Could not list audio devices: {e}") from e

@dataclass
class AudioSample:
    """Container for audio sample data and metadata."""
    timestamp: datetime
    rms: float
    raw_data: np.ndarray
    sample_rate: int
    
    @property
    def db(self) -> float:
        """Convert RMS to decibels (dBFS)."""
        if self.rms > 0:
            return 20 * np.log10(self.rms)
        return -100  # Silence

class AudioCapture:
    """
    Audio capture and noise level analysis.
    
    This class provides methods to start/stop audio capture and access
    noise level measurements.
    """
    
    def __init__(self, 
                 sample_rate: int = DEFAULT_SAMPLE_RATE,
                 channels: int = DEFAULT_CHANNELS,
                 block_size: int = DEFAULT_BLOCK_SIZE,
                 device: Optional[int] = None):
        """
        Initialize audio capture.
        
        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1=mono, 2=stereo)
            block_size: Number of samples per block
            device: Audio device ID (None for default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_size = block_size
        self.device = device
        self._running = False
        self._stream = None
        self._callback = None
        self._last_sample = None
        self._device_info = None
        
        # Validate audio device
        self._validate_audio_device()
    
    def _validate_audio_device(self) -> None:
        """Validate the audio device and update settings if needed."""
        try:
            devices = sd.query_devices()
            if self.device is not None and self.device >= len(devices):
                logger.warning(f"Device {self.device} not found, using default")
                self.device = None
                
            if self.device is not None:
                device_info = devices[self.device]
                max_channels = device_info['max_input_channels']
                if max_channels < self.channels:
                    logger.warning(f"Device only supports {max_channels} channels, adjusting")
                    self.channels = max_channels
                
                self._device_info = {
                    'name': device_info['name'],
                    'sample_rate': device_info.get('default_samplerate', self.sample_rate)
                }
                
                # Update sample rate to device's default if not explicitly set
                if self.sample_rate == DEFAULT_SAMPLE_RATE and 'default_samplerate' in device_info:
                    self.sample_rate = int(device_info['default_samplerate'])
                    logger.info(f"Using device sample rate: {self.sample_rate} Hz")
                    
        except Exception as e:
            logger.error(f"Error validating audio device: {e}")
            raise AudioDeviceError(f"Invalid audio device: {e}") from e
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio stream."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        try:
            # Calculate RMS of the audio block
            rms = np.sqrt(np.mean(np.square(indata)))
            
            # Create audio sample
            sample = AudioSample(
                timestamp=datetime.now(),
                rms=float(rms),
                raw_data=indata.copy(),
                sample_rate=self.sample_rate
            )
            
            # Store the sample
            self._last_sample = sample
            
            # Notify callback if provided
            if self._callback:
                self._callback(sample)
                
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
    
    def start(self, callback=None):
        """
        Start audio capture.
        
        Args:
            callback: Optional callback function to receive audio samples
            
        Raises:
            AudioDeviceError: If audio device cannot be opened
        """
        if self._running:
            logger.warning("Audio capture is already running")
            return
            
        self._callback = callback
        
        try:
            # Start audio stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.block_size,
                device=self.device,
                dtype='float32',
                callback=self._audio_callback
            )
            
            self._running = True
            self._stream.start()
            logger.info(f"Audio capture started on device {self.device or 'default'}")
            
        except Exception as e:
            self._running = False
            logger.error(f"Failed to start audio capture: {e}")
            raise AudioDeviceError(f"Could not start audio capture: {e}") from e
    
    def stop(self) -> None:
        """Stop audio capture."""
        if not self._running:
            return
            
        self._running = False
        
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
                logger.info("Audio capture stopped")
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
            finally:
                self._stream = None
    
    def get_current_level(self):
        """
        Get the most recent audio sample.
        
        Returns:
            AudioSample or None if no samples available
        """
        return self._last_sample
    
    def is_running(self) -> bool:
        """Check if audio capture is running."""
        return self._running


def main():
    """Example usage of the AudioCapture class."""
    
    def print_level(sample):
        print(f"\rNoise level: {sample.db:.1f} dBFS", end="", flush=True)
    
    print("Starting audio capture (press Ctrl+C to stop)...")
    
    capture = None
    try:
        capture = AudioCapture()
        capture.start(callback=print_level)
        
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if capture:
            capture.stop()
        print("Done.")


if __name__ == "__main__":
    main()
