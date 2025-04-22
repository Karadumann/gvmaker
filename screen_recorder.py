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
import psutil

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        available_memory = psutil.virtual_memory().available
        queue_size = min(2000, int(available_memory / (1024 * 1024 * 10)))
        self.frame_queue = queue.Queue(maxsize=queue_size)
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        cpu_count = os.cpu_count() or 4
        self.thread_pool = ThreadPoolExecutor(max_workers=max(4, cpu_count * 2))
        self.sct = mss.mss()
        self.frame_cache = {}
        self.cache_size = 100
        
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
        
    def _capture_frames(self):
        frame_time = 1 / self.fps
        next_frame_time = time.time()
        
        while self.recording:
            current_time = time.time()
            
            if current_time >= next_frame_time:
                try:
                    frame = np.array(self.sct.grab(self.selected_region))
                    
                    if frame is not None and frame.size > 0:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR, dst=frame)
                        
                        try:
                            if not self.frame_queue.full():
                                self.frame_queue.put(frame)
                        except:
                            print("Error adding frame to queue")
                            
                    next_frame_time = current_time + frame_time
                except Exception as e:
                    print(f"Error capturing frame: {str(e)}")
                    continue
                    
            time.sleep(0.0005)
            
    def process_frame_chunk(self, chunk, quality):
        processed_frames = []
        for frame in chunk:
            if frame is None:
                continue
                
            frame_key = hash(frame.tobytes())
            if frame_key in self.frame_cache:
                processed_frames.append(self.frame_cache[frame_key])
                continue
                
            if quality == "low":
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
            elif quality == "medium":
                frame = cv2.resize(frame, None, fx=0.75, fy=0.75)
                
            if len(self.frame_cache) >= self.cache_size:
                oldest_key = next(iter(self.frame_cache))
                del self.frame_cache[oldest_key]
            self.frame_cache[frame_key] = frame
            
            processed_frames.append(frame)
            
        return processed_frames

    def _process_frames(self):
        chunk_size = 10
        current_chunk = []
        
        while self.recording or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                current_chunk.append(frame)
                
                if len(current_chunk) >= chunk_size or self.frame_queue.empty():
                    processed_chunk = self.process_frame_chunk(current_chunk, self.quality)
                    
                    for frame in processed_chunk:
                        if frame is not None:
                            self.frames.append(frame)
                            
                    current_chunk = []
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Frame processing error: {e}")
                continue

    def stop_recording(self):
        if not self.recording:
            return None
            
        print("Stopping recording...")
        self.recording = False
        
        self.capture_thread.join()
        self.process_thread.join()
        
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
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                chunk_size = 200
                frames_written = 0
                for i in range(0, len(self.processed_frames), chunk_size):
                    chunk = self.processed_frames[i:i + chunk_size]
                    for frame in chunk:
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
                total_frames = len(self.processed_frames)
                pil_frames = [None] * total_frames
                
                def convert_frame_optimized(args):
                    idx, frame = args
                    if self.quality == "medium":
                        frame = cv2.resize(frame, None, fx=0.75, fy=0.75)
                    elif self.quality == "low":
                        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    if self.quality == "low":
                        img = img.quantize(colors=64)
                    elif self.quality == "medium":
                        img = img.quantize(colors=128)
                    else:
                        img = img.quantize(colors=256)
                    
                    return idx, img
                
                frame_data = list(enumerate(self.processed_frames))
                results = list(self.thread_pool.map(convert_frame_optimized, frame_data))
                
                for idx, img in results:
                    pil_frames[idx] = img
                
                print(f"Converted {len(pil_frames)} frames to optimized GIF format")
                
                if self.quality == "high":
                    optimize = True
                    quality = 90
                elif self.quality == "medium":
                    optimize = True
                    quality = 70
                else:
                    optimize = True
                    quality = 50
                
                duration = max(20, int(1000/self.fps))
                
                pil_frames[0].save(
                    filepath,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=duration,
                    loop=0,
                    optimize=optimize,
                    quality=quality
                )
                
            except Exception as e:
                print(f"Error saving GIF: {str(e)}")
                return None
            
        self.processed_frames = []
        
        print(f"Recording saved to: {filepath}")
        return filepath

    def pause(self):
        self.recording = False
        
    def resume(self):
        self.recording = True
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.start() 