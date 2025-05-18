"""
Setting detail page for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets.action_button import ActionButton, DetailedActionButton

class SettingDetailPage(QWidget):
    """Detail page for a specific Windows setting"""
    
    def __init__(self, db_manager, settings_manager, parent=None):
        """Initialize setting detail page
        
        Args:
            db_manager: Database manager instance
            settings_manager: Settings manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store managers
        self.db_manager = db_manager
        self.settings_manager = settings_manager
        
        # Initialize state
        self.current_setting = None
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for content
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header section
        header_layout = QVBoxLayout()
        
        # Add back button
        back_button = QPushButton("← Back")
        back_button.setObjectName("back-button")
        back_button.setFixedWidth(100)
        back_button.clicked.connect(self.on_back_clicked)
        header_layout.addWidget(back_button)
        
        # Setting name
        self.name_label = QLabel()
        self.name_label.setObjectName("setting-name")
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.name_label)
        
        # Setting description
        self.description_label = QLabel()
        self.description_label.setObjectName("setting-description")
        self.description_label.setStyleSheet("color: #555; font-size: 14px;")
        self.description_label.setWordWrap(True)
        header_layout.addWidget(self.description_label)
        
        # Setting metadata
        metadata_layout = QHBoxLayout()
        
        # Category
        self.category_label = QLabel()
        self.category_label.setObjectName("setting-category")
        self.category_label.setStyleSheet("color: #777; font-size: 12px;")
        metadata_layout.addWidget(self.category_label)
        
        # Access method
        self.access_method_label = QLabel()
        self.access_method_label.setObjectName("setting-access-method")
        self.access_method_label.setStyleSheet("color: #777; font-size: 12px;")
        metadata_layout.addWidget(self.access_method_label)
        
        # Add metadata to header
        header_layout.addLayout(metadata_layout)
        
        # Add header to scroll layout
        scroll_layout.addLayout(header_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(separator)
        
        # Create actions section
        actions_group = QGroupBox("Available Actions")
        actions_group.setObjectName("actions-group")
        
        # Actions layout
        self.actions_layout = QVBoxLayout(actions_group)
        
        # Add actions group to scroll layout
        scroll_layout.addWidget(actions_group)
        
        # Create details section
        details_group = QGroupBox("Technical Details")
        details_group.setObjectName("details-group")
        
        # Details layout
        details_layout = QGridLayout(details_group)
        details_layout.setColumnStretch(1, 1)
        
        # Registry path
        details_layout.addWidget(QLabel("Registry Path:"), 0, 0)
        self.registry_path_label = QLabel()
        self.registry_path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.registry_path_label.setWordWrap(True)
        details_layout.addWidget(self.registry_path_label, 0, 1)
        
        # PowerShell command
        details_layout.addWidget(QLabel("PowerShell:"), 1, 0)
        self.powershell_label = QLabel()
        self.powershell_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.powershell_label.setWordWrap(True)
        details_layout.addWidget(self.powershell_label, 1, 1)
        
        # Control Panel path
        details_layout.addWidget(QLabel("Control Panel:"), 2, 0)
        self.control_panel_label = QLabel()
        self.control_panel_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_layout.addWidget(self.control_panel_label, 2, 1)
        
        # Settings app path
        details_layout.addWidget(QLabel("Settings App:"), 3, 0)
        self.settings_app_label = QLabel()
        self.settings_app_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_layout.addWidget(self.settings_app_label, 3, 1)
        
        # Group Policy path
        details_layout.addWidget(QLabel("Group Policy:"), 4, 0)
        self.group_policy_label = QLabel()
        self.group_policy_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.group_policy_label.setWordWrap(True)
        details_layout.addWidget(self.group_policy_label, 4, 1)
        
        # Add details group to scroll layout
        scroll_layout.addWidget(details_group)
        
        # Add stretch
        scroll_layout.addStretch()
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(scroll_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll_area)
    
    def load_setting(self, setting_id):
        """Load setting details
        
        Args:
            setting_id: Setting ID
        """
        # Get setting details
        setting = self.db_manager.get_setting_by_id(setting_id)
        
        if not setting:
            return
        
        # Store current setting
        self.current_setting = setting
        
        # Update header
        self.name_label.setText(setting['name'])
        self.description_label.setText(setting['description'] if setting['description'] else "")
        self.category_label.setText(f"Category: {setting['category_name']}")
        self.access_method_label.setText(f"Access Method: {setting['access_method_name']}")
        
        # Update details
        self.registry_path_label.setText("N/A")
        self.powershell_label.setText(setting['powershell_command'] if setting['powershell_command'] else "N/A")
        self.control_panel_label.setText(setting['control_panel_path'] if setting['control_panel_path'] else "N/A")
        self.settings_app_label.setText(setting['ms_settings_path'] if setting['ms_settings_path'] else "N/A")
        self.group_policy_label.setText(setting['group_policy_path'] if setting['group_policy_path'] else "N/A")
        
        # Load actions
        self.load_actions(setting_id)
    
    def load_actions(self, setting_id):
        """Load actions for a setting
        
        Args:
            setting_id: Setting ID
        """
        # Clear current actions
        self.clear_actions()
        
        # Get actions from database
        actions = self.db_manager.get_actions_for_setting(setting_id)
        
        if not actions:
            # Show no actions message
            no_actions = QLabel("No actions available for this setting.")
            no_actions.setAlignment(Qt.AlignCenter)
            no_actions.setStyleSheet("color: #777; padding: 20px;")
            self.actions_layout.addWidget(no_actions)
            return
        
        # Add action buttons for each action
        for action in actions:
            # Determine action type
            action_type = "primary" if action.get('is_default', 0) == 1 else "default"
            
            # Check if action is warning/destructive
            if any(keyword in action['name'].lower() for keyword in ['disable', 'remove', 'delete', 'clear']):
                action_type = "warning"
            
            # Create action button
            action_button = DetailedActionButton(
                action['name'],
                action['description'],
                action_type
            )
            
            # Store action data
            action_button.setProperty("action_id", action['id'])
            
            # Connect signal
            action_button.clicked.connect(lambda checked=False, a=action: self.on_action_clicked(a))
            
            # Add to layout
            self.actions_layout.addWidget(action_button)
        
        # Add stretch to push buttons to the top
        self.actions_layout.addStretch()
    
    def clear_actions(self):
        """Clear actions layout"""
        # Remove all widgets from actions layout
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def on_action_clicked(self, action):
        """Handle action button click
        
        Args:
            action: Action dictionary
        """
        # Log the action being executed
        print(f"Action: {action['name']}, Command: {action['powershell_command']}")
        
        # Special handling for Night Light
        if "night light" in action['name'].lower():
            result = self.settings_manager.toggle_night_light("enable" in action['name'].lower())
        else:
            # Apply the action
            result = self.settings_manager.apply_setting_action(action)
        
        # Show result in a notification or dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Action Result")
        
        if result.get('success', False):
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(f"Action '{action['name']}' completed successfully.")
            
            if result.get('requires_manual_action', False):
                msg_box.setInformativeText("Please complete the action in the opened settings window.")
            
            if result.get('message'):
                msg_box.setDetailedText(result['message'])
        else:
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(f"Action '{action['name']}' failed.")
            
            if result.get('requires_admin', False):
                msg_box.setInformativeText("This action requires administrator privileges.")
            
            if result.get('message'):
                msg_box.setDetailedText(result['message'])
        
        msg_box.exec_()
    
    def on_back_clicked(self):
        """Handle back button click"""
        # Get parent window
        main_window = self.window()
        
        # Go back to previous page
        if hasattr(main_window, 'content_area'):
            # Find the index of the page that was active before
            # Default to search page (index 0)
            main_window.content_area.set_current_index(0)
            
            # Update navigation button state
            if hasattr(main_window, 'sidebar'):
                main_window.sidebar.handle_nav_click(0)