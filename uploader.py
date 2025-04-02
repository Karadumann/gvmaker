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
            # Check file size (ImgBB limit is 32MB)
            file_size = os.path.getsize(file_path)
            if file_size > 32 * 1024 * 1024:  # 32MB in bytes
                return {
                    'success': False,
                    'error': f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds 32MB limit"
                }
            
            # Read file as binary and encode as base64
            with open(file_path, 'rb') as file:
                file_data = file.read()
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                
                payload = {
                    'key': self.imgbb_api_key,
                    'image': encoded_data
                }
                
                print(f"Uploading file: {file_path}")  # Debug print
                print(f"File size: {file_size / 1024 / 1024:.1f}MB")  # Debug print
                print(f"API Key present: {'Yes' if self.imgbb_api_key else 'No'}")  # Debug print
                
                response = requests.post(self.upload_url, data=payload)
                
                # Print response for debugging
                print(f"Response status: {response.status_code}")  # Debug print
                print(f"Response content: {response.text[:200]}...")  # Debug print
                
                response.raise_for_status()
                
                return {
                    'success': True,
                    'data': response.json()
                }
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(error_msg)  # Debug print
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            print(error_msg)  # Debug print
            return {
                'success': False,
                'error': error_msg
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
            
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.gif']:  # Only allow GIF files
            return f"Error: File type {ext} not supported. Only GIF files are allowed."
            
        result = self.upload_file(file_path)
        
        if result['success']:
            try:
                return result['data']['data']['url']
            except KeyError:
                error_msg = f"Error: Unexpected API response format: {result['data']}"
                print(error_msg)  # Debug print
                return error_msg
        else:
            return f"Error uploading file: {result['error']}" 