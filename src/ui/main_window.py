"""
Main window for WinRegi application
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

from ..database.db_manager import DatabaseManager
from ..ai_engine.search_engine import SearchEngine
from ..windows_api.settings_manager import SettingsManager

from .search_page import SearchPage
from .settings_page import SettingsPage
from .setting_detail import SettingDetailPage
from .theme_manager import ThemeManager

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, is_admin=False):
        """Initialize main window
        
        Args:
            is_admin: Whether the application is running with admin privileges
        """
        super().__init__()
        
        # Store admin status
        self.is_admin = is_admin
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.db_manager.connect()
        self.db_manager.initialize_database()
        
        self.search_engine = SearchEngine(self.db_manager)
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager(self)
        
        # Set up UI
        self.init_ui()
        
        # Set window properties
        window_title = "WinRegi - AI-Powered Windows Registry Manager"
        if self.is_admin:
            window_title += " (Administrator)"
        self.setWindowTitle(window_title)
        self.resize(1024, 768)
        
        # Apply initial theme
        self.theme_manager.apply_theme("light")
    
    def init_ui(self):
        """Initialize user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create content area
        content = self.create_content()
        main_layout.addWidget(content)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def create_header(self) -> QWidget:
        """Create header widget
        
        Returns:
            Header widget
        """
        from PyQt5.QtGui import QFont, QColor, QPalette
        
        header = QWidget()
        header.setObjectName("app-header")
        header.setMinimumHeight(60)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # App logo and title
        logo_title_container = QWidget()
        logo_title_layout = QHBoxLayout(logo_title_container)
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title with custom font
        title_label = QLabel("WinRegi")
        title_label.setObjectName("app-title")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        
        # Subtitle
        subtitle_label = QLabel("AI-Powered Windows Settings")
        subtitle_label.setObjectName("app-subtitle")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        
        # Create vertical layout for title and subtitle
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Add title to logo-title layout
        logo_title_layout.addWidget(title_container)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # Admin status indicator
        admin_indicator = QWidget()
        admin_indicator.setObjectName("admin-indicator")
        admin_indicator.setFixedSize(120, 30)
        
        admin_layout = QHBoxLayout(admin_indicator)
        admin_layout.setContentsMargins(10, 5, 10, 5)
        
        # Icon for admin status
        admin_icon = QLabel("🔒")
        admin_icon.setFixedSize(20, 20)
        
        # Admin status text
        if self.is_admin:
            admin_text = QLabel("Admin")
            admin_indicator.setProperty("admin-status", "admin")
        else:
            admin_text = QLabel("Limited")
            admin_indicator.setProperty("admin-status", "limited")
        
        admin_layout.addWidget(admin_icon)
        admin_layout.addWidget(admin_text)
        
        # Theme toggle button
        theme_button = QPushButton()
        theme_button.setObjectName("theme-button")
        theme_button.setToolTip("Toggle theme")
        theme_button.setFixedSize(32, 32)
        theme_button.clicked.connect(self.toggle_theme)
        
        # Add widgets to layout
        header_layout.addWidget(logo_title_container)
        header_layout.addWidget(spacer)
        header_layout.addWidget(admin_indicator)
        header_layout.addWidget(theme_button)
        
        return header
    
    def create_content(self) -> QWidget:
        """Create content widget
        
        Returns:
            Content widget
        """
        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setObjectName("main-tabs")
        tab_widget.setDocumentMode(True)
        
        # Create search page
        self.search_page = SearchPage(self.search_engine, self.settings_manager, self.db_manager)
        tab_widget.addTab(self.search_page, "Search")
        
        # Create settings page
        self.settings_page = SettingsPage(self.db_manager, self.settings_manager)
        tab_widget.addTab(self.settings_page, "Categories")
        
        # Create detail page
        self.detail_page = SettingDetailPage(self.db_manager, self.settings_manager)
        tab_widget.addTab(self.detail_page, "Setting Details")
        tab_widget.setTabVisible(2, False)  # Hide detail tab until needed
        
        # Connect signals
        self.search_page.setting_selected.connect(self.show_setting_detail)
        self.settings_page.setting_selected.connect(self.show_setting_detail)
        
        return tab_widget
    
    def show_setting_detail(self, setting_id):
        """Show setting detail page for the selected setting
        
        Args:
            setting_id: Setting ID to display
        """
        # Update detail page with selected setting
        self.detail_page.load_setting(setting_id)
        
        # Show detail tab
        tab_widget = self.findChild(QTabWidget, "main-tabs")
        tab_widget.setTabVisible(2, True)
        tab_widget.setCurrentIndex(2)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_theme = self.theme_manager.current_theme
        new_theme = "dark" if current_theme == "light" else "light"
        self.theme_manager.apply_theme(new_theme)
    
    def closeEvent(self, event):
        """Handle window close event
        
        Args:
            event: Close event
        """
        # Clean up database connection
        self.db_manager.disconnect()
        
        # Accept the close event
        event.accept()