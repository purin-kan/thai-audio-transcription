"""
Setup module for Thai Audio Transcription
Handles one-time configuration like FFmpeg PATH detection
"""

import os
import subprocess


def setup_ffmpeg_path():
    """
    Locate and add FFmpeg to the system PATH if not already there.
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        # Check if ffmpeg is already available
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Try common FFmpeg installation paths
    common_paths = [
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
        os.path.expanduser(r"~\AppData\Local\ffmpeg\bin"),
        # WinGet installation paths
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin"),
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links"),
    ]
    
    for path in common_paths:
        ffmpeg_exe = os.path.join(path, "ffmpeg.exe")
        if os.path.exists(ffmpeg_exe):
            # Add to PATH
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
            return True
    
    return False


def initialize():
    """
    Run all one-time setup tasks.
    Call this once at the start of the application.
    """
    print("🔧 Initializing setup...\n")
    
    # Setup FFmpeg
    if not setup_ffmpeg_path():
        print("⚠️ Warning: FFmpeg not found in PATH.")
        print("   Download from: https://ffmpeg.org/download.html")
        print("   Or install via: winget install ffmpeg\n")
    else:
        print("✅ FFmpeg found and configured\n")
