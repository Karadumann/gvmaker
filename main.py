import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from screen_recorder import ScreenRecorder
import os
from dotenv import load_dotenv, set_key
from uploader import MediaUploader
import threading
import time
import webbrowser
import pyperclip
import requests
import pyautogui
import keyboard
from datetime import datetime
import sys
from settings import Settings
from settings_dialog import SettingsDialog
import cv2
import numpy as np
import imageio
from PIL import Image

class APIKeyDialog(simpledialog.Dialog):
    def body(self, master):
        ttk.Label(master, text="Please enter your ImgBB API key:").grid(row=0, pady=5)
        ttk.Label(master, text="(Get it from https://api.imgbb.com/)").grid(row=1, pady=5)
        
        self.api_key = ttk.Entry(master, width=50)
        self.api_key.grid(row=2, pady=10, padx=5)
        
        # Create a button to open ImgBB website
        ttk.Button(master, text="Get API Key", 
                  command=lambda: webbrowser.open("https://api.imgbb.com/")).grid(row=3, pady=5)
        
        return self.api_key
        
    def apply(self):
        self.result = self.api_key.get()

class AboutDialog(simpledialog.Dialog):
    def body(self, master):
        # App info
        info_frame = ttk.Frame(master)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Title
        title = ttk.Label(info_frame, text="Screen Recorder", font=("Helvetica", 14, "bold"))
        title.pack(pady=5)
        
        # Version
        version = ttk.Label(info_frame, text="Version 1.1.0")
        version.pack()
        
        # Description
        desc = """A simple and efficient screen recorder that allows you to:
• Record screen areas as Video or GIF
• Adjust FPS and quality settings
• Save recordings to Desktop
• Share recordings via ImgBB
• Easy-to-use interface"""
        
        description = ttk.Label(info_frame, text=desc, justify="left", wraplength=300)
        description.pack(pady=10)
        
        # Developer info
        dev_info = ttk.Label(info_frame, text="Developed by Berk Karaduman")
        dev_info.pack()
        
        # GitHub link
        github_frame = ttk.Frame(info_frame)
        github_frame.pack(pady=5)
        
        github_label = ttk.Label(github_frame, text="GitHub: ")
        github_label.pack(side="left")
        
        github_link = ttk.Label(
            github_frame, 
            text="github.com/Karadumann/gvmaker",
            foreground="blue",
            cursor="hand2"
        )
        github_link.pack(side="left")
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/berkkaraduman/gvmaker"))
        
        return info_frame
        
    def buttonbox(self):
        # Add only OK button
        box = ttk.Frame(self)
        ok_button = ttk.Button(box, text="OK", width=10, command=self.ok, default="active")
        ok_button.pack(padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

class ScreenRecorderApp:
    def __init__(self):
        self.root = ttk.Window(themename="darkly")
        self.root.title("Screen Recorder")
        self.root.geometry("400x750")
        self.root.resizable(False, False)
        
        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                application_path = sys._MEIPASS
            else:
                # Running as script
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not set icon: {str(e)}")
        
        # Center the window
        self.center_window()
        
        # Initialize variables
        self.recorder = ScreenRecorder()
        self.uploader = MediaUploader()
        self.recording = False
        self.paused = False
        self.frames = []
        self.start_time = None
        self.record_thread = None
        
        # Initialize settings
        self.settings = Settings()
        
        # Initialize timer
        self.timer_active = False
        self.timer_thread = None
        
        # Setup UI
        self.setup_ui()
        
        # Setup hotkeys
        self.setup_hotkeys()
        
        # Check API key
        self.check_api_key()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Timer frame at top left
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(anchor=NW, pady=(0, 10))
        
        # Timer label
        self.timer_label = ttk.Label(
            timer_frame,
            text="00:00:00",
            font=("Helvetica", 12, "bold"),
            bootstyle="primary"
        )
        self.timer_label.pack(side=LEFT, padx=5)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Screen Recorder",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))
        
        # Format selection frame
        format_frame = ttk.LabelFrame(main_frame, text="Format", padding=10)
        format_frame.pack(fill=X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value="video")
        ttk.Radiobutton(
            format_frame,
            text="Video (MP4)",
            variable=self.format_var,
            value="video",
            command=self.update_fps_options
        ).pack(anchor=W)
        ttk.Radiobutton(
            format_frame,
            text="GIF",
            variable=self.format_var,
            value="gif",
            command=self.update_fps_options
        ).pack(anchor=W)
        
        # FPS selection frame
        self.fps_frame = ttk.LabelFrame(main_frame, text="FPS", padding=10)
        self.fps_frame.pack(fill=X, pady=(0, 10))
        
        self.fps_var = tk.StringVar(value="30")
        fps_options = ["60", "30", "15", "10", "5"]
        for fps in fps_options:
            ttk.Radiobutton(
                self.fps_frame,
                text=f"{fps} FPS",
                variable=self.fps_var,
                value=fps
            ).pack(anchor=W)
            
        # Quality selection frame
        quality_frame = ttk.LabelFrame(main_frame, text="Quality", padding=10)
        quality_frame.pack(fill=X, pady=(0, 10))
        
        self.quality_var = tk.StringVar(value="high")
        ttk.Radiobutton(
            quality_frame,
            text="High",
            variable=self.quality_var,
            value="high"
        ).pack(anchor=W)
        ttk.Radiobutton(
            quality_frame,
            text="Medium",
            variable=self.quality_var,
            value="medium"
        ).pack(anchor=W)
        ttk.Radiobutton(
            quality_frame,
            text="Low",
            variable=self.quality_var,
            value="low"
        ).pack(anchor=W)
        
        # API Key status frame
        api_frame = ttk.LabelFrame(main_frame, text="API Key Status", padding=10)
        api_frame.pack(fill=X, pady=(0, 10))
        
        self.api_status_label = ttk.Label(
            api_frame,
            text="Checking...",
            font=("Helvetica", 10)
        )
        self.api_status_label.pack(anchor=W)
        
        # Record button
        self.record_button = ttk.Button(
            main_frame,
            text="Start Recording (F8)",
            command=self.toggle_recording,
            bootstyle="success",
            width=20
        )
        self.record_button.pack(pady=10)
        
        # Pause button
        self.pause_button = ttk.Button(
            main_frame,
            text="Pause (F9)",
            command=self.toggle_pause,
            state=tk.DISABLED,
            bootstyle="secondary",
            width=20
        )
        self.pause_button.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Lists container frame
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill=BOTH, expand=YES)
        
        # Recent uploads/recordings frame
        self.uploads_frame = ttk.LabelFrame(lists_frame, text="Recent Uploads", padding=10)
        self.uploads_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        # Create a frame for the uploads listbox and scrollbar
        uploads_list_frame = ttk.Frame(self.uploads_frame)
        uploads_list_frame.pack(fill=BOTH, expand=YES)
        
        # Add scrollbar for uploads
        uploads_scrollbar = ttk.Scrollbar(uploads_list_frame)
        uploads_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Recent uploads listbox
        self.uploads_listbox = tk.Listbox(
            uploads_list_frame,
            yscrollcommand=uploads_scrollbar.set,
            selectmode=tk.SINGLE,
            height=6,
            font=("Helvetica", 9),
            foreground="blue",
            cursor="hand2"
        )
        self.uploads_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        uploads_scrollbar.config(command=self.uploads_listbox.yview)
        
        # Bind double-click event for uploads
        self.uploads_listbox.bind('<Double-Button-1>', self.open_url)
        
        # Recent recordings frame
        self.recordings_frame = ttk.LabelFrame(lists_frame, text="Recent Recordings", padding=10)
        self.recordings_frame.pack(fill=BOTH, expand=YES)
        
        # Create a frame for the recordings listbox and scrollbar
        list_frame = ttk.Frame(self.recordings_frame)
        list_frame.pack(fill=BOTH, expand=YES)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Recent recordings listbox
        self.recordings_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=6,
            font=("Helvetica", 9)
        )
        self.recordings_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.config(command=self.recordings_listbox.yview)
        
        # Bind double-click event for recordings
        self.recordings_listbox.bind('<Double-Button-1>', self.open_recording)
        
        # Update recordings list
        self.update_recordings_list()
        
        # URL frame for showing share links
        self.url_frame = ttk.Frame(main_frame)
        self.url_label = ttk.Label(
            self.url_frame,
            text="",
            font=("Helvetica", 9),
            foreground="blue",
            cursor="hand2"
        )
        self.url_label.pack(side=LEFT, fill=X, expand=YES)
        self.url_label.bind("<Button-1>", lambda e: webbrowser.open(self.current_url))
        
        # Copy URL button
        self.copy_button = ttk.Button(
            self.url_frame,
            text="Copy URL",
            command=self.copy_url,
            width=10
        )
        
        # Setup menu
        self.setup_menu()
        
        # Initial format selection update
        self.update_format_selection()
        
    def setup_hotkeys(self):
        """Setup keyboard shortcuts"""
        shortcuts = self.settings.settings["shortcuts"]
        keyboard.add_hotkey(shortcuts["start_stop"], self.toggle_recording)
        keyboard.add_hotkey(shortcuts["pause"], self.toggle_pause)
        
    def setup_menu(self):
        """Setup the application menu"""
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
        settings_menu.add_command(label="Preferences", command=self.show_settings)
        settings_menu.add_command(label="Change API Key", command=self.change_api_key)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """Screen Recorder v1.0
        
A simple screen recording tool that can capture your screen as video or GIF.

Features:
• Record screen as MP4 or GIF
• Adjustable FPS and quality
• Automatic ImgBB upload
• Hotkey support (F8)
• Modern dark theme

Created by Berk Karaduman
© 2025"""
        
        messagebox.showinfo("About", about_text)
        
    def check_api_key(self):
        """Check if API key exists, if not ask for it"""
        # Get the path to the user's AppData/Local folder
        app_data = os.path.join(os.getenv('LOCALAPPDATA'), 'ScreenRecorder')
        self.config_file = os.path.join(app_data, 'config.env')
        
        # Create directory if it doesn't exist
        if not os.path.exists(app_data):
            os.makedirs(app_data)
            
        # Load existing config
        load_dotenv(self.config_file)
        
        # Check if API key exists
        if not os.getenv('IMGBB_API_KEY'):
            # Show dialog to get API key
            dialog = APIKeyDialog(self.root)
            api_key = dialog.result
            
            if api_key:
                # Save API key to config file
                with open(self.config_file, 'w') as f:
                    f.write(f'IMGBB_API_KEY={api_key}')
                os.environ['IMGBB_API_KEY'] = api_key
            else:
                # If user cancels, exit application
                self.root.destroy()
                exit()
                
    def change_api_key(self):
        """Show dialog to change API key"""
        dialog = APIKeyDialog(self.root)
        api_key = dialog.result
        
        if api_key:
            # Save new API key
            with open(self.config_file, 'w') as f:
                f.write(f'IMGBB_API_KEY={api_key}')
            os.environ['IMGBB_API_KEY'] = api_key
            self.update_api_status()  # Update status after changing key
            
    def update_api_status(self):
        """Update API status indicator"""
        api_key = os.getenv('IMGBB_API_KEY')
        if not api_key:
            self.api_status_label.config(text="⬤ API Key Missing", foreground="red")
            return False
            
        if self.test_api_key(api_key):
            self.api_status_label.config(text="⬤ API Key Active", foreground="green")
            return True
        else:
            self.api_status_label.config(text="⬤ API Key Invalid", foreground="red")
            return False
        
    def test_api_key(self, api_key):
        """Test if the API key is valid"""
        try:
            # Try to upload a small test image
            test_payload = {
                'key': api_key,
                'image': 'R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='  # 1x1 transparent GIF
            }
            response = requests.post('https://api.imgbb.com/1/upload', data=test_payload)
            return response.status_code == 200 and 'data' in response.json()
        except:
            return False
            
    def update_timer(self):
        """Update timer display"""
        if self.timer_active and not self.paused:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Check if we should stop recording based on timer settings
            timer_settings = self.settings.get_timer_settings()
            if timer_settings["enabled"] and timer_settings["stop_after"] > 0:
                if elapsed >= timer_settings["stop_after"]:
                    self.stop_recording()
                    
        self.root.after(1000, self.update_timer)  # Update every second
        
    def start_timer(self):
        """Start the timer"""
        self.timer_active = True
        self.start_time = time.time()
        self.update_timer()
        
    def stop_timer(self):
        """Stop the timer"""
        self.timer_active = False
        self.timer_label.config(text="00:00:00")
        
    def toggle_recording(self):
        """Toggle recording state"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start recording"""
        # Check timer settings
        timer_settings = self.settings.get_timer_settings()
        if timer_settings["enabled"] and timer_settings["start_delay"] > 0:
            # Start countdown
            self.status_label.config(text=f"Starting in {timer_settings['start_delay']} seconds...")
            self.root.after(timer_settings["start_delay"] * 1000, self._start_recording_impl)
        else:
            self._start_recording_impl()
            
    def _start_recording_impl(self):
        """Actual recording start implementation"""
        try:
            self.recorder.start_recording(
                format_type=self.format_var.get(),
                fps=int(self.fps_var.get()),
                quality=self.quality_var.get()
            )
            
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Recording in progress...")
            self.start_timer()  # Start timer when recording begins
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.recording = False
            self.record_button.config(text="Start Recording")
            
    def stop_recording(self):
        """Stop recording and save"""
        self.recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Stopping recording...")
        self.stop_timer()  # Stop timer when recording ends
        
        try:
            # Stop video recording
            file_path = self.recorder.stop_recording()
            if file_path:
                # Show file path and upload
                self.show_file_path(file_path)
                self.status_label.config(text="Uploading recording...")
                share_url = self.uploader.get_share_url(file_path)
                
                if share_url and not share_url.startswith("Error"):
                    self.show_url(share_url)
                    self.status_label.config(text="Recording saved and uploaded successfully!")
                else:
                    error_msg = share_url if share_url else "Unknown upload error"
                    self.status_label.config(text=f"Upload failed: {error_msg}")
            else:
                self.status_label.config(text="Error: No recording found")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            
    def show_file_path(self, file_path):
        """Show file path as clickable link"""
        self.current_file_path = file_path
        self.recordings_listbox.insert(tk.END, file_path)
        
    def open_recording(self, event=None):
        """Open the selected recording's location"""
        selected_index = self.recordings_listbox.curselection()
        if selected_index:
            file_path = self.recordings_listbox.get(selected_index)
            if os.path.exists(file_path):
                # Open file location in explorer and select the file
                os.system(f'explorer /select,"{file_path}"')
                
    def open_url(self, event=None):
        """Open the selected URL in browser"""
        selected_index = self.uploads_listbox.curselection()
        if selected_index:
            url = self.uploads_listbox.get(selected_index)
            webbrowser.open(url)
            
    def open_recordings_folder(self):
        """Open the recordings folder in explorer"""
        folder_path = os.path.dirname(self.current_file_path)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
            
    def show_url(self, url):
        """Show URL and copy button"""
        self.current_url = url
        
        # Show URL frame if not already visible
        if not self.url_frame.winfo_ismapped():
            self.url_frame.pack(fill="x", padx=5, pady=5)
            
        # Update URL label with clickable link
        self.url_label.config(
            text=f"Click to open: {url}",
            foreground="light blue",
            cursor="hand2"
        )
        self.url_label.pack(side="left", fill="x", expand=True)
        
        # Show copy button
        self.copy_button.pack(side="right", padx=5)
        
        # Add URL to recent uploads list with clickable style
        self.uploads_listbox.insert(0, url)  # Add at the top of the list
        if self.uploads_listbox.size() > 10:  # Keep only last 10 uploads
            self.uploads_listbox.delete(10, tk.END)
        
        # Auto copy URL to clipboard
        self.copy_url()
        self.status_label.config(text="URL copied to clipboard! Click the link to open in browser.")
            
    def copy_url(self):
        """Copy URL to clipboard"""
        if hasattr(self, 'current_url'):
            pyperclip.copy(self.current_url)
            self.status_label.config(text="URL copied to clipboard!")
            
    def update_fps_options(self):
        """Update FPS options based on format selection"""
        if self.format_var.get() == "video":
            self.fps_frame.pack(fill=X, pady=(0, 10))
            self.update_format_selection()
        else:
            self.fps_frame.pack_forget()
            self.update_format_selection()
            
    def update_format_selection(self):
        """Update UI based on format selection"""
        if self.format_var.get() == "video":
            self.uploads_frame.pack_forget()
            self.recordings_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
        else:
            self.recordings_frame.pack_forget()
            self.uploads_frame.pack(fill=BOTH, expand=YES, pady=(0, 10))
            
    def update_recordings_list(self):
        """Update the list of recent recordings"""
        # Clear current list
        self.recordings_listbox.delete(0, tk.END)
        
        # Get desktop path
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Look for recordings in desktop
        for file in os.listdir(desktop):
            if file.endswith(('.mp4', '.gif')):
                file_path = os.path.join(desktop, file)
                self.recordings_listbox.insert(tk.END, file_path)
                
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.root)
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
        
        # Reload settings
        self.settings.load_settings()
        self.setup_hotkeys()
        
    def toggle_pause(self):
        """Toggle pause state"""
        if self.recording:
            if self.paused:
                self.recorder.resume_recording()
                self.paused = False
                self.status_label.config(text="Recording in progress...")
            else:
                self.recorder.pause_recording()
                self.paused = True
                self.status_label.config(text="Recording paused")
            
    def run(self):
        # Check API status when starting
        self.root.after(1000, self.update_api_status)  # Check after 1 second
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenRecorderApp()
    app.run() 