"""
Settings manager module for handling application settings.
"""

import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key
import requests

class SettingsManager:
    """
    Manages application settings.
    """
    
    def __init__(self):
        self.settings_file = os.path.join(
            os.path.expanduser("~"),
            ".gvmaker",
            "settings.json"
        )
        self.settings = self._load_settings()
        load_dotenv()
        
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file or create default settings.
        
        Returns:
            Dictionary containing settings
        """
        default_settings = {
            "api_key": "",
            "output_format": "video",
            "fps": 30,
            "quality": "high",
            "output_dir": os.path.join(os.path.expanduser("~"), "Desktop", "Screen Recordings")
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Update with any missing default settings
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
            
        return default_settings
        
    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
        
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.save_settings()
        
    def get_api_key(self) -> Optional[str]:
        """Get the API key setting."""
        return self.get_setting("api_key")
        
    def set_api_key(self, api_key: str) -> None:
        """Set the API key setting."""
        self.set_setting("api_key", api_key)
        
    def get_output_format(self) -> str:
        """Get the output format setting."""
        return self.get_setting("output_format", "video")
        
    def set_output_format(self, format_type: str) -> None:
        """Set the output format setting."""
        self.set_setting("output_format", format_type)
        
    def get_fps(self) -> int:
        """Get the FPS setting."""
        return self.get_setting("fps", 30)
        
    def set_fps(self, fps: int) -> None:
        """Set the FPS setting."""
        self.set_setting("fps", fps)
        
    def get_quality(self) -> str:
        """Get the quality setting."""
        return self.get_setting("quality", "high")
        
    def set_quality(self, quality: str) -> None:
        """Set the quality setting."""
        self.set_setting("quality", quality)
        
    def get_output_dir(self) -> str:
        """Get the output directory setting."""
        return self.get_setting("output_dir")
        
    def set_output_dir(self, output_dir: str) -> None:
        """Set the output directory setting."""
        self.set_setting("output_dir", output_dir)
        
    def check_api_key(self):
        api_key = os.getenv('IMGBB_API_KEY')
        if not api_key:
            return False, "API key not found"
        return self.test_api_key(api_key)
        
    def change_api_key(self, new_key):
        if self.test_api_key(new_key)[0]:
            set_key('.env', 'IMGBB_API_KEY', new_key)
            return True, "API key updated successfully"
        return False, "Invalid API key"
        
    def test_api_key(self, api_key):
        try:
            response = requests.post(
                'https://api.imgbb.com/1/upload',
                data={'key': api_key},
                files={'image': ('test.txt', 'test')}
            )
            return response.status_code == 400, "API key is valid" if response.status_code == 400 else "Invalid API key"
        except Exception as e:
            return False, f"Error testing API key: {str(e)}" 