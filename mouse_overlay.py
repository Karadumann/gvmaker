import tkinter as tk
import pyautogui
import threading
import time

class MouseOverlay:
    def __init__(self, settings):
        self.settings = settings
        self.mouse_settings = settings.get_mouse_settings()
        self.active = False
        self.click_windows = []
        self.highlight_window = None
        
    def start(self):
        """Start mouse visualization"""
        self.active = True
        if self.mouse_settings["show_clicks"]:
            threading.Thread(target=self._monitor_clicks, daemon=True).start()
        if self.mouse_settings["highlight_cursor"]:
            self._create_highlight_window()
            threading.Thread(target=self._update_highlight, daemon=True).start()
            
    def stop(self):
        """Stop mouse visualization"""
        self.active = False
        self._clear_click_windows()
        if self.highlight_window:
            self.highlight_window.destroy()
            self.highlight_window = None
            
    def _create_highlight_window(self):
        """Create transparent window for cursor highlight"""
        self.highlight_window = tk.Tk()
        self.highlight_window.overrideredirect(True)
        self.highlight_window.attributes('-alpha', 0.3)
        self.highlight_window.attributes('-topmost', True)
        self.highlight_window.configure(bg=self.mouse_settings["highlight_color"])
        
        # Set initial size
        size = self.mouse_settings["highlight_size"]
        self.highlight_window.geometry(f"{size}x{size}")
        
    def _update_highlight(self):
        """Update highlight window position"""
        while self.active and self.highlight_window:
            try:
                x, y = pyautogui.position()
                size = self.mouse_settings["highlight_size"]
                self.highlight_window.geometry(f"{size}x{size}+{x-size//2}+{y-size//2}")
                time.sleep(1/60)  # 60 FPS update rate
            except:
                pass
                
    def _monitor_clicks(self):
        """Monitor and visualize mouse clicks"""
        last_click_time = 0
        while self.active:
            try:
                x, y = pyautogui.position()
                if pyautogui.mouseDown():
                    current_time = time.time()
                    if current_time - last_click_time > 0.1:  # Debounce clicks
                        self._show_click(x, y)
                        last_click_time = current_time
                time.sleep(1/30)  # 30 FPS check rate
            except:
                pass
                
    def _show_click(self, x, y):
        """Show click visualization"""
        click_window = tk.Toplevel()
        click_window.overrideredirect(True)
        click_window.attributes('-alpha', 0.5)
        click_window.attributes('-topmost', True)
        
        # Create circular click indicator
        size = 20
        canvas = tk.Canvas(click_window, width=size, height=size, 
                         bg='systemtransparent', highlightthickness=0)
        canvas.create_oval(0, 0, size, size, fill=self.mouse_settings["click_color"])
        canvas.pack()
        
        # Position window
        click_window.geometry(f"{size}x{size}+{x-size//2}+{y-size//2}")
        
        # Add to list and schedule removal
        self.click_windows.append(click_window)
        self._schedule_click_removal(click_window)
        
    def _schedule_click_removal(self, window):
        """Schedule click visualization removal"""
        def remove():
            if window in self.click_windows:
                self.click_windows.remove(window)
                window.destroy()
                
        window.after(500, remove)  # Remove after 500ms
        
    def _clear_click_windows(self):
        """Clear all click visualizations"""
        for window in self.click_windows:
            window.destroy()
        self.click_windows.clear() 