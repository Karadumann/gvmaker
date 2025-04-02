# Screen Recorder & GIF Maker

A modern, fast, and efficient screen recording and GIF creation tool.

## Features

- Screen region selection
- High-quality video recording
- GIF creation
- Automatic upload to ImgBB/Imgur
- Secure sharing with private URLs
- Modern UI with dark/light theme
- Keyboard shortcuts
- System tray integration

## Requirements

- Python 3.11+
- FFmpeg (for video recording)
- Node.js (for frontend)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/screen-recorder.git
cd screen-recorder
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Create a `.env` file in the root directory and add your API keys:
```
IMGBB_API_KEY=your_imgbb_api_key
```

## Usage

1. Start the backend server:
```bash
python main.py
```

2. Start the frontend:
```bash
cd frontend
npm start
```

## License

MIT License 