"""
Search page for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets.search_bar import SearchBar
from .widgets.setting_card import SettingCard

class SearchPage(QWidget):
    """Search page with AI-powered search functionality"""
    
    # Signal emitted when a setting is selected
    setting_selected = pyqtSignal(int)
    
    def __init__(self, search_engine, settings_manager, db_manager, parent=None):
        """Initialize search page
        
        Args:
            search_engine: Search engine instance
            settings_manager: Settings manager instance
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store managers
        self.search_engine = search_engine
        self.settings_manager = settings_manager
        self.db_manager = db_manager
        
        # Initialize state
        self.search_results = []
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create search bar
        self.search_bar = SearchBar()
        self.search_bar.search_requested.connect(self.on_search)
        layout.addWidget(self.search_bar)
        
        # Create results section
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(0, 20, 0, 0)
        
        # Create results header
        self.results_header = QLabel("Recommended Settings")
        self.results_header.setObjectName("results-header")
        self.results_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        results_layout.addWidget(self.results_header)
        
        # Create results container
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(10)
        
        # Create scroll area for results
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(self.results_container)
        results_layout.addWidget(scroll_area)
        
        # Add results section to main layout
        layout.addLayout(results_layout)
        
        # Show initial recommendations
        self.show_recommendations()
    
    def on_search(self, query):
        """Handle search request
        
        Args:
            query: Search query
        """
        # Update header
        self.results_header.setText(f"Search Results for: {query}")
        
        # Clear previous results
        self.clear_results()
        
        # Perform search
        self.search_results = self.search_engine.search(query)
        
        # Show results
        self.show_results(self.search_results)
    
    def show_recommendations(self):
        """Show recommended settings"""
        # Get recommendations
        recommendations = self.search_engine.get_setting_recommendations()
        
        # Show results
        self.show_results(recommendations)
    
    def show_results(self, results):
        """Show search results
        
        Args:
            results: List of result dictionaries
        """
        # Clear previous results
        self.clear_results()
        
        if not results:
            # Show no results message
            no_results = QLabel("No settings found. Try a different search query.")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("color: #777; padding: 20px;")
            self.results_layout.addWidget(no_results)
            return
        
        # Add setting cards for each result
        for result in results:
            # Create setting card
            setting_card = SettingCard(
                result['id'],
                result['name'],
                result['description'],
                result.get('category_name', '')
            )
            
            # Connect signals
            setting_card.clicked.connect(self.on_setting_selected)
            setting_card.action_requested.connect(self.on_setting_action)
            
            # Add to layout
            self.results_layout.addWidget(setting_card)
        
        # Add stretch to push cards to the top
        self.results_layout.addStretch()
    
    def clear_results(self):
        """Clear search results"""
        # Remove all widgets from results layout
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def on_setting_selected(self, setting_id):
        """Handle setting selection
        
        Args:
            setting_id: Selected setting ID
        """
        # Emit signal to show setting details
        self.setting_selected.emit(setting_id)
    
    def on_setting_action(self, setting_id):
        """Handle setting action request
        
        Args:
            setting_id: Setting ID
        """
        # Get setting details
        setting = self.db_manager.get_setting_by_id(setting_id)
        
        if not setting:
            return
        
        # Get recommended actions for the setting
        actions = self.settings_manager.get_recommended_actions(setting_id, self.db_manager)
        
        if not actions:
            return
        
        # Get default action (if any)
        default_action = next((action for action in actions if action.get('is_default', 0) == 1), actions[0])
        
        # Apply the action
        result = self.settings_manager.apply_setting_action(default_action)
        
        # Check if admin privileges are required
        if result.get('requires_admin', False):
            from PyQt5.QtWidgets import QMessageBox
            
            # Show admin privileges required message
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Administrator Privileges Required")
            msg_box.setText("This operation requires administrator privileges.")
            
            # Add detailed text with instructions
            msg_box.setDetailedText(
                "To perform this operation, you need to:\n\n"
                "1. Close this application\n"
                "2. Right-click on the application shortcut\n"
                "3. Select 'Run as administrator'\n"
                "4. Try this operation again"
            )
            
            # Add buttons
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # Show the message box
            msg_box.exec_()
            return
        
        # Show result in a notification
        from PyQt5.QtWidgets import QMessageBox
        
        # Create message box
        msg_box = QMessageBox()
        
        if result.get('success', False):
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Operation Successful")
        else:
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Operation Failed")
        
        # Set text
        msg_box.setText(result.get('message', 'Operation completed'))
        
        # Add buttons
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Show the message box
        msg_box.exec_()