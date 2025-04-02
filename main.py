import tkinter as tk
from tkinter import ttk, simpledialog
from screen_recorder import ScreenRecorder
import os
from dotenv import load_dotenv, set_key
from uploader import MediaUploader
import threading
import time
import webbrowser
import pyperclip
import requests

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
        version = ttk.Label(info_frame, text="Version 1.0.0")
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
        self.root = tk.Tk()
        self.root.title("Screen Recorder")
        self.root.minsize(500, 350)  # Minimum window size
        
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Add mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Check and get API key
        self.check_api_key()
        
        # Initialize components
        self.screen_recorder = ScreenRecorder()
        self.media_uploader = MediaUploader()
        self.is_recording = False
        
        self.setup_ui()
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
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
                
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change API Key", command=self.change_api_key)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
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
            
    def show_about(self):
        """Show about dialog"""
        AboutDialog(self.root)
        
    def setup_ui(self):
        # Setup menu
        self.setup_menu()
        
        # API Status indicator
        self.api_status_label = ttk.Label(self.scrollable_frame, text="⬤ Checking API...", foreground="gray")
        self.api_status_label.pack(pady=5)
        
        # Format selection
        format_frame = ttk.LabelFrame(self.scrollable_frame, text="Format", padding="5")
        format_frame.pack(fill="x", padx=5, pady=5)
        
        self.format_var = tk.StringVar(value="video")
        ttk.Radiobutton(format_frame, text="Video", variable=self.format_var, value="video").pack(side="left", padx=5)
        ttk.Radiobutton(format_frame, text="GIF", variable=self.format_var, value="gif").pack(side="left", padx=5)
        
        # FPS selection
        fps_frame = ttk.LabelFrame(self.scrollable_frame, text="FPS", padding="5")
        fps_frame.pack(fill="x", padx=5, pady=5)
        
        self.fps_var = tk.StringVar(value="30")
        ttk.Entry(fps_frame, textvariable=self.fps_var, width=10).pack(side="left", padx=5)
        ttk.Label(fps_frame, text="(default: 30)").pack(side="left", padx=5)
        
        # Quality selection
        quality_frame = ttk.LabelFrame(self.scrollable_frame, text="Quality", padding="5")
        quality_frame.pack(fill="x", padx=5, pady=5)
        
        self.quality_var = tk.StringVar(value="high")
        ttk.Radiobutton(quality_frame, text="High", variable=self.quality_var, value="high").pack(side="left", padx=5)
        ttk.Radiobutton(quality_frame, text="Medium", variable=self.quality_var, value="medium").pack(side="left", padx=5)
        ttk.Radiobutton(quality_frame, text="Low", variable=self.quality_var, value="low").pack(side="left", padx=5)
        
        # Record button
        self.record_button = ttk.Button(self.scrollable_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(pady=20)
        
        # Status label
        self.status_label = ttk.Label(self.scrollable_frame, text="Ready to record")
        self.status_label.pack(pady=10)
        
        # File path frame (created but hidden initially)
        self.file_path_frame = ttk.Frame(self.scrollable_frame)
        self.file_path_label = ttk.Label(
            self.file_path_frame, 
            text="", 
            foreground="blue", 
            cursor="hand2"
        )
        self.file_path_label.pack(side="left", padx=5)
        self.file_path_label.bind("<Button-1>", self.open_file_location)
        
        self.open_folder_button = ttk.Button(
            self.file_path_frame,
            text="Open Folder",
            command=self.open_recordings_folder
        )
        self.open_folder_button.pack(side="left", padx=5)
        
        # URL frame
        self.url_frame = ttk.Frame(self.scrollable_frame)
        
        # URL label
        self.url_label = ttk.Label(self.url_frame, text="", foreground="blue", cursor="hand2")
        self.url_label.pack(side="left", padx=5)
        self.url_label.bind("<Button-1>", self.open_url)
        
        # Copy button
        self.copy_button = ttk.Button(self.url_frame, text="Copy URL", command=self.copy_url)
        self.copy_button.pack(side="left", padx=5)
        
        # Hide frames initially
        self.file_path_frame.pack_forget()
        self.url_frame.pack_forget()
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.record_button.config(text="Stop Recording")
        self.status_label.config(text="Select area to record...")
        self.file_path_frame.pack_forget()  # Hide file path frame when starting new recording
        
        # Start recording in a separate thread
        threading.Thread(target=self.record_screen).start()
        
    def record_screen(self):
        try:
            self.screen_recorder.start_recording(
                format_type=self.format_var.get(),
                fps=int(self.fps_var.get()),
                quality=self.quality_var.get()
            )
            self.status_label.config(text="Recording in progress...")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.is_recording = False
            self.record_button.config(text="Start Recording")
            
    def stop_recording(self):
        self.is_recording = False
        self.record_button.config(text="Start Recording")
        self.status_label.config(text="Stopping recording...")
        
        try:
            file_path = self.screen_recorder.stop_recording()
            if file_path:
                # Show file path as clickable link
                self.show_file_path(file_path)
                
                # Upload the file
                self.status_label.config(text="Uploading recording...")
                share_url = self.media_uploader.get_share_url(file_path)
                
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
        self.file_path_label.config(text=f"Click to open: {file_path}")
        self.file_path_frame.pack(fill="x", padx=5, pady=5)
        
        # Ensure the new content is visible
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)  # Scroll to bottom
        
    def open_file_location(self, event=None):
        """Open the file location in explorer"""
        if hasattr(self, 'current_file_path') and os.path.exists(self.current_file_path):
            # Open file in explorer and select it
            os.system(f'explorer /select,"{self.current_file_path}"')
            
    def open_recordings_folder(self):
        """Open the recordings folder in explorer"""
        folder_path = os.path.dirname(self.current_file_path)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
            
    def show_url(self, url):
        """Show URL and copy button"""
        self.current_url = url
        self.url_label.config(text=f"Click to open: {url}")
        self.url_frame.pack(fill="x", padx=5, pady=5)
        self.copy_button.pack(side="left", padx=5)
        # Auto copy URL
        self.copy_url()
            
    def open_url(self, event):
        """Open URL in default browser"""
        if hasattr(self, 'current_url'):
            webbrowser.open(self.current_url)
            
    def copy_url(self):
        """Copy URL to clipboard"""
        if hasattr(self, 'current_url'):
            pyperclip.copy(self.current_url)
            self.status_label.config(text="URL copied to clipboard!")
            
    def run(self):
        # Check API status when starting
        self.root.after(1000, self.update_api_status)  # Check after 1 second
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenRecorderApp()
    app.run() 