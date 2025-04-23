import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab, Image
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import mss
import queue
import threading
import imageio
from concurrent.futures import ThreadPoolExecutor
import win32gui
import win32ui
import win32con
import ctypes
from ctypes import wintypes

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.frame_queue = queue.Queue(maxsize=1000)
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        self.processed_frames = []
        self.frames = []
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        cpu_count = os.cpu_count() or 4
        self.thread_pool = ThreadPoolExecutor(max_workers=max(4, cpu_count * 2))
        self.frame_cache = {}
        self.cache_size = 100
        
        self.use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
        if self.use_gpu:
            print("GPU acceleration enabled")
            self.gpu_frame = cv2.cuda_GpuMat()
        
    def select_region(self):
        root = tk.Tk()
        root.attributes('-alpha', 0.3)
        root.attributes('-fullscreen', True)
        canvas = tk.Canvas(root, cursor="cross")
        canvas.pack(fill="both", expand=True)
        start_x = start_y = end_x = end_y = None
        selection_rect = None
        
        def on_press(event):
            nonlocal start_x, start_y, selection_rect
            start_x = event.x
            start_y = event.y
            if selection_rect:
                canvas.delete(selection_rect)
            selection_rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red')
            
        def on_drag(event):
            nonlocal end_x, end_y
            end_x = event.x
            end_y = event.y
            canvas.coords(selection_rect, start_x, start_y, end_x, end_y)
            
        def on_release(event):
            nonlocal start_x, start_y, end_x, end_y
            if start_x and start_y and end_x and end_y:
                x1, x2 = min(start_x, end_x), max(start_x, end_x)
                y1, y2 = min(start_y, end_y), max(start_y, end_y)
                root.selected_region = {"left": x1, "top": y1, "width": x2-x1+1, "height": y2-y1+1}
                root.quit()
                
        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        instructions = canvas.create_text(
            root.winfo_screenwidth()/2, 50,
            text="Click and drag to select recording area. Press ESC to cancel.",
            fill="white",
            font=("Arial", 16)
        )
        
        def on_esc(event):
            root.selected_region = None
            root.quit()
        root.bind("<Escape>", on_esc)
        
        root.mainloop()
        root.destroy()
        return root.selected_region
        
    def start_recording(self, region=None, format_type="video", fps=30, quality="high"):
        if self.recording:
            return
            
        self.recording = True
        self.format_type = format_type
        self.fps = fps
        self.quality = quality
        self.frames = []  # Reset frames at start
        self.processed_frames = []  # Reset processed frames at start
        
        if not region:
            region = self.select_region()
            if not region:
                self.recording = False
                raise Exception("No region selected")
                
        self.selected_region = region
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.process_thread = threading.Thread(target=self._process_frames)
        self.capture_thread.start()
        self.process_thread.start()
        
    def _capture_frame_fast(self, region):
        """Faster frame capture using win32gui"""
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
        
    def _capture_frames(self):
        print("Starting frame capture...")
        frame_time = 1 / self.fps
        next_frame_time = time.time()
        frames_captured = 0
        
        while self.recording:
            current_time = time.time()
            
            if current_time >= next_frame_time:
                try:
                    frame = self._capture_frame_fast(self.selected_region)
                    
                    if frame is not None and frame.size > 0:
                        if self.use_gpu:
                            self.gpu_frame.upload(frame)
                            frame = self.gpu_frame.download()
                            
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
        
    def process_frame_chunk(self, chunk, quality):
        processed_frames = []
        for frame in chunk:
            if frame is None:
                continue
                
            try:
                if quality == "low":
                    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                elif quality == "medium":
                    frame = cv2.resize(frame, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)
                    
                if self.use_gpu:
                    self.gpu_frame.upload(frame)
                    frame = self.gpu_frame.download()
                    
                processed_frames.append(frame)
            except Exception as e:
                print(f"Error processing frame in chunk: {str(e)}")
                continue
                
        return processed_frames

    def _process_frames(self):
        print("Starting frame processing...")
        chunk_size = 10
        current_chunk = []
        self.processed_frames = []
        frames_processed = 0
        
        while self.recording or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                if frame is not None:
                    current_chunk.append(frame)
                    frames_processed += 1
                    print(f"Processing frame {frames_processed}")
                
                if len(current_chunk) >= chunk_size or (not self.recording and current_chunk):
                    processed_chunk = self.process_frame_chunk(current_chunk, self.quality)
                    self.processed_frames.extend(processed_chunk)
                    current_chunk = []
                    
            except queue.Empty:
                if not self.recording and current_chunk:
                    processed_chunk = self.process_frame_chunk(current_chunk, self.quality)
                    self.processed_frames.extend(processed_chunk)
                    current_chunk = []
                continue
            except Exception as e:
                print(f"Frame processing error: {e}")
                import traceback
                traceback.print_exc()
                continue
                
        print(f"Frame processing stopped. Total frames processed: {frames_processed}")
        print(f"Total frames in processed_frames: {len(self.processed_frames)}")

    def stop_recording(self):
        if not self.recording:
            print("Not currently recording!")
            return None
            
        print("Stopping recording...")
        self.recording = False
        
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()
        
        print(f"Number of processed frames: {len(self.processed_frames)}")
        if not self.processed_frames:
            print("No frames were processed!")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format_type == "video":
            filename = f"recording_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                height, width = self.processed_frames[0].shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    print("Failed to open video writer!")
                    return None
                
                frames_written = 0
                for frame in self.processed_frames:
                    if frame is not None:
                        out.write(frame)
                        frames_written += 1
                        
                print(f"Wrote {frames_written} frames to video")
                out.release()
                
            except Exception as e:
                print(f"Error saving video: {str(e)}")
                return None
            
        else:  
            filename = f"recording_{timestamp}.gif"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                print("Converting frames to GIF format...")
                pil_frames = []
                
                for frame in self.processed_frames:
                    if frame is not None:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                        
                        if self.quality == "low":
                            img = img.quantize(colors=64)
                        elif self.quality == "medium":
                            img = img.quantize(colors=128)
                        else:
                            img = img.quantize(colors=256)
                        
                        pil_frames.append(img)
                
                print(f"Converted {len(pil_frames)} frames to GIF format")
                
                if not pil_frames:
                    print("No frames to save!")
                    return None
                
                duration = max(20, int(1000/self.fps)) 
                
                print(f"Saving GIF with {len(pil_frames)} frames...")
                pil_frames[0].save(
                    filepath,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=duration,
                    loop=0,
                    optimize=True
                )
                
            except Exception as e:
                print(f"Error saving GIF: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
            
        print(f"Recording saved to: {filepath}")
        return filepath

    def pause(self):
        self.recording = False
        
    def resume(self):
        self.recording = True
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.start() 