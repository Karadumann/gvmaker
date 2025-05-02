"""
Core functionality package containing the main recording and processing modules.
"""

from .frame_capture import FrameCapture
from .frame_processor import FrameProcessor
from .region_selector import RegionSelector
from .screen_recorder import ScreenRecorder

__all__ = ['FrameCapture', 'FrameProcessor', 'RegionSelector', 'ScreenRecorder'] 