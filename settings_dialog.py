import tkinter as tk
from tkinter import ttk
import keyboard

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Settings")
        self.geometry("400x300")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.shortcuts_tab = self.create_shortcuts_tab()
        self.output_tab = self.create_output_tab()
        
        # Add tabs to notebook
        notebook.add(self.shortcuts_tab, text="Shortcuts")
        notebook.add(self.output_tab, text="Output")
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=10)
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def create_shortcuts_tab(self):
        """Create shortcuts settings tab"""
        frame = ttk.Frame(self, padding="10")
        
        # Get current shortcuts
        shortcuts = self.settings.get_shortcuts()
        
        # Start/Stop recording shortcut
        ttk.Label(frame, text="Start/Stop Recording:").grid(row=0, column=0, sticky=tk.W, pady=5)
        start_stop_entry = ttk.Entry(frame, width=20)
        start_stop_entry.insert(0, shortcuts["start_stop"])
        start_stop_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Pause shortcut
        ttk.Label(frame, text="Pause/Resume:").grid(row=1, column=0, sticky=tk.W, pady=5)
        pause_entry = ttk.Entry(frame, width=20)
        pause_entry.insert(0, shortcuts["pause"])
        pause_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Store entries for later use
        self.shortcut_entries = {
            "start_stop": start_stop_entry,
            "pause": pause_entry
        }
        
        return frame
        
    def create_output_tab(self):
        """Create output settings tab"""
        frame = ttk.Frame(self, padding="10")
        
        # Get current output settings
        output_settings = self.settings.get_output_settings()
        
        # Save location
        ttk.Label(frame, text="Save Location:").grid(row=0, column=0, sticky=tk.W, pady=5)
        location_var = tk.StringVar(value=output_settings["save_location"])
        location_combo = ttk.Combobox(frame, textvariable=location_var, values=["desktop", "documents", "downloads"], state="readonly")
        location_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Filename prefix
        ttk.Label(frame, text="Filename Prefix:").grid(row=1, column=0, sticky=tk.W, pady=5)
        prefix_entry = ttk.Entry(frame, width=30)
        prefix_entry.insert(0, output_settings["filename_prefix"])
        prefix_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Store entries for later use
        self.output_entries = {
            "save_location": location_var,
            "filename_prefix": prefix_entry
        }
        
        return frame
        
    def save_settings(self):
        """Save all settings"""
        try:
            # Save shortcuts
            shortcuts = {}
            for action, entry in self.shortcut_entries.items():
                key = entry.get().lower()
                try:
                    keyboard.parse_hotkey(key)
                    shortcuts[action] = key
                except:
                    tk.messagebox.showerror("Error", f"Invalid shortcut key: {key}")
                    return
                    
            self.settings.update_shortcuts(shortcuts)
            
            # Save output settings
            output_settings = {
                "save_location": self.output_entries["save_location"].get(),
                "filename_prefix": self.output_entries["filename_prefix"].get()
            }
            self.settings.update_output_settings(output_settings)
            
            self.destroy()
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save settings: {str(e)}") 