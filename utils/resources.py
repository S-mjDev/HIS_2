import os
import sys
from tkinter import PhotoImage


def get_resource_path(relative_path):
    """Get absolute path to resource, supporting PyInstaller bundles.
    
    Returns path relative to project root, not the calling module.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Normal Python execution - go up to project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(current_dir)  # Go up from utils/ to project root
    
    return os.path.join(base_path, relative_path)


def set_window_icon(window, icon_file="qphn.ico"):
    """Set window icon from ico or jpg file, with fallback support."""
    try:
        icon_path = get_resource_path(icon_file)
        if not os.path.exists(icon_path):
            # Try with .ico extension if file not found
            if not icon_file.endswith('.ico'):
                icon_path = get_resource_path(icon_file.replace('.jpg', '.ico'))
        
        if icon_path.endswith('.ico'):
            window.iconbitmap(icon_path)
        else:
            # For JPG or other formats, use iconphoto
            icon = PhotoImage(file=icon_path)
            window.iconphoto(True, icon)
    except Exception as e:
        # Silent fail - window just won't have custom icon
        pass


def load_image(image_file):
    """Load an image file and return PhotoImage object. Returns None if fails."""
    try:
        image_path = get_resource_path(image_file)
        if os.path.exists(image_path):
            return PhotoImage(file=image_path)
    except Exception:
        pass
    return None
