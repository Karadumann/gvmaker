import cv2
import numpy as np
import pyautogui
import time
from PIL import ImageGrab, Image
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        # Get user's Desktop folder
        self.base_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_dir = os.path.join(self.base_dir, "Screen Recordings")
        self.selected_region = None
        
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
                root.selected_region = {"x": x1, "y": y1, "width": x2-x1, "height": y2-y1}
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
        self.frames = []
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
        
        # Start recording in a separate thread
        import threading
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()
        
    def _record(self):
        """Internal recording function"""
        while self.recording:
            # Capture the screen
            screenshot = ImageGrab.grab(bbox=(
                self.selected_region["x"],
                self.selected_region["y"],
                self.selected_region["x"] + self.selected_region["width"],
                self.selected_region["y"] + self.selected_region["height"]
            ))
            
            # Convert to numpy array
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Add frame to list
            self.frames.append(frame)
            
            # Control frame rate
            time.sleep(1/self.fps)
            
    def stop_recording(self):
        """Stop recording and save the file"""
        if not self.recording:
            return None
            
        self.recording = False
        self.recording_thread.join()
        
        if not self.frames:
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.format_type == "video":
            filename = f"recording_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            # Get frame dimensions
            height, width = self.frames[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
            
            # Write frames
            for frame in self.frames:
                out.write(frame)
                
            out.release()
            
        else:  # GIF
            filename = f"recording_{timestamp}.gif"
            filepath = os.path.join(self.output_dir, filename)
            
            # Convert frames to PIL Images
            pil_frames = []
            for frame in self.frames:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_frames.append(Image.fromarray(frame_rgb))
                
            # Save as GIF
            duration = int(1000/self.fps)  # Duration in milliseconds
            pil_frames[0].save(
                filepath,
                save_all=True,
                append_images=pil_frames[1:],
                duration=duration,
                loop=0
            )
            
        print(f"Recording saved to: {filepath}")  # Debug print
        return filepath 