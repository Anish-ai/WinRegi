#!/usr/bin/env python3
"""
WinRegi - AI-Powered Windows Registry Manager
Main entry point for the application
"""
import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox
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

def main():
    """Initialize and run the WinRegi application"""
    # Set up environment
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("WinRegi")
    app.setOrganizationName("WinRegi")
    
    # Check for administrator privileges
    admin_status = is_admin()
    
    # Create and show main window
    window = MainWindow(is_admin=admin_status)
    window.show()
    
    # Show admin status notification
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
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()