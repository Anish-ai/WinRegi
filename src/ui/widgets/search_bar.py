"""
Search bar widget for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QHBoxLayout, 
    QVBoxLayout, QLabel, QCompleter, QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

class SearchBar(QWidget):
    """Search bar widget with AI-powered search functionality"""
    
    # Signal emitted when search is requested
    search_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize search bar widget
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        from PyQt5.QtGui import QFont, QIcon
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Create search heading
        heading = QLabel("Ask AI to find Windows settings")
        heading.setObjectName("search-heading")
        
        # Create heading font
        heading_font = QFont()
        heading_font.setPointSize(16)
        heading_font.setBold(True)
        heading.setFont(heading_font)
        
        layout.addWidget(heading)
        
        # Create search container with styling
        search_container = QWidget()
        search_container.setObjectName("search-container")
        search_container.setMinimumHeight(50)
        search_container.setProperty("class", "search-container")
        
        # Create search bar layout
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_layout.setSpacing(10)
        
        # Create search icon
        search_icon = QLabel("🔍")
        search_icon.setFixedSize(24, 24)
        search_icon.setObjectName("search-icon")
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search-input")
        self.search_input.setPlaceholderText("Type your question (e.g., 'How to turn on night light?')")
        self.search_input.setMinimumHeight(40)
        self.search_input.returnPressed.connect(self.on_search)
        
        # Remove border from search input
        self.search_input.setStyleSheet("border: none; background: transparent; font-size: 14px;")
        
        # Create search button
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("search-button")
        self.search_button.setMinimumHeight(36)
        self.search_button.setFixedWidth(100)
        self.search_button.clicked.connect(self.on_search)
        
        # Add widgets to search layout
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
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
        examples_heading.setStyleSheet("font-weight: bold; color: #555;")
        
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
            example_button = QPushButton(example)
            example_button.setObjectName("example-button")
            example_button.setProperty("class", "example-button")
            example_button.setCursor(Qt.PointingHandCursor)
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
        """Use an example query
        
        Args:
            example_text: Example query text
        """
        self.search_input.setText(example_text)
        self.on_search()
    
    def set_completer(self, items):
        """Set completer for search input
        
        Args:
            items: List of completion items
        """
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(completer)
    
    def on_search(self):
        """Handle search button click or Enter key press"""
        query = self.search_input.text().strip()
        if query:
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