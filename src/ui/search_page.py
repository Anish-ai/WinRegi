"""
Search page for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets.search_bar import SearchBar
from .widgets.setting_card import SettingCard

class SearchPage(QWidget):
    """Search page with AI-powered search functionality"""
    
    # Signal emitted when a setting is selected
    setting_selected = pyqtSignal(int)
    # Signal emitted when a command is selected
    command_selected = pyqtSignal(int)
    
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
        
        # Get command manager if available
        try:
            from ..windows_api.command_manager import CommandManager
            self.command_manager = CommandManager(self.db_manager)
        except ImportError:
            self.command_manager = None
    
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
        
        # Create results header with animation
        self.results_header = QLabel("Recommended Settings & Commands")
        self.results_header.setObjectName("results-header")
        self.results_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #28C058;")
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
    
    def on_search(self):
        """Handle search button click"""
        # Get search query
        query = self.search_bar.get_query()
        
        if not query:
            return
        
        # Update header
        self.results_header.setText(f"Search Results for '{query}'")
        
        try:
            # Get search results
            results = self.search_engine.search(query)
            
            # Show results
            self.show_results(results)
        except Exception as e:
            print(f"Error during search: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error message
            self.clear_results()
            error_label = QLabel(f"An error occurred during search: {str(e)}")
            error_label.setStyleSheet("color: red;")
            error_label.setWordWrap(True)
            self.results_layout.addWidget(error_label)
    
    def show_recommendations(self):
        """Show recommended settings"""
        # Get recommendations
        recommendations = self.search_engine.get_setting_recommendations()
        
        # Show results
        self.show_results(recommendations)
    
    def show_results(self, results):
        """Show search results
        
        Args:
            results: List of search results
        """
        # Clear previous results
        self.clear_results()
        
        if not results:
            # Show no results message
            no_results = QLabel("No results found. Try a different search term.")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("color: #777; padding: 20px;")
            self.results_layout.addWidget(no_results)
            return
        
        # Group results by type
        settings_results = [r for r in results if r.get('result_type', '') == 'setting']
        command_results = [r for r in results if r.get('result_type', '') == 'command']
        
        # Show settings results
        if settings_results:
            # Add settings header
            settings_header = QLabel("Settings")
            settings_header.setObjectName("results-section-header")
            settings_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
            self.results_layout.addWidget(settings_header)
            
            # Add setting cards
            for result in settings_results:
                setting_card = SettingCard(
                    result['id'],
                    result['name'],
                    result.get('description', ''),
                    result.get('category_name', '')
                )
                
                # Connect signals
                setting_card.clicked.connect(self.on_setting_selected)
                setting_card.action_requested.connect(self.on_setting_action)
                
                # Add to layout
                self.results_layout.addWidget(setting_card)
        
        # Show command results
        if command_results:
            # Add commands header
            commands_header = QLabel("Commands")
            commands_header.setObjectName("results-section-header")
            commands_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
            self.results_layout.addWidget(commands_header)
            
            # Add command cards
            for result in command_results:
                # Create a setting card for the command (reusing the component)
                command_card = SettingCard(
                    result['id'],
                    result['name'],
                    result.get('description', ''),
                    result.get('category_name', 'Command')
                )
                
                # Set action button text to "Execute" for commands
                command_card.action_button.setText("Execute")
                
                # Connect signals - use command-specific handlers
                command_card.clicked.connect(self.on_command_selected)
                command_card.action_requested.connect(self.on_command_action)
                
                # Add to layout
                self.results_layout.addWidget(command_card)
        
        # Add stretch to push results to the top
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
        msg_box = QMessageBox()
        
        if result.get('success', False):
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Operation Successful")
            msg_box.setText(f"Action '{default_action['name']}' completed successfully.")
            if result.get('message'):
                msg_box.setDetailedText(result.get('message'))
        else:
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Operation Failed")
            msg_box.setText(f"Action '{default_action['name']}' failed.")
            if result.get('message'):
                msg_box.setDetailedText(result.get('message'))
        
        # Add buttons
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Show the message box
        msg_box.exec_()
    
    def on_command_selected(self, command_id):
        """Handle command selection
        
        Args:
            command_id: Selected command ID
        """
        # Emit signal to show command details
        self.command_selected.emit(command_id)
    
    def on_command_action(self, command_id):
        """Handle command action request (execute)
        
        Args:
            command_id: Command ID
        """
        print(f"Executing command with ID: {command_id}")
        
        if not hasattr(self, 'command_manager') or not self.command_manager:
            # Try to create command manager if it doesn't exist
            try:
                from ..windows_api.command_manager import CommandManager
                self.command_manager = CommandManager(self.db_manager)
            except ImportError as e:
                print(f"Error importing CommandManager: {e}")
                QMessageBox.warning(
                    self,
                    "Error",
                    "Command execution is not available."
                )
                return
        
        # Get command details
        command = self.db_manager.get_command_by_id(command_id)
        if not command:
            print(f"Command with ID {command_id} not found")
            return
        
        print(f"Executing command: {command['name']}")
        print(f"Command type: {command['command_type']}")
        print(f"Command value: {command['command_value']}")
        
        # Execute command
        success, output = self.command_manager.execute_command(command_id)
        
        print(f"Command execution result: {'Success' if success else 'Failed'}")
        if output:
            print(f"Output: {output}")
        
        # Show result based on command type
        if command["command_type"] in ["powershell", "batch"]:
            # These command types can produce output that's useful to show
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Command Execution Result")
            
            if success:
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText(f"Command '{command['name']}' executed successfully.")
                if output:
                    msg_box.setDetailedText(output)
            else:
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText(f"Command '{command['name']}' failed to execute.")
                msg_box.setDetailedText(output)
            
            msg_box.exec_()
        else:
            # Other command types may not produce useful output
            if not success:
                QMessageBox.warning(
                    self,
                    "Command Failed",
                    f"Command '{command['name']}' failed to execute:\n{output}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Command Executed",
                    f"Command '{command['name']}' executed successfully."
                )