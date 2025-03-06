#!/usr/bin/env python3
"""
WinRegi - AI-Powered Windows Registry Manager
Main entry point for the application
"""
import sys
import os
import ctypes
import traceback
import time
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from src.ui.main_window import MainWindow

def is_admin():
    """Check if the application is running with administrator privileges
    
    Returns:
        True if running as administrator, False otherwise
    """
    try:
        if sys.platform == 'win32':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return False
    except:
        return False

def run_as_admin():
    """Re-run the application with administrator privileges
    
    Returns:
        True if the elevation was requested, False otherwise
    """
    if sys.platform != 'win32':
        return False
        
    try:
        if getattr(sys, 'frozen', False):
            # If the application is frozen (executable)
            executable = sys.executable
        else:
            # If running as a script
            executable = sys.executable
            args = [sys.executable] + sys.argv
        
        # Trigger UAC prompt to elevate
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, " ".join(sys.argv), None, 1
        )
        
        # ShellExecuteW returns a value greater than 32 if successful
        return ret > 32
    except:
        traceback.print_exc()
        return False

def show_splash_screen():
    """Show splash screen while loading the application
    
    Returns:
        Splash screen object
    """
    splash_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "splash.png")
    
    # Check if splash image exists, use a blank one if not
    if not os.path.exists(splash_image):
        # Create a simple pixmap
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.white)
    else:
        pixmap = QPixmap(splash_image)
    
    splash = QSplashScreen(pixmap)
    
    # Add version text
    splash.showMessage("Loading WinRegi v1.0.0...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    splash.show()
    
    return splash

def main():
    """Initialize and run the WinRegi application"""
    # Request admin privileges on Windows
    if sys.platform == 'win32' and not is_admin():
        # Try to restart as administrator
        if run_as_admin():
            # Elevation was requested, close this instance
            sys.exit(0)
    
    # Set up environment
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("WinRegi")
    app.setOrganizationName("WinRegi")
    
    # Show splash screen
    splash = show_splash_screen()
    
    # Make sure the splash screen is visible for at least 1 second
    start_time = time.time()
    
    # Check for administrator privileges
    admin_status = is_admin()
    
    # Create main window
    window = MainWindow(is_admin=admin_status)
    
    # Ensure minimum splash time and then show main window
    def show_main():
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            QTimer.singleShot(int((1.0 - elapsed) * 1000), show_main)
        else:
            window.show()
            splash.finish(window)
            
            # Show admin status notification if needed
            if not admin_status:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("Limited Functionality")
                msg_box.setText("WinRegi is running with limited privileges.")
                msg_box.setInformativeText(
                    "Some operations that modify system settings will require administrator privileges. "
                    "Restart the application as administrator for full functionality."
                )
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()
    
    # Start the show_main chain
    QTimer.singleShot(0, show_main)
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()