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
            
    def upload_recording(self, recording_path: str, platform: str = "ImgBB") -> Optional[str]:
        """
        Upload a recording file.
        
        Args:
            recording_path: Path to the recording file
            platform: Platform to upload to
            
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
        if platform == "ImgBB":
            return self.upload_file(recording_path)
        elif platform == "YouTube":
            return self.upload_youtube(recording_path)
        elif platform == "Google Drive":
            return self.upload_gdrive(recording_path)
        elif platform == "Dropbox":
            return self.upload_dropbox(recording_path)
        else:
            try:
                import tkinter.messagebox as mb
                mb.showerror("Upload Platform", f"Unknown platform: {platform}")
            except Exception:
                pass
            return None

    def upload_youtube(self, file_path: str) -> Optional[str]:
        """
        Upload a video to YouTube using YouTube Data API v3.
        Returns the video URL if successful, otherwise None.
        """
        try:
            import os
            import pickle
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import tkinter.messagebox as mb
            from google.auth.transport.requests import Request

            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            CLIENT_SECRETS_FILE = "credentials.json"
            API_SERVICE_NAME = "youtube"
            API_VERSION = "v3"
            CREDENTIALS_PICKLE = "youtube_token.pickle"

            # Authenticate user
            creds = None
            if os.path.exists(CREDENTIALS_PICKLE):
                with open(CREDENTIALS_PICKLE, "rb") as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(CREDENTIALS_PICKLE, "wb") as token:
                    pickle.dump(creds, token)

            youtube = build(API_SERVICE_NAME, API_VERSION, credentials=creds)

            body = {
                "snippet": {
                    "title": os.path.basename(file_path),
                    "description": "Uploaded by GV Maker",
                    "tags": ["screen recording", "GV Maker"],
                    "categoryId": "22"  
                },
                "status": {
                    "privacyStatus": "unlisted"
                }
            }
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
            if "id" in response:
                video_url = f"https://youtu.be/{response['id']}"
                mb.showinfo("YouTube Upload", f"Upload successful!\n{video_url}")
                return video_url
            else:
                mb.showerror("YouTube Upload", "Upload failed.")
                return None
        except Exception as e:
            try:
                import tkinter.messagebox as mb
                mb.showerror("YouTube Upload", f"Error: {str(e)}")
            except Exception:
                pass
            return None

    def upload_gdrive(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Google Drive and return a shareable link.
        """
        try:
            import os
            import pickle
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            import tkinter.messagebox as mb

            SCOPES = ["https://www.googleapis.com/auth/drive.file"]
            CLIENT_SECRETS_FILE = "credentials.json"
            CREDENTIALS_PICKLE = "gdrive_token.pickle"

            creds = None
            if os.path.exists(CREDENTIALS_PICKLE):
                with open(CREDENTIALS_PICKLE, "rb") as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(CREDENTIALS_PICKLE, "wb") as token:
                    pickle.dump(creds, token)

            service = build("drive", "v3", credentials=creds)
            file_metadata = {"name": os.path.basename(file_path)}
            media = MediaFileUpload(file_path, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            file_id = file.get("id")
            # Make file shareable
            service.permissions().create(
                fileId=file_id,
                body={"role": "reader", "type": "anyone"},
            ).execute()
            link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            mb.showinfo("Google Drive Upload", f"Upload successful!\n{link}")
            return link
        except Exception as e:
            try:
                import tkinter.messagebox as mb
                mb.showerror("Google Drive Upload", f"Error: {str(e)}")
            except Exception:
                pass
            return None

    def upload_dropbox(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Dropbox and return a shareable link.
        """
        try:
            import dropbox
            import tkinter.simpledialog as sd
            import tkinter.messagebox as mb
            import os
            token_path = "dropbox_token.txt"
            if os.path.exists(token_path):
                with open(token_path, "r") as f:
                    access_token = f.read().strip()
            else:
                access_token = sd.askstring("Dropbox Token", "Enter your Dropbox access token:")
                if not access_token:
                    mb.showerror("Dropbox Upload", "No access token provided.")
                    return None
                with open(token_path, "w") as f:
                    f.write(access_token)
            dbx = dropbox.Dropbox(access_token)
            dest_path = f"/{os.path.basename(file_path)}"
            with open(file_path, "rb") as f:
                dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dest_path)
            mb.showinfo("Dropbox Upload", f"Upload successful!\n{shared_link_metadata.url}")
            return shared_link_metadata.url
        except Exception as e:
            try:
                import tkinter.messagebox as mb
                mb.showerror("Dropbox Upload", f"Error: {str(e)}")
            except Exception:
                pass
            return None 