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

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.frame_queue = queue.Queue(maxsize=300)  # Limit queue size to prevent memory issues
        # Get user's Desktop folder
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        self.overlay_window = None
        
        # Create recordings directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            # Try to open the folder in Windows Explorer
            try:
                os.startfile(self.output_dir)
            except:
                pass  # Ignore if can't open folder
            
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
        
    def create_overlay_window(self):
        """Create a semi-transparent overlay window to show recording area"""
        if self.overlay_window:
            self.overlay_window.destroy()
            
        self.overlay_window = tk.Tk()
        self.overlay_window.attributes('-alpha', 0.3)  # Semi-transparent
        self.overlay_window.attributes('-topmost', True)  # Always on top
        self.overlay_window.overrideredirect(True)  # No window decorations
        
        # Set window size and position
        self.overlay_window.geometry(f"{self.selected_region['width']}x{self.selected_region['height']}+{self.selected_region['left']}+{self.selected_region['top']}")
        
        # Create canvas with red border
        canvas = tk.Canvas(self.overlay_window, highlightthickness=2, highlightbackground='red')
        canvas.pack(fill="both", expand=True)
        
        # Add recording indicator text
        canvas.create_text(
            self.selected_region['width']/2, 20,
            text="Recording in progress...",
            fill="red",
            font=("Arial", 12, "bold")
        )
        
        return self.overlay_window
        
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
        
        # Create and show overlay window
        self.overlay_window = self.create_overlay_window()
        
        # Start recording and processing threads
        self.capture_thread = threading.Thread(target=self._capture_frames)
        self.process_thread = threading.Thread(target=self._process_frames)
        
        self.capture_thread.start()
        self.process_thread.start()
        
    def _capture_frames(self):
        """Capture frames in a separate thread"""
        # Create a new mss instance for this thread
        with mss.mss() as sct:
            frame_time = 1 / self.fps
            next_frame_time = time.time()
            
            while self.recording:
                current_time = time.time()
                
                # Only capture if it's time for the next frame
                if current_time >= next_frame_time:
                    try:
                        # Capture frame using mss
                        frame = np.array(sct.grab(self.selected_region))
                        
                        if frame is not None and frame.size > 0:
                            # Convert BGRA to BGR
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                            
                            # Add to queue if not full
                            try:
                                if not self.frame_queue.full():
                                    self.frame_queue.put(frame)
                                else:
                                    # If queue is full, wait a bit
                                    time.sleep(0.001)
                            except:
                                print("Error adding frame to queue")
                                
                        # Calculate next frame time
                        next_frame_time = current_time + frame_time
                    except Exception as e:
                        print(f"Error capturing frame: {str(e)}")
                        continue
                        
                # Small sleep to prevent high CPU usage
                time.sleep(0.001)
            
    def _process_frames(self):
        """Process frames in a separate thread"""
        self.processed_frames = []
        frame_count = 0
        last_frame = None
        
        while self.recording or not self.frame_queue.empty():
            try:
                # Get frame from queue with timeout
                frame = self.frame_queue.get(timeout=0.1)
                
                if frame is not None and frame.size > 0:
                    # Apply quality settings
                    try:
                        if self.quality == "medium":
                            frame = cv2.resize(frame, None, fx=0.75, fy=0.75)
                        elif self.quality == "low":
                            frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                            
                        self.processed_frames.append(frame)
                        last_frame = frame
                        frame_count += 1
                    except Exception as e:
                        print(f"Error processing frame: {str(e)}")
                        if last_frame is not None:
                            self.processed_frames.append(last_frame)
                            frame_count += 1
                            
            except queue.Empty:
                if self.recording:  # Only continue if still recording
                    continue
                else:
                    break  # Stop if recording is done and queue is empty
                    
        print(f"Processed {frame_count} frames")  # Debug info
                
    def stop_recording(self):
        """Stop recording and save the file"""
        if not self.recording:
            return None
            
        print("Stopping recording...")  # Debug info
        self.recording = False
        
        # Close overlay window
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
        
        # Wait for threads to finish
        print("Waiting for capture thread...")  # Debug info
        self.capture_thread.join()
        print("Waiting for process thread...")  # Debug info
        self.process_thread.join()
        
        print(f"Total frames captured: {len(self.processed_frames)}")  # Debug info
        
        if not self.processed_frames:
            print("No frames were processed!")  # Debug info
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format_type == "video":
            filename = f"recording_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                # Get frame dimensions
                height, width = self.processed_frames[0].shape[:2]
                
                # Create video writer with H.264 codec
                fourcc = cv2.VideoWriter_fourcc(*'avc1')
                out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                if not out.isOpened():
                    print("Failed to create video writer!")  # Debug info
                    # Try with different codec
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
                
                # Write frames in chunks for better performance
                chunk_size = 100
                frames_written = 0
                for i in range(0, len(self.processed_frames), chunk_size):
                    chunk = self.processed_frames[i:i + chunk_size]
                    for frame in chunk:
                        out.write(frame)
                        frames_written += 1
                        
                print(f"Wrote {frames_written} frames to video")  # Debug info
                out.release()
                
            except Exception as e:
                print(f"Error saving video: {str(e)}")  # Debug info
                return None
            
        else:  # GIF
            filename = f"recording_{timestamp}.gif"
            filepath = os.path.join(self.output_dir, filename)
            
            try:
                # Convert frames to PIL Images in chunks
                pil_frames = []
                chunk_size = 50
                frames_converted = 0
                for i in range(0, len(self.processed_frames), chunk_size):
                    chunk = self.processed_frames[i:i + chunk_size]
                    for frame in chunk:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_frames.append(Image.fromarray(frame_rgb))
                        frames_converted += 1
                        
                print(f"Converted {frames_converted} frames to PIL images")  # Debug info
                
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
                    
                # Save as GIF with optimizations
                duration = int(1000/self.fps)  # Duration in milliseconds
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
                print(f"Error saving GIF: {str(e)}")  # Debug info
                return None
            
        # Clear memory
        self.processed_frames = []
        
        print(f"Recording saved to: {filepath}")  # Debug print
        return filepath 