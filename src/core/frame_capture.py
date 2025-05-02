"""
Module for handling frame capture functionality using various methods.
"""

import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import time
from typing import Optional, Dict, Any

class FrameCapture:
    """
    Handles frame capture from screen using different methods.
    """
    
    def __init__(self):
        self.use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if self.use_gpu:
            print("GPU acceleration enabled")
            self.gpu_frame = cv2.cuda_GpuMat()
            
    def capture_frame(self, region: Dict[str, int]) -> Optional[np.ndarray]:
        """
        Capture a frame from the specified region using the fastest available method.
        
        Args:
            region: Dictionary containing 'left', 'top', 'width', 'height' of the region
            
        Returns:
            Captured frame as numpy array or None if capture failed
        """
        try:
            frame = self._capture_frame_fast(region)
            if frame is not None and self.use_gpu:
                self.gpu_frame.upload(frame)
                frame = self.gpu_frame.download()
            return frame
        except Exception as e:
            print(f"Error capturing frame: {str(e)}")
            return None
            
    def _capture_frame_fast(self, region: Dict[str, int]) -> np.ndarray:
        """
        Fast frame capture using win32gui.
        
        Args:
            region: Dictionary containing 'left', 'top', 'width', 'height'
            
        Returns:
            Captured frame as numpy array
        """
        hwnd = win32gui.GetDesktopWindow()
        width = region['width']
        height = region['height']
        
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (width, height), dcObj, (region['left'], region['top']), win32con.SRCCOPY)
        
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype='uint8')
        img.shape = (height, width, 4)
        
        # Clean up
        win32gui.DeleteObject(dataBitMap.GetHandle())
        cDC.DeleteDC()
        dcObj.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) 