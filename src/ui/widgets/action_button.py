"""
Action button widget for WinRegi application
"""
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, pyqtSignal

class ActionButton(QPushButton):
    """Enhanced button for actions with description"""
    
    def __init__(self, title, description=None, action_type="default", parent=None):
        """Initialize action button
        
        Args:
            title: Button title
            description: Button description (optional)
            action_type: Action type (default, primary, warning, etc.)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store data
        self.action_title = title
        self.action_description = description
        self.action_type = action_type
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set button text
        self.setText(self.action_title)
        
        # Set button properties
        self.setObjectName("action-button")
        
        # Add class based on action type
        if self.action_type == "primary":
            self.setProperty("class", "action-button primary-action")
        elif self.action_type == "warning":
            self.setProperty("class", "action-button warning-action")
        else:
            self.setProperty("class", "action-button")
        
        # Set tooltip
        if self.action_description:
            self.setToolTip(self.action_description)

class DetailedActionButton(QWidget):
    """Action button with title and description"""
    
    # Signal emitted when button is clicked
    clicked = pyqtSignal()
    
    def __init__(self, title, description=None, action_type="default", parent=None):
        """Initialize detailed action button
        
        Args:
            title: Button title
            description: Button description (optional)
            action_type: Action type (default, primary, warning, etc.)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store data
        self.action_title = title
        self.action_description = description
        self.action_type = action_type
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Create button
        self.button = ActionButton(self.action_title, self.action_description, self.action_type)
        self.button.clicked.connect(self.clicked.emit)
        layout.addWidget(self.button)
        
        # Create description label
        if self.action_description:
            self.description_label = QLabel(self.action_description)
            self.description_label.setObjectName("action-description")
            self.description_label.setStyleSheet("color: #777; font-size: 11px;")
            self.description_label.setWordWrap(True)
            self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            layout.addWidget(self.description_label)
    
    def setEnabled(self, enabled):
        """Set whether the button is enabled
        
        Args:
            enabled: Whether the button should be enabled
        """
        self.button.setEnabled(enabled)
        super().setEnabled(enabled)