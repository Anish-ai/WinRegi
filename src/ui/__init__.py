"""
UI module for WinRegi application
"""
from .main_window import MainWindow
from .search_page import SearchPage
from .settings_page import SettingsPage
from .setting_detail import SettingDetailPage
from .theme_manager import ThemeManager

__all__ = [
    'MainWindow', 
    'SearchPage', 
    'SettingsPage', 
    'SettingDetailPage',
    'ThemeManager'
]