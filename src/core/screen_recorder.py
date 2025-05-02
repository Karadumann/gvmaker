"""
Main screen recorder module that coordinates frame capture, processing, and region selection.
"""

import queue
import threading
import time
from typing import Optional, Dict, List
import os
from datetime import datetime

from .frame_capture import FrameCapture
from .frame_processor import FrameProcessor
from .region_selector import RegionSelector

class ScreenRecorder:
    """
    Main screen recorder class that coordinates all components.
    """
    
    def __init__(self):
        self.recording = False
        self.paused = False
        self.frame_queue = queue.Queue(maxsize=1000)
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        self.processed_frames = []
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.frame_capture = FrameCapture()
        self.frame_processor = FrameProcessor()
        self.region_selector = RegionSelector()
        
    def select_region(self) -> Optional[Dict[str, int]]:
        """
        Select recording region using GUI overlay.
        
        Returns:
            Dictionary containing region coordinates or None if selection cancelled
        """
        return self.region_selector.select_region()
        
    def start_recording(self, region: Optional[Dict[str, int]] = None,
                       format_type: str = "video",
                       fps: int = 30,
                       quality: str = "high") -> None:
        """
        Start screen recording.
        
        Args:
            region: Dictionary containing region coordinates
            format_type: Output format ('video' or 'gif')
            fps: Frames per second
            quality: Quality setting ('low', 'medium', 'high')
        """
        if self.recording:
            return
            
        self.recording = True
        self.format_type = format_type
        self.fps = fps
        self.quality = quality
        self.processed_frames = []
        
        if not region:
            region = self.select_region()
            if not region:
                self.recording = False
                try:
                    import tkinter.messagebox as mb
                    mb.showwarning("No Region Selected", "No region was selected for recording!")
                except Exception:
                    pass
                return
                
        self.selected_region = region
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.process_thread = threading.Thread(target=self._process_frames)
        self.capture_thread.start()
        self.process_thread.start()
        
    def _capture_frames(self) -> None:
        """Capture frames in a separate thread."""
        print("Starting frame capture...")
        frame_time = 1 / self.fps
        next_frame_time = time.time()
        frames_captured = 0
        
        while self.recording:
            if self.paused:
                time.sleep(0.1)
                continue
            current_time = time.time()
            
            if current_time >= next_frame_time:
                try:
                    frame = self.frame_capture.capture_frame(self.selected_region)
                    
                    if frame is not None and frame.size > 0:
                        frames_captured += 1
                        try:
                            self.frame_queue.put(frame, timeout=0.1)
                        except queue.Full:
                            print("Frame queue is full, dropping frame")
                        except Exception as e:
                            print(f"Error adding frame to queue: {str(e)}")
                            
                    next_frame_time = current_time + frame_time
                except Exception as e:
                    print(f"Error capturing frame: {str(e)}")
                    continue
                    
            time.sleep(0.001)
            
        print(f"Frame capture stopped. Total frames captured: {frames_captured}")
        
    def _process_frames(self) -> None:
        """Process captured frames in a separate thread."""
        print("Starting frame processing...")
        chunk_size = 10
        current_chunk = []
        frames_processed = 0
        
        while self.recording or not self.frame_queue.empty():
            if self.paused:
                time.sleep(0.1)
                continue
            try:
                frame = self.frame_queue.get(timeout=1)
                if frame is not None:
                    current_chunk.append(frame)
                    frames_processed += 1
                
                if len(current_chunk) >= chunk_size or (not self.recording and current_chunk):
                    processed_chunk = self.frame_processor.process_frame_chunk(
                        current_chunk, self.quality
                    )
                    self.processed_frames.extend(processed_chunk)
                    current_chunk = []
                    
            except queue.Empty:
                if not self.recording and current_chunk:
                    processed_chunk = self.frame_processor.process_frame_chunk(
                        current_chunk, self.quality
                    )
                    self.processed_frames.extend(processed_chunk)
                    current_chunk = []
                continue
            except Exception as e:
                print(f"Frame processing error: {e}")
                continue
                
        print(f"Frame processing stopped. Total frames processed: {frames_processed}")
        
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save the output.
        
        Returns:
            Path to the saved recording or None if recording failed
        """
        if not self.recording:
            print("Not currently recording!")
            return None
            
        print("Stopping recording...")
        self.recording = False
        
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
            
        if not self.processed_frames:
            print("No frames were processed!")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.format_type == "video":
            output_path = os.path.join(self.output_dir, f"recording_{timestamp}.mp4")
            self._save_video(output_path)
        else:
            output_path = os.path.join(self.output_dir, f"recording_{timestamp}.gif")
            self._save_gif(output_path)
            
        return output_path
        
    def _save_video(self, output_path: str) -> None:
        """Save processed frames as video."""
        import cv2
        
        if not self.processed_frames:
            return
            
        height, width = self.processed_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
        
        for frame in self.processed_frames:
            out.write(frame)
            
        out.release()
        
    def _save_gif(self, output_path: str) -> None:
        """Save processed frames as GIF."""
        import imageio
        import cv2
        if not self.processed_frames:
            return
        frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in self.processed_frames]
        imageio.mimsave(output_path, frames, fps=self.fps)
        
    def pause(self) -> None:
        """Pause recording."""
        self.paused = True
        
    def resume(self) -> None:
        """Resume recording."""
        self.paused = False 