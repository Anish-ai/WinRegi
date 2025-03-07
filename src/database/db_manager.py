"""
Database manager for WinRegi application
Handles database connections, queries, and data management
"""
import os
import sqlite3
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from .schema import SCHEMA, DEFAULT_CATEGORIES, DEFAULT_ACCESS_METHODS, SAMPLE_SETTINGS, SAMPLE_ACTIONS, SAMPLE_COMMANDS

class DatabaseManager:
    """Manages database operations for the WinRegi application"""
    
    def __init__(self, db_path: str = None):
        """Initialize the database manager with the specified database path
        
        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            # Use default path - create data directory if it doesn't exist
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "winregi.db")
        else:
            self.db_path = db_path
        
        self.conn = None
        self.cursor = None
        
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            # Re-raise to allow caller to handle or fail gracefully
            raise
        
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                print(f"Error disconnecting from database: {e}")
        self.conn = None
        self.cursor = None
        
    def initialize_database(self) -> None:
        """Create database schema and populate with initial data"""
        try:
            if not self.conn:
                self.connect()
                
            # Create tables
            self.cursor.executescript(SCHEMA)
            self.conn.commit()
            
            # Populate categories if empty
            self.cursor.execute("SELECT COUNT(*) FROM categories")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(
                    "INSERT INTO categories (id, name, description, icon_path) VALUES (?, ?, ?, ?)",
                    DEFAULT_CATEGORIES
                )
                self.conn.commit()
            
            # Populate access methods if empty
            self.cursor.execute("SELECT COUNT(*) FROM access_methods")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(
                    "INSERT INTO access_methods (id, name, description) VALUES (?, ?, ?)",
                    DEFAULT_ACCESS_METHODS
                )
                self.conn.commit()
                
            # Populate sample settings if empty
            self.cursor.execute("SELECT COUNT(*) FROM settings")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(
                    """INSERT INTO settings 
                       (id, name, description, category_id, access_method_id, 
                        registry_path, powershell_command, control_panel_path, 
                        ms_settings_path, group_policy_path, tags, keywords)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    SAMPLE_SETTINGS
                )
                self.conn.commit()
                
            # Populate sample actions if empty
            self.cursor.execute("SELECT COUNT(*) FROM setting_actions")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(
                    """INSERT INTO setting_actions 
                       (id, setting_id, name, description, action_type, action_value, is_default)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    SAMPLE_ACTIONS
                )
                self.conn.commit()
                
            # Populate sample commands if empty
            self.cursor.execute("SELECT COUNT(*) FROM custom_commands")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(
                    """INSERT INTO custom_commands 
                       (id, name, description, command_type, command_value, category_id, tags)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    SAMPLE_COMMANDS
                )
                self.conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            # If we have a connection, try to roll back any failed transaction
            if self.conn:
                try:
                    self.conn.rollback()
                except:
                    pass
            raise
            
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all setting categories
        
        Returns:
            List of category dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("SELECT id, name, description, icon_path FROM categories")
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_settings_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get all settings in a specific category
        
        Args:
            category_id: ID of the category to filter by
            
        Returns:
            List of setting dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT s.id, s.name, s.description, s.category_id, c.name as category_name,
                       s.access_method_id, a.name as access_method_name
                FROM settings s
                JOIN categories c ON s.category_id = c.id
                JOIN access_methods a ON s.access_method_id = a.id
                WHERE s.category_id = ?
            """, (category_id,))
            
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting settings by category: {e}")
            return []
    
    def get_setting_by_id(self, setting_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific setting
        
        Args:
            setting_id: ID of the setting to retrieve
            
        Returns:
            Dictionary containing setting details or None if not found
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT s.*, c.name as category_name, a.name as access_method_name
                FROM settings s
                JOIN categories c ON s.category_id = c.id
                JOIN access_methods a ON s.access_method_id = a.id
                WHERE s.id = ?
            """, (setting_id,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting setting by ID: {e}")
            return None
    
    def get_actions_for_setting(self, setting_id: int) -> List[Dict[str, Any]]:
        """Get all available actions for a specific setting
        
        Args:
            setting_id: ID of the setting
            
        Returns:
            List of action dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT id, setting_id, name, description, action_type, action_value, is_default
                FROM setting_actions
                WHERE setting_id = ?
            """, (setting_id,))
            
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting actions for setting: {e}")
            return []
    
    def search_settings(self, query: str) -> List[Dict[str, Any]]:
        """Search for settings matching the given query
        
        Args:
            query: Search string
            
        Returns:
            List of matching setting dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            # Ensure database tables exist
            try:
                self.cursor.execute("SELECT COUNT(*) FROM settings")
            except sqlite3.OperationalError:
                print("Database tables not found, initializing database")
                self.initialize_database()
            
            # Simple search implementation using SQL LIKE
            # In a real application, this would be replaced with the AI search engine
            search_terms = query.lower().split()
            results = []
            
            # Return empty list if no search terms
            if not search_terms:
                return []
            
            for term in search_terms:
                try:
                    like_pattern = f"%{term}%"
                    self.cursor.execute("""
                        SELECT s.id, s.name, s.description, s.category_id, c.name as category_name,
                               s.access_method_id, a.name as access_method_name
                        FROM settings s
                        JOIN categories c ON s.category_id = c.id
                        JOIN access_methods a ON s.access_method_id = a.id
                        WHERE LOWER(s.name) LIKE ? 
                           OR LOWER(s.description) LIKE ? 
                           OR LOWER(s.tags) LIKE ? 
                           OR LOWER(s.keywords) LIKE ?
                    """, (like_pattern, like_pattern, like_pattern, like_pattern))
                    
                    for row in self.cursor.fetchall():
                        result = dict(row)
                        if result not in results:
                            results.append(result)
                except Exception as e:
                    print(f"Error searching with term '{term}': {e}")
                    # Continue with next term instead of failing
            
            return results
        except Exception as e:
            print(f"Error in search_settings: {e}")
            traceback.print_exc()
            return []
    
    def log_search_query(self, query: str) -> None:
        """Log a search query to the history
        
        Args:
            query: The search query to log
        """
        try:
            if not self.conn:
                self.connect()
                
            # Ensure the table exists
            try:
                self.cursor.execute("SELECT COUNT(*) FROM search_history")
            except sqlite3.OperationalError:
                # Table doesn't exist, initialize the database
                self.initialize_database()
                
            self.cursor.execute(
                "INSERT INTO search_history (query) VALUES (?)",
                (query,)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error logging search query: {e}")
            # Silently fail for logging errors - they're non-critical
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of search history dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT id, query, timestamp
                FROM search_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []
    
    # Custom Commands Management
    
    def get_all_commands(self) -> List[Dict[str, Any]]:
        """Get all custom commands
        
        Returns:
            List of command dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT c.id, c.name, c.description, c.command_type, c.command_value, 
                       c.category_id, cat.name as category_name, c.tags, c.created_at, c.last_used
                FROM custom_commands c
                LEFT JOIN categories cat ON c.category_id = cat.id
                ORDER BY c.name
            """)
            
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting commands: {e}")
            return []
    
    def get_command_by_id(self, command_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific command by ID
        
        Args:
            command_id: ID of the command to retrieve
            
        Returns:
            Dictionary containing command details or None if not found
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT c.id, c.name, c.description, c.command_type, c.command_value, 
                       c.category_id, cat.name as category_name, c.tags, c.created_at, c.last_used
                FROM custom_commands c
                LEFT JOIN categories cat ON c.category_id = cat.id
                WHERE c.id = ?
            """, (command_id,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting command by ID: {e}")
            return None
    
    def add_command(self, name: str, description: str, command_type: str, command_value: str, 
                  category_id: int = None, tags: str = None) -> int:
        """Add a new custom command
        
        Args:
            name: Command name
            description: Command description
            command_type: Type of command (system, powershell, etc.)
            command_value: Actual command to execute
            category_id: Category ID for the command (optional)
            tags: Comma-separated tags for better search (optional)
            
        Returns:
            ID of the newly added command
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                INSERT INTO custom_commands (name, description, command_type, command_value, category_id, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, command_type, command_value, category_id, tags))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding command: {e}")
            if self.conn:
                self.conn.rollback()
            return -1
    
    def update_command(self, command_id: int, name: str, description: str, command_type: str, 
                      command_value: str, category_id: int = None, tags: str = None) -> bool:
        """Update an existing custom command
        
        Args:
            command_id: ID of the command to update
            name: New command name
            description: New command description
            command_type: New command type
            command_value: New command value
            category_id: Category ID for the command (optional)
            tags: Comma-separated tags for better search (optional)
            
        Returns:
            True if the command was updated, False otherwise
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                UPDATE custom_commands
                SET name = ?, description = ?, command_type = ?, command_value = ?, 
                    category_id = ?, tags = ?
                WHERE id = ?
            """, (name, description, command_type, command_value, category_id, tags, command_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating command: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def delete_command(self, command_id: int) -> bool:
        """Delete a custom command
        
        Args:
            command_id: ID of the command to delete
            
        Returns:
            True if the command was deleted, False otherwise
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("DELETE FROM custom_commands WHERE id = ?", (command_id,))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting command: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def update_command_usage(self, command_id: int) -> bool:
        """Update the last used timestamp for a command
        
        Args:
            command_id: ID of the command that was used
            
        Returns:
            True if the timestamp was updated, False otherwise
        """
        try:
            if not self.conn:
                self.connect()
                
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("""
                UPDATE custom_commands
                SET last_used = ?
                WHERE id = ?
            """, (current_time, command_id))
            
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating command usage: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """Search for commands matching the given query
        
        Args:
            query: Search string
            
        Returns:
            List of matching command dictionaries
        """
        try:
            if not self.conn:
                self.connect()
                
            # Simple search implementation using SQL LIKE
            search_terms = query.lower().split()
            results = []
            
            # Return empty list if no search terms
            if not search_terms:
                return []
                
            for term in search_terms:
                try:
                    like_pattern = f"%{term}%"
                    self.cursor.execute("""
                        SELECT c.id, c.name, c.description, c.command_type, c.command_value, 
                               c.category_id, cat.name as category_name, c.tags, c.created_at, c.last_used
                        FROM custom_commands c
                        LEFT JOIN categories cat ON c.category_id = cat.id
                        WHERE LOWER(c.name) LIKE ? 
                           OR LOWER(c.description) LIKE ? 
                           OR LOWER(c.command_value) LIKE ?
                           OR LOWER(c.tags) LIKE ?
                           OR LOWER(cat.name) LIKE ?
                    """, (like_pattern, like_pattern, like_pattern, like_pattern, like_pattern))
                    
                    for row in self.cursor.fetchall():
                        result = dict(row)
                        if result not in results:
                            results.append(result)
                except Exception as e:
                    print(f"Error searching commands with term '{term}': {e}")
                    # Continue with next term instead of failing
            
            return results
        except Exception as e:
            print(f"Error in search_commands: {e}")
            return []
            
    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a category by its name
        
        Args:
            name: Category name
            
        Returns:
            Dictionary containing category details or None if not found
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                SELECT id, name, description, icon_path 
                FROM categories 
                WHERE LOWER(name) = LOWER(?)
            """, (name,))
            
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting category by name: {e}")
            return None
            
    def add_category(self, name: str, description: str = None, icon_path: str = None) -> int:
        """Add a new category
        
        Args:
            name: Category name
            description: Category description (optional)
            icon_path: Path to category icon (optional)
            
        Returns:
            ID of the newly added category
        """
        try:
            if not self.conn:
                self.connect()
                
            self.cursor.execute("""
                INSERT INTO categories (name, description, icon_path)
                VALUES (?, ?, ?)
            """, (name, description, icon_path))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error adding category: {e}")
            if self.conn:
                self.conn.rollback()
            return -1
    
    def get_commands_in_search_results(self, query: str) -> List[Dict[str, Any]]:
        """Get commands that match the search query for inclusion in search results
        
        Args:
            query: Search query
            
        Returns:
            List of matching command dictionaries with result_type='command'
        """
        try:
            commands = self.search_commands(query)
            for command in commands:
                command['result_type'] = 'command'
            return commands
        except Exception as e:
            print(f"Error getting commands in search results: {e}")
            return []