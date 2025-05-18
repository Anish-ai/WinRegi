#!/usr/bin/env python3
"""
WinRegi - AI-Powered Windows Registry Manager
Main entry point with hot reloading capability
"""
import sys
import os
import ctypes
import traceback
import time
import subprocess
import importlib
import threading
import argparse
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

# Try to import watchdog for hot reloading
try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Keep track of the main window instance for reloading
global_window = None
global_app = None

class ReloadSignaler(QObject):
    """Signal emitter for triggering UI reloads from file system events"""
    reload_signal = pyqtSignal()

# Create a global instance of the signaler
reload_signaler = ReloadSignaler()

def parse_arguments():
    """Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="WinRegi - Windows Registry Manager")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with hot reload")
    parser.add_argument("--no-admin", action="store_true", help="Skip admin elevation prompt")
    return parser.parse_args()

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

def run_as_admin(args):
    """Re-run the application with administrator privileges
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        True if the elevation was requested, False otherwise
    """
    if sys.platform != 'win32':
        return False
        
    try:
        # Build command line arguments for the elevated process
        cmd_args = []
        if args.dev:
            cmd_args.append("--dev")
        
        if getattr(sys, 'frozen', False):
            # If the application is frozen (executable)
            executable = sys.executable
            args_str = " ".join(cmd_args)
        else:
            # If running as a script
            executable = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            args_str = f"{script_path} {' '.join(cmd_args)}"
        
        # Trigger UAC prompt to elevate
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, args_str, None, 1
        )
        
        # ShellExecuteW returns a value greater than 32 if successful
        return ret > 32
    except:
        traceback.print_exc()
        return False

def show_splash_screen(args):
    """Show splash screen while loading the application
    
    Args:
        args: Parsed command line arguments
        
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
    status = "Development Mode" if args.dev else "v1.0.0"
    splash.showMessage(f"Loading WinRegi {status}...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    splash.show()
    
    return splash

def reload_ui():
    """Reload the UI components after code changes"""
    global global_window, global_app
    
    if global_window:
        print("Reloading UI components...")
        try:
            # Save the current window state and position
            geometry = global_window.geometry()
            
            # Reload the main window module
            # from src.ui import main_window
            # importlib.reload(main_window)
            # Reload all modules in the src directory and its subdirectories
            for module_name, module in list(sys.modules.items()):
                if module_name.startswith('src.') and hasattr(module, '__file__'):
                    try:
                        print(f"Reloading module: {module_name}")
                        importlib.reload(module)
                    except Exception as e:
                        print(f"Error reloading {module_name}: {e}")
            
            # Import main_window after reloading all modules
            from src.ui import main_window
            
            # Create a new main window instance
            old_window = global_window
            global_window = main_window.MainWindow(is_admin=is_admin())
            
            # Restore window geometry
            global_window.setGeometry(geometry)
            
            # Show the new window and close the old one
            global_window.show()
            old_window.close()
            
            print("UI reload completed successfully")
        except Exception as e:
            print(f"Error during UI reload: {e}")
            traceback.print_exc()
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Reload Error")
            msg_box.setText("An error occurred while reloading the UI.")
            msg_box.setInformativeText(f"Error: {str(e)}\n\nSome changes may require a full application restart.")
            msg_box.setDetailedText(traceback.format_exc())
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

def setup_file_watcher(directories):
    """Set up a file watcher to monitor code changes
    
    Args:
        directories: List of directories to watch for changes
    
    Returns:
        Observer instance or None if watchdog is not available
    """
    if not WATCHDOG_AVAILABLE:
        print("Warning: watchdog library not installed. Hot reload functionality is disabled.")
        return None
        
    class CodeChangeHandler(FileSystemEventHandler):
        """Watchdog handler that detects code changes"""
        def __init__(self):
            super().__init__()
            self.last_reload_time = time.time()
            self.cooldown = 1.0  # Cooldown period in seconds to avoid multiple reloads
            
        def on_modified(self, event):
            # Only reload for Python files
            if event.src_path.endswith('.py'):
                current_time = time.time()
                if current_time - self.last_reload_time > self.cooldown:
                    self.last_reload_time = current_time
                    print(f"Change detected in: {event.src_path}")
                    # Use the signaler to emit the reload signal
                    reload_signaler.reload_signal.emit()
    
    observer = Observer()
    handler = CodeChangeHandler()
    
    for directory in directories:
        if os.path.exists(directory):
            observer.schedule(handler, directory, recursive=True)
            print(f"Watching directory: {directory}")
    
    observer.start()
    return observer

def run_migrations():
    """Run database migrations if needed"""
    try:
        migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
        if os.path.exists(migrations_dir):
            # Run update_to_powershell.py migration
            powershell_migration = os.path.join(migrations_dir, "update_to_powershell.py")
            if os.path.exists(powershell_migration):
                print("Running PowerShell migration...")
                subprocess.run([sys.executable, powershell_migration], check=True)
                
            # Run fix_powershell_commands.py migration
            fix_commands_migration = os.path.join(migrations_dir, "fix_powershell_commands.py")
            if os.path.exists(fix_commands_migration):
                print("Running PowerShell command fixes...")
                subprocess.run([sys.executable, fix_commands_migration], check=True)
    except Exception as e:
        print(f"Error running migrations: {e}")

def main():
    """Initialize and run the WinRegi application with hot reload"""
    global global_window, global_app
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Request admin privileges on Windows if not in no-admin mode
    if sys.platform == 'win32' and not is_admin() and not args.no_admin:
        # Try to restart as administrator
        if run_as_admin(args):
            # Elevation was requested, close this instance
            sys.exit(0)
    
    # Run pre-startup checks and initialization
    pre_startup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pre_startup.py")
    if os.path.exists(pre_startup_script):
        try:
            subprocess.run([sys.executable, pre_startup_script], check=True)
        except subprocess.CalledProcessError:
            print("WARNING: Pre-startup initialization failed!")
        except Exception as e:
            print(f"Error running pre-startup: {e}")
    
    # Run database migrations
    run_migrations()
    
    # Set up environment
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    global_app = app
    app.setApplicationName("WinRegi")
    app.setOrganizationName("WinRegi")
    
    # Load custom stylesheet if available
    custom_style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "custom_styles.css")
    if os.path.exists(custom_style_path):
        try:
            with open(custom_style_path, 'r') as f:
                custom_style = f.read()
                app.setStyleSheet(custom_style)
        except Exception as e:
            print(f"Error loading custom stylesheet: {e}")
    
    # Show splash screen
    splash = show_splash_screen(args)
    
    # Make sure the splash screen is visible for at least 1 second
    start_time = time.time()
    
    # Check for administrator privileges
    admin_status = is_admin()
    
    # Set up file watcher for development mode
    observer = None
    if args.dev:
        # Check if watchdog is available
        if not WATCHDOG_AVAILABLE:
            print("WARNING: watchdog library not installed. To enable hot reload, install it with:")
            print("pip install watchdog")
        else:
            # Directories to watch
            base_dir = os.path.dirname(os.path.abspath(__file__))
            watch_dirs = [
                os.path.join(base_dir, "src"),
            ]
            observer = setup_file_watcher(watch_dirs)
            
            # Connect the reload signal
            reload_signaler.reload_signal.connect(reload_ui)
    
    # Import here to make reloading work properly
    from src.ui.main_window import MainWindow
    
    # Create main window
    global_window = MainWindow(is_admin=admin_status)
    
    # Ensure minimum splash time and then show main window
    def show_main():
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            QTimer.singleShot(int((1.0 - elapsed) * 1000), show_main)
        else:
            global_window.show()
            splash.finish(global_window)
            
            # Show privilege status notification
            show_status_notifications(admin_status, args)
    
    # Start the show_main chain
    QTimer.singleShot(0, show_main)
    
    # Run the application
    exit_code = app.exec_()
    
    # Clean up the observer if it exists
    if observer:
        observer.stop()
        observer.join()
    
    sys.exit(exit_code)

def show_status_notifications(admin_status, args):
    """Show status notifications about privileges and development mode
    
    Args:
        admin_status: Whether the application is running with admin privileges
        args: Parsed command line arguments
    """
    # Show admin status notification if needed
    if not admin_status and not args.no_admin:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Limited Functionality")
        msg_box.setText("WinRegi is running with limited privileges.")
        msg_box.setInformativeText(
            "Some operations that modify system settings will require administrator privileges.\n\n"
            "You can:\n"
            "1. Restart the application as administrator for full functionality\n"
            "2. Use the '--no-admin' flag to suppress this warning"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    # Show development mode notification
    if args.dev:
        reload_status = "enabled" if WATCHDOG_AVAILABLE else "disabled (install watchdog)"
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Development Mode")
        msg_box.setText(f"WinRegi is running in development mode with hot reload {reload_status}.")
        msg_box.setInformativeText(
            "UI components will automatically reload when Python files are modified.\n"
            "Note: Some changes may require a full application restart.\n\n"
            f"Admin privileges: {'Yes' if admin_status else 'No'}\n"
            f"To run without admin elevation, use: --dev --no-admin"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

if __name__ == "__main__":
    main()