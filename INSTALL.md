# WinRegi Installation Guide

WinRegi is an AI-powered Windows Registry Manager designed to simplify Windows system customization.

## System Requirements

- Windows 10 or Windows 11
- Administrator privileges (for registry modifications)

## Installation - Easy Method (Recommended)

1. Download the latest release from the [Releases](https://github.com/winregi/winregi/releases) page
2. Run the installer 
3. Follow the on-screen instructions

The application will automatically request administrator privileges when needed.

## Installation from Source

### 1. Requirements

- Python 3.8 or higher
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/winregi/winregi.git
cd winregi
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

### 6. Building an Executable (Optional)

To build a standalone executable:

```bash
python build_exe.py
```

This will create a `dist/WinRegi` directory containing the executable and all necessary files.

## Installation for Developers

### 1. Clone the Repository

```bash
git clone https://github.com/winregi/winregi.git
cd winregi
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
pip install -e .
```

This installs the package in development mode, allowing you to make changes to the code without reinstalling.

### 4. Run Tests

```bash
pytest tests
```

## Features

- **Light/Dark Mode**: Toggle between light and dark themes with smooth transitions
- **Custom Commands Management**: Create, edit, and execute custom commands
- **AI-Powered Search**: Find Windows settings using natural language
- **Registry Management**: View and modify Windows Registry settings safely
- **Administrator Mode**: Automatically runs with admin privileges for full functionality

## Troubleshooting

### Missing Dependencies

If you encounter errors related to missing dependencies, try:

```bash
pip install --upgrade -r requirements.txt
```

### Permission Issues

WinRegi requires administrator privileges to modify Windows Registry settings. If you encounter permission issues:

1. Close the application
2. Right-click on the WinRegi shortcut or executable
3. Select "Run as administrator"

### PyQt Installation Issues

If you encounter issues installing PyQt5:

```bash
pip install --upgrade pip
pip install PyQt5
```

## Uninstallation

### Executable Version

Use the Windows Control Panel > Programs > Uninstall a program

### Source Installation

To uninstall WinRegi:

1. Deactivate the virtual environment:
   ```bash
   deactivate
   ```

2. Delete the directory containing the application.