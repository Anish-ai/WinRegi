"""
Main window for WinRegi application with modern UI design
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QSplitter, QSizePolicy,
    QStackedWidget, QToolButton, QFrame, QScrollArea, QGraphicsDropShadowEffect, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup,
    pyqtSignal, QSize, QTimer, QEvent
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QFontDatabase, QPainter, QPainterPath

from ..database.db_manager import DatabaseManager
from ..ai_engine.search_engine import SearchEngine
from ..windows_api.settings_manager import SettingsManager

from .search_page import SearchPage
from .settings_page import SettingsPage
from .setting_detail import SettingDetailPage
from .commands_page import CommandsPage
from .theme_manager import ThemeManager, ThemeToggleSwitch

class NavigationButton(QToolButton):
    """Modern styled navigation button for sidebar"""
    
    def __init__(self, text, icon_text, parent=None):
        """Initialize navigation button
        
        Args:
            text: Button text
            icon_text: Emoji or text to use as icon
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set properties
        self.setText(text)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(40)  # Reduced from 50 to 40
        
        # Set icon text
        self.icon_text = icon_text
        
        # Style sheet is applied via theme manager
        self.setObjectName("nav-button")
        
        # Create icon label
        self.icon_label = QLabel(icon_text)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setObjectName("nav-icon")
        self.icon_label.setStyleSheet("background: transparent; font-size: 16px;")
        
        # Layout (we'll override the paint event)
        self.setIconSize(QSize(24, 24))
    
    def paintEvent(self, event):
        """Custom paint event for nav button with active indicator"""
        super().paintEvent(event)
        
        # Only draw indicator if checked
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw active indicator bar on left
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#28C058" if not self.property("dark_mode") else "#38E078"))
            painter.drawRoundedRect(0, 5, 4, self.height() - 10, 2, 2)

