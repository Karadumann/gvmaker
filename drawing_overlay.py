import tkinter as tk
from tkinter import ttk
import keyboard

class DrawingOverlay:
    def __init__(self, settings):
        self.settings = settings
        self.drawing_settings = settings.get_drawing_settings()
        self.active = False
        self.current_shape = None
        self.start_x = None
        self.start_y = None
        
    def start(self):
        """Start drawing overlay"""
        self.active = True
        self._create_overlay_window()
        self._create_toolbar()
        
    def stop(self):
        """Stop drawing overlay"""
        self.active = False
        if hasattr(self, 'window'):
            self.window.destroy()
            
    def _create_overlay_window(self):
        """Create transparent overlay window"""
        self.window = tk.Tk()
        self.window.attributes('-alpha', 0.01, '-topmost', True)
        self.window.attributes('-fullscreen', True)
        
        # Create canvas
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self._start_drawing)
        self.canvas.bind('<B1-Motion>', self._draw)
        self.canvas.bind('<ButtonRelease-1>', self._finish_drawing)
        
        # Bind escape key to exit
        keyboard.on_press_key('esc', lambda _: self.stop())
        
    def _create_toolbar(self):
        """Create floating toolbar"""
        self.toolbar = tk.Toplevel(self.window)
        self.toolbar.overrideredirect(True)
        self.toolbar.attributes('-topmost', True)
        
        # Create frame
        frame = ttk.Frame(self.toolbar)
        frame.pack(padx=5, pady=5)
        
        # Shape buttons
        shapes = self.drawing_settings["shapes"]
        for shape in shapes:
            ttk.Button(frame, text=shape.title(),
                      command=lambda s=shape: self._set_shape(s)).pack(side="left", padx=2)
                      
        # Color picker
        ttk.Button(frame, text="Color",
                  command=self._choose_color).pack(side="left", padx=2)
                  
        # Clear button
        ttk.Button(frame, text="Clear",
                  command=self._clear_canvas).pack(side="left", padx=2)
                  
        # Position toolbar
        self.toolbar.geometry('+10+10')
        
    def _set_shape(self, shape):
        """Set current drawing shape"""
        self.current_shape = shape
        
    def _choose_color(self):
        """Open color chooser"""
        color = tk.colorchooser.askcolor(self.drawing_settings["pen_color"])[1]
        if color:
            self.drawing_settings["pen_color"] = color
            
    def _clear_canvas(self):
        """Clear all drawings"""
        self.canvas.delete("all")
        
    def _start_drawing(self, event):
        """Start drawing shape"""
        self.start_x = event.x
        self.start_y = event.y
        
        if self.current_shape == "text":
            self._add_text(event.x, event.y)
            
    def _draw(self, event):
        """Draw shape preview"""
        if not self.current_shape or self.current_shape == "text":
            return
            
        # Remove previous preview
        self.canvas.delete("preview")
        
        # Draw new preview
        if self.current_shape == "rectangle":
            self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.drawing_settings["pen_color"],
                width=self.drawing_settings["pen_size"],
                tags="preview"
            )
        elif self.current_shape == "circle":
            self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.drawing_settings["pen_color"],
                width=self.drawing_settings["pen_size"],
                tags="preview"
            )
        elif self.current_shape == "arrow":
            self._draw_arrow(
                self.start_x, self.start_y, event.x, event.y,
                self.drawing_settings["pen_color"],
                self.drawing_settings["pen_size"],
                "preview"
            )
            
    def _finish_drawing(self, event):
        """Finish drawing shape"""
        if not self.current_shape or self.current_shape == "text":
            return
            
        # Remove preview
        self.canvas.delete("preview")
        
        # Draw final shape
        if self.current_shape == "rectangle":
            self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.drawing_settings["pen_color"],
                width=self.drawing_settings["pen_size"]
            )
        elif self.current_shape == "circle":
            self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.drawing_settings["pen_color"],
                width=self.drawing_settings["pen_size"]
            )
        elif self.current_shape == "arrow":
            self._draw_arrow(
                self.start_x, self.start_y, event.x, event.y,
                self.drawing_settings["pen_color"],
                self.drawing_settings["pen_size"]
            )
            
    def _add_text(self, x, y):
        """Add text annotation"""
        text = tk.simpledialog.askstring("Add Text", "Enter text:")
        if text:
            self.canvas.create_text(
                x, y,
                text=text,
                fill=self.drawing_settings["pen_color"],
                font=("Arial", self.drawing_settings["pen_size"] * 5)
            )
            
    def _draw_arrow(self, x1, y1, x2, y2, color, width, tags=""):
        """Draw arrow shape"""
        # Calculate arrow head
        arrow_head_size = width * 5
        dx = x2 - x1
        dy = y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        if length == 0:
            return
            
        # Normalize direction
        dx = dx / length
        dy = dy / length
        
        # Calculate arrow head points
        x3 = x2 - arrow_head_size * dx + arrow_head_size * dy * 0.5
        y3 = y2 - arrow_head_size * dy - arrow_head_size * dx * 0.5
        x4 = x2 - arrow_head_size * dx - arrow_head_size * dy * 0.5
        y4 = y2 - arrow_head_size * dy + arrow_head_size * dx * 0.5
        
        # Draw arrow line and head
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags=tags)
        self.canvas.create_polygon(x2, y2, x3, y3, x4, y4, 
                                 fill=color, outline=color, tags=tags) 