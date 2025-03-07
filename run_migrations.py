#!/usr/bin/env python3
"""
Run database migrations for WinRegi
This script runs all pending migrations
"""
import importlib.util
import sys
from pathlib import Path

def load_module(file_path):
    """Load a Python module from file path"""
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_migrations():
    """Run all migrations"""
    print("WinRegi Migration Runner")
    print("=======================")
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print(f"No migrations directory found at {migrations_dir}")
        return False
    
    # Get all Python files
    migration_files = sorted(migrations_dir.glob("*.py"))
    
    if not migration_files:
        print("No migration files found.")
        return True
    
    print(f"Found {len(migration_files)} migration file(s).")
    
    # Run all migrations in order
    success = True
    for migration_file in migration_files:
        print(f"\nRunning migration: {migration_file.name}")
        try:
            migration_module = load_module(migration_file)
            if hasattr(migration_module, 'migrate_database'):
                migration_module.migrate_database()
            else:
                print(f"WARNING: Migration file {migration_file.name} has no migrate_database function!")
                success = False
        except Exception as e:
            print(f"ERROR: Failed to run migration {migration_file.name}: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    if run_migrations():
        print("\nAll migrations completed successfully!")
        sys.exit(0)
    else:
        print("\nSome migrations failed. See errors above.")
        sys.exit(1)