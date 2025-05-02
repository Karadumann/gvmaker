# GV Maker - Screen Recorder

A simple and efficient screen recorder that allows you to record your screen as video or GIF.

## Features

- Record any screen area as Video or GIF
- Choose output format and quality directly from the main screen
- Save recordings to Desktop (in a 'Screen Recordings' folder)
- Clickable links: open saved file location or uploaded URL with one click
- Share recordings via ImgBB (URL auto-copied to clipboard)
- Easy-to-use, modern dark themed interface
- Hotkey support (F8: Start/Stop, F9: Pause/Resume)
- Compact, responsive window

## Installation (Development)

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

## Usage (Development)

1. Run the application:
```bash
gvmaker
```

2. Configure your ImgBB API key from the main screen or settings dialog.

3. Use the following hotkeys:
- F8: Start/Stop recording
- F9: Pause/Resume recording

## Usage (Windows Executable)

1. Build the project with PyInstaller (or use the provided `.exe` in the `dist` folder).
2. Copy the entire `dist` folder to the target PC.
3. Run `GVMaker.exe`.
4. Enter your ImgBB API key when prompted (for sharing/uploading). Recording works without API key, but upload requires it.
5. All dependencies are bundled, but if you see DLL errors, install the latest [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

## Main Screen Overview

- **Output Format & Quality:** Select before each recording.
- **Start/Stop/Pause:** Control recording with buttons or hotkeys.
- **Recording saved to:** Click the path to open the folder.
- **Share Recording:** Uploads to ImgBB, copies URL to clipboard, and shows a clickable link.
- **Compact UI:** No unnecessary empty space.


## Troubleshooting

- **API key errors:** Make sure you enter a valid ImgBB API key in the app.
- **DLL errors:** Install Visual C++ Redistributable (see above).
- **No recording saved:** Make sure you select a region and do not pause before stopping for too long.
- **Upload fails:** Check your API key and internet connection.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 

## API Keys and Credentials Setup

To upload to Google Drive, YouTube, or Dropbox with GV Maker, each user must add their own API credentials.

### For Google Drive and YouTube (credentials.json)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and sign in with your Google account.
2. Create a new project or select an existing one.
3. In "APIs & Services" > "Library":
   - Enable **Google Drive API** and **YouTube Data API v3**.
4. Go to "APIs & Services" > "Credentials".
5. Click "Create Credentials" > "OAuth client ID".
   - Application type: Desktop app
   - Give it a name and create.
6. Download the generated `credentials.json` file.
7. Place this file in the main application folder (the gvmaker directory).

> **Note:** The first time you upload, you will be asked to sign in with your Google account. This is a one-time process; subsequent uploads will use the saved credentials.

### For Dropbox Access Token

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps).
2. Click "Create App" to make a new app.
   - Choose "Scoped access" and either "Full dropbox" or "App folder".
3. In the app settings, generate an access token.
4. Enter this token in the app settings window (or paste it when prompted during your first upload).

### Adding Credentials to the App

- For Google Drive/YouTube: Place the `credentials.json` file in the main folder.
- For Dropbox: Enter your access token in the app settings.

---

If you have any issues or need help with these steps, please contact us!
