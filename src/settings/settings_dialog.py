"""
Settings dialog module for configuring application settings.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Any
from .settings_manager import SettingsManager
import os
import webbrowser

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
        self.geometry("400x700")
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
        
        # Google credentials.json
        cred_frame = ttk.LabelFrame(main_frame, text="Google Drive/YouTube credentials.json", padding="5")
        cred_frame.pack(fill=X, pady=5)
        cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
        self.cred_status_var = tk.StringVar()
        if os.path.exists(cred_path):
            self.cred_status_var.set("credentials.json is present.")
        else:
            self.cred_status_var.set("credentials.json is missing!")
        cred_status_label = ttk.Label(cred_frame, textvariable=self.cred_status_var, style="info.TLabel")
        cred_status_label.pack(fill=X, padx=5, pady=2)
        cred_button = ttk.Button(
            cred_frame,
            text="Select credentials.json",
            command=self._select_credentials,
            style="info.TButton"
        )
        cred_button.pack(pady=5)

        # Dropbox Access Token
        dropbox_frame = ttk.LabelFrame(main_frame, text="Dropbox Access Token", padding="5")
        dropbox_frame.pack(fill=X, pady=5)
        self.dropbox_token_var = tk.StringVar(value=self._load_dropbox_token())
        dropbox_entry = ttk.Entry(dropbox_frame, textvariable=self.dropbox_token_var, show="*")
        dropbox_entry.pack(fill=X, padx=5, pady=5)
        dropbox_save_button = ttk.Button(
            dropbox_frame,
            text="Save Token",
            command=self._save_dropbox_token,
            style="info.TButton"
        )
        dropbox_save_button.pack(pady=5)
        
        # API Guide Button
        guide_button = ttk.Button(
            main_frame,
            text="API Guide",
            command=self._show_api_guide,
            style="secondary.TButton"
        )
        guide_button.pack(fill=X, pady=5)
        
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

    def _select_credentials(self):
        from tkinter import filedialog, messagebox
        import shutil, os
        file_path = filedialog.askopenfilename(
            title="Select credentials.json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            dest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "credentials.json")
            try:
                shutil.copy(file_path, dest_path)
                self.cred_status_var.set("credentials.json is present.")
                messagebox.showinfo("Credentials", "credentials.json copied successfully.")
            except Exception as e:
                messagebox.showerror("Credentials", f"Failed to copy: {str(e)}")

    def _load_dropbox_token(self):
        import os
        token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dropbox_token.txt")
        if os.path.exists(token_path):
            with open(token_path, "r") as f:
                return f.read().strip()
        return ""

    def _save_dropbox_token(self):
        from tkinter import messagebox
        import os
        token = self.dropbox_token_var.get().strip()
        token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dropbox_token.txt")
        try:
            with open(token_path, "w") as f:
                f.write(token)
            messagebox.showinfo("Dropbox Token", "Token saved successfully.")
        except Exception as e:
            messagebox.showerror("Dropbox Token", f"Failed to save token: {str(e)}")

    def _show_api_guide(self):
        import webbrowser
        import tkinter as tk
        guide_text = (
            "How to get API credentials for Google Drive, YouTube, and Dropbox:\n\n"
            "Google Drive & YouTube (credentials.json):\n"
            "1. Go to https://console.cloud.google.com/ and sign in.\n"
            "2. Create a new project or select an existing one.\n"
            "3. In 'APIs & Services' > 'Library', enable both Google Drive API and YouTube Data API v3.\n"
            "4. Go to 'APIs & Services' > 'Credentials'.\n"
            "5. Click 'Create Credentials' > 'OAuth client ID'.\n"
            "   - Application type: Desktop app\n"
            "   - Give it a name and create.\n"
            "6. Download the generated credentials.json file and place it in the main app folder.\n\n"
            "Dropbox Access Token:\n"
            "1. Go to https://www.dropbox.com/developers/apps.\n"
            "2. Click 'Create App' to make a new app.\n"
            "   - Choose 'Scoped access' and either 'Full dropbox' or 'App folder'.\n"
            "3. In the app settings, generate an access token.\n"
            "4. Enter this token in the app settings.\n"
        )
        win = tk.Toplevel(self)
        win.title("API Guide")
        win.geometry("600x500")
        text = tk.Text(win, wrap="word", font=("Arial", 11), padx=10, pady=10)
        text.insert("1.0", guide_text)
        text.config(state="disabled", cursor="arrow", bg=win.cget("bg"))
        text.pack(fill="both", expand=True)

        def tag_url(url):
            idx = text.search(url, "1.0", tk.END)
            if idx:
                end = f"{idx}+{len(url)}c"
                text.config(state="normal")
                text.tag_add(url, idx, end)
                text.tag_config(url, foreground="#1E90FF", underline=1)
                text.tag_bind(url, "<Button-1>", lambda e, u=url: webbrowser.open(u))
                text.config(state="disabled")

        tag_url("https://console.cloud.google.com/")
        tag_url("https://www.dropbox.com/developers/apps")

        close_btn = tk.Button(win, text="Close", command=win.destroy)
        close_btn.pack(pady=8) 