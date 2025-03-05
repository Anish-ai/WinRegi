"""
Setting card widget for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, 
    QVBoxLayout, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap

class SettingCard(QFrame):
    """Card widget displaying a Windows setting"""
    
    # Signal emitted when card is clicked
    clicked = pyqtSignal(int)
    
    # Signal emitted when action button is clicked
    action_requested = pyqtSignal(int)
    
    def __init__(self, setting_id, name, description, category=None, parent=None):
        """Initialize setting card widget
        
        Args:
            setting_id: Setting ID
            name: Setting name
            description: Setting description
            category: Setting category (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store setting data
        self.setting_id = setting_id
        self.setting_name = name
        self.setting_description = description
        self.setting_category = category
        
        # Set up UI
        self.init_ui()
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setObjectName("setting-card")
        self.setProperty("class", "setting-card")
        
        # Add mouse tracking
        self.setMouseTracking(True)
    
    def init_ui(self):
        """Initialize user interface"""
        from PyQt5.QtGui import QFont, QIcon
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Create icon/category indicator
        icon_layout = QVBoxLayout()
        icon_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        
        # Create category icon/badge
        self.category_badge = QLabel()
        self.category_badge.setObjectName("category-badge")
        self.category_badge.setFixedSize(40, 40)
        self.category_badge.setAlignment(Qt.AlignCenter)
        
        # Set icon based on category (using emoji as fallback)
        category_icons = {
            "System": "⚙️",
            "Display": "🖥️",
            "Network": "🌐",
            "Privacy": "🔒",
            "Security": "🛡️",
            "Performance": "⚡",
            "Power": "🔋",
            "Apps": "📱",
            "Updates": "🔄",
            "Storage": "💾"
        }
        
        if self.setting_category in category_icons:
            self.category_badge.setText(category_icons.get(self.setting_category, "⚙️"))
        else:
            self.category_badge.setText("⚙️")
        
        self.category_badge.setStyleSheet("font-size: 24px; background-color: #f5f9ff; border-radius: 20px;")
        
        icon_layout.addWidget(self.category_badge)
        layout.addLayout(icon_layout)
        
        # Create content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        
        # Setting name with custom font
        self.name_label = QLabel(self.setting_name)
        self.name_label.setObjectName("setting-name")
        
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        content_layout.addWidget(self.name_label)
        
        # Setting description
        if self.setting_description:
            self.description_label = QLabel(self.setting_description)
            self.description_label.setObjectName("setting-description")
            self.description_label.setWordWrap(True)
            
            desc_font = QFont()
            desc_font.setPointSize(10)
            self.description_label.setFont(desc_font)
            
            content_layout.addWidget(self.description_label)
        
        # Setting category as a badge/tag
        if self.setting_category:
            category_container = QWidget()
            category_container.setObjectName("category-container")
            category_container.setFixedHeight(26)
            category_container.setMaximumWidth(150)
            
            category_layout = QHBoxLayout(category_container)
            category_layout.setContentsMargins(8, 2, 8, 2)
            
            self.category_label = QLabel(self.setting_category)
            self.category_label.setObjectName("setting-category")
            
            cat_font = QFont()
            cat_font.setPointSize(9)
            self.category_label.setFont(cat_font)
            
            category_layout.addWidget(self.category_label)
            content_layout.addWidget(category_container)
        
        # Add content layout to main layout
        layout.addLayout(content_layout, 1)
        
        # Create button area
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        button_layout.setSpacing(8)
        
        # Details button
        self.details_button = QPushButton("Details")
        self.details_button.setObjectName("setting-details")
        self.details_button.setProperty("class", "action-button")
        self.details_button.setCursor(Qt.PointingHandCursor)
        self.details_button.clicked.connect(self.on_details)
        
        # Action button
        self.action_button = QPushButton("Apply")
        self.action_button.setObjectName("setting-action")
        self.action_button.setProperty("class", "action-button primary-action")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.clicked.connect(self.on_action)
        
        button_layout.addWidget(self.details_button)
        button_layout.addWidget(self.action_button)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
    
    def on_details(self):
        """Handle details button click"""
        self.clicked.emit(self.setting_id)
    
    def on_action(self):
        """Handle action button click"""
        self.action_requested.emit(self.setting_id)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.setting_id)
        
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter event
        
        Args:
            event: Mouse event
        """
        # Change cursor to pointing hand
        self.setCursor(Qt.PointingHandCursor)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event
        
        Args:
            event: Mouse event
        """
        # Reset cursor
        self.setCursor(Qt.ArrowCursor)
        
        super().leaveEvent(event)