"""
Theme manager for WinRegi application
Handles application theming and styles with modern UI elements
"""
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QWidget, QHBoxLayout, QLabel, 
    QGraphicsDropShadowEffect, QGraphicsBlurEffect, QVBoxLayout
)
from PyQt5.QtGui import QPalette, QColor, QIcon, QPainter, QPen, QBrush, QFontDatabase
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QRect, QSize, 
    pyqtProperty, QObject, QParallelAnimationGroup, QSequentialAnimationGroup, 
    QTimer, pyqtSignal
)
import os
import json
import math
from pathlib import Path

class ThemeToggleSwitch(QWidget):
    """Modern toggle switch widget for theme switching with animated transitions"""
    
    # Signal emitted when switch is toggled
    toggled = pyqtSignal(bool)
    
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
        self._hovered = False
        self._pressed = False
        
        # Create animation for sliding motion
        self._slide_animation = QPropertyAnimation(self, b"circle_position")
        self._slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_animation.setDuration(250)  # ms
        
        # Create animation for bounce effect
        self._bounce_animation = QPropertyAnimation(self, b"circle_position")
        self._bounce_animation.setEasingCurve(QEasingCurve.OutBounce)
        self._bounce_animation.setDuration(350)  # ms
        
        # Create sequential animation group for smooth transitions
        self._animation = QSequentialAnimationGroup()
        self._animation.addAnimation(self._slide_animation)
        self._animation.addAnimation(self._bounce_animation)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Add shadow effect
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(10)
        self._shadow.setColor(QColor(0, 0, 0, 40))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)
    
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
                # Setup animations
                start_pos = self._circle_position
                end_pos = 28 if checked else 4
                bounce_pos = end_pos + (2 if checked else -2)
                
                # Configure slide animation
                self._slide_animation.setStartValue(start_pos)
                self._slide_animation.setEndValue(bounce_pos)
                
                # Configure bounce animation
                self._bounce_animation.setStartValue(bounce_pos)
                self._bounce_animation.setEndValue(end_pos)
                
                # Start the animation sequence
                self._animation.start()
                
                # Emit signal
                self.toggled.emit(checked)
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
        
        # Get theme mode from checked state
        dark_mode = self._checked
        
        # Calculate rect for background
        track_rect = QRect(0, 0, self.width(), self.height())
        
        # Determine colors based on state
        if dark_mode:
            # Dark mode - green accent
            track_color = QColor("#2A2A2A")
            track_color_hover = QColor("#333333")
            accent_color = QColor("#38E078")
            accent_color_hover = QColor("#4FE88A")
        else:
            # Light mode - slightly darker green accent
            track_color = QColor("#EEEEEE")
            track_color_hover = QColor("#E5E5E5")
            accent_color = QColor("#28C058")
            accent_color_hover = QColor("#33CF63")
        
        # Apply hover effect
        if self._hovered and not self._pressed:
            track_color = track_color_hover
            accent_color = accent_color_hover
        
        # Draw track with rounded corners
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(track_rect, 14, 14)
        
        # Calculate thumb/circle size with press effect
        circle_size = 20
        if self._pressed:
            circle_size = 18  # Smaller when pressed
        
        # Calculate y position to center the circle
        y_pos = (self.height() - circle_size) / 2
        
        # Draw thumb/circle with glow effect if hovered
        painter.setBrush(QBrush(accent_color))
        
        # Add glow if hovered
        if self._hovered and not self._pressed:
            # Draw subtle glow around circle
            glow_color = QColor(accent_color)
            glow_color.setAlpha(40)
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(
                int(self._circle_position - 2), 
                int(y_pos - 2), 
                circle_size + 4, 
                circle_size + 4
            )
            
            # Reset to main color
            painter.setBrush(QBrush(accent_color))
        
        # Draw the main circle
        painter.drawEllipse(
            int(self._circle_position), 
            int(y_pos), 
            circle_size, 
            circle_size
        )
        
        # Draw icon inside thumb based on theme mode
        if dark_mode:
            # Draw moon icon (simple crescent)
            painter.setPen(QPen(QColor("#222222"), 1))
            painter.setBrush(QBrush(QColor("#222222")))
            painter.drawEllipse(int(self._circle_position) + 6, int(y_pos) + 4, 12, 12)
            painter.setBrush(QBrush(accent_color))
            painter.drawEllipse(int(self._circle_position) + 8, int(y_pos) + 3, 12, 12)
        else:
            # Draw sun icon (simple circle with rays)
            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            painter.drawEllipse(int(self._circle_position) + 6, int(y_pos) + 6, 8, 8)
            
            # Draw rays
            for i in range(8):
                angle = i * 45
                if angle % 90 == 0:  # Longer rays at cardinal directions
                    length = 5
                else:
                    length = 3
                rad_angle = angle * math.pi / 180
                x1 = int(self._circle_position) + 10 + 5 * math.cos(rad_angle)
                y1 = int(y_pos) + 10 + 5 * math.sin(rad_angle)
                x2 = int(self._circle_position) + 10 + (5 + length) * math.cos(rad_angle)
                y2 = int(y_pos) + 10 + (5 + length) * math.sin(rad_angle)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
    
    def mousePressEvent(self, event):
        """Handle mouse press event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            # Toggle the switch state
            self.set_checked(not self._checked)
            self.clicked()
            self.update()
    
    def enterEvent(self, event):
        """Handle mouse enter event
        
        Args:
            event: Enter event
        """
        self._hovered = True
        self.setCursor(Qt.PointingHandCursor)
        self.update()
    
    def leaveEvent(self, event):
        """Handle mouse leave event
        
        Args:
            event: Leave event
        """
        self._hovered = False
        self._pressed = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
    
    def clicked(self):
        """Handle click event - to be overridden by parent"""
        pass


class ThemeManager:
    """Manages application themes and styles with modern UI elements"""
    
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
        os.makedirs(os.path.join(self.resource_path, "fonts"), exist_ok=True)
        
        # Theme config path
        self.config_path = os.path.join(self.resource_path, "theme_config.json")
        
        # Load saved theme if exists
        self.load_theme_config()
        
        # Load fonts
        self.load_fonts()
        
        # Theme stylesheets
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }
    
    def load_fonts(self):
        """Load custom fonts for the application"""
        # For now, we'll just register system fonts
        # In a real application, you would include font files in resources
        # and load them here
        pass
    
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
            background-color: #f8f9fa;
            color: #333333;
        }
        
        /* Header */
        #app-header {
            background-color: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid #e9ecef;
            padding: 10px;
            border-radius: 0px 0px 15px 15px;
        }
        
        #app-title {
            font-family: 'Segoe UI', sans-serif;
            font-size: 24px;
            font-weight: bold;
            color: #28C058;
        }
        
        #app-subtitle {
            font-family: 'Segoe UI', sans-serif;
            color: #6c757d;
        }
        
        #admin-indicator {
            border-radius: 15px;
            color: #ffffff;
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            transition: background-color 0.3s;
        }
        
        #admin-indicator[admin-status="admin"] {
            background-color: rgba(40, 192, 88, 0.9);
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.3);
        }
        
        #admin-indicator[admin-status="limited"] {
            background-color: rgba(255, 152, 0, 0.9);
            box-shadow: 0 2px 5px rgba(255, 152, 0, 0.3);
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: none;
            border-radius: 10px;
            background-color: #ffffff;
            padding: 5px;
        }
        
        QTabBar::tab {
            padding: 10px 20px;
            margin-right: 4px;
            background-color: rgba(238, 238, 238, 0.7);
            border: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            transition: background-color 0.3s;
        }
        
        QTabBar::tab:hover {
            background-color: rgba(220, 255, 235, 0.7);
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            color: #28C058;
            font-weight: bold;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* Search bar */
        QLineEdit {
            padding: 10px 15px;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            selection-background-color: #b9eac8;
            selection-color: #333333;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        QLineEdit:focus {
            border: 1px solid #28C058;
            box-shadow: 0 0 0 3px rgba(40, 192, 88, 0.15);
        }
        
        #search-heading {
            color: #333333;
            margin-bottom: 15px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
        }
        
        #search-container {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: box-shadow 0.3s, transform 0.2s;
        }
        
        #search-container:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }
        
        #search-input {
            font-size: 15px;
            color: #333333;
            border: none;
            background: transparent;
            padding: 12px;
            border-radius: 25px;
        }
        
        #search-button {
            background-color: #28C058;
            color: white;
            border-radius: 20px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            padding: 8px 16px;
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.3);
            transition: all 0.2s;
        }
        
        #search-button:hover {
            background-color: #33CF63;
            box-shadow: 0 4px 10px rgba(40, 192, 88, 0.4);
            transform: translateY(-1px);
        }
        
        #search-button:pressed {
            background-color: #239A47;
            box-shadow: 0 1px 3px rgba(40, 192, 88, 0.3);
            transform: translateY(1px);
        }
        
        #examples-container {
            margin-top: 15px;
            padding: 5px;
        }
        
        .example-button {
            background-color: #f8f9fa;
            color: #555555;
            border: 1px solid #e9ecef;
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
            transition: all 0.2s ease-in-out;
        }
        
        .example-button:hover {
            background-color: #e9fff0;
            border-color: #b9eac8;
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* Buttons */
        QPushButton {
            padding: 10px 18px;
            background-color: #28C058;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.3);
            transition: all 0.2s;
        }
        
        QPushButton:hover {
            background-color: #33CF63;
            box-shadow: 0 4px 10px rgba(40, 192, 88, 0.4);
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background-color: #239A47;
            box-shadow: 0 1px 3px rgba(40, 192, 88, 0.3);
            transform: translateY(1px);
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #999999;
            box-shadow: none;
        }
        
        /* Theme toggle switch */
        #theme-toggle {
            border: none;
            background-color: transparent;
        }
        
        #theme-toggle-container {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 20px;
            padding: 5px 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(5px);
            transition: all 0.3s;
        }
        
        #theme-toggle-container:hover {
            background-color: rgba(255, 255, 255, 0.9);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }
        
        #theme-mode-label {
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #666666;
            transition: color 0.3s;
        }
        
        /* Lists and Trees */
        QListWidget, QTreeWidget, QTableWidget {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 5px;
            font-family: 'Segoe UI', sans-serif;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f1f3f5;
            border-radius: 5px;
            margin: 2px 0;
            transition: background-color 0.2s;
        }
        
        QListWidget::item:hover, QTreeWidget::item:hover {
            background-color: #f8f9fa;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #e5f7ea;
            color: #28C058;
            border-left: 3px solid #28C058;
        }
        
        /* Scroll bars */
        QScrollBar:vertical {
            background-color: #f8f9fa;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #d1d1d1;
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
            transition: background-color 0.2s;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #aaaaaa;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Horizontal scrollbar */
        QScrollBar:horizontal {
            background-color: #f8f9fa;
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #d1d1d1;
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #aaaaaa;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Cards */
        .setting-card {
            background-color: #ffffff;
            border: 1px solid #f1f3f5;
            border-radius: 15px;
            padding: 5px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .setting-card:hover {
            border: 1px solid #b9eac8;
            background-color: #f7fff9;
            box-shadow: 0 5px 15px rgba(40, 192, 88, 0.1);
            transform: translateY(-2px);
        }
        
        #setting-name {
            color: #333333;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            font-size: 14px;
        }
        
        #setting-description {
            color: #6c757d;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        
        #category-container {
            background-color: #f7fff9;
            border-radius: 13px;
            transition: background-color 0.3s;
        }
        
        #setting-category {
            color: #28C058;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }
        
        #category-badge {
            background-color: #e5f7ea;
            border-radius: 20px;
            border: 1px solid #b9eac8;
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.1);
            transition: all 0.3s;
        }
        
        /* Labels */
        .heading {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 10px;
        }
        
        .subheading {
            font-size: 14px;
            color: #6c757d;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 5px;
        }
        
        /* Action buttons */
        .action-button {
            padding: 8px 15px;
            background-color: #f8f9fa;
            color: #495057;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            transition: all 0.2s;
        }
        
        .action-button:hover {
            background-color: #e9ecef;
            border: 1px solid #dee2e6;
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        .action-button:pressed {
            transform: translateY(1px);
            box-shadow: none;
        }
        
        .primary-action {
            background-color: #28C058;
            color: #ffffff;
            border: none;
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.3);
        }
        
        .primary-action:hover {
            background-color: #33CF63;
            box-shadow: 0 4px 10px rgba(40, 192, 88, 0.4);
            border: none;
        }
        
        .primary-action:pressed {
            background-color: #239A47;
            box-shadow: 0 1px 3px rgba(40, 192, 88, 0.3);
        }
        
        .warning-action {
            background-color: #ff9800;
            color: #ffffff;
            border: none;
            box-shadow: 0 2px 5px rgba(255, 152, 0, 0.3);
        }
        
        .warning-action:hover {
            background-color: #f57c00;
            border: none;
            box-shadow: 0 4px 10px rgba(255, 152, 0, 0.4);
        }
        
        .warning-action:pressed {
            background-color: #e65100;
            box-shadow: 0 1px 3px rgba(255, 152, 0, 0.3);
        }
        
        /* Theme buttons */
        #light-theme-button {
            background-color: #ffffff;
            color: #333333;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        #light-theme-button:hover {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
        }
        
        #dark-theme-button {
            background-color: #343a40;
            color: #ffffff;
            border: 1px solid #495057;
            border-radius: 10px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        #dark-theme-button:hover {
            background-color: #212529;
            border: 1px solid #343a40;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        }
        
        /* Theme section */
        #theme-section {
            background-color: rgba(248, 249, 250, 0.7);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        
        #theme-section:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }
        
        /* Custom Command UI */
        #commands-section {
            background-color: rgba(248, 249, 250, 0.7);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        
        #commands-section:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
        }
        
        #command-list {
            background-color: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 5px;
        }
        
        #command-list-item {
            padding: 15px;
            border-bottom: 1px solid #f1f3f5;
            border-radius: 8px;
            margin: 5px 0;
            transition: all 0.2s;
        }
        
        #command-list-item:hover {
            background-color: #f7fff9;
            transform: translateX(5px);
        }
        
        #command-name {
            font-weight: bold;
            color: #333333;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        
        #command-description {
            color: #6c757d;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        
        #command-value {
            color: #28C058;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }
        
        #add-command-button {
            background-color: #28C058;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px 15px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(40, 192, 88, 0.3);
            transition: all 0.2s;
        }
        
        #add-command-button:hover {
            background-color: #33CF63;
            box-shadow: 0 4px 10px rgba(40, 192, 88, 0.4);
            transform: translateY(-1px);
        }
        
        /* Panel headers */
        #panel-header {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }
        
        /* Category panel */
        #category-panel {
            background-color: rgba(255, 255, 255, 0.7);
            border-right: 1px solid #e9ecef;
            border-radius: 15px 0 0 15px;
        }
        
        /* Settings panel */
        #settings-panel {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 0 15px 15px 0;
        }
        
        /* Results header */
        #results-header {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }
        
        /* Make dialog look modern */
        QDialog {
            border-radius: 15px;
            background-color: #ffffff;
        }
        
        QMessageBox {
            background-color: #ffffff;
            border-radius: 15px;
        }
        
        QMessageBox QLabel {
            font-family: 'Segoe UI', sans-serif;
            color: #333333;
            font-size: 14px;
        }
        
        QMessageBox QPushButton {
            min-width: 100px;
            min-height: 30px;
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #f8f9fa;
            color: #6c757d;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            padding: 3px 10px;
            border-top: 1px solid #e9ecef;
        }
        
        /* Splitter handle */
        QSplitter::handle {
            background-color: #e9ecef;
            width: 1px;
        }
        
        QSplitter::handle:hover {
            background-color: #28C058;
        }
        
        /* Main tabs with indicators */
        QTabWidget#main-tabs::tab-bar {
            alignment: center;
        }
        
        QTabWidget#main-tabs QTabBar::tab {
            min-width: 120px;
            padding: 10px 20px;
        }
        
        QTabWidget#main-tabs QTabBar::tab:selected {
            border-bottom: 2px solid #28C058;
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
            background-color: rgba(40, 40, 40, 0.7);
            border-bottom: 1px solid #2d2d2d;
            padding: 10px;
            border-radius: 0px 0px 15px 15px;
            backdrop-filter: blur(10px);
        }
        
        #app-title {
            font-family: 'Segoe UI', sans-serif;
            font-size: 24px;
            font-weight: bold;
            color: #38E078;
        }
        
        #app-subtitle {
            font-family: 'Segoe UI', sans-serif;
            color: #adb5bd;
        }
        
        #admin-indicator {
            border-radius: 15px;
            color: #ffffff;
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            transition: background-color 0.3s;
        }
        
        #admin-indicator[admin-status="admin"] {
            background-color: rgba(56, 224, 120, 0.8);
            box-shadow: 0 2px 10px rgba(56, 224, 120, 0.3);
        }
        
        #admin-indicator[admin-status="limited"] {
            background-color: rgba(239, 108, 0, 0.8);
            box-shadow: 0 2px 10px rgba(239, 108, 0, 0.3);
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: none;
            border-radius: 10px;
            background-color: #1e1e1e;
            padding: 5px;
        }
        
        QTabBar::tab {
            padding: 10px 20px;
            margin-right: 4px;
            background-color: rgba(38, 38, 38, 0.7);
            border: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
            transition: background-color 0.3s;
        }
        
        QTabBar::tab:hover {
            background-color: rgba(30, 55, 42, 0.7);
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            color: #38E078;
            font-weight: bold;
            box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.2);
        }
        
        /* Search bar */
        QLineEdit {
            padding: 10px 15px;
            border: 1px solid #2d2d2d;
            border-radius: 10px;
            background-color: #262626;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            selection-background-color: #1e372a;
            selection-color: #e0e0e0;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
        }
        
        QLineEdit:focus {
            border: 1px solid #38E078;
            box-shadow: 0 0 0 3px rgba(56, 224, 120, 0.15);
        }
        
        #search-heading {
            color: #e0e0e0;
            margin-bottom: 15px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
        }
        
        #search-container {
            background-color: rgba(38, 38, 38, 0.9);
            border: 1px solid #2d2d2d;
            border-radius: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: box-shadow 0.3s, transform 0.2s;
            backdrop-filter: blur(10px);
        }
        
        #search-container:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
            background-color: rgba(45, 45, 45, 0.9);
        }
        
        #search-input {
            font-size: 15px;
            color: #e0e0e0;
            border: none;
            background: transparent;
            padding: 12px;
            border-radius: 25px;
        }
        
        #search-button {
            background-color: #38E078;
            color: white;
            border-radius: 20px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            padding: 8px 16px;
            box-shadow: 0 2px 10px rgba(56, 224, 120, 0.3);
            transition: all 0.2s;
        }
        
        #search-button:hover {
            background-color: #4FE88A;
            box-shadow: 0 4px 15px rgba(56, 224, 120, 0.4);
            transform: translateY(-1px);
        }
        
        #search-button:pressed {
            background-color: #2BB25C;
            box-shadow: 0 1px 5px rgba(56, 224, 120, 0.3);
            transform: translateY(1px);
        }
        
        #examples-container {
            margin-top: 15px;
            padding: 5px;
        }
        
        .example-button {
            background-color: #2d2d2d;
            color: #adb5bd;
            border: 1px solid #3d3d3d;
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 12px;
            font-family: 'Segoe UI', sans-serif;
            transition: all 0.2s ease-in-out;
        }
        
        .example-button:hover {
            background-color: #1e372a;
            border-color: #38E078;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(56, 224, 120, 0.2);
            color: #e0e0e0;
        }
        
        /* Buttons */
        QPushButton {
            padding: 10px 18px;
            background-color: #38E078;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            box-shadow: 0 2px 10px rgba(56, 224, 120, 0.3);
            transition: all 0.2s;
        }
        
        QPushButton:hover {
            background-color: #4FE88A;
            box-shadow: 0 4px 15px rgba(56, 224, 120, 0.4);
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background-color: #2BB25C;
            box-shadow: 0 1px 5px rgba(56, 224, 120, 0.3);
            transform: translateY(1px);
        }
        
        QPushButton:disabled {
            background-color: #333333;
            color: #777777;
            box-shadow: none;
        }
        
        /* Theme toggle switch */
        #theme-toggle {
            border: none;
            background-color: transparent;
        }
        
        #theme-toggle-container {
            background-color: rgba(30, 30, 30, 0.7);
            border-radius: 20px;
            padding: 5px 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(5px);
            transition: all 0.3s;
        }
        
        #theme-toggle-container:hover {
            background-color: rgba(40, 40, 40, 0.9);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        
        #theme-mode-label {
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            color: #adb5bd;
            transition: color 0.3s;
        }
        
        /* Lists and Trees */
        QListWidget, QTreeWidget, QTableWidget {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 10px;
            padding: 5px;
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
        }
        
        QListWidget::item, QTreeWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2d2d2d;
            border-radius: 5px;
            margin: 2px 0;
            transition: background-color 0.2s;
        }
        
        QListWidget::item:hover, QTreeWidget::item:hover {
            background-color: #262626;
        }
        
        QListWidget::item:selected, QTreeWidget::item:selected {
            background-color: #1e372a;
            color: #38E078;
            border-left: 3px solid #38E078;
        }
        
        /* Scroll bars */
        QScrollBar:vertical {
            background-color: #1e1e1e;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3d3d3d;
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
            transition: background-color 0.2s;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4d4d4d;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Horizontal scrollbar */
        QScrollBar:horizontal {
            background-color: #1e1e1e;
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #3d3d3d;
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #4d4d4d;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Cards */
        .setting-card {
            background-color: rgba(30, 30, 30, 0.8);
            border: 1px solid #2d2d2d;
            border-radius: 15px;
            padding: 5px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .setting-card:hover {
            border: 1px solid #38E078;
            background-color: rgba(30, 55, 42, 0.7);
            box-shadow: 0 5px 15px rgba(56, 224, 120, 0.2);
            transform: translateY(-2px);
        }
        
        #setting-name {
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            font-size: 14px;
        }
        
        #setting-description {
            color: #adb5bd;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        
        #category-container {
            background-color: rgba(30, 55, 42, 0.7);
            border-radius: 13px;
            transition: background-color 0.3s;
        }
        
        #setting-category {
            color: #38E078;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
        }
        
        #category-badge {
            background-color: #1e372a;
            border-radius: 20px;
            border: 1px solid #38E078;
            box-shadow: 0 2px 8px rgba(56, 224, 120, 0.2);
            transition: all 0.3s;
        }
        
        /* Labels */
        .heading {
            font-size: 18px;
            font-weight: bold;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 10px;
        }
        
        .subheading {
            font-size: 14px;
            color: #adb5bd;
            font-family: 'Segoe UI', sans-serif;
            margin-bottom: 5px;
        }
        
        /* Action buttons */
        .action-button {
            padding: 8px 15px;
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            border-radius: 10px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
            transition: all 0.2s;
        }
        
        .action-button:hover {
            background-color: #363636;
            border: 1px solid #4d4d4d;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        .action-button:pressed {
            transform: translateY(1px);
            box-shadow: none;
        }
        
        .primary-action {
            background-color: #38E078;
            color: #ffffff;
            border: none;
            box-shadow: 0 2px 10px rgba(56, 224, 120, 0.3);
        }
        
        .primary-action:hover {
            background-color: #4FE88A;
            box-shadow: 0 4px 15px rgba(56, 224, 120, 0.4);
            border: none;
        }
        
        .primary-action:pressed {
            background-color: #2BB25C;
            box-shadow: 0 1px 5px rgba(56, 224, 120, 0.3);
        }
        
        .warning-action {
            background-color: #d84315;
            color: #ffffff;
            border: none;
            box-shadow: 0 2px 10px rgba(216, 67, 21, 0.3);
        }
        
        .warning-action:hover {
            background-color: #bf360c;
            border: none;
            box-shadow: 0 4px 15px rgba(216, 67, 21, 0.4);
        }
        
        .warning-action:pressed {
            background-color: #a02a09;
            box-shadow: 0 1px 5px rgba(216, 67, 21, 0.3);
        }
        
        /* Theme buttons */
        #light-theme-button {
            background-color: #f8f9fa;
            color: #333333;
            border: 1px solid #4d4d4d;
            border-radius: 10px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
        }
        
        #light-theme-button:hover {
            background-color: #ffffff;
            border: 1px solid #6c757d;
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.15);
        }
        
        #dark-theme-button {
            background-color: #212529;
            color: #e0e0e0;
            border: 1px solid #343a40;
            border-radius: 10px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        #dark-theme-button:hover {
            background-color: #16181b;
            border: 1px solid #212529;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
        }
        
        /* Theme section */
        #theme-section {
            background-color: rgba(34, 34, 34, 0.7);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333333;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        
        #theme-section:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
            transform: translateY(-2px);
            background-color: rgba(38, 38, 38, 0.7);
        }
        
        /* Custom Command UI */
        #commands-section {
            background-color: rgba(34, 34, 34, 0.7);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #333333;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        }
        
        #commands-section:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
            transform: translateY(-2px);
            background-color: rgba(38, 38, 38, 0.7);
        }
        
        #command-list {
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 10px;
            padding: 5px;
        }
        
        #command-list-item {
            padding: 15px;
            border-bottom: 1px solid #2d2d2d;
            border-radius: 8px;
            margin: 5px 0;
            transition: all 0.2s;
        }
        
        #command-list-item:hover {
            background-color: #1e372a;
            transform: translateX(5px);
        }
        
        #command-name {
            font-weight: bold;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }
        
        #command-description {
            color: #adb5bd;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        
        #command-value {
            color: #38E078;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            background-color: #262626;
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid #3d3d3d;
        }
        
        #add-command-button {
            background-color: #38E078;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px 15px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(56, 224, 120, 0.3);
            transition: all 0.2s;
        }
        
        #add-command-button:hover {
            background-color: #4FE88A;
            box-shadow: 0 4px 15px rgba(56, 224, 120, 0.4);
            transform: translateY(-1px);
        }
        
        /* Panel headers */
        #panel-header {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: bold;
            color: #e0e0e0;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #333333;
        }
        
        /* Category panel */
        #category-panel {
            background-color: rgba(30, 30, 30, 0.7);
            border-right: 1px solid #2d2d2d;
            border-radius: 15px 0 0 15px;
        }
        
        /* Settings panel */
        #settings-panel {
            background-color: rgba(30, 30, 30, 0.7);
            border-radius: 0 15px 15px 0;
        }
        
        /* Results header */
        #results-header {
            font-family: 'Segoe UI', sans-serif;
            font-size: 18px;
            font-weight: bold;
            color: #e0e0e0;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #333333;
        }
        
        /* Make dialog look modern */
        QDialog {
            border-radius: 15px;
            background-color: #1e1e1e;
        }
        
        QMessageBox {
            background-color: #1e1e1e;
            border-radius: 15px;
        }
        
        QMessageBox QLabel {
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
            font-size: 14px;
        }
        
        QMessageBox QPushButton {
            min-width: 100px;
            min-height: 30px;
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #1a1a1a;
            color: #adb5bd;
            font-family: 'Segoe UI', sans-serif;
            font-size: 12px;
            padding: 3px 10px;
            border-top: 1px solid #2d2d2d;
        }
        
        /* Splitter handle */
        QSplitter::handle {
            background-color: #2d2d2d;
            width: 1px;
        }
        
        QSplitter::handle:hover {
            background-color: #38E078;
        }
        
        /* Main tabs with indicators */
        QTabWidget#main-tabs::tab-bar {
            alignment: center;
        }
        
        QTabWidget#main-tabs QTabBar::tab {
            min-width: 120px;
            padding: 10px 20px;
        }
        
        QTabWidget#main-tabs QTabBar::tab:selected {
            border-bottom: 2px solid #38E078;
        }
        """
    
    def apply_theme(self, theme_name: str, save=True):
        """Apply a theme to the application with smooth transition animation
        
        Args:
            theme_name: Name of the theme to apply
            save: Whether to save the theme selection to config
        """
        if theme_name not in self.themes:
            return
        
        # Store current theme
        self.current_theme = theme_name
        
        # Apply stylesheet
        # Get the base theme
        stylesheet = self.themes[theme_name]
        
        # Add modern UI styles
        try:
            # Path to modern UI styles
            styles_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "modern_ui_styles.css"
            )
            
            # If file exists, read it and append to stylesheet
            if os.path.exists(styles_path):
                with open(styles_path, 'r') as f:
                    modern_styles = f.read()
                    stylesheet += modern_styles
                    
                    # Add theme-specific overrides
                    is_dark = theme_name == "dark"
                    if is_dark:
                        # Dark theme specific overrides
                        stylesheet += """
                        /* Dark theme specific overrides */
                        #app-container {
                            background-color: #121212;
                        }
                        
                        #sidebar-nav {
                            background-color: #1a1a1a;
                            border-right: 1px solid #2d2d2d;
                        }
                        
                        #header-search-container {
                            background-color: rgba(38, 38, 38, 0.7);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                        }
                        
                        #header-search-button {
                            color: #adb5bd;
                        }
                        
                        #nav-button {
                            color: #adb5bd;
                        }
                        
                        #nav-button:hover {
                            background-color: rgba(40, 40, 40, 0.8);
                        }
                        
                        #nav-button:checked {
                            background-color: #1e372a;
                            color: #38E078;
                        }
                        
                        #status-bar {
                            background-color: rgba(26, 26, 26, 0.8);
                            border-top: 1px solid #2d2d2d;
                            color: #adb5bd;
                        }
                        """
                    else:
                        # Light theme specific overrides
                        stylesheet += """
                        /* Light theme specific overrides */
                        #app-container {
                            background-color: #f8f9fa;
                        }
                        
                        #sidebar-nav {
                            background-color: #f0f2f5;
                            border-right: 1px solid #e9ecef;
                        }
                        
                        #header-search-container {
                            background-color: rgba(240, 240, 240, 0.5);
                            border: 1px solid rgba(0, 0, 0, 0.05);
                        }
                        
                        #header-search-button {
                            color: #888;
                        }
                        
                        #nav-button {
                            color: #555;
                        }
                        
                        #nav-button:hover {
                            background-color: rgba(255, 255, 255, 0.8);
                        }
                        
                        #nav-button:checked {
                            background-color: #e5f7ea;
                            color: #28C058;
                        }
                        
                        #status-bar {
                            background-color: rgba(240, 240, 240, 0.5);
                            border-top: 1px solid #e9ecef;
                            color: #888;
                        }
                        """
        except Exception as e:
            print(f"Failed to load modern UI styles: {e}")
        
        # Apply the combined stylesheet
        QApplication.instance().setStyleSheet(stylesheet)
        
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
            
            # Update theme mode label
            theme_mode_label = self.parent.findChild(QLabel, "theme-mode-label")
            if theme_mode_label:
                theme_mode_label.setText("Dark Mode" if theme_name == "dark" else "Light Mode")
        
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
        container.setFixedWidth(130)
        
        # Create layout
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
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
            
        toggle.clicked = toggle_theme
        
        # Add widgets to layout
        layout.addWidget(mode_label)
        layout.addWidget(toggle)
        
        return container