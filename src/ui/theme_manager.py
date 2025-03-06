"""
Theme manager for WinRegi application
Handles application theming and styles
"""
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QPalette, QColor, QIcon, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize, pyqtProperty, QObject
import os
import json
import math
from pathlib import Path

class ThemeToggleSwitch(QWidget):
    """Custom toggle switch widget for theme switching"""
    
    def __init__(self, parent=None):
        """Initialize the toggle switch
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("theme-toggle")
        
        # Set fixed size
        self.setFixedSize(56, 28)
        
        # Initialize state
        self._checked = False
        self._circle_position = 4
        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setEasingCurve(QEasingCurve.OutBounce)
        self._animation.setDuration(300)  # ms
        
        # Set mouseover tracking
        self.setMouseTracking(True)
        
    def is_checked(self):
        """Get the checked state
        
        Returns:
            bool: Whether the switch is checked
        """
        return self._checked
    
    def set_checked(self, checked, animate=True):
        """Set the checked state
        
        Args:
            checked: New state
            animate: Whether to animate the transition
        """
        if self._checked != checked:
            self._checked = checked
            
            if animate:
                # Animate the switch circle
                end_pos = 28 if checked else 4
                self._animation.setStartValue(self._circle_position)
                self._animation.setEndValue(end_pos)
                self._animation.start()
            else:
                # Set position without animation
                self._circle_position = 28 if checked else 4
                self.update()
    
    def circle_position(self):
        """Get the current circle position
        
        Returns:
            Current position of the switch circle
        """
        return self._circle_position
    
    def set_circle_position(self, pos):
        """Set circle position (used by animation)
        
        Args:
            pos: New position
        """
        self._circle_position = pos
        self.update()
    
    # Define property for animation
    circle_position = pyqtProperty(float, circle_position, set_circle_position)
    
    def paintEvent(self, event):
        """Custom paint event to draw the toggle switch
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get theme mode from parent
        dark_mode = self._checked
        
        # Calculate rect for background
        track_rect = QRect(0, 0, self.width(), self.height())
        
        # Draw track background
        if dark_mode:
            # Dark mode - green accent
            track_color = QColor("#2A2A2A")
            accent_color = QColor("#38E078")
        else:
            # Light mode - slightly darker green accent
            track_color = QColor("#EEEEEE")
            accent_color = QColor("#28C058")
            
        # Draw track
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(track_rect, 14, 14)
        
        # Draw thumb/circle
        painter.setBrush(QBrush(accent_color))
        painter.drawEllipse(
            int(self._circle_position), 
            4, 
            20, 
            20
        )
        
        # Draw icon inside thumb if needed
        if dark_mode:
            # Draw moon icon (simple crescent)
            painter.setPen(QPen(QColor("#222222"), 1))
            painter.setBrush(QBrush(QColor("#222222")))
            painter.drawEllipse(int(self._circle_position) + 6, 8, 12, 12)
            painter.setBrush(QBrush(accent_color))
            painter.drawEllipse(int(self._circle_position) + 8, 7, 12, 12)
        else:
            # Draw sun icon (simple circle with rays)
            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            painter.drawEllipse(int(self._circle_position) + 6, 10, 8, 8)
            # Draw rays
            for i in range(8):
                angle = i * 45
                if angle % 90 == 0:  # Longer rays at cardinal directions
                    length = 5
                else:
                    length = 3
                rad_angle = angle * math.pi / 180
                x1 = int(self._circle_position) + 10 + 5 * math.cos(rad_angle)
                y1 = 14 + 5 * math.sin(rad_angle)
                x2 = int(self._circle_position) + 10 + (5 + length) * math.cos(rad_angle)
                y2 = 14 + (5 + length) * math.sin(rad_angle)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def mousePressEvent(self, event):
        """Handle mouse press event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            # Toggle the switch state
            self.set_checked(not self._checked)
            self.clicked()
    
    def clicked(self):
        """Handle click event - to be overridden by parent"""
        pass


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
        
        # Create resources directory if it doesn't exist
        os.makedirs(self.resource_path, exist_ok=True)
        os.makedirs(os.path.join(self.resource_path, "icons"), exist_ok=True)
        
        # Theme config path
        self.config_path = os.path.join(self.resource_path, "theme_config.json")
        
        # Load saved theme if exists
        self.load_theme_config()
        
        # Theme stylesheets
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }
    
    def load_theme_config(self):
        """Load theme configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "light")
            except:
                # If any error occurs, use default theme
                self.current_theme = "light"
    
    def save_theme_config(self):
        """Save theme configuration to file"""
        config = {
            "theme": self.current_theme
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
        except:
            # If save fails, just continue
            pass
    
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
            color: #28C058;
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
            background-color: #28C058;
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
            color: #28C058;
        }
        
        /* Search bar */
        QLineEdit {
            padding: 8px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #28C058;
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
            background-color: #28C058;
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
            background-color: #28C058;
            color: #ffffff;
            border: none;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #33CF63;
        }
        
        QPushButton:pressed {
            background-color: #239A47;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
        }
        
        /* Theme toggle switch */
        #theme-toggle {
            border: none;
            background-color: transparent;
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
            background-color: #e5f7ea;
            color: #28C058;
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
            border: 1px solid #b9eac8;
            background-color: #f5fff8;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        #setting-name {
            color: #333333;
        }
        
        #setting-description {
            color: #666666;
        }
        
        #category-container {
            background-color: #f5fff8;
            border-radius: 13px;
        }
        
        #setting-category {
            color: #28C058;
            font-weight: bold;
        }
        
        #category-badge {
            background-color: #e5f7ea;
            border-radius: 20px;
            border: 1px solid #b9eac8;
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
            background-color: #28C058;
            color: #ffffff;
            border: none;
        }
        
        .primary-action:hover {
            background-color: #33CF63;
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
        
        /* Custom Command UI */
        #commands-section {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #eeeeee;
        }
        
        #command-list {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 4px;
        }
        
        #command-list-item {
            padding: 10px;
            border-bottom: 1px solid #eeeeee;
        }
        
        #command-list-item:hover {
            background-color: #f5fff8;
        }
        
        #command-name {
            font-weight: bold;
            color: #333333;
        }
        
        #command-description {
            color: #666666;
        }
        
        #command-value {
            color: #28C058;
            font-family: monospace;
        }
        
        #add-command-button {
            background-color: #28C058;
            color: #ffffff;
            border-radius: 4px;
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
            color: #38E078;
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
            background-color: #38E078;
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
            color: #38E078;
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
            border: 1px solid #38E078;
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
            background-color: #38E078;
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
            background-color: #38E078;
            color: #ffffff;
            border: none;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #4FE88A;
        }
        
        QPushButton:pressed {
            background-color: #2BB25C;
        }
        
        QPushButton:disabled {
            background-color: #333333;
            color: #777777;
        }
        
        /* Theme toggle switch */
        #theme-toggle {
            border: none;
            background-color: transparent;
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
            background-color: #1e372a;
            color: #38E078;
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
            border: 1px solid #38E078;
            background-color: #1e372a;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.25);
        }
        
        #setting-name {
            color: #e0e0e0;
        }
        
        #setting-description {
            color: #aaaaaa;
        }
        
        #category-container {
            background-color: #1e372a;
            border-radius: 13px;
        }
        
        #setting-category {
            color: #38E078;
            font-weight: bold;
        }
        
        #category-badge {
            background-color: #1e372a;
            border-radius: 20px;
            border: 1px solid #38E078;
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
            background-color: #38E078;
            color: #ffffff;
            border: none;
        }
        
        .primary-action:hover {
            background-color: #4FE88A;
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
        
        /* Custom Command UI */
        #commands-section {
            background-color: #222222;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #333333;
        }
        
        #command-list {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 4px;
        }
        
        #command-list-item {
            padding: 10px;
            border-bottom: 1px solid #2d2d2d;
        }
        
        #command-list-item:hover {
            background-color: #1e372a;
        }
        
        #command-name {
            font-weight: bold;
            color: #e0e0e0;
        }
        
        #command-description {
            color: #aaaaaa;
        }
        
        #command-value {
            color: #38E078;
            font-family: monospace;
        }
        
        #add-command-button {
            background-color: #38E078;
            color: #ffffff;
            border-radius: 4px;
        }
        """
    
    def apply_theme(self, theme_name: str, save=True):
        """Apply a theme to the application
        
        Args:
            theme_name: Name of the theme to apply
            save: Whether to save the theme selection to config
        """
        if theme_name not in self.themes:
            return
        
        # Store current theme
        self.current_theme = theme_name
        
        # Apply stylesheet
        QApplication.instance().setStyleSheet(self.themes[theme_name])
        
        # Update theme toggle in parent if exists
        if self.parent:
            theme_toggle = self.parent.findChild(ThemeToggleSwitch, "theme-toggle")
            if theme_toggle:
                theme_toggle.set_checked(theme_name == "dark", animate=True)
            
            # For backward compatibility
            theme_button = self.parent.findChild(QPushButton, "theme-button")
            if theme_button:
                icon_name = "light_mode.png" if theme_name == "dark" else "dark_mode.png"
                icon_path = os.path.join(self.resource_path, "icons", icon_name)
                
                # Use default icon if resource doesn't exist
                if not os.path.exists(icon_path):
                    theme_button.setText("<")
                else:
                    theme_button.setIcon(QIcon(icon_path))
        
        # Save theme config if requested
        if save:
            self.save_theme_config()
    
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
    
    def create_theme_toggle(self, parent=None) -> QWidget:
        """Create a theme toggle switch widget
        
        Args:
            parent: Parent widget
            
        Returns:
            Theme toggle widget
        """
        # Create container widget
        container = QWidget(parent)
        container.setObjectName("theme-toggle-container")
        container.setFixedWidth(120)
        
        # Create layout
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Create mode label
        mode_label = QLabel(parent)
        mode_label.setObjectName("theme-mode-label")
        mode_label.setText("Dark Mode" if self.current_theme == "dark" else "Light Mode")
        
        # Create toggle switch
        toggle = ThemeToggleSwitch(parent)
        toggle.set_checked(self.current_theme == "dark", animate=False)
        
        # Override click handler
        def toggle_theme():
            new_theme = "dark" if self.current_theme == "light" else "light"
            self.apply_theme(new_theme)
            mode_label.setText("Dark Mode" if new_theme == "dark" else "Light Mode")
            
        toggle.clicked = toggle_theme
        
        # Add widgets to layout
        layout.addWidget(mode_label)
        layout.addWidget(toggle)
        
        return container