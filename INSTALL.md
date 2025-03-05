# WinRegi Installation Guide

WinRegi is an AI-powered Windows Registry Manager designed to simplify Windows system customization.

## System Requirements

- Windows 10 or Windows 11
- Python 3.8 or higher
- Administrator privileges (for registry modifications)

## Installation Steps

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

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

## Troubleshooting

### Missing Dependencies

If you encounter errors related to missing dependencies, try:

```bash
pip install --upgrade -r requirements.txt
```

### Permission Issues

WinRegi requires administrator privileges to modify Windows Registry settings. If you encounter permission issues:

1. Close the application
2. Right-click on the command prompt or PowerShell
3. Select "Run as administrator"
4. Navigate to the WinRegi directory and run the application again

### PyQt Installation Issues

If you encounter issues installing PyQt5:

```bash
pip install --upgrade pip
pip install PyQt5
```

## Uninstallation

To uninstall WinRegi:

1. Deactivate the virtual environment:
   ```bash
   deactivate
   ```

2. Delete the directory containing the application.