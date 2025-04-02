import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()

class MediaUploader:
    def __init__(self):
        self.imgbb_api_key = os.getenv('IMGBB_API_KEY')
        if not self.imgbb_api_key:
            print("Warning: IMGBB_API_KEY not found in environment variables")
        self.upload_url = "https://api.imgbb.com/1/upload"

    def upload_file(self, file_path):
        """
        Upload a file to ImgBB
        :param file_path: Path to the file to upload
        :return: dict with upload response
        """
        try:
            # Read file as binary and encode as base64
            with open(file_path, 'rb') as file:
                file_data = file.read()
                encoded_data = base64.b64encode(file_data)
                
                payload = {
                    'key': self.imgbb_api_key,
                    'image': encoded_data
                }
                
                response = requests.post(self.upload_url, data=payload)
                response.raise_for_status()
                
                return {
                    'success': True,
                    'data': response.json()
                }
        except Exception as e:
            print(f"Upload error: {str(e)}")  # Debug print
            return {
                'success': False,
                'error': str(e)
            }

    def get_share_url(self, file_path):
        """
        Upload file and return shareable URL
        :param file_path: Path to the file to upload
        :return: Shareable URL or error message
        """
        if not self.imgbb_api_key:
            return "Error: IMGBB_API_KEY not found. Please set it in your .env file"
            
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        result = self.upload_file(file_path)
        
        if result['success']:
            try:
                return result['data']['data']['url']
            except KeyError:
                return f"Error: Unexpected API response format: {result['data']}"
        else:
            return f"Error uploading file: {result['error']}" 