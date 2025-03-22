"""
Theme manager for WinRegi application
Handles application theme switching and styling
"""
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSlider, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

class ThemeToggleSwitch(QWidget):
    """Custom toggle switch widget for theme switching"""
    
    # Signal emitted when toggled
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        """Initialize theme toggle switch
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set fixed size
        self.setFixedSize(50, 26)
        
        # Initialize state
        self._checked = False
        self._track_color = QColor(200, 200, 200)
        self._thumb_color = QColor(255, 255, 255)
        self._track_opacity = 0.6
        
        # Animation properties
        self._thumb_position = 4  # Start position (left)
        
        # Create animation
        self._animation = QPropertyAnimation(self, b"thumb_position")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
    
    def get_thumb_position(self):
        """Get thumb position property
        
        Returns:
            Current thumb position
        """
        return self._thumb_position
    
    def set_thumb_position(self, position):
        """Set thumb position property
        
        Args:
            position: New thumb position
        """
        self._thumb_position = position
        self.update()
    
    # Define property for animation
    thumb_position = pyqtProperty(float, get_thumb_position, set_thumb_position)
    
    def isChecked(self):
        """Get checked state
        
        Returns:
            True if switch is checked, False otherwise
        """
        return self._checked
    
    def setChecked(self, checked):
        """Set checked state
        
        Args:
            checked: New checked state
        """
        if self._checked != checked:
            self._checked = checked
            
            # Update thumb position based on checked state
            end_position = 28 if checked else 4
            
            # Animate thumb position
            self._animation.setStartValue(self._thumb_position)
            self._animation.setEndValue(end_position)
            self._animation.start()
            
            # Update colors
            if checked:
                self._track_color = QColor(56, 224, 120, 128)  # Green with alpha
                self._thumb_color = QColor(56, 224, 120)  # Green
            else:
                self._track_color = QColor(200, 200, 200, 128)  # Gray with alpha
                self._thumb_color = QColor(255, 255, 255)  # White
            
            # Emit toggled signal
            self.toggled.emit(checked)
    
    def paintEvent(self, event):
        """Custom paint event
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track
        track_opacity = self._track_opacity
        if self._checked:
            track_color = QColor(56, 224, 120, int(255 * track_opacity))
        else:
            track_color = QColor(200, 200, 200, int(255 * track_opacity))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 13, 13)
        
        # Draw thumb
        painter.setBrush(self._thumb_color)
        painter.drawEllipse(
            int(self._thumb_position),
            3,
            20,
            20
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)
            self.update()

