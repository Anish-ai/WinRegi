"""
Modern animated search bar widget for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QHBoxLayout, 
    QVBoxLayout, QLabel, QCompleter, QListWidget,
    QGraphicsDropShadowEffect, QSizePolicy, QFrame
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QPropertyAnimation, 
    QEasingCurve, QTimer, QRect, QPoint, pyqtProperty
)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPainterPath, QFont

class AnimatedButton(QPushButton):
    """Button with press animation effect"""
    
    def __init__(self, text="", parent=None):
        """Initialize animated button
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        # Set properties
        self.setObjectName("search-button")
        self.setCursor(Qt.PointingHandCursor)
        
        # Initialize animation properties
        self._scale_factor = 1.0
        self._hover_state = 0.0
        
        # Create press animation
        self._press_animation = QPropertyAnimation(self, b"scale_factor")
        self._press_animation.setDuration(100)
        self._press_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # Create hover animation
        self._hover_animation = QPropertyAnimation(self, b"hover_state")
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
    
    # Define property for animation
    scale_factor = pyqtProperty(float, get_scale_factor, set_scale_factor)
    
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
        self.update()
    
    # Define property for animation
    hover_state = pyqtProperty(float, get_hover_state, set_hover_state)
    
    def enterEvent(self, event):
        """Handle mouse enter event
        
        Args:
            event: Enter event
        """
        # Add hover effect
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event
        
        Args:
            event: Leave event
        """
        # Remove hover effect
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press event
        
        Args:
            event: Mouse event
        """
        if event and event.button() == Qt.LeftButton:
            self._is_pressed = True
            
            # Start press animation
            self._press_animation.setStartValue(1.0)
            self._press_animation.setEndValue(0.95)
            self._press_animation.start()
            
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        if event and event.button() == Qt.LeftButton and self._is_pressed:
            self._is_pressed = False
            
            # Start release animation
            self._press_animation.setStartValue(0.95)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()
            
        super().mouseReleaseEvent(event)
    
    def simulate_click(self):
        """Simulate a button click with animation"""
        # Start press animation
        self._press_animation.setStartValue(1.0)
        self._press_animation.setEndValue(0.95)
        self._press_animation.start()
        
        # Schedule release animation
        QTimer.singleShot(100, lambda: self._simulate_release())
    
    def _simulate_release(self):
        """Simulate button release part of the animation"""
        # Start release animation
        self._press_animation.setStartValue(0.95)
        self._press_animation.setEndValue(1.0)
        self._press_animation.start()
    
    def paintEvent(self, event):
        """Custom paint event to apply scale transform
        
        Args:
            event: Paint event
        """
        # Save painter state
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Scale the button
        painter.save()
        
        # Apply scale transform
        painter.translate(self.rect().center())
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-self.rect().center())
        
        # Draw button
        super().paintEvent(event)
        
        # Restore painter state
        painter.restore()

