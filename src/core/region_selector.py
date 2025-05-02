"""
Module for handling screen region selection.
"""

import tkinter as tk
from typing import Optional, Dict

class RegionSelector:
    """
    Handles screen region selection using a GUI overlay.
    """
    
    def __init__(self):
        self.root = None
        self.canvas = None
        self.selection_rect = None
        self.start_x = self.start_y = self.end_x = self.end_y = None
        
    def select_region(self) -> Optional[Dict[str, int]]:
        """
        Open a GUI overlay for region selection.
        
        Returns:
            Dictionary containing selected region coordinates or None if selection cancelled
        """
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        
        self._setup_bindings()
        self._show_instructions()
        
        self.root.mainloop()
        self.root.destroy()
        
        if self.start_x and self.start_y and self.end_x and self.end_y:
            x1, x2 = min(self.start_x, self.end_x), max(self.start_x, self.end_x)
            y1, y2 = min(self.start_y, self.end_y), max(self.start_y, self.end_y)
            return {
                "left": x1,
                "top": y1,
                "width": x2 - x1 + 1,
                "height": y2 - y1 + 1
            }
        return None
        
    def _setup_bindings(self):
        """Setup mouse and keyboard bindings for region selection."""
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", self._on_esc)
        
    def _show_instructions(self):
        """Display instructions for region selection."""
        self.canvas.create_text(
            self.root.winfo_screenwidth()/2, 50,
            text="Click and drag to select recording area. Press ESC to cancel.",
            fill="white",
            font=("Arial", 16)
        )
        
    def _on_press(self, event):
        """Handle mouse press event."""
        self.start_x = event.x
        self.start_y = event.y
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red'
        )
        
    def _on_drag(self, event):
        """Handle mouse drag event."""
        self.end_x = event.x
        self.end_y = event.y
        self.canvas.coords(
            self.selection_rect,
            self.start_x, self.start_y, self.end_x, self.end_y
        )
        
    def _on_release(self, event):
        """Handle mouse release event."""
        self.end_x = event.x
        self.end_y = event.y
        self.root.quit()
        
    def _on_esc(self, event):
        """Handle ESC key press event."""
        self.start_x = self.start_y = self.end_x = self.end_y = None
        self.root.quit() 