"""
Theme manager for WinRegi application
Handles application theming and styles
"""
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
import os
from pathlib import Path

class ThemeManager:
    """Manages application themes and styles"""
    
    def __init__(self, parent=None):
        """Initialize theme manager
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.current_theme = "light"
        
        # Get resource path
        self.resource_path = str(Path(__file__).parent.parent.parent / "resources")
        
        # Theme stylesheets
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }
    
    def _get_light_theme(self) -> str:
        """Get light theme stylesheet
        
        Returns:
            Light theme stylesheet
        """
        return """
        /* Main application */
        QMainWindow, QDialog {
            background-color: #f5f5f5;
            color: #333333;
        }
        
        /* Header */
        #app-header {
            background-color: #ffffff;
            border-bottom: 1px solid #dddddd;
        }
        
        #app-title {
            font-size: 24px;
            font-weight: bold;
            color: #2979ff;
        }
        
        #app-subtitle {
            color: #666666;
        }
        
        #admin-indicator {
            border-radius: 15px;
            color: #ffffff;
            font-weight: bold;
        }
        
        #admin-indicator[admin-status="admin"] {
            background-color: #4caf50;
        }
        
        #admin-indicator[admin-status="limited"] {
            background-color: #ff9800;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #dddddd;
            border-radius: 5px;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            padding: 8px 16px;
            margin-right: 2px;
            background-color: #eeeeee;
            border: 1px solid #dddddd;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
            color: #2979ff;
        }
        
        /* Search bar */
        QLineEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #2979ff;
        }
        
        #search-heading {
            color: #333333;
            margin-bottom: 10px;
        }
        
        #search-container {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 25px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
        }
        
        #search-input {
            font-size: 14px;
            color: #333333;
        }
        
        #search-button {
            background-color: #2979ff;
            color: white;
            border-radius: 18px;
            font-weight: bold;
        }
        
        #examples-container {
            margin-top: 5px;
        }
        
        .example-button {
            background-color: #f5f5f5;
            color: #555555;
            border: 1px solid #eeeeee;
            border-radius: 15px;
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .example-button:hover {
            background-color: #eeeeee;
            border-color: #dddddd;
        }
        
        /* Buttons */
        QPushButton {
            padding: 8px 16px;
            background-color: #2979ff;
            color: #ffffff;
            border: none;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #2962ff;
        }
        
        QPushButton:pressed {
            background-color: #1565c0;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
        }
        
        /* Theme button */
        #theme-button {
            padding: 4px;
            background-color: transparent;
            border-radius: 16px;
        }
        
        #theme-button:hover {
            background-color: #eeeeee;
        }
        
        /* Lists and Trees */
        QListWidget, QTreeWidget, QTableWidget {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 4px;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 4px;
            border-bottom: 1px solid #eeeeee;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #e3f2fd;
            color: #2979ff;
        }
        
        /* Scroll bars */
        QScrollBar:vertical {
            background-color: #f5f5f5;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #bbbbbb;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #999999;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Cards */
        .setting-card {
            background-color: #ffffff;
            border: 1px solid #eeeeee;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
        }
        
        .setting-card:hover {
            border: 1px solid #bbdefb;
            background-color: #f5f9ff;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        #setting-name {
            color: #333333;
        }
        
        #setting-description {
            color: #666666;
        }
        
        #category-container {
            background-color: #f5f9ff;
            border-radius: 13px;
        }
        
        #setting-category {
            color: #2979ff;
            font-weight: bold;
        }
        
        #category-badge {
            background-color: #f0f7ff;
            border-radius: 20px;
            border: 1px solid #e3f2fd;
        }
        
        /* Labels */
        .heading {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
        }
        
        .subheading {
            font-size: 14px;
            color: #666666;
        }
        
        /* Action buttons */
        .action-button {
            padding: 6px 12px;
            background-color: #f5f5f5;
            color: #333333;
            border: 1px solid #dddddd;
            border-radius: 4px;
        }
        
        .action-button:hover {
            background-color: #eeeeee;
            border: 1px solid #cccccc;
        }
        
        .primary-action {
            background-color: #2979ff;
            color: #ffffff;
            border: none;
        }
        
        .primary-action:hover {
            background-color: #2962ff;
            border: none;
        }
        
        .warning-action {
            background-color: #ff9800;
            color: #ffffff;
            border: none;
        }
        
        .warning-action:hover {
            background-color: #f57c00;
            border: none;
        }
        
        /* Theme buttons */
        #light-theme-button {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #dddddd;
            border-radius: 4px;
            font-weight: bold;
        }
        
        #light-theme-button:hover {
            background-color: #f5f5f5;
            border: 1px solid #cccccc;
        }
        
        #dark-theme-button {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            font-weight: bold;
        }
        
        #dark-theme-button:hover {
            background-color: #444444;
            border: 1px solid #666666;
        }
        
        /* Theme section */
        #theme-section {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #eeeeee;
        }
        """
    
    def _get_dark_theme(self) -> str:
        """Get dark theme stylesheet
        
        Returns:
            Dark theme stylesheet
        """
        return """
        /* Main application */
        QMainWindow, QDialog {
            background-color: #121212;
            color: #e0e0e0;
        }
        
        /* Header */
        #app-header {
            background-color: #1e1e1e;
            border-bottom: 1px solid #333333;
        }
        
        #app-title {
            font-size: 24px;
            font-weight: bold;
            color: #64b5f6;
        }
        
        #app-subtitle {
            color: #aaaaaa;
        }
        
        #admin-indicator {
            border-radius: 15px;
            color: #ffffff;
            font-weight: bold;
        }
        
        #admin-indicator[admin-status="admin"] {
            background-color: #43a047;
        }
        
        #admin-indicator[admin-status="limited"] {
            background-color: #ef6c00;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #2d2d2d;
            border-radius: 5px;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            padding: 8px 16px;
            margin-right: 2px;
            background-color: #262626;
            border: 1px solid #2d2d2d;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            color: #e0e0e0;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom-color: #1e1e1e;
            color: #64b5f6;
        }
        
        /* Search bar */
        QLineEdit {
            padding: 8px;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            background-color: #262626;
            color: #e0e0e0;
        }
        
        QLineEdit:focus {
            border: 1px solid #64b5f6;
        }
        
        #search-heading {
            color: #e0e0e0;
            margin-bottom: 10px;
        }
        
        #search-container {
            background-color: #262626;
            border: 1px solid #3d3d3d;
            border-radius: 25px;
            box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        #search-input {
            font-size: 14px;
            color: #e0e0e0;
        }
        
        #search-button {
            background-color: #1565c0;
            color: white;
            border-radius: 18px;
            font-weight: bold;
        }
        
        #examples-container {
            margin-top: 5px;
        }
        
        .example-button {
            background-color: #2d2d2d;
            color: #aaaaaa;
            border: 1px solid #3d3d3d;
            border-radius: 15px;
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .example-button:hover {
            background-color: #363636;
            border-color: #444444;
        }
        
        /* Buttons */
        QPushButton {
            padding: 8px 16px;
            background-color: #0d47a1;
            color: #ffffff;
            border: none;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #1565c0;
        }
        
        QPushButton:pressed {
            background-color: #0a3880;
        }
        
        QPushButton:disabled {
            background-color: #333333;
            color: #777777;
        }
        
        /* Theme button */
        #theme-button {
            padding: 4px;
            background-color: transparent;
            border-radius: 16px;
        }
        
        #theme-button:hover {
            background-color: #333333;
        }
        
        /* Lists and Trees */
        QListWidget, QTreeWidget, QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 4px;
            color: #e0e0e0;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 4px;
            border-bottom: 1px solid #2d2d2d;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #0d47a1;
            color: #ffffff;
        }
        
        /* Scroll bars */
        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #444444;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #555555;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Cards */
        .setting-card {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 12px;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.15);
        }
        
        .setting-card:hover {
            border: 1px solid #0d47a1;
            background-color: #222d40;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.25);
        }
        
        #setting-name {
            color: #e0e0e0;
        }
        
        #setting-description {
            color: #aaaaaa;
        }
        
        #category-container {
            background-color: #0d2b5c;
            border-radius: 13px;
        }
        
        #setting-category {
            color: #64b5f6;
            font-weight: bold;
        }
        
        #category-badge {
            background-color: #0d2b5c;
            border-radius: 20px;
            border: 1px solid #1565c0;
        }
        
        /* Labels */
        .heading {
            font-size: 18px;
            font-weight: bold;
            color: #e0e0e0;
        }
        
        .subheading {
            font-size: 14px;
            color: #aaaaaa;
        }
        
        /* Action buttons */
        .action-button {
            padding: 6px 12px;
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 4px;
        }
        
        .action-button:hover {
            background-color: #333333;
            border: 1px solid #444444;
        }
        
        .primary-action {
            background-color: #0d47a1;
            color: #ffffff;
            border: none;
        }
        
        .primary-action:hover {
            background-color: #1565c0;
            border: none;
        }
        
        .warning-action {
            background-color: #d84315;
            color: #ffffff;
            border: none;
        }
        
        .warning-action:hover {
            background-color: #bf360c;
            border: none;
        }
        
        /* Theme buttons */
        #light-theme-button {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #555555;
            border-radius: 4px;
            font-weight: bold;
        }
        
        #light-theme-button:hover {
            background-color: #eeeeee;
            border: 1px solid #666666;
        }
        
        #dark-theme-button {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border: 1px solid #333333;
            border-radius: 4px;
            font-weight: bold;
        }
        
        #dark-theme-button:hover {
            background-color: #262626;
            border: 1px solid #444444;
        }
        
        /* Theme section */
        #theme-section {
            background-color: #222222;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #333333;
        }
        """
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application
        
        Args:
            theme_name: Name of the theme to apply
        """
        if theme_name not in self.themes:
            return
        
        # Store current theme
        self.current_theme = theme_name
        
        # Apply stylesheet
        QApplication.instance().setStyleSheet(self.themes[theme_name])
        
        # Update theme button icon
        if self.parent:
            theme_button = self.parent.findChild(QPushButton, "theme-button")
            if theme_button:
                icon_name = "light_mode.png" if theme_name == "dark" else "dark_mode.png"
                icon_path = os.path.join(self.resource_path, "icons", icon_name)
                
                # Use default icon if resource doesn't exist
                if not os.path.exists(icon_path):
                    theme_button.setText("<")
                else:
                    theme_button.setIcon(QIcon(icon_path))
    
    def get_icon(self, name: str) -> QIcon:
        """Get an icon from the resources
        
        Args:
            name: Icon name
            
        Returns:
            QIcon object
        """
        icon_path = os.path.join(self.resource_path, "icons", name)
        
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        else:
            return QIcon()