class ExampleButton(QPushButton):
    """Pill-shaped example button with hover animation"""
    
    def __init__(self, text, parent=None):
        """Initialize example button
        
        Args:
            text: Button text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        # Set properties
        self.setObjectName("example-button")
        self.setProperty("class", "example-button")
        self.setCursor(Qt.PointingHandCursor)
        
        # Initialize hover value
        self._hover_value = 0.0
        
        # Create hover animation
        self._hover_animation = QPropertyAnimation(self, b"hover_value")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    def get_hover_value(self):
        """Get hover value
        
        Returns:
            Current hover value
        """
        return self._hover_value
    
    def set_hover_value(self, value):
        """Set hover value
        
        Args:
            value: New hover value
        """
        self._hover_value = value
        self.update()
    
    # Define property for animation - using a different name from the instance variable 
    # to avoid recursion
    hover_value = pyqtProperty(float, get_hover_value, set_hover_value)
    
    def enterEvent(self, event):
        """Handle mouse enter event
        
        Args:
            event: Enter event
        """
        # Start hover animation
        self._hover_animation.setStartValue(0.0)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event
        
        Args:
            event: Leave event
        """
        # Start hover animation
        self._hover_animation.setStartValue(1.0)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event with hover effect
        
        Args:
            event: Paint event
        """
        # Use default paint event for now
        # Can be customized further if needed
        super().paintEvent(event)

class SearchBar(QWidget):
    """Modern search bar widget with AI-powered search functionality"""
    
    # Signal emitted when search is requested
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize search bar widget
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize state
        self._is_expanded = False
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Create search heading
        heading = QLabel("Ask AI to find Windows settings")
        heading.setObjectName("search-heading")
        
        # Create heading font
        heading_font = QFont("Segoe UI", 20, QFont.Bold)
        heading.setFont(heading_font)
        
        layout.addWidget(heading)
        
        # Create search container with styling
        search_container = QFrame()
        search_container.setObjectName("search-container")
        search_container.setMinimumHeight(56)
        search_container.setProperty("class", "search-container")
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        search_container.setGraphicsEffect(shadow)
        
        # Create search bar layout
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 0, 20, 0)
        search_layout.setSpacing(10)
        
        # Create search icon
        self.search_icon = QLabel("🔍")
        self.search_icon.setFixedSize(24, 24)
        self.search_icon.setObjectName("search-icon")
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search-input")
        self.search_input.setPlaceholderText("Type your question (e.g., 'How to turn on night light?')")
        self.search_input.setMinimumHeight(40)
        self.search_input.returnPressed.connect(self.on_search)
        
        # Create search button with animation
        self.search_button = AnimatedButton("Search")
        self.search_button.setObjectName("search-button")
        self.search_button.setMinimumHeight(40)
        self.search_button.setFixedWidth(100)
        self.search_button.clicked.connect(self.on_search)
        
        # Add widgets to search layout
        search_layout.addWidget(self.search_icon)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        
        # Add search container to main layout
        layout.addWidget(search_container)
        
        # Create examples section
        examples_container = QWidget()
        examples_container.setObjectName("examples-container")
        
        examples_layout = QVBoxLayout(examples_container)
        examples_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create examples heading
        examples_heading = QLabel("Try asking:")
        examples_heading.setObjectName("examples-heading")
        examples_heading.setStyleSheet("font-weight: bold; color: #555; font-family: 'Segoe UI';")
        
        # Create examples
        examples = [
            "How to speed up my PC?", 
            "Turn off telemetry", 
            "Disable startup programs",
            "Change power settings",
            "Enable dark mode"
        ]
        
        # Add examples heading
        examples_layout.addWidget(examples_heading)
        
        # Create examples buttons layout
        examples_buttons_layout = QHBoxLayout()
        examples_buttons_layout.setSpacing(10)
        
        # Add example buttons
        for example in examples:
            example_button = ExampleButton(example)
            example_button.clicked.connect(lambda checked, text=example: self.use_example(text))
            examples_buttons_layout.addWidget(example_button)
        
        # Add stretch to ensure buttons don't expand too much
        examples_buttons_layout.addStretch()
        
        # Add example buttons layout to examples layout
        examples_layout.addLayout(examples_buttons_layout)
        
        # Add examples container to main layout
        layout.addWidget(examples_container)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Set focus to search input
        self.search_input.setFocus()
    
    def use_example(self, example_text):
        """Use an example query with animation
        
        Args:
            example_text: Example query text
        """
        # Set text with typing effect
        self.search_input.clear()
        self.search_input.setFocus()
        
        # Schedule delayed typing effect
        self._current_text = ""
        self._target_text = example_text
        self._type_index = 0
        
        # Start typing
        QTimer.singleShot(100, self.type_next_character)
    
    def type_next_character(self):
        """Type next character in the example text"""
        if self._type_index < len(self._target_text):
            # Add next character
            self._current_text += self._target_text[self._type_index]
            self.search_input.setText(self._current_text)
            self.search_input.setCursorPosition(len(self._current_text))
            
            # Schedule next character
            self._type_index += 1
            QTimer.singleShot(30, self.type_next_character)
        else:
            # Typing complete, trigger search
            QTimer.singleShot(300, self.on_search)
    
    def set_completer(self, items):
        """Set completer for search input
        
        Args:
            items: List of completion items
        """
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.search_input.setCompleter(completer)
    
    def on_search(self):
        """Handle search button click or Enter key press with animation"""
        query = self.search_input.text().strip()
        if query:
            # Use the safer simulate_click method instead of directly calling mousePressEvent/mouseReleaseEvent
            try:
                self.search_button.simulate_click()
            except Exception as e:
                print(f"Button animation error (ignoring): {e}")
            
            # Emit search signal after slight delay for better UX
            self.search_requested.emit(query)
    
    def get_query(self):
        """Get the current search query
        
        Returns:
            Current search query
        """
        return self.search_input.text().strip()
    
    def set_query(self, query):
        """Set the search query
        
        Args:
            query: Search query to set
        """
        self.search_input.setText(query)
    
    def clear(self):
        """Clear the search input"""
        self.search_input.clear()