"""
Module for handling frame processing and optimization.
"""

import cv2
import numpy as np
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import os

class FrameProcessor:
    """
    Handles frame processing and optimization.
    """
    
    def __init__(self):
        self.use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if self.use_gpu:
            self.gpu_frame = cv2.cuda_GpuMat()
            
        cpu_count = os.cpu_count() or 4
        self.thread_pool = ThreadPoolExecutor(max_workers=max(4, cpu_count * 2))
        
    def process_frame(self, frame: np.ndarray, quality: str = "high") -> Optional[np.ndarray]:
        """
        Process a single frame according to quality settings.
        
        Args:
            frame: Input frame to process
            quality: Quality setting ('low', 'medium', 'high')
            
        Returns:
            Processed frame or None if processing failed
        """
        try:
            if quality == "low":
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            elif quality == "medium":
                frame = cv2.resize(frame, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)
                
            if self.use_gpu:
                self.gpu_frame.upload(frame)
                frame = self.gpu_frame.download()
                
            return frame
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return None
            
    def process_frame_chunk(self, chunk: List[np.ndarray], quality: str) -> List[np.ndarray]:
        """
        Process a chunk of frames in parallel.
        
        Args:
            chunk: List of frames to process
            quality: Quality setting ('low', 'medium', 'high')
            
        Returns:
            List of processed frames
        """
        processed_frames = []
        futures = []
        
        for frame in chunk:
            if frame is None:
                continue
            future = self.thread_pool.submit(self.process_frame, frame, quality)
            futures.append(future)
            
        for future in futures:
            try:
                processed_frame = future.result()
                if processed_frame is not None:
                    processed_frames.append(processed_frame)
            except Exception as e:
                print(f"Error processing frame in chunk: {str(e)}")
                continue
                
        return processed_frames 