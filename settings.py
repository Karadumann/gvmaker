import json
import os
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        self.default_settings = {
            "shortcuts": {
                "start_stop": "f8",
                "pause": "f9"
            },
            "output": {
                "save_location": "desktop",
                "filename_prefix": "screen_recording"
            },
            "timer": {
                "enabled": False,
                "start_delay": 0,
                "stop_after": 0
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load settings from file or create default"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_settings.copy()
        return self.default_settings.copy()
        
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
            
    def get_shortcuts(self):
        """Get all shortcuts"""
        return self.settings["shortcuts"]
        
    def update_shortcuts(self, shortcuts):
        """Update shortcuts"""
        self.settings["shortcuts"].update(shortcuts)
        
    def get_output_settings(self):
        """Get output settings"""
        return self.settings["output"]
        
    def update_output_settings(self, output_settings):
        """Update output settings"""
        self.settings["output"].update(output_settings)
        
    def get_timer_settings(self):
        """Get timer settings"""
        return self.settings["timer"]
        
    def update_timer_settings(self, enabled=None, start_delay=None, stop_after=None):
        """Update timer settings"""
        if enabled is not None:
            self.settings["timer"]["enabled"] = enabled
        if start_delay is not None:
            self.settings["timer"]["start_delay"] = start_delay
        if stop_after is not None:
            self.settings["timer"]["stop_after"] = stop_after 