class ThemeManager:
    """Manages application themes and styles"""
    
    def __init__(self, parent=None):
        """Initialize theme manager
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.current_theme = "light"
        
        # Theme stylesheets
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme()
        }
    
    def _get_light_theme(self):
        """Get light theme stylesheet
        
        Returns:
            Light theme stylesheet
        """
        return """
        /* Main window */
        #main-window {
            background-color: #f5f5f5;
        }
        
        #app-container {
            background-color: #ffffff;
            border-radius: 10px;
        }
        
        /* Header */
        #app-header {
            background-color: #ffffff;
            border-bottom: 1px solid #e0e0e0;
        }
        
        #app-title {
            color: #333333;
        }
        
        #app-subtitle {
            color: #666666;
        }
        
        /* Sidebar */
        #sidebar-nav {
            background-color: #f5f5f5;
            border-right: 1px solid #e0e0e0;
        }
        
        #nav-button {
            background-color: transparent;
            color: #333333;
            border: none;
            text-align: left;
            padding-left: 15px;
        }
        
        #nav-button:hover {
            background-color: #e8e8e8;
        }
        
        #nav-button:checked {
            background-color: #e0f2f1;
            color: #28C058;
        }
        
        #settings-button {
            background-color: #f0f0f0;
            color: #333333;
            border: 1px solid #e0e0e0;
        }
        
        #settings-button:hover {
            background-color: #e8e8e8;
        }
        
        /* Window controls */
        #minimize-btn, #maximize-btn, #close-btn {
            background-color: transparent;
            border: none;
            border-radius: 12px;
            color: #666666;
            font-weight: bold;
        }
        
        #minimize-btn:hover, #maximize-btn:hover {
            background-color: #e0e0e0;
        }
        
        #close-btn:hover {
            background-color: #ff5252;
            color: white;
        }
        
        /* Content area */
        #content-area {
            background-color: #ffffff;
        }
        
        /* Status bar */
        #status-bar {
            background-color: #f5f5f5;
            color: #666666;
            border-top: 1px solid #e0e0e0;
        }
        
        /* Search bar */
        #search-heading {
            color: #333333;
        }
        
        #search-container {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        #search-input {
            border: none;
            background-color: transparent;
            color: #333333;
        }
        
        #search-button {
            background-color: #28C058;
            color: white;
            border: none;
        }
        
        /* Setting cards */
        .setting-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        /* Action buttons */
        .action-button {
            background-color: #f0f0f0;
            color: #333333;
            border: 1px solid #e0e0e0;
        }
        
        .primary-action {
            background-color: #28C058;
            color: white;
            border: none;
        }
        
        .warning-action {
            background-color: #ff5252;
            color: white;
            border: none;
        }
        """
    
    def _get_dark_theme(self):
        """Get dark theme stylesheet
        
        Returns:
            Dark theme stylesheet
        """
        return """
        /* Main window */
        #main-window {
            background-color: #121212;
        }
        
        #app-container {
            background-color: #1e1e1e;
            border-radius: 10px;
        }
        
        /* Header */
        #app-header {
            background-color: #1e1e1e;
            border-bottom: 1px solid #333333;
        }
        
        #app-title {
            color: #ffffff;
        }
        
        #app-subtitle {
            color: #aaaaaa;
        }
        
        /* Sidebar */
        #sidebar-nav {
            background-color: #252525;
            border-right: 1px solid #333333;
        }
        
        #nav-button {
            background-color: transparent;
            color: #e0e0e0;
            border: none;
            text-align: left;
            padding-left: 15px;
        }
        
        #nav-button:hover {
            background-color: #333333;
        }
        
        #nav-button:checked {
            background-color: #1e372a;
            color: #38E078;
        }
        
        #settings-button {
            background-color: #333333;
            color: #e0e0e0;
            border: 1px solid #444444;
        }
        
        #settings-button:hover {
            background-color: #444444;
        }
        
        /* Window controls */
        #minimize-btn, #maximize-btn, #close-btn {
            background-color: transparent;
            border: none;
            border-radius: 12px;
            color: #aaaaaa;
            font-weight: bold;
        }
        
        #minimize-btn:hover, #maximize-btn:hover {
            background-color: #333333;
        }
        
        #close-btn:hover {
            background-color: #ff5252;
            color: white;
        }
        
        /* Content area */
        #content-area {
            background-color: #1e1e1e;
        }
        
        /* Status bar */
        #status-bar {
            background-color: #252525;
            color: #aaaaaa;
            border-top: 1px solid #333333;
        }
        
        /* Search bar */
        #search-heading {
            color: #e0e0e0;
        }
        
        #search-container {
            background-color: #252525;
            border: 1px solid #333333;
        }
        
        #search-input {
            border: none;
            background-color: transparent;
            color: #e0e0e0;
        }
        
        #search-button {
            background-color: #38E078;
            color: white;
            border: none;
        }
        
        /* Setting cards */
        .setting-card {
            background-color: #252525;
            border: 1px solid #333333;
        }
        
        /* Action buttons */
        .action-button {
            background-color: #333333;
            color: #e0e0e0;
            border: 1px solid #444444;
        }
        
        .primary-action {
            background-color: #38E078;
            color: white;
            border: none;
        }
        
        .warning-action {
            background-color: #ff5252;
            color: white;
            border: none;
        }
        """
    
    def apply_theme(self, theme_name):
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
    
    def create_theme_toggle(self, parent=None):
        """Create a theme toggle switch widget
        
        Args:
            parent: Parent widget
            
        Returns:
            Theme toggle widget
        """
        # Create container widget
        container = QWidget(parent)
        container.setObjectName("theme-toggle-container")
        
        # Create layout
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create toggle switch
        toggle = ThemeToggleSwitch(parent)
        toggle.setObjectName("theme-toggle")
        toggle.setChecked(self.current_theme == "dark")
        toggle.toggled.connect(lambda checked: parent.toggle_theme())
        
        # Add widgets to layout
        layout.addWidget(toggle)
        
        return container