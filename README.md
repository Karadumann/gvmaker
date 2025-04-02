# Screen Recorder & GIF Maker

A simple and efficient screen recording and GIF creation tool with automatic upload capability.

## Features

- Screen region selection with visual guide
- Video recording (MP4)
- GIF creation
- Automatic upload to ImgBB
- Automatic URL copying
- Saves recordings to Desktop
- Modern UI with easy controls
- Customizable FPS and quality settings
- Secure API key management

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

3. Select recording format (Video/GIF), FPS, and quality settings
4. Click "Start Recording"
5. Select the screen region you want to record
6. Click "Stop Recording" when done
7. The recording will be:
   - Saved to "Screen Recordings" folder on your Desktop
   - Automatically uploaded to ImgBB
   - URL will be copied to your clipboard

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