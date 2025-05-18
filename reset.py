import os
import shutil
import sys
import traceback
import stat
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def reset_application():
    """Reset the WinRegi application by clearing all data and cache files"""
    try:
        # Get the current directory
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        data_dir = current_dir / 'data'
        
        # Remove data directory if it exists
        if data_dir.exists() and data_dir.is_dir():
            try:
                shutil.rmtree(data_dir, onerror=remove_readonly)
                logging.info(f"Data directory removed: {data_dir}")
            except Exception as e:
                logging.error(f"Failed to remove data directory: {str(e)}")
                logging.error(traceback.format_exc())
                return False
        else:
            logging.info("No data directory found.")
            
        # Create empty data directory
        os.makedirs(data_dir, exist_ok=True)
        logging.info(f"Created empty data directory: {data_dir}")
        
        logging.info("\nReset completed successfully! The application will start with fresh data on next launch.")
        
    except Exception as e:
        logging.error(f"Error during reset: {str(e)}")
        logging.error(traceback.format_exc())
        return False
    
    return True

if __name__ == "__main__":
    print("\nWinRegi Reset Utility")
    print("===================\n")
    
    confirm = input("This will delete all data in the current directory. Continue? (y/n): ")
    
    if confirm.lower() == 'y':
        success = reset_application()
        if success:
            print("\nYou can now restart the application for a fresh experience.")
    else:
        print("Reset cancelled.")