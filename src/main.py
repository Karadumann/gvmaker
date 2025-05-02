"""
Main application entry point for the Screen Recorder.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from src.core.screen_recorder import ScreenRecorder
from src.settings.settings_manager import SettingsManager
from src.utils.uploader import MediaUploader
from src.ui.ui import UI
import threading
import time

class ScreenRecorderApp:
    """
    Main application class that coordinates all components.
    """
    def __init__(self):
        """
        Initialize the application and its components.
        """
        self.root = ttk.Window(themename="darkly")
        self.root.title("Screen Recorder")
        self.root.geometry("400x400")
        self.root.minsize(400, 400)
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.recorder = ScreenRecorder()
        self.uploader = MediaUploader(self.settings_manager)
        
        # Setup UI
        self.ui = UI(
            self.root,
            self.recorder,
            self.uploader,
            self.settings_manager
        )
        
        # Connect UI callbacks to recorder logic
        self.ui.on_start_recording = self._start_recording
        self.ui.on_stop_recording = self._stop_recording
        self.ui.on_pause_recording = self._pause_recording
        self.ui.on_resume_recording = self._resume_recording
        self._timer_thread = None
        self._timer_running = False
        self._last_frame_count = 0

    def _start_recording(self):
        format_type = self.ui.get_output_format()
        quality = self.ui.get_quality()
        fps = self.settings_manager.get_fps()
        self.recorder.start_recording(format_type=format_type, quality=quality, fps=fps)
        self._start_timer()

    def _stop_recording(self):
        self._stop_timer()
        return self.recorder.stop_recording()

    def _pause_recording(self):
        self.recorder.pause()
        self._stop_timer()

    def _resume_recording(self):
        self.recorder.resume()
        self._start_timer()

    def _start_timer(self):
        self._timer_running = True
        self._timer_start_time = time.time()
        self._last_frame_count = 0
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()

    def _stop_timer(self):
        self._timer_running = False

    def _timer_loop(self):
        while self._timer_running:
            elapsed = int(time.time() - self._timer_start_time)
            self.ui.update_elapsed_time(elapsed)
            # FPS: use processed_frames length as a proxy
            frame_count = len(self.recorder.processed_frames)
            fps = frame_count - self._last_frame_count
            self._last_frame_count = frame_count
            self.ui.update_fps(fps)
            time.sleep(1)

    def run(self):
        """
        Start the application main loop.
        """
        self.root.mainloop()

def main():
    """
    Application entry point.
    """
    app = ScreenRecorderApp()
    app.run()

if __name__ == "__main__":
    main() 