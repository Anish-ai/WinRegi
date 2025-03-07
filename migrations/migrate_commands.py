#!/usr/bin/env python3
"""
Database migration script for WinRegi
Adds category_id and tags columns to custom_commands table
"""
import os
import sqlite3
import sys
from pathlib import Path

def get_db_path():
    """Get database path"""
    # Use the same path logic as the main application
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(f"Creating data directory: {data_dir}")
        data_dir.mkdir(exist_ok=True)
    
    return str(data_dir / "winregi.db")

def migrate_database():
    """Perform database migration"""
    db_path = get_db_path()
    
    print(f"Migrating database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist. Nothing to migrate.")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("PRAGMA table_info(custom_commands)")
        columns = {column[1] for column in cursor.fetchall()}
        
        if 'category_id' in columns and 'tags' in columns:
            print("Migration already applied. Nothing to do.")
            conn.close()
            return
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Create a temporary table with the new structure
        print("Creating temporary table...")
        cursor.execute("""
            CREATE TABLE custom_commands_new (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                command_type TEXT NOT NULL,
                command_value TEXT NOT NULL,
                category_id INTEGER,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # Copy existing data
        print("Copying existing data...")
        cursor.execute("""
            INSERT INTO custom_commands_new (id, name, description, command_type, command_value, created_at, last_used)
            SELECT id, name, description, command_type, command_value, created_at, last_used
            FROM custom_commands
        """)
        
        # Drop the old table
        print("Replacing old table...")
        cursor.execute("DROP TABLE custom_commands")
        
        # Rename the new table
        cursor.execute("ALTER TABLE custom_commands_new RENAME TO custom_commands")
        
        # Commit transaction
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("WinRegi Database Migration Tool")
    print("==============================")
    
    success = migrate_database()
    
    if success:
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1)