# WinRegi

WinRegi is an AI-powered Windows Registry Manager built with PyQt5, providing an intuitive interface for accessing and modifying Windows Registry settings.

## Project Structure

### Frontend (UI)
- `src/ui/main_window.py` - Main application window with sidebar navigation
- `src/ui/search_page.py` - Search interface for finding registry settings
- `src/ui/settings_page.py` - Settings management interface
- `src/ui/setting_detail.py` - Detailed view for individual settings
- `src/ui/theme_manager.py` - Handles light/dark theme switching and styles
- `src/ui/modern_ui_styles.css` - CSS styles for modern UI elements

### UI Widgets
- `src/ui/widgets/action_button.py` - Custom action buttons with animations
- `src/ui/widgets/category_list.py` - Category navigation component
- `src/ui/widgets/search_bar.py` - Search input with suggestions
- `src/ui/widgets/setting_card.py` - Card component for displaying settings

### Backend
- `src/windows_api/registry_manager.py` - Core functionality for registry operations
- `src/windows_api/settings_manager.py` - Manages Windows settings interactions
- `src/windows_api/powershell_manager.py` - PowerShell interface for advanced registry tasks

### AI Engine
- `src/ai_engine/nlp_processor.py` - Natural language processing for commands
- `src/ai_engine/search_engine.py` - Intelligent search functionality

### Database
- `src/database/db_manager.py` - Database operations and management
- `src/database/schema.py` - Database schema definitions

### Entry Points
- `main.py` - Main application entry point
- `debug_main.py` - Debug version with enhanced logging

### Configuration
- `WinRegi.spec` - PyInstaller specification file
- `requirements.txt` - Python dependencies
- `setup.py` - Installation script

## Features

- Modern glassmorphism UI with light/dark themes
- Natural language search for registry settings
- Category-based navigation of Windows settings
- Real-time registry modification with safeguards
- Collapsible sidebar navigation
- Animated UI elements and transitions

## Installation

See `INSTALL.md` for detailed installation instructions.

## License

This project is licensed under the terms specified in the `LICENSE` file.