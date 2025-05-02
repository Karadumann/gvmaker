"""
API key dialog module for configuring the ImgBB API key.
"""

import tkinter as tk
from tkinter import ttk, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser

class APIKeyDialog(simpledialog.Dialog):
    """
    Dialog for entering the ImgBB API key.
    """
    
    def body(self, master):
        """Create dialog body."""
        ttk.Label(master, text="Please enter your ImgBB API key:").grid(row=0, pady=5)
        link = ttk.Label(master, text="Click here to get an API key", foreground="blue", cursor="hand2")
        link.grid(row=1, pady=5)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://api.imgbb.com/"))
        self.api_key = ttk.Entry(master, width=50)
        self.api_key.grid(row=2, pady=10, padx=5)
        self.status_label = ttk.Label(master, text="", foreground="red")
        self.status_label.grid(row=3, pady=5)
        return self.api_key
        
    def validate(self):
        api_key = self.api_key.get()
        if not api_key:
            self.status_label.config(text="API key cannot be empty!")
            return 0
        # Basit doğrulama: uzunluk kontrolü (isteğe bağlı daha gelişmiş kontrol eklenebilir)
        if len(api_key) < 10:
            self.status_label.config(text="API key is too short!")
            return 0
        # Burada gerçek API doğrulaması yapılabilir (isteğe bağlı)
        self.status_label.config(text="")
        return 1

    def apply(self):
        """Get the entered API key."""
        self.result = self.api_key.get() 