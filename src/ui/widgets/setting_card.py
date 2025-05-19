"""
Modern setting card widget for WinRegi application with animations and effects
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, 
    QVBoxLayout, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QPropertyAnimation, 
    QEasingCurve, QTimer, QRect, QPoint, pyqtProperty
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QPainter, QPainterPath

class AnimatedButton(QPushButton):
    """Button with hover, press and click animations"""
    
    def __init__(self, text="", parent=None):
        """Initialize animated button
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        # Set cursor to pointing hand
        self.setCursor(Qt.PointingHandCursor)
        
        # Initialize state
        self._scale_factor = 1.0
        self._hover_opacity = 0.0
        self._is_pressed = False
        
        # Create scale animation
        self._scale_animation = QPropertyAnimation(self, b"scale_factor")
        self._scale_animation.setDuration(100)
        self._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Create hover animation
        self._hover_animation = QPropertyAnimation(self, b"hover_opacity")
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def get_scale_factor(self):
        """Get scale factor property
        
        Returns:
            Current scale factor
        """
        return self._scale_factor
    
    def set_scale_factor(self, factor):
        """Set scale factor property
        
        Args:
            factor: New scale factor
        """
        self._scale_factor = factor
        self.update()
    
    # Define property for scale animation
    scale_factor = pyqtProperty(float, get_scale_factor, set_scale_factor)
    
    def get_hover_opacity(self):
        """Get hover opacity property
        
        Returns:
            Current hover opacity
        """
        return self._hover_opacity
    
    def set_hover_opacity(self, opacity):
        """Set hover opacity property
        
        Args:
            opacity: New hover opacity
        """
        self._hover_opacity = opacity
        self.update()
    
    # Define property for hover animation
    hover_opacity = pyqtProperty(float, get_hover_opacity, set_hover_opacity)
    
    def enterEvent(self, event):
        """Handle mouse enter event
        
        Args:
            event: Enter event
        """
        # Start hover animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event
        
        Args:
            event: Leave event
        """
        # Start hover animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_opacity)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            
            # Start press animation
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(0.95)
            self._scale_animation.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton and self._is_pressed:
            self._is_pressed = False
            
            # Start release animation
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(1.0)
            self._scale_animation.start()
        
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event with animation effects
        
        Args:
            event: Paint event
        """
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Save state
        painter.save()
        
        # Apply scale transform if pressed
        painter.translate(self.rect().center())
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-self.rect().center())
        
        # Draw button (base class implementation)
        super().paintEvent(event)
        
        # Draw hover overlay if hovered
        if self._hover_opacity > 0:
            # Create a semi-transparent overlay
            painter.setOpacity(self._hover_opacity * 0.1)
            
            if self.property("class") == "primary-action":
                painter.fillRect(self.rect(), QColor("#ffffff"))
            else:
                # Different hover effect for secondary buttons
                painter.fillRect(self.rect(), QColor("#000000"))
        
        # Restore state
        painter.restore()

class SettingCard(QFrame):
    """Modern card widget displaying a Windows setting with animations"""
    
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
        
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)
        
        # Add mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Initialize animation properties
        self._hover_state = 0.0
        self._y_offset = 0.0

        # Store the original y position
        self._original_y = None
        
        # Create hover animation
        self._hover_animation = QPropertyAnimation(self, b"hover_state")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Create elevation animation
        self._elevation_animation = QPropertyAnimation(self, b"y_offset")
        self._elevation_animation.setDuration(200)
        self._elevation_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def get_hover_state(self):
        """Get hover state property
        
        Returns:
            Current hover state
        """
        return self._hover_state
    
    def set_hover_state(self, state):
        """Set hover state property
        
        Args:
            state: New hover state
        """
        self._hover_state = state
        
        # Update shadow blur radius and color based on hover state
        self.shadow.setBlurRadius(15 + self._hover_state * 10)
        
        # Interpolate shadow opacity
        base_opacity = 40
        hover_opacity = 80
        opacity = int(base_opacity + self._hover_state * (hover_opacity - base_opacity))
        self.shadow.setColor(QColor(0, 0, 0, opacity))
        
        self.update()
    
    # Define property for hover animation
    hover_state = pyqtProperty(float, get_hover_state, set_hover_state)
    
    def get_y_offset(self):
        """Get Y offset property
        
        Returns:
            Current Y offset
        """
        return self._y_offset
    
    def set_y_offset(self, offset):
        """Set Y offset property
        
        Args:
            offset: New Y offset
        """
        # Store value and convert to int if needed
        self._y_offset = offset
        offset = int(offset)
        
        # Store original position if not already stored
        if self._original_y is None:
            self._original_y = self.y()
        
        # Apply offset transform by moving the widget relative to original position
        self.move(self.x(), self._original_y - offset)
    
    # Define property for elevation animation
    y_offset = pyqtProperty(float, get_y_offset, set_y_offset)
    
    def init_ui(self):
        """Initialize user interface"""
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
        self.name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        
        content_layout.addWidget(self.name_label)
        
        # Setting description
        if self.setting_description:
            self.description_label = QLabel(self.setting_description)
            self.description_label.setObjectName("setting-description")
            self.description_label.setWordWrap(True)
            self.description_label.setFont(QFont("Segoe UI", 10))
            
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
            self.category_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
            
            category_layout.addWidget(self.category_label)
            content_layout.addWidget(category_container)
        
        # Add content layout to main layout
        layout.addLayout(content_layout, 1)
        
        # Create button area
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        button_layout.setSpacing(8)
        
        # Details button
        self.details_button = AnimatedButton("Details")
        self.details_button.setObjectName("setting-details")
        self.details_button.setProperty("class", "action-button")
        self.details_button.setCursor(Qt.PointingHandCursor)
        self.details_button.clicked.connect(self.on_details)
        self.details_button.setMinimumHeight(36)
        
        # Action button
        self.action_button = AnimatedButton("Apply")
        self.action_button.setObjectName("setting-action")
        self.action_button.setProperty("class", "primary-action")
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.clicked.connect(self.on_action)
        self.action_button.setMinimumHeight(36)
        
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
    
    def enterEvent(self, event):
        """Handle mouse enter event with animation
        
        Args:
            event: Mouse event
        """
        # Start hover animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_state)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        # Start elevation animation
        self._elevation_animation.stop()
        self._elevation_animation.setStartValue(self._y_offset)
        self._elevation_animation.setEndValue(3.0)
        self._elevation_animation.start()
        
        # Change cursor to pointing hand
        self.setCursor(Qt.PointingHandCursor)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event with animation
        
        Args:
            event: Mouse event
        """
        # Start hover animation
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_state)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        # Start elevation animation
        self._elevation_animation.stop()
        self._elevation_animation.setStartValue(self._y_offset)
        self._elevation_animation.setEndValue(0.0)
        self._elevation_animation.start()
        
        # Reset cursor
        self.setCursor(Qt.ArrowCursor)
        
        super().leaveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            # Apply press-and-release animation
            self.setCursor(Qt.PointingHandCursor)
            
            # Emit clicked signal
            self.clicked.emit(self.setting_id)
        
        super().mouseReleaseEvent(event)
    
    def apply_consistent_styling(self):
        """Apply consistent styling to the card"""
        # Set consistent height
        self.setMinimumHeight(120)
        self.setMaximumHeight(160)
        
        # Set rounded corners and shadow
        self.setStyleSheet("""
            QFrame#setting-card {
                border-radius: 10px;
                background-color: white;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Ensure buttons have consistent size
        self.details_button.setFixedWidth(100)
        self.action_button.setFixedWidth(100)