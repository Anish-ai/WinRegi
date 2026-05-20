<p align="start">
  <img src="https://i.ibb.co/v706hBb/Frame-1.png" alt="WinRegi Logo" width="600"/>
</p> 

# AI-Powered Windows Settings Explorer (WinRegi)

## 🚀 Project Overview

WinRegi is an **AI-powered Windows Registry and Settings Manager** built using **PyQt** and **Python**, designed to help users **explore and modify Windows settings effortlessly**. With an AI-integrated search feature, users can find settings based on natural language queries instead of exact keywords.

### 🎯 Why This Project?

Finding the right Windows settings can be frustrating due to:  
✅ A vast number of system settings  
✅ Different categories and locations of settings  
✅ Need to remember exact technical terms

**Solution:** A **smart, AI-powered search assistant** that allows users to type what they want in simple words and **instantly get relevant settings**!

---

## 🛠️ Tech Stack

### 🔹 Backend
- **Python** (Main logic, AI processing, Windows API interaction)
- **PyQt** (GUI framework for desktop app development)
- **Windows API & Registry Access** (For settings modification)
- **Natural Language Processing (NLP)** (For AI-powered search)
- **SQLite** (For storing thousands of pre-defined settings in a structured format)
- **Watchdog** (For hot reloading in development mode)

### 🔹 Frontend (UI)
- **PyQt Designer** (For visually designing UI)
- **Custom Widgets** (For a modern look and feel)
- **Modern glassmorphism UI** with light/dark themes
- **Dedicated UI for Every Setting** (Ensuring easy navigation and interaction)

---

## 🏗️ Architecture

### Backend Components

1. **Settings Database** 📂
   - The app maintains a structured database of Windows settings
   - Contains **thousands of pre-stored settings** with corresponding access methods
   - Structured with categories, settings, and actions

2. **AI Search Engine** 🔍
   - Users can type queries like:
     - "How to make my PC faster?"
     - "Enable dark mode"
     - "Stop background apps"
   - Natural language processing for search queries
   - Keyword extraction and intent detection
   - Relevance scoring and result ranking

3. **Windows API Module**
   - Registry management for reading/writing registry values
   - PowerShell command execution
   - Settings app and Control Panel integration

4. **Hot Reloading Module** 🔄
   - Monitors file changes during development using `watchdog`
   - Automatically reloads the UI when code changes are detected
   - Supports seamless development workflow

### Frontend Components

1. **Main Window**
   - Tabbed interface for search and categorized settings
   - Theme management (light/dark mode)
   - Collapsible sidebar navigation

2. **Search Page**
   - Natural language search bar
   - AI-powered search results
   - Setting cards with quick actions

3. **Settings Page**
   - Categorized display of Windows settings
   - Category list navigation
   - Setting details view

4. **Setting Detail Page**
   - Detailed information about a specific setting
   - Multiple action options (enable, disable, etc.)
   - Technical details (registry paths, PowerShell commands)

5. **UI Widgets**
   - Reusable UI components like search bar, setting cards, action buttons
   - Animated UI elements and transitions

---

## 📌 Features

✅ **AI-Powered Search**: No need to remember exact names of settings. Just describe what you want.  
✅ **Quick Actions**: Modify settings instantly from the app.  
✅ **Deep Windows Integration**: Uses Windows API, Registry, and PowerShell for control.  
✅ **Categorized Settings**: Organizes thousands of Windows settings into sections.  
✅ **User-Friendly UI**: Built with PyQt for a smooth experience with light/dark themes.  
✅ **Favorites & History**: Keep track of most-used settings.  
✅ **Dedicated UI for Each Setting**: Visually rich interface for each setting.  
✅ **AI Suggestions Instead of Direct Actions**: Ensures user has full control over modifications.  
✅ **Expanded Settings Database**: Includes Group Policy settings and PowerShell automation scripts.  
✅ **AI Auto-Apply Mode** ⚡: AI applies recommended changes automatically with a confirmation prompt.  
✅ **Security Enhancements** 🔒: AI validation layer to prevent harmful or unintended modifications.  
✅ **Hot Reloading** 🔄: Automatically reloads the UI during development when code changes are detected.  
✅ **Development Mode**: Run the app with `--dev` flag for hot reloading and enhanced debugging.  
✅ **Admin Privilege Control**: Use `--no-admin` flag to skip admin elevation prompts.  

---

## 🖥️ Installation Guide

### 📌 System Requirements
- Windows 10 or Windows 11
- Administrator privileges (for registry modifications)

The application will automatically request administrator privileges when needed.

### Installation from Source

#### Prerequisites
- Python 3.8 or higher
- Git
- pip
- Virtual Environment (recommended)

#### Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/winregi.git
cd winregi

# Create a virtual environment
python -m venv venv
venv\Scripts\activate    # For Windows
source venv/bin/activate  # For Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### For Developers

To install in development mode:

```bash
# After cloning and creating a virtual environment
pip install -e .

# Install watchdog for hot reloading
pip install watchdog

# Run the app in development mode
python main.py --dev
```

### Building an Executable (Optional)

```bash
python build_exe.py
```

This will create a `dist/WinRegi` directory containing the executable and all necessary files.

---

## 🚀 Usage

### Running the Application

1. **Normal Mode**:
   ```bash
   python main.py
   ```

2. **Development Mode**:
   ```bash
   python main.py --dev
   ```
   - Enables hot reloading and enhanced logging

3. **Skip Admin Elevation**:
   ```bash
   python main.py --no-admin
   ```

### Using the Application

1. **Search for Settings**: Type your query in natural language (e.g., "How to enable dark mode?")

2. **Browse Categorized Settings**: Navigate through categories (System, Privacy, Performance, Customization)

3. **Modify Settings**: View detailed information and apply changes directly

4. **Favorites & History**: Save frequently used settings and view recently accessed ones

5. **AI Auto-Apply Mode**: Enable for automatic application of recommended changes

---

## 🔧 Example Queries & Responses

| **User Query** | **Suggested Settings & Actions** |
|--------------|----------------|
| "Turn on night mode" | ✅ Open Night Light settings UI with options to customize |
| "Make text bigger" | ✅ Show accessibility settings with slider control |
| "Disable background apps" | ✅ List background apps, let user toggle which to disable |
| "Improve battery life" | ✅ Suggest power settings adjustments, allow user to apply changes |
| "Speed up PC" | ✅ Recommend startup app removal, service tweaks, and performance settings |

---

## 📚 Where We Get Windows Settings & Methods

We gather Windows settings from multiple sources:
- **Windows Registry Keys** 🗝️
- **Group Policy Settings (gpedit.msc)** 📜
- **Control Panel & PowerShell Commands** ⚡
- **Windows Settings URLs (ms-settings://)** 🏗️
- **Public Microsoft Documentation** 📄
- **Pre-Stored Structured Database** 📊

---

## 📂 Project Structure

```
winregi/
├── main.py                   # Main application entry point
├── debug_main.py             # Debug version with enhanced logging
├── src/
│   ├── ui/                   # User interface components
│   │   ├── main_window.py    # Main application window with sidebar
│   │   ├── search_page.py    # Search interface
│   │   ├── settings_page.py  # Settings management interface
│   │   ├── setting_detail.py # Detailed view for individual settings
│   │   ├── theme_manager.py  # Handles light/dark theme switching and styles
│   │   ├── modern_ui_styles.css  # CSS styles for modern UI elements
│   │   └── widgets/          # Reusable UI components
│   │       ├── action_button.py  # Custom action buttons with animations
│   │       ├── category_list.py  # Category navigation component
│   │       ├── search_bar.py     # Search input with suggestions
│   │       └── setting_card.py   # Card component for displaying settings
│   ├── windows_api/          # Windows API integration
│   │   ├── registry_manager.py    # Core functionality for registry operations
│   │   ├── settings_manager.py    # Manages Windows settings interactions
│   │   └── powershell_manager.py  # PowerShell interface for advanced registry tasks
│   ├── ai_engine/            # AI components
│   │   ├── nlp_processor.py  # Natural language processing for commands
│   │   └── search_engine.py  # Intelligent search functionality
│   └── database/             # Database components
│       ├── db_manager.py     # Database operations and management
│       └── schema.py         # Database schema definitions
├── WinRegi.spec              # PyInstaller specification file
├── requirements.txt          # Python dependencies
└── setup.py                  # Installation script
```

---

## 💡 Future Improvements

🔹 **Voice-Based Search** 🎙️ (Find settings with voice commands)  
🔹 **Enhanced AI Search** (More sophisticated NLP models, learning from user interactions)  
🔹 **User Preferences** (Customize settings based on usage patterns)  
🔹 **Integration with Windows Assistant** 🤖  
🔹 **Smart Recommendations** (Suggest optimizations based on usage)  
🔹 **Windows Troubleshooting Wizards**  
🔹 **System Optimization Presets**  
🔹 **Backup and Restore Functionality**

---

## 🤝 Contributing

We welcome contributions to improve this project!

1. **Fork the Repository** 🍴
2. **Create a Feature Branch** (`git checkout -b feature-name`)
3. **Commit Your Changes** (`git commit -m "Added new feature"`)
4. **Push to Your Branch** (`git push origin feature-name`)
5. **Submit a Pull Request** 🚀

### Areas Where We Need Help
- Expanding the settings database
- Improving the AI search capabilities
- Adding new features
- Fixing bugs
- Improving documentation
- Writing tests

---

## ❓ Troubleshooting

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Permission Issues
Run as administrator or use the `--no-admin` flag (limited functionality).

### PyQt Installation Issues
```bash
pip install --upgrade pip
pip install PyQt5
```

### Hot Reloading Not Working
Ensure `watchdog` is installed and run with `--dev` flag.

---

## 📜 License

This project is licensed under the **MIT License**. Feel free to use and modify it! 🎉

---

## 📧 Contact

👤 **Developer**: Anish Kumar  
📩 Email: aniskum59431@gmail.com  
🔗 GitHub: [Anish-ai](https://github.com/Anish-ai)  
🔗 LinkedIn: [Anish Kumar](https://www.linkedin.com/in/anish-kumar-71779326a/)  

---

_🚀 Made with ❤️ to make Windows settings easier for everyone!_
