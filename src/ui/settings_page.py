"""
Settings page for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from .widgets.category_list import CategoryList
from .widgets.setting_card import SettingCard

class SettingsPage(QWidget):
    """Settings page with categorized Windows settings"""
    
    # Signal emitted when a setting is selected
    setting_selected = pyqtSignal(int)
    
    def __init__(self, db_manager, settings_manager, parent=None):
        """Initialize settings page
        
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
        self.current_category = None
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # Create category panel
        category_panel = self.create_category_panel()
        splitter.addWidget(category_panel)
        
        # Create settings panel
        settings_panel = self.create_settings_panel()
        splitter.addWidget(settings_panel)
        
        # Set initial splitter sizes (1:3 ratio)
        splitter.setSizes([1, 3])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Load categories
        self.load_categories()
    
    def create_category_panel(self):
        """Create category panel
        
        Returns:
            Category panel widget
        """
        # Create panel widget
        panel = QWidget()
        panel.setObjectName("category-panel")
        panel.setMinimumWidth(200)
        
        # Create layout
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        header = QLabel("Categories")
        header.setObjectName("panel-header")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Create category list
        self.category_list = CategoryList()
        self.category_list.category_selected.connect(self.on_category_selected)
        layout.addWidget(self.category_list)
        
        return panel
    
    def create_settings_panel(self):
        """Create settings panel
        
        Returns:
            Settings panel widget
        """
        # Create panel widget
        panel = QWidget()
        panel.setObjectName("settings-panel")
        
        # Create layout
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Create header
        self.settings_header = QLabel("Select a category")
        self.settings_header.setObjectName("panel-header")
        self.settings_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.settings_header)
        
        # Create special Windows theme section
        theme_section = self.create_theme_section()
        layout.addWidget(theme_section)
        
        # Create separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #dddddd; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Create settings container
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(10)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(self.settings_container)
        layout.addWidget(scroll_area)
        
        return panel
    
    def create_theme_section(self):
        """Create Windows theme section
        
        Returns:
            Theme section widget
        """
        # Create theme section widget
        theme_section = QWidget()
        theme_section.setObjectName("theme-section")
        
        # Create layout
        layout = QVBoxLayout(theme_section)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create theme header
        theme_header = QLabel("Windows Theme")
        theme_header.setObjectName("theme-header")
        theme_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(theme_header)
        
        # Create theme description
        theme_description = QLabel("Change the appearance of Windows between light and dark modes.")
        theme_description.setObjectName("theme-description")
        theme_description.setWordWrap(True)
        layout.addWidget(theme_description)
        
        # Create theme buttons layout
        theme_buttons_layout = QHBoxLayout()
        theme_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # Create light theme button
        self.light_theme_button = QPushButton("Light Theme")
        self.light_theme_button.setObjectName("light-theme-button")
        self.light_theme_button.setFixedHeight(36)
        self.light_theme_button.clicked.connect(lambda: self.apply_windows_theme("light"))
        theme_buttons_layout.addWidget(self.light_theme_button)
        
        # Create dark theme button
        self.dark_theme_button = QPushButton("Dark Theme")
        self.dark_theme_button.setObjectName("dark-theme-button")
        self.dark_theme_button.setFixedHeight(36)
        self.dark_theme_button.clicked.connect(lambda: self.apply_windows_theme("dark"))
        theme_buttons_layout.addWidget(self.dark_theme_button)
        
        # Add theme buttons layout to main layout
        layout.addLayout(theme_buttons_layout)
        
        return theme_section
    
    def load_categories(self):
        """Load categories from database"""
        # Clear current categories
        self.category_list.clear_categories()
        
        # Get categories from database
        categories = self.db_manager.get_all_categories()
        
        # Add categories to list
        for category in categories:
            self.category_list.add_category(
                category['id'],
                category['name'],
                category['description'],
                category['icon_path']
            )
    
    def on_category_selected(self, category_id):
        """Handle category selection
        
        Args:
            category_id: Selected category ID
        """
        # Store current category
        self.current_category = category_id
        
        # Get category from database
        categories = self.db_manager.get_all_categories()
        category = next((c for c in categories if c['id'] == category_id), None)
        
        if not category:
            return
        
        # Update header
        self.settings_header.setText(category['name'])
        
        # Load settings for the category
        self.load_category_settings(category_id)
    
    def load_category_settings(self, category_id):
        """Load settings for a category
        
        Args:
            category_id: Category ID
        """
        # Clear current settings
        self.clear_settings()
        
        # Get settings from database
        settings = self.db_manager.get_settings_by_category(category_id)
        
        if not settings:
            # Show no settings message
            no_settings = QLabel("No settings found in this category.")
            no_settings.setAlignment(Qt.AlignCenter)
            no_settings.setStyleSheet("color: #777; padding: 20px;")
            self.settings_layout.addWidget(no_settings)
            return
        
        # Add setting cards for each setting
        for setting in settings:
            # Create setting card
            setting_card = SettingCard(
                setting['id'],
                setting['name'],
                setting['description']
            )
            
            # Connect signals
            setting_card.clicked.connect(self.on_setting_selected)
            setting_card.action_requested.connect(self.on_setting_action)
            
            # Add to layout
            self.settings_layout.addWidget(setting_card)
        
        # Add stretch to push cards to the top
        self.settings_layout.addStretch()
    
    def clear_settings(self):
        """Clear settings panel"""
        # Remove all widgets from settings layout
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
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
        
        # Show result in a notification dialog
        self.show_action_result(result)
    
    def apply_windows_theme(self, theme):
        """Apply Windows theme (light/dark)
        
        Args:
            theme: Theme to apply ('light' or 'dark')
        """
        from PyQt5.QtWidgets import QMessageBox
        
        # Apply the theme
        result = self.settings_manager.set_windows_theme(theme)
        
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
        
        # Show result dialog
        self.show_action_result(result)
    
    def show_action_result(self, result):
        """Show action result in a dialog
        
        Args:
            result: Result dictionary from settings manager
        """
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