class SidebarNavigation(QWidget):
    """Collapsible sidebar navigation"""
    
    # Signal emitted when a navigation item is selected
    navigation_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize sidebar navigation
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set fixed width for expanded state
        self.expanded_width = 180
        self.collapsed_width = 50
        self.is_expanded = True
        
        # Set object name for styling
        self.setObjectName("sidebar-nav")
        
        # Initialize UI
        self.init_ui()
        
        # Apply shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(2, 0)
        self.setGraphicsEffect(self.shadow)
        
        # Set initial width
        self.setFixedWidth(self.expanded_width)
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("sidebar-toggle")
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setText("≡")
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        # Create header layout for the toggle button
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.toggle_button)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Add some spacing
        layout.addSpacing(10)
        
        # Create navigation buttons
        self.nav_buttons = []
        
        # Search button
        self.search_button = NavigationButton("Search", "🔍")
        self.search_button.setChecked(True)  # Set as default active page
        self.search_button.clicked.connect(lambda: self.handle_nav_click(0))
        layout.addWidget(self.search_button)
        self.nav_buttons.append(self.search_button)
        
        # Categories button
        self.categories_button = NavigationButton("Categories", "📁")
        self.categories_button.clicked.connect(lambda: self.handle_nav_click(1))
        layout.addWidget(self.categories_button)
        self.nav_buttons.append(self.categories_button)
        
        # Commands button
        self.commands_button = NavigationButton("Commands", "⌨️")
        self.commands_button.clicked.connect(lambda: self.handle_nav_click(2))
        layout.addWidget(self.commands_button)
        self.nav_buttons.append(self.commands_button)
        
        # Add spacer to push buttons to top
        layout.addStretch()
        
        # Add settings button at bottom
        self.settings_button = QPushButton("Settings")
        self.settings_button.setObjectName("settings-button")
        self.settings_button.setFixedHeight(40)
        self.settings_button.clicked.connect(self.on_settings_clicked)  # Connect to handler
        layout.addWidget(self.settings_button)
    
    def handle_nav_click(self, index):
        """Handle navigation button click
        
        Args:
            index: Navigation index
        """
        # Update checked state of buttons
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
        
        # Emit signal with selected index
        self.navigation_changed.emit(index)
    
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states"""
        # Set target width
        target_width = self.collapsed_width if self.is_expanded else self.expanded_width
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Start animation
        self.animation.start()
        
        # Update toggle button text
        self.toggle_button.setText("≡" if self.is_expanded else "≡")
        
        # Update button style
        for button in self.nav_buttons:
            button.setToolButtonStyle(Qt.ToolButtonIconOnly if self.is_expanded else Qt.ToolButtonTextBesideIcon)
        
        # Update expanded state
        self.is_expanded = not self.is_expanded

    def on_settings_clicked(self):
        """Handle settings button click"""
        # Create a simple settings dialog
        dialog = QDialog(self.parent())
        dialog.setWindowTitle("Settings")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Add settings content
        title = QLabel("Application Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Add theme toggle
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        theme_label = QLabel("Application Theme:")
        theme_layout.addWidget(theme_label)
        
        theme_toggle = ThemeToggleSwitch()
        theme_toggle.setChecked(self.parent().theme_manager.current_theme == "dark")
        theme_toggle.toggled.connect(self.parent().toggle_theme)
        theme_layout.addWidget(theme_toggle)
        
        layout.addWidget(theme_container)
        
        # Add version info
        version_label = QLabel("WinRegi v1.0.0")
        version_label.setStyleSheet("color: #777; margin-top: 20px;")
        layout.addWidget(version_label)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        # Show dialog
        dialog.exec_()

class ContentArea(QStackedWidget):
    """Content area with animated page transitions"""
    
    def __init__(self, parent=None):
        """Initialize content area
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set properties
        self.setObjectName("content-area")
        
        # Current and next widget for animation
        self.current_widget = None
        self.next_widget = None
        
        # Animation properties
        self.animation_duration = 300
    
    def add_widget(self, widget):
        """Add widget to content area
        
        Args:
            widget: Widget to add
        """
        self.addWidget(widget)
        
        # Set as current widget if first widget
        if self.count() == 1:
            self.current_widget = widget
    
    def set_current_index(self, index):
        """Set current widget index with animation
        
        Args:
            index: Widget index
        """
        if index < 0 or index >= self.count():
            return
        
        # Get next widget
        self.next_widget = self.widget(index)
        
        # Don't animate if it's the same widget
        if self.current_widget == self.next_widget:
            return
        
        # Create fade-in/fade-out animations
        fade_out = QPropertyAnimation(self.current_widget, b"windowOpacity")
        fade_out.setDuration(self.animation_duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutCubic)
        
        fade_in = QPropertyAnimation(self.next_widget, b"windowOpacity")
        fade_in.setDuration(self.animation_duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InCubic)
        
        # Create animation group
        self.animation_group = QSequentialAnimationGroup()
        
        # Add animations to group
        self.animation_group.addAnimation(fade_out)
        
        # Connect animation finished signal
        fade_out.finished.connect(lambda: self.setCurrentWidget(self.next_widget))
        
        self.animation_group.addAnimation(fade_in)
        
        # Start animation
        self.animation_group.start()
        
        # Update current widget
        self.current_widget = self.next_widget

class MainWindow(QMainWindow):
    """Main application window with modern UI design"""
    
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
        
        # Set window properties
        window_title = "WinRegi - AI-Powered Windows Registry Manager"
        if self.is_admin:
            window_title += " (Administrator)"
        self.setWindowTitle(window_title)
        self.resize(1200, 800)
        
        # Enable custom window frame with move & resize capabilities
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set up UI
        self.init_ui()
        
        # Apply initial theme - load from saved config
        self.theme_manager.apply_theme(self.theme_manager.current_theme)
    
    def init_ui(self):
        """Initialize user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        central_widget.setObjectName("main-window")
        
        # Main layout with margin for drop shadow
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # Create app container with rounded corners
        app_container = QFrame()
        app_container.setObjectName("app-container")
        app_container.setFrameShape(QFrame.StyledPanel)
        
        # Container layout
        container_layout = QVBoxLayout(app_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Create header
        header = self.create_header()
        container_layout.addWidget(header)
        
        # Create content layout (sidebar + main content)
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = SidebarNavigation()
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)
        
        # Create content pages container
        self.content_area = ContentArea()
        
        # Create search page
        self.search_page = SearchPage(self.search_engine, self.settings_manager, self.db_manager)
        self.content_area.add_widget(self.search_page)
        
        # Create settings page
        self.settings_page = SettingsPage(self.db_manager, self.settings_manager)
        self.content_area.add_widget(self.settings_page)
        
        # Create commands page
        self.commands_page = CommandsPage(self.db_manager)
        self.content_area.add_widget(self.commands_page)
        
        # Create detail page
        self.detail_page = SettingDetailPage(self.db_manager, self.settings_manager)
        self.content_area.add_widget(self.detail_page)
        
        # Add sidebar and content area to content layout
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.content_area)
        
        # Add content layout to container
        container_layout.addLayout(content_layout, 1)
        
        # Create status bar
        status_bar = QLabel("Ready")
        status_bar.setObjectName("status-bar")
        status_bar.setFixedHeight(25)
        status_bar.setIndent(10)
        container_layout.addWidget(status_bar)
        
        # Add shadow effect to app container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        app_container.setGraphicsEffect(shadow)
        
        # Add app container to main layout
        main_layout.addWidget(app_container)
        
        # Connect signals
        self.search_page.setting_selected.connect(self.show_setting_detail)
        self.settings_page.setting_selected.connect(self.show_setting_detail)
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def create_header(self) -> QWidget:
        """Create header widget with modern glassmorphism effect
        
        Returns:
            Header widget
        """
        # Create header container
        header = QWidget()
        header.setObjectName("app-header")
        header.setFixedHeight(60)  # Reduced from 70 to 60
        
        # Use horizontal layout for header
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 5, 15, 5)  # Reduced margins
        
        # App logo and title
        logo_title_container = QWidget()
        logo_title_layout = QHBoxLayout(logo_title_container)
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        
        # App icon/logo (using emoji as placeholder)
        logo_label = QLabel("🔧")
        logo_label.setObjectName("app-logo")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(32, 32)  # Reduced from 40x40
        logo_label.setStyleSheet("font-size: 20px;")  # Reduced font size
        
        # Create title container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Title with custom font
        title_label = QLabel("WinRegi")
        title_label.setObjectName("app-title")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")  # Adjusted font size
        
        # Subtitle
        subtitle_label = QLabel("AI-Powered Windows Settings")
        subtitle_label.setObjectName("app-subtitle")
        subtitle_label.setStyleSheet("font-size: 11px; color: #666;")  # Adjusted font size
        
        # Add to title layout
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Add logo and title to container
        logo_title_layout.addWidget(logo_label)
        logo_title_layout.addWidget(title_container)
        
        # Add logo/title container to header
        header_layout.addWidget(logo_title_container)
        
        # Add search bar in header
        search_container = QWidget()
        search_container.setObjectName("header-search-container")
        search_container.setMinimumWidth(300)  # Reduced from 400
        search_container.setFixedHeight(36)  # Reduced from 40
        search_container.setStyleSheet("background-color: rgba(240, 240, 240, 0.8); border-radius: 18px;")
        
        # Create search layout
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(5)
        
        # Search icon
        search_icon = QLabel("🔍")
        search_icon.setObjectName("header-search-icon")
        search_icon.setFixedSize(16, 16)
        search_icon.setAlignment(Qt.AlignCenter)
        
        # Create header search input
        self.header_search = QPushButton("Search settings and commands...")
        self.header_search.setObjectName("header-search-button")
        self.header_search.setCursor(Qt.PointingHandCursor)
        self.header_search.setStyleSheet("text-align: left; border: none; background: transparent; color: #666;")
        self.header_search.clicked.connect(self.focus_search)
        
        # Add to search layout
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.header_search, 1)
        
        # Add searchbar to header
        header_layout.addWidget(search_container, 1)
        
        # Add stretch to push admin indicator and theme toggle to the right
        header_layout.addStretch()
        
        # Admin status indicator
        admin_indicator = QWidget()
        admin_indicator.setObjectName("admin-indicator")
        admin_indicator.setFixedSize(100, 26)  # Reduced size
        admin_indicator.setProperty("admin-status", "admin" if self.is_admin else "limited")
        
        # Set style based on admin status
        if self.is_admin:
            admin_indicator.setStyleSheet("background-color: rgba(76, 175, 80, 0.2); border-radius: 13px;")
        else:
            admin_indicator.setStyleSheet("background-color: rgba(255, 152, 0, 0.2); border-radius: 13px;")
        
        admin_layout = QHBoxLayout(admin_indicator)
        admin_layout.setContentsMargins(8, 3, 8, 3)  # Reduced margins
        
        # Icon for admin status
        admin_icon = QLabel("🔒")
        admin_icon.setFixedSize(16, 16)  # Reduced size
        
        # Admin status text
        admin_text = QLabel("Admin" if self.is_admin else "Limited")
        admin_text.setStyleSheet("font-size: 11px;")  # Reduced font size
        
        admin_layout.addWidget(admin_icon)
        admin_layout.addWidget(admin_text)
        
        # Create theme toggle switch
        theme_container = self.theme_manager.create_theme_toggle(self)
        theme_container.setToolTip("Toggle between light and dark mode")
        
        # Create window control container
        window_controls = QWidget()
        window_controls.setObjectName("window-controls")
        window_controls.setFixedWidth(90)
        
        # Window control layout
        window_layout = QHBoxLayout(window_controls)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(5)
        
        # Create minimize, maximize and close buttons
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setObjectName("minimize-btn")
        self.minimize_btn.setFixedSize(25, 25)
        self.minimize_btn.clicked.connect(self.showMinimized)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("maximize-btn")
        self.maximize_btn.setFixedSize(25, 25)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close-btn")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.close)
        
        # Add buttons to window control layout
        window_layout.addWidget(self.minimize_btn)
        window_layout.addWidget(self.maximize_btn)
        window_layout.addWidget(self.close_btn)
        
        # Add components to header layout
        header_layout.addWidget(admin_indicator)
        header_layout.addWidget(theme_container)
        header_layout.addWidget(window_controls)
        
        return header
    
    def focus_search(self):
        """Focus the search bar in search page"""
        # Switch to search page
        self.content_area.set_current_index(0)
        self.sidebar.handle_nav_click(0)
        
        # Get search bar input and focus it
        search_bar = self.search_page.search_bar
        search_input = search_bar.search_input
        QTimer.singleShot(300, lambda: search_input.setFocus())
    
    def on_navigation_changed(self, index):
        """Handle navigation change
        
        Args:
            index: Navigation index
        """
        # Skip detail page in navigation
        self.content_area.set_current_index(index)
    
    def show_setting_detail(self, setting_id):
        """Show setting detail page for the selected setting
        
        Args:
            setting_id: Setting ID to display
        """
        # Update detail page with selected setting
        self.detail_page.load_setting(setting_id)
        
        # Show detail page (it's at index 3)
        self.content_area.set_current_index(3)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_theme = self.theme_manager.current_theme
        new_theme = "dark" if current_theme == "light" else "light"
        self.theme_manager.apply_theme(new_theme)
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")
    
    def mousePressEvent(self, event):
        """Handle mouse press event for custom window dragging
        
        Args:
            event: Mouse event
        """
        # Check if left button was pressed on header
        if event.button() == Qt.LeftButton:
            # Find header widget
            header = self.findChild(QWidget, "app-header")
            if header and header.geometry().contains(event.pos()):
                # Store initial position
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
            else:
                self._drag_pos = None
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for custom window dragging
        
        Args:
            event: Mouse event
        """
        # Move window if dragging enabled
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event
        
        Args:
            event: Mouse event
        """
        # Reset drag position
        self._drag_pos = None
    
    def closeEvent(self, event):
        """Handle window close event
        
        Args:
            event: Close event
        """
        # Clean up database connection
        self.db_manager.disconnect()
        
        # Accept the close event
        event.accept()