"""
Media uploader module for handling file uploads to external services.
"""

import os
import requests
from typing import Optional
from ..settings.settings_manager import SettingsManager

class MediaUploader:
    """
    Handles media file uploads to external services.
    """
    
    def __init__(self, settings_manager: SettingsManager):
        """
        Initialize the uploader.
        
        Args:
            settings_manager: Settings manager instance
        """
        self.settings_manager = settings_manager
        
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to the configured service.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            URL of the uploaded file or None if upload failed
        """
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            try:
                import tkinter.messagebox as mb
                mb.showerror("API Key", "No API key configured. Please set your API key in settings.")
            except Exception:
                pass
            return None
            
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    'https://api.imgbb.com/1/upload',
                    data={'key': api_key},
                    files={'image': f}
                )
                
            if response.status_code == 200:
                return response.json()['data']['url']
            else:
                try:
                    import tkinter.messagebox as mb
                    mb.showerror("Upload Failed", f"Upload failed: {response.text}")
                except Exception:
                    pass
                return None
                
        except Exception as e:
            try:
                import tkinter.messagebox as mb
                mb.showerror("Upload Error", f"Error uploading file: {str(e)}")
            except Exception:
                pass
            return None
            
    def upload_recording(self, recording_path: str) -> Optional[str]:
        """
        Upload a recording file.
        
        Args:
            recording_path: Path to the recording file
            
        Returns:
            URL of the uploaded recording or None if upload failed
        """
        if not os.path.exists(recording_path):
            try:
                import tkinter.messagebox as mb
                mb.showerror("File Not Found", f"File not found: {recording_path}")
            except Exception:
                pass
            return None
            
        return self.upload_file(recording_path) 