# Screen Recorder & GIF Maker

A simple and efficient screen recording and GIF creation tool with automatic upload capability.

## Features

- Screen region selection with visual guide
- Video recording (MP4)
- GIF creation with optimized performance
- Automatic GIF upload to ImgBB
- Automatic URL copying
- Saves recordings to Desktop
- Modern dark theme UI
- Customizable FPS and quality settings
- Secure API key management
- Recording timer with start delay
- Pause/Resume recording (F9)
- Recent recordings history
- Recent uploads history with clickable links
- Keyboard shortcuts (F8 for start/stop)
- Multi-threaded processing for better performance

## Requirements

- Python 3.11+
- Windows 10/11

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Karadumann/gvmaker.git
cd gvmaker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. On first run, you'll be asked to enter your ImgBB API key
   - You can get a free API key from [ImgBB](https://api.imgbb.com/)
   - The API key will be securely stored in AppData/Local/ScreenRecorder
   - You can change the API key anytime from Settings menu

3. Select recording format:
   - Video (MP4): High-quality video recording
   - GIF: Optimized GIF with automatic upload

4. Configure settings:
   - FPS: 5-60 FPS options
   - Quality: Low/Medium/High
   - Start delay (optional)

5. Click "Start Recording" or press F8
6. Select the screen region you want to record
7. Use F9 to pause/resume recording
8. Click "Stop Recording" or press F8 again when done

For GIF recordings:
- File will be saved to Desktop
- Automatically uploaded to ImgBB
- URL will be copied to clipboard
- Link will appear in Recent Uploads

For Video recordings:
- File will be saved to Desktop
- Can be accessed from Recent Recordings list

## Performance Features

- Multi-threaded frame processing
- Optimized GIF creation
- Parallel frame conversion
- Memory-efficient operations
- Configurable quality settings

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller screen_recorder.spec
```

The executable will be created in the `dist` folder.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Author

- [Berk Karaduman](https://github.com/Karadumann)

## License

[MIT](LICENSE) 