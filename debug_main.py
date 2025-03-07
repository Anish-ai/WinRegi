#!/usr/bin/env python3
"""
WinRegi - AI-Powered Windows Registry Manager
Debug version with enhanced error handling and logging
"""
import sys
import os
import ctypes
import traceback
import time
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from src.ui.main_window import MainWindow

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("winregi_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WinRegi")

# Add exception hook to catch unhandled exceptions
def exception_hook(exctype, value, tb):
    """
    Global exception handler to log unhandled exceptions
    """
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Unhandled exception: {error_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

def is_admin():
    """Check if the application is running with administrator privileges
    
    Returns:
        True if running as administrator, False otherwise
    """
    try:
        if sys.platform == 'win32':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return False
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
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
    except Exception as e:
        logger.error(f"Error running as admin: {e}")
        traceback.print_exc()
        return False

def show_splash_screen():
    """Show splash screen while loading the application
    
    Returns:
        Splash screen object
    """
    try:
        splash_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "splash.png")
        
        # Check if splash image exists, use a blank one if not
        if not os.path.exists(splash_image):
            logger.warning(f"Splash image not found at {splash_image}")
            # Create a simple pixmap
            pixmap = QPixmap(500, 300)
            pixmap.fill(Qt.white)
        else:
            pixmap = QPixmap(splash_image)
        
        splash = QSplashScreen(pixmap)
        
        # Add version text
        splash.showMessage("Loading WinRegi v1.0.0 (Debug Mode)...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        splash.show()
        
        return splash
    except Exception as e:
        logger.error(f"Error creating splash screen: {e}")
        # Return dummy splash screen that can be .finish()'ed without error
        pixmap = QPixmap(1, 1)
        return QSplashScreen(pixmap)

def main():
    """Initialize and run the WinRegi application"""
    logger.info("Starting WinRegi in debug mode")
    
    # Request admin privileges on Windows
    if sys.platform == 'win32' and not is_admin():
        logger.info("Not running as admin, attempting to elevate privileges")
        # Try to restart as administrator
        if run_as_admin():
            # Elevation was requested, close this instance
            logger.info("Elevation requested, closing this instance")
            sys.exit(0)
    
    # Set up environment
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Add error handling for database initialization
    try:
        from src.database.db_manager import DatabaseManager
        logger.info("Pre-initializing database...")
        db_manager = DatabaseManager()
        db_manager.connect()
        db_manager.initialize_database()
        db_manager.disconnect()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        traceback.print_exc()
    
    # Create application
    logger.info("Creating QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName("WinRegi")
    app.setOrganizationName("WinRegi")
    
    # Show splash screen
    logger.info("Showing splash screen")
    splash = show_splash_screen()
    
    # Make sure the splash screen is visible for at least 1 second
    start_time = time.time()
    
    # Check for administrator privileges
    admin_status = is_admin()
    logger.info(f"Admin status: {admin_status}")
    
    # Create main window
    try:
        logger.info("Creating main window")
        window = MainWindow(is_admin=admin_status)
        logger.info("Main window created successfully")
    except Exception as e:
        logger.critical(f"Error creating main window: {e}")
        traceback.print_exc()
        if splash:
            splash.close()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Fatal Error")
        msg_box.setText("Failed to initialize application")
        msg_box.setDetailedText(f"Error: {str(e)}\n\n{traceback.format_exc()}")
        msg_box.exec_()
        sys.exit(1)
    
    # Patch search functionality with error handling
    try:
        from PyQt5.QtCore import pyqtSlot
        
        # Patch the on_search method in SearchPage to catch exceptions
        original_on_search = window.search_page.on_search
        
        @pyqtSlot(str)
        def patched_on_search(query):
            try:
                logger.info(f"Search requested: '{query}'")
                original_on_search(query)
                logger.info("Search completed successfully")
            except Exception as e:
                logger.error(f"Error during search: {e}")
                traceback.print_exc()
                # Show error message
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Search Error")
                msg_box.setText(f"An error occurred while searching: {str(e)}")
                msg_box.setDetailedText(traceback.format_exc())
                msg_box.exec_()
        
        # Replace the method
        window.search_page.on_search = patched_on_search
        logger.info("Search method patched with error handling")
    except Exception as e:
        logger.error(f"Failed to patch search method: {e}")
    
    # Ensure minimum splash time and then show main window
    def show_main():
        try:
            elapsed = time.time() - start_time
            if elapsed < 1.0:
                QTimer.singleShot(int((1.0 - elapsed) * 1000), show_main)
            else:
                logger.info("Showing main window")
                window.show()
                splash.finish(window)
                
                # Show admin status notification if needed
                if not admin_status:
                    logger.info("Showing limited privileges notification")
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
        except Exception as e:
            logger.error(f"Error in show_main: {e}")
            traceback.print_exc()
    
    # Start the show_main chain
    QTimer.singleShot(0, show_main)
    
    logger.info("Entering main event loop")
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}")
        traceback.print_exc()
        
        # Show error dialog
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Fatal Error")
        msg_box.setText("A fatal error occurred when starting the application")
        msg_box.setDetailedText(f"Error: {str(e)}\n\n{traceback.format_exc()}")
        msg_box.exec_()
        
        sys.exit(1)