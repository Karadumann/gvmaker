import unittest
from unittest.mock import MagicMock, patch
from src.recording import RecordingManager
from screen_recorder import ScreenRecorder

class TestRecordingManager(unittest.TestCase):
    def setUp(self):
        self.mock_recorder = MagicMock(spec=ScreenRecorder)
        self.manager = RecordingManager(self.mock_recorder)
        
    def test_start_recording(self):
        self.manager.start_recording()
        self.assertTrue(self.manager.recording)
        self.assertFalse(self.manager.paused)
        self.mock_recorder.start_recording.assert_called_once()
        
    def test_stop_recording(self):
        self.manager.recording = True
        result = self.manager.stop_recording()
        self.assertFalse(self.manager.recording)
        self.mock_recorder.stop_recording.assert_called_once()
        
    def test_toggle_pause(self):
        self.manager.recording = True
        self.manager.toggle_pause()
        self.assertTrue(self.manager.paused)
        self.mock_recorder.pause_recording.assert_called_once()
        
        self.manager.toggle_pause()
        self.assertFalse(self.manager.paused)
        self.mock_recorder.resume_recording.assert_called_once()
        
    def test_get_recording_status(self):
        self.manager.recording = True
        self.manager.paused = False
        status = self.manager.get_recording_status()
        self.assertTrue(status['recording'])
        self.assertFalse(status['paused'])
        self.assertIsNotNone(status['elapsed_time'])

if __name__ == '__main__':
    unittest.main() 