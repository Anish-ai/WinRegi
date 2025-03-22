#!/usr/bin/env python3
"""
Database migration script for WinRegi
Updates the schema to use PowerShell commands for all actions
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
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check if settings table has powershell_get_command column
        cursor.execute("PRAGMA table_info(settings)")
        columns = {column[1] for column in cursor.fetchall()}
        
        if 'powershell_get_command' not in columns:
            print("Adding powershell_get_command column to settings table...")
            cursor.execute("ALTER TABLE settings ADD COLUMN powershell_get_command TEXT")
        
        # Check if setting_actions table has the right structure
        cursor.execute("PRAGMA table_info(setting_actions)")
        columns = {column[1] for column in cursor.fetchall()}
        
        if 'action_type' in columns and 'action_value' in columns and 'powershell_command' not in columns:
            print("Updating setting_actions table structure...")
            
            # Create a temporary table with the new structure
            cursor.execute("""
                CREATE TABLE setting_actions_new (
                    id INTEGER PRIMARY KEY,
                    setting_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    powershell_command TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    FOREIGN KEY (setting_id) REFERENCES settings(id)
                )
            """)
            
            # Copy data from old table to new table, converting action_type and action_value to powershell_command
            cursor.execute("""
                SELECT id, setting_id, name, description, action_type, action_value, is_default
                FROM setting_actions
            """)
            
            for row in cursor.fetchall():
                id, setting_id, name, description, action_type, action_value, is_default = row
                
                # Convert registry actions to PowerShell commands
                if action_type == 'registry':
                    if '=' in action_value:
                        path, value = action_value.split('=', 1)
                        powershell_command = f"Set-ItemProperty -Path '{path.replace('HKCU\\', 'HKCU:\\')}' -Name 'Value' -Value {value}"
                    else:
                        powershell_command = action_value
                else:
                    # For other types, just use the action_value as is
                    powershell_command = action_value
                
                # Insert into new table
                cursor.execute("""
                    INSERT INTO setting_actions_new (id, setting_id, name, description, powershell_command, is_default)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id, setting_id, name, description, powershell_command, is_default))
            
            # Drop old table and rename new table
            cursor.execute("DROP TABLE setting_actions")
            cursor.execute("ALTER TABLE setting_actions_new RENAME TO setting_actions")
        
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