#!/usr/bin/env python3
"""
Pre-startup checks and initialization for WinRegi
This runs before the main application to ensure everything is set up
"""
import os
import sys
import subprocess
from pathlib import Path

def initialize_app():
    """Run initialization tasks"""
    # Get application directory
    app_dir = Path(__file__).parent
    
    # Create data directory if it doesn't exist
    data_dir = app_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Run migrations if available
    run_migrations_script = app_dir / "run_migrations.py"
    if run_migrations_script.exists():
        print("Running database migrations...")
        try:
            result = subprocess.run(
                [sys.executable, str(run_migrations_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("WARNING: Database migrations failed:")
                print(result.stderr)
            else:
                print("Database migrations completed successfully.")
        except Exception as e:
            print(f"Error running migrations: {e}")
    
    return True

if __name__ == "__main__":
    print("WinRegi Pre-Startup")
    print("==================")
    
    if initialize_app():
        print("Initialization complete.")
        sys.exit(0)
    else:
        print("Initialization failed!")
        sys.exit(1)