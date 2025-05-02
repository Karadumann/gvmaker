import platform

def notify(title: str, message: str):
    if platform.system() == "Windows":
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5, threaded=True, icon_path=None)
            return
        except Exception:
            pass  
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="GV Maker",
            timeout=5
        )
    except Exception:
        pass 