"""
Settings dialog module for configuring application settings.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any
from .settings_manager import SettingsManager

class SettingsDialog(tk.Toplevel):
    """
    Dialog for configuring application settings.
    """
    
    def __init__(self, parent: tk.Tk, settings_manager: SettingsManager):
        """
        Initialize the settings dialog.
        
        Args:
            parent: Parent window
            settings_manager: Settings manager instance
        """
        super().__init__(parent)
        self.settings_manager = settings_manager
        
        self.title("Settings")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI components."""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=BOTH, expand=YES)
        
        # API Key
        api_frame = ttk.LabelFrame(main_frame, text="API Key", padding="5")
        api_frame.pack(fill=X, pady=5)
        
        self.api_key_var = tk.StringVar(value=self.settings_manager.get_api_key())
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*")
        api_entry.pack(fill=X, padx=5, pady=5)
        verify_button = ttk.Button(
            api_frame,
            text="Validate",
            command=self._verify_api_key,
            style="info.TButton"
        )
        verify_button.pack(pady=5)
        
        # FPS
        fps_frame = ttk.LabelFrame(main_frame, text="Frames Per Second", padding="5")
        fps_frame.pack(fill=X, pady=5)
        
        self.fps_var = tk.StringVar(value=str(self.settings_manager.get_fps()))
        fps_entry = ttk.Entry(fps_frame, textvariable=self.fps_var)
        fps_entry.pack(fill=X, padx=5, pady=5)
        
        # Output Directory
        dir_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
        dir_frame.pack(fill=X, pady=5)
        
        self.dir_var = tk.StringVar(value=self.settings_manager.get_output_dir())
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var)
        dir_entry.pack(fill=X, padx=5, pady=5)
        
        browse_button = ttk.Button(
            dir_frame,
            text="Browse",
            command=self._browse_directory,
            style="info.TButton"
        )
        browse_button.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=self._save_settings,
            style="success.TButton"
        )
        save_button.pack(side=RIGHT, padx=5)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            style="danger.TButton"
        )
        cancel_button.pack(side=RIGHT, padx=5)
        
    def _browse_directory(self):
        """Open directory browser dialog."""
        directory = filedialog.askdirectory(
            initialdir=self.dir_var.get(),
            title="Select Output Directory"
        )
        if directory:
            self.dir_var.set(directory)
            
    def _save_settings(self):
        """Save settings and close dialog."""
        try:
            self.settings_manager.set_api_key(self.api_key_var.get())
            self.settings_manager.set_fps(int(self.fps_var.get()))
            self.settings_manager.set_output_dir(self.dir_var.get())
            self.destroy()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def show(self):
        """Show the dialog and wait for it to close."""
        self.transient(self.master)
        self.grab_set()
        self.wait_window()

    def _verify_api_key(self):
        api_key = self.api_key_var.get()
        if not api_key:
            tk.messagebox.showwarning("API Key", "API key cannot be empty!")
            return
        if len(api_key) < 10:
            tk.messagebox.showerror("API Key", "API key is too short!")
            return
        tk.messagebox.showinfo("API Key", "API key format is valid.") 