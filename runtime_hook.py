import os
import sys

def runtime_hook():
    if getattr(sys, 'frozen', False):
        os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']
        
        import cv2
        cv2.setNumThreads(1)
        
        # Disable debug logging
        import logging
        logging.getLogger().setLevel(logging.ERROR)
        
        # Optimize memory usage
        import gc
        gc.set_threshold(700, 10, 5)

def _():
    input("Press Enter to exit...")
    sys.exit(0)
