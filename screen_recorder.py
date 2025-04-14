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

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        # Increase queue size for better performance
        self.frame_queue = queue.Queue(maxsize=2000)  # Increased from 1000 to 2000
        # Get user's Desktop folder
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        
        # Create recordings directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.thread_pool = ThreadPoolExecutor(max_workers=8)  # Increased from 4 to 8
        
        # Initialize mss instance for better performance
        self.sct = mss.mss()
        
    def select_region(self):
        """Open a window to select screen region"""
        root = tk.Tk()
        root.attributes('-alpha', 0.3)  # Make window semi-transparent
        root.attributes('-fullscreen', True)  # Make window fullscreen
        
        # Create a canvas that covers the entire screen
        canvas = tk.Canvas(root, cursor="cross")
        canvas.pack(fill="both", expand=True)
        
        # Variables to store selection coordinates
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
                # Ensure coordinates are in correct order
                x1, x2 = min(start_x, end_x), max(start_x, end_x)
                y1, y2 = min(start_y, end_y), max(start_y, end_y)
                # Add 1 pixel to ensure proper capture
                root.selected_region = {"left": x1, "top": y1, "width": x2-x1+1, "height": y2-y1+1}
                root.quit()
                
        # Bind mouse events
        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        # Add instructions
        instructions = canvas.create_text(
            root.winfo_screenwidth()/2, 50,
            text="Click and drag to select recording area. Press ESC to cancel.",
            fill="white",
            font=("Arial", 16)
        )
        
        # Handle ESC key
        def on_esc(event):
            root.selected_region = None
            root.quit()
        root.bind("<Escape>", on_esc)
        
        root.mainloop()
        root.destroy()
        
        return root.selected_region
        
    def start_recording(self, region=None, format_type="video", fps=30, quality="high"):
        """Start screen recording"""
        if self.recording:
            return
            
        self.recording = True
        self.format_type = format_type
        self.fps = fps
        self.quality = quality
        
        # If no region provided, let user select it
        if not region:
            region = self.select_region()
            if not region:
                self.recording = False
                raise Exception("No region selected")
                
        self.selected_region = region
        
        # Start recording and processing threads
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.process_thread = threading.Thread(target=self._process_frames)
        
        self.capture_thread.start()
        self.process_thread.start()
        
    def _capture_frames(self):
        """Capture frames in a separate thread"""
        frame_time = 1 / self.fps
        next_frame_time = time.time()
        
        while self.recording:
            current_time = time.time()
            
            # Only capture if it's time for the next frame
            if current_time >= next_frame_time:
                try:
                    # Capture frame using mss with optimized settings
                    frame = np.array(self.sct.grab(self.selected_region))
                    
                    if frame is not None and frame.size > 0:
                        # Convert BGRA to BGR using optimized method
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR, dst=frame)
                        
                        # Add to queue if not full
                        try:
                            if not self.frame_queue.full():
                                self.frame_queue.put(frame)
                            else:
                                # If queue is full, skip frame instead of waiting
                                pass
                        except:
                            print("Error adding frame to queue")
                            
                    # Calculate next frame time
                    next_frame_time = current_time + frame_time
                except Exception as e:
                    print(f"Error capturing frame: {str(e)}")
                    continue
                    
            # Small sleep to prevent high CPU usage
            time.sleep(0.0005)  # Reduced sleep time
            
    def process_frame_chunk(self, chunk, quality):
        """Process a chunk of frames in parallel"""
        processed_frames = []
        for frame in chunk:
            if frame is not None and frame.size > 0:
                try:
                    if quality == "medium":
                        frame = cv2.resize(frame, None, fx=0.75, fy=0.75)
                    elif quality == "low":
                        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                    processed_frames.append(frame)
                except Exception as e:
                    print(f"Error processing frame: {str(e)}")
        return processed_frames

    def _process_frames(self):
        """Process frames in a separate thread with parallel processing"""
        self.processed_frames = []
        frame_count = 0
        chunk = []
        chunk_size = 100  # Increased from 50 to 100
        
        while self.recording or not self.frame_queue.empty():
            try:
                # Get frame from queue with shorter timeout
                frame = self.frame_queue.get(timeout=0.05)  # Reduced timeout
                chunk.append(frame)
                
                # Process chunk when it reaches the desired size
                if len(chunk) >= chunk_size:
                    # Split chunk into larger sub-chunks for better parallel processing
                    sub_chunks = [chunk[i:i + 20] for i in range(0, len(chunk), 20)]  # Increased from 10 to 20
                    futures = []
                    
                    # Submit sub-chunks for parallel processing
                    for sub_chunk in sub_chunks:
                        future = self.thread_pool.submit(self.process_frame_chunk, sub_chunk, self.quality)
                        futures.append(future)
                    
                    # Collect results
                    for future in futures:
                        self.processed_frames.extend(future.result())
                        frame_count += len(future.result())
                    
                    chunk = []
                    
            except queue.Empty:
                if self.recording:
                    continue
                else:
                    # Process remaining frames
                    if chunk:
                        processed = self.process_frame_chunk(chunk, self.quality)
                        self.processed_frames.extend(processed)
                        frame_count += len(processed)
                    break
                    
        print(f"Processed {frame_count} frames")

    def stop_recording(self):
        """Stop recording and save the file"""
        if not self.recording:
            return None
            
        print("Stopping recording...")
        self.recording = False
        
        # Wait for threads to finish
        self.capture_thread.join()
        self.process_thread.join()
        
        if not self.processed_frames:
            print("No frames were processed!")
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format_type == "video":
            filename = f"recording_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                # Get frame dimensions
                height, width = self.processed_frames[0].shape[:2]
                
                # Create video writer with FFmpeg codec
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    print("Failed to create video writer!")
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                # Write frames in larger chunks for better performance
                chunk_size = 200  # Increased from 100 to 200
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
            
        else:  # GIF
            filename = f"recording_{timestamp}.gif"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                # Pre-allocate list for better performance
                total_frames = len(self.processed_frames)
                pil_frames = [None] * total_frames
                
                # Use thread pool for parallel conversion with optimized settings
                def convert_frame_optimized(args):
                    idx, frame = args
                    # Resize before conversion to reduce memory usage
                    if self.quality == "medium":
                        frame = cv2.resize(frame, None, fx=0.75, fy=0.75)
                    elif self.quality == "low":
                        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                    
                    # Convert to RGB and reduce colors for smaller file size
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # Reduce colors based on quality setting
                    if self.quality == "low":
                        img = img.quantize(colors=64)  # Reduce to 64 colors
                    elif self.quality == "medium":
                        img = img.quantize(colors=128)  # Reduce to 128 colors
                    else:  # high quality
                        img = img.quantize(colors=256)  # Use full 256 colors
                    
                    return idx, img
                
                # Convert frames in parallel with index tracking
                frame_data = list(enumerate(self.processed_frames))
                results = list(self.thread_pool.map(convert_frame_optimized, frame_data))
                
                # Place frames in correct order
                for idx, img in results:
                    pil_frames[idx] = img
                
                print(f"Converted {len(pil_frames)} frames to optimized GIF format")
                
                # Optimize GIF settings based on quality
                if self.quality == "high":
                    optimize = True
                    quality = 90
                elif self.quality == "medium":
                    optimize = True
                    quality = 70
                else:  # low
                    optimize = True
                    quality = 50
                
                # Calculate optimal duration based on FPS
                duration = max(20, int(1000/self.fps))  # Minimum 20ms (50 FPS max)
                
                # Save as GIF with optimizations
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
            
        # Clear memory
        self.processed_frames = []
        
        print(f"Recording saved to: {filepath}")
        return filepath

    def pause(self):
        """Pause recording"""
        self.recording = False
        
    def resume(self):
        """Resume recording"""
        self.recording = True
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.capture_thread.start() 