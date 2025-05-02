"""
User interface module for the screen recorder application.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser
from typing import Callable, Optional
from ..core.screen_recorder import ScreenRecorder
from ..settings.settings_manager import SettingsManager
from ..utils.uploader import MediaUploader
from .api_key_dialog import APIKeyDialog
from .about_dialog import AboutDialog
import pyperclip

class UI:
    """
    User interface class for the screen recorder application.
    """
    
    def __init__(self, root: ttk.Window,
                 recorder: ScreenRecorder,
                 uploader: MediaUploader,
                 settings_manager: SettingsManager):
        """
        Initialize the UI components.
        
        Args:
            root: Main application window
            recorder: Screen recorder instance
            uploader: Media uploader instance
            settings_manager: Settings manager instance
        """
        self.root = root
        self.recorder = recorder
        self.uploader = uploader
        self.settings_manager = settings_manager
        
        self.on_start_recording: Optional[Callable] = None
        self.on_stop_recording: Optional[Callable] = None
        self.on_pause_recording: Optional[Callable] = None
        self.on_resume_recording: Optional[Callable] = None
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Setup the user interface components."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # API Key Status Frame
        self.api_frame = ttk.Frame(self.main_frame)
        self.api_frame.pack(fill=X, pady=5)
        self.api_status_label = ttk.Label(self.api_frame, text="", style="warning.TLabel")
        self.api_status_label.pack(side=LEFT, padx=5)
        self.api_key_button = ttk.Button(
            self.api_frame,
            text="Add / Change API Key",
            command=self._show_api_key_dialog,
            style="info.TButton"
        )
        self.api_key_button.pack(side=LEFT, padx=5)
        self._update_api_key_status()
        
        # Output Format and Quality
        self.format_quality_frame = ttk.Frame(self.main_frame)
        self.format_quality_frame.pack(fill=X, pady=5)
        ttk.Label(self.format_quality_frame, text="Output Format:").pack(side=LEFT, padx=5)
        self.format_var = tk.StringVar(value=self.settings_manager.get_output_format())
        self.format_combo = ttk.Combobox(
            self.format_quality_frame,
            textvariable=self.format_var,
            values=["video", "gif"],
            state="readonly",
            width=8
        )
        self.format_combo.pack(side=LEFT, padx=5)
        ttk.Label(self.format_quality_frame, text="Quality:").pack(side=LEFT, padx=5)
        self.quality_var = tk.StringVar(value=self.settings_manager.get_quality())
        self.quality_combo = ttk.Combobox(
            self.format_quality_frame,
            textvariable=self.quality_var,
            values=["low", "medium", "high"],
            state="readonly",
            width=8
        )
        self.quality_combo.pack(side=LEFT, padx=5)
        
        # Control buttons
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=X, pady=10)
        
        self.start_button = ttk.Button(
            self.control_frame,
            text="Start Recording",
            command=self._on_start_recording,
            style="success.TButton"
        )
        self.start_button.pack(side=LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            self.control_frame,
            text="Stop Recording",
            command=self._on_stop_recording,
            style="danger.TButton",
            state=DISABLED
        )
        self.stop_button.pack(side=LEFT, padx=5)
        
        self.pause_button = ttk.Button(
            self.control_frame,
            text="Pause",
            command=self._on_pause_recording,
            style="warning.TButton",
            state=DISABLED
        )
        self.pause_button.pack(side=LEFT, padx=5)
        
        # Settings button
        self.settings_button = ttk.Button(
            self.main_frame,
            text="Settings",
            command=self._show_settings,
            style="info.TButton"
        )
        self.settings_button.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            self.main_frame,
            text="Ready to record",
            style="info.TLabel"
        )
        self.status_label.pack(pady=10)
        
        # Recording path label (clickable)
        self.recording_path_label = ttk.Label(
            self.main_frame,
            text="",
            foreground="#1E90FF",
            cursor="hand2",
            font=("Arial", 10, "underline")
        )
        self.recording_path_label.pack(pady=2)
        self.recording_path_label.bind("<Button-1>", self._on_open_recording_folder)
        
        # Share button (initially hidden)
        self.share_button = ttk.Button(
            self.main_frame,
            text="Share Recording",
            command=self._on_share_recording,
            style="primary.TButton"
        )
        self.share_button.pack(pady=5)
        self.share_button.pack_forget()
        
        # Upload URL label (clickable)
        self.upload_url_label = ttk.Label(
            self.main_frame,
            text="",
            foreground="#1E90FF",
            cursor="hand2",
            font=("Arial", 10, "underline")
        )
        self.upload_url_label.pack(pady=2)
        self.upload_url_label.bind("<Button-1>", self._on_open_upload_url)
        
    def _on_start_recording(self):
        """Handle start recording button click."""
        if self.on_start_recording:
            try:
                self.on_start_recording()
                self.start_button.configure(state=DISABLED)
                self.stop_button.configure(state=NORMAL)
                self.pause_button.configure(state=NORMAL)
                self.status_label.configure(text="Recording...")
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}")
                
    def _on_stop_recording(self):
        """Handle stop recording button click."""
        if self.on_stop_recording:
            try:
                output_path = self.on_stop_recording()
                if output_path:
                    self.status_label.configure(text=f"Recording saved to:")
                    self.last_recording_path = output_path
                    self.recording_path_label.configure(text=output_path)
                    self.share_button.pack(pady=5)
                else:
                    self.status_label.configure(text="No frames were recorded!")
                    self.recording_path_label.configure(text="")
                    self.share_button.pack_forget()
                    self.upload_url_label.configure(text="")
            except Exception as e:
                import tkinter.messagebox as mb
                mb.showerror("Error", str(e))
                self.status_label.configure(text=f"Error: {str(e)}")
                self.recording_path_label.configure(text="")
                self.share_button.pack_forget()
                self.upload_url_label.configure(text="")
            finally:
                self.start_button.configure(state=NORMAL)
                self.stop_button.configure(state=DISABLED)
                self.pause_button.configure(state=DISABLED)
                self.pause_button.configure(text="Pause")
        else:
            self.start_button.configure(state=NORMAL)
            self.stop_button.configure(state=DISABLED)
            self.pause_button.configure(state=DISABLED)
            self.pause_button.configure(text="Pause")
                
    def _on_pause_recording(self):
        """Handle pause recording button click."""
        if self.pause_button.cget("text") == "Pause":
            if self.on_pause_recording:
                self.on_pause_recording()
                self.pause_button.configure(text="Resume")
                self.status_label.configure(text="Recording paused")
        else:
            if self.on_resume_recording:
                self.on_resume_recording()
                self.pause_button.configure(text="Pause")
                self.status_label.configure(text="Recording...")
                
    def _show_settings(self):
        """Show settings dialog."""
        from ..settings.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.root, self.settings_manager)
        dialog.show()
        
    def setup_menu(self):
        """Setup the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Recordings Folder", command=self.open_recordings_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Settings", command=self._show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def show_about(self):
        """Show about dialog."""
        AboutDialog(self.root)
        
    def open_recordings_folder(self):
        """Open the recordings folder."""
        import os
        import subprocess
        output_dir = self.settings_manager.get_output_dir()
        if os.path.exists(output_dir):
            subprocess.Popen(f'explorer "{output_dir}"')

    def _update_api_key_status(self):
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            self.api_status_label.configure(text="API key is missing!", style="danger.TLabel")
        else:
            self.api_status_label.configure(text="API key is set", style="success.TLabel")

    def _show_api_key_dialog(self):
        from .api_key_dialog import APIKeyDialog
        dialog = APIKeyDialog(self.root)
        result = dialog.result
        if result:
            self.settings_manager.set_api_key(result)
            self._update_api_key_status()
            self.status_label.configure(text="API key saved.")
        else:
            self.status_label.configure(text="API key not entered.")

    def get_output_format(self):
        return self.format_var.get()

    def get_quality(self):
        return self.quality_var.get()

    def _on_share_recording(self):
        import tkinter.messagebox as mb
        if not hasattr(self, 'last_recording_path') or not self.last_recording_path:
            mb.showwarning("Share Recording", "No recording to share!")
            return
        url = self.uploader.upload_recording(self.last_recording_path)
        if url:
            pyperclip.copy(url)
            self.upload_url_label.configure(text=url)
            self._last_upload_url = url
            mb.showinfo("Share Recording", f"Upload successful!\nURL copied to clipboard.")
        else:
            self.upload_url_label.configure(text="")
            mb.showerror("Share Recording", "Upload failed. Please check your API key and internet connection.")

    def _on_open_recording_folder(self, event=None):
        import os
        import subprocess
        if hasattr(self, 'last_recording_path') and self.last_recording_path:
            folder = os.path.dirname(self.last_recording_path)
            if os.path.exists(folder):
                subprocess.Popen(f'explorer "{folder}"')

    def _on_open_upload_url(self, event=None):
        import webbrowser
        if hasattr(self, '_last_upload_url') and self._last_upload_url:
            webbrowser.open(self._last_upload_url) 