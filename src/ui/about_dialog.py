"""
About dialog module for displaying application information.
"""

import tkinter as tk
from tkinter import ttk, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser

class AboutDialog(simpledialog.Dialog):
    """
    Dialog for displaying application information.
    """
    
    def body(self, master):
        """Create dialog body."""
        info_frame = ttk.Frame(master)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        title = ttk.Label(info_frame, text="Screen Recorder", font=("Helvetica", 14, "bold"))
        title.pack(pady=5)
        
        version = ttk.Label(info_frame, text="Version 1.1.0")
        version.pack()
        
        desc = """A simple and efficient screen recorder that allows you to:
• Record screen areas as Video or GIF
• Adjust FPS and quality settings
• Save recordings to Desktop
• Share recordings via ImgBB
• Easy-to-use interface"""
        
        description = ttk.Label(info_frame, text=desc, justify="left", wraplength=300)
        description.pack(pady=10)
        
        dev_info = ttk.Label(info_frame, text="Developed by Berk Karaduman")
        dev_info.pack()
        
        github_frame = ttk.Frame(info_frame)
        github_frame.pack(pady=5)
        
        github_label = ttk.Label(github_frame, text="GitHub: ")
        github_label.pack(side=LEFT)
        
        github_link = ttk.Label(
            github_frame,
            text="github.com/Karadumann/gvmaker",
            foreground="blue",
            cursor="hand2"
        )
        github_link.pack(side=LEFT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/karadumann/gvmaker"))
        
        return info_frame
        
    def buttonbox(self):
        """Create dialog buttons."""
        box = ttk.Frame(self)
        ok_button = ttk.Button(box, text="OK", width=10, command=self.ok, default="active")
        ok_button.pack(padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack() 