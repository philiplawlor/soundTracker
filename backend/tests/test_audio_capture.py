"""
Tests for the audio_capture module.
"""

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from datetime import datetime

# Import the module to test
from ..audio_capture import AudioCapture, AudioSample


class TestAudioSample(unittest.TestCase):
    """Test the AudioSample class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        self.sample = AudioSample(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            rms=0.5,
            raw_data=self.sample_data,
            sample_rate=44100
        )
    
    def test_db_property(self):
        """Test the db property calculation."""
        # Test with non-zero RMS
        self.assertAlmostEqual(self.sample.db, -6.0206, places=4)
        
        # Test with zero RMS
        zero_sample = AudioSample(
            timestamp=datetime.now(),
            rms=0.0,
            raw_data=np.array([0.0]),
            sample_rate=44100
        )
        self.assertEqual(zero_sample.db, -np.inf)


class TestAudioCapture(unittest.TestCase):
    """Test the AudioCapture class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.audio_capture = AudioCapture(sample_rate=44100, channels=1, block_size=1024)
        
    @patch('sounddevice.InputStream')
    def test_start_stop(self, mock_stream):
        """Test starting and stopping audio capture."""
        # Mock the stream
        mock_stream.return_value.__enter__.return_value = None
        
        # Start capture
        self.audio_capture.start()
        self.assertTrue(self.audio_capture.is_running())
        
        # Stop capture
        self.audio_capture.stop()
        self.assertFalse(self.audio_capture.is_running())
    
    @patch('sounddevice.InputStream')
    def test_audio_callback(self, mock_stream):
        """Test the audio callback function."""
        # Set up mock callback
        mock_callback = MagicMock()
        self.audio_capture._callback = mock_callback
        
        # Create test data
        test_data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        
        # Call the callback
        self.audio_capture._audio_callback(
            indata=test_data,
            frames=4,
            time_info={},
            status=0
        )
        
        # Check that the callback was called with an AudioSample
        self.assertEqual(mock_callback.call_count, 1)
        sample = mock_callback.call_args[0][0]
        self.assertIsInstance(sample, AudioSample)
        self.assertAlmostEqual(sample.rms, 0.26925824)  # Expected RMS for test_data
    
    @patch('sounddevice.InputStream')
    def test_get_current_level(self, mock_stream):
        """Test getting the current noise level."""
        # Initially should be None
        self.assertIsNone(self.audio_capture.get_current_level())
        
        # Create a test sample
        test_data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        self.audio_capture._last_sample = AudioSample(
            timestamp=datetime.now(),
            rms=0.5,
            raw_data=test_data,
            sample_rate=44100
        )
        
        # Should now return the dB value
        self.assertAlmostEqual(self.audio_capture.get_current_level(), -6.0206, places=4)


if __name__ == '__main__':
    unittest.main()
