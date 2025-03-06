#!/usr/bin/env python3
"""
Build script for packaging WinRegi as a Windows executable using PyInstaller
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create resources structure
    os.makedirs("resources/icons", exist_ok=True)
    
    # Create a splash screen if it doesn't exist
    if not os.path.exists("resources/splash.png"):
        print("Creating placeholder splash screen...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image with white background
            width, height = 600, 300
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            
            # Draw on the image
            draw = ImageDraw.Draw(image)
            
            # Try to use a nice font if available
            try:
                if platform.system() == "Windows":
                    font = ImageFont.truetype("arial.ttf", 36)
                else:
                    font = ImageFont.truetype("FreeSans.ttf", 36)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Draw title
            draw.text((width//2, height//2 - 50), "WinRegi", fill=(56, 224, 120), anchor="mm", font=font)
            
            # Draw subtitle
            try:
                if platform.system() == "Windows":
                    subtitle_font = ImageFont.truetype("arial.ttf", 20)
                else:
                    subtitle_font = ImageFont.truetype("FreeSans.ttf", 20)
            except:
                subtitle_font = ImageFont.load_default()
                
            draw.text((width//2, height//2 + 20), "AI-Powered Windows Registry Manager", fill=(100, 100, 100), anchor="mm", font=subtitle_font)
            
            # Save the image
            image.save("resources/splash.png")
            print("Splash screen created successfully.")
        except Exception as e:
            print(f"Failed to create splash screen: {e}")
            print("Continuing without splash screen...")
    
    # Define PyInstaller command
    pyinstaller_args = [
        "pyinstaller",
        "--name=WinRegi",
        "--windowed",  # No console window
        "--icon=resources/icons/app.ico" if os.path.exists("resources/icons/app.ico") else None,
        "--add-data=resources;resources",  # Include resources folder
        "--hidden-import=sqlite3",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Overwrite output directory
        "main.py"
    ]
    
    # Remove None arguments
    pyinstaller_args = [arg for arg in pyinstaller_args if arg is not None]
    
    # Run PyInstaller
    print("Building executable with PyInstaller...")
    subprocess.check_call(pyinstaller_args)
    
    # Create output directories
    dist_dir = Path("dist/WinRegi")
    data_dir = dist_dir / "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Copy additional files
    print("Copying additional files...")
    
    # Copy documentation files
    for doc_file in ["README.md", "LICENSE", "INSTALL.md"]:
        if os.path.exists(doc_file):
            shutil.copy(doc_file, dist_dir)
    
    print("Build completed successfully!")
    print(f"Executable is available at: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    build_executable()