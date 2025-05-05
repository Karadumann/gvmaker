import requests
import webbrowser
import os
import sys
import threading
from packaging import version
from src import __version__

GITHUB_REPO = "Karadumann/gvmaker"

LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def check_for_update():
    try:
        response = requests.get(LATEST_RELEASE_API, timeout=5)
        response.raise_for_status()
        data = response.json()
        latest = data["tag_name"].lstrip("v")
        download_url = None
        for asset in data.get("assets", []):
            if asset["name"].endswith(".exe"):
                download_url = asset["browser_download_url"]
                break
        if version.parse(latest) > version.parse(__version__):
            return latest, data["html_url"], download_url
        return None, None, None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None, None, None


def prompt_update_if_available():
    latest, url, download_url = check_for_update()
    if latest:
        print(f"New version {latest} is available! Download: {url}")
        # Show GUI popup in a separate thread to avoid blocking
        threading.Thread(target=show_update_popup, args=(latest, url, download_url), daemon=True).start()
    else:
        print("You are using the latest version.")


def show_update_popup(latest, url, download_url):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide main window
        msg = f"A new version ({latest}) is available!\n\nWould you like to download it now?"
        if messagebox.askyesno("Update Available", msg):
            if download_url:
                # Download and launch installer
                download_and_run_installer(download_url)
            else:
                webbrowser.open(url)
        root.destroy()
    except Exception as e:
        print(f"Popup failed: {e}")
        # Fallback: open in browser
        webbrowser.open(url)


def download_and_run_installer(download_url):
    import tempfile
    import shutil
    import requests
    from tkinter import messagebox
    try:
        local_filename = download_url.split("/")[-1]
        temp_dir = tempfile.gettempdir()
        local_path = os.path.join(temp_dir, local_filename)
        print(f"Downloading update to {local_path} ...")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        print("Download complete.")
        messagebox.showinfo("Update", f"Download complete. The installer will now run. Please follow the setup instructions.")
        # Launch the installer
        os.startfile(local_path)
        # Optionally, exit the current app
        sys.exit(0)
    except Exception as e:
        print(f"Failed to download or run installer: {e}")
        messagebox.showerror("Update Error", f"Failed to download or run installer. Please download manually.\n{download_url}")
        webbrowser.open(download_url) 