# GV Maker - Screen Recorder

A simple and efficient screen recorder that allows you to record your screen as video or GIF.

## Features

- Record screen areas as Video or GIF
- Adjust FPS and quality settings
- Save recordings to Desktop
- Share recordings via ImgBB
- Easy-to-use interface
- Hotkey support
- Modern dark theme

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Karadumann/gvmaker.git
cd gvmaker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

1. Run the application:
```bash
gvmaker
```

2. Configure your ImgBB API key in the settings menu.

3. Use the following hotkeys:
- F8: Start/Stop recording
- F9: Pause/Resume recording

## Development

### Setup Development Environment

1. Install development dependencies:
```bash
pip install -e ".[dev]"
```

2. Run tests:
```bash
python -m unittest discover tests
```

3. Format code:
```bash
black .
```

4. Lint code:
```bash
pylint src tests
```

### Project Structure

```
gvmaker/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── ui.py
│   ├── recording.py
│   ├── settings_manager.py
│   ├── screen_recorder.py
│   ├── uploader.py
│   ├── settings.py
│   ├── settings_dialog.py
│   ├── drawing_overlay.py
│   └── mouse_overlay.py
├── tests/
│   └── test_recording.py
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 