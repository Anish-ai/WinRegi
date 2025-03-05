"""
Database manager for WinRegi application
Handles database connections, queries, and data management
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from .schema import SCHEMA, DEFAULT_CATEGORIES, DEFAULT_ACCESS_METHODS, SAMPLE_SETTINGS, SAMPLE_ACTIONS

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
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cursor = None
        
    def initialize_database(self) -> None:
        """Create database schema and populate with initial data"""
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
            
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all setting categories
        
        Returns:
            List of category dictionaries
        """
        if not self.conn:
            self.connect()
            
        self.cursor.execute("SELECT id, name, description, icon_path FROM categories")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_settings_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get all settings in a specific category
        
        Args:
            category_id: ID of the category to filter by
            
        Returns:
            List of setting dictionaries
        """
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
    
    def get_setting_by_id(self, setting_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific setting
        
        Args:
            setting_id: ID of the setting to retrieve
            
        Returns:
            Dictionary containing setting details or None if not found
        """
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
    
    def get_actions_for_setting(self, setting_id: int) -> List[Dict[str, Any]]:
        """Get all available actions for a specific setting
        
        Args:
            setting_id: ID of the setting
            
        Returns:
            List of action dictionaries
        """
        if not self.conn:
            self.connect()
            
        self.cursor.execute("""
            SELECT id, setting_id, name, description, action_type, action_value, is_default
            FROM setting_actions
            WHERE setting_id = ?
        """, (setting_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_settings(self, query: str) -> List[Dict[str, Any]]:
        """Search for settings matching the given query
        
        Args:
            query: Search string
            
        Returns:
            List of matching setting dictionaries
        """
        if not self.conn:
            self.connect()
            
        # Simple search implementation using SQL LIKE
        # In a real application, this would be replaced with the AI search engine
        search_terms = query.lower().split()
        results = []
        
        for term in search_terms:
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
        
        return results
    
    def log_search_query(self, query: str) -> None:
        """Log a search query to the history
        
        Args:
            query: The search query to log
        """
        if not self.conn:
            self.connect()
            
        self.cursor.execute(
            "INSERT INTO search_history (query) VALUES (?)",
            (query,)
        )
        self.conn.commit()
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of search history dictionaries
        """
        if not self.conn:
            self.connect()
            
        self.cursor.execute("""
            SELECT id, query, timestamp
            FROM search_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]