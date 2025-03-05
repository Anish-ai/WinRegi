"""
Database schema for WinRegi application
Defines the structure of the SQLite database
"""

SCHEMA = """
-- Settings Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon_path TEXT
);

-- Access Methods Table
CREATE TABLE IF NOT EXISTS access_methods (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Windows Settings Table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    access_method_id INTEGER,
    registry_path TEXT,
    powershell_command TEXT,
    control_panel_path TEXT,
    ms_settings_path TEXT,
    group_policy_path TEXT,
    tags TEXT,
    keywords TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (access_method_id) REFERENCES access_methods(id)
);

-- Setting Actions Table
CREATE TABLE IF NOT EXISTS setting_actions (
    id INTEGER PRIMARY KEY,
    setting_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    action_type TEXT NOT NULL,
    action_value TEXT NOT NULL,
    is_default BOOLEAN DEFAULT 0,
    FOREIGN KEY (setting_id) REFERENCES settings(id)
);

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Settings Table
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY,
    profile_id INTEGER,
    setting_id INTEGER,
    action_id INTEGER,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES user_profiles(id),
    FOREIGN KEY (setting_id) REFERENCES settings(id),
    FOREIGN KEY (action_id) REFERENCES setting_actions(id)
);

-- Search History Table
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Predefined categories for settings
DEFAULT_CATEGORIES = [
    (1, "System", "System-wide settings", "system.png"),
    (2, "Display", "Monitor and graphics settings", "display.png"),
    (3, "Network", "Network and internet settings", "network.png"),
    (4, "Privacy", "Privacy and security settings", "privacy.png"),
    (5, "Personalization", "Appearance and customization", "personalization.png"),
    (6, "Apps", "Application management", "apps.png"),
    (7, "Accounts", "User accounts and authentication", "accounts.png"),
    (8, "Time & Language", "Regional and language settings", "time_language.png"),
    (9, "Gaming", "Game-related settings", "gaming.png"),
    (10, "Accessibility", "Ease of access settings", "accessibility.png"),
    (11, "Update & Security", "Windows Update and security", "update_security.png")
]

# Predefined access methods
DEFAULT_ACCESS_METHODS = [
    (1, "Registry", "Modify Windows Registry settings"),
    (2, "PowerShell", "Execute PowerShell commands"),
    (3, "Control Panel", "Open specific Control Panel applets"),
    (4, "Settings App", "Open the Windows Settings app"),
    (5, "Group Policy", "Modify Local Group Policy settings")
]

# Sample settings data for initial population
SAMPLE_SETTINGS = [
    # System category
    (1, "Night Light", "Reduces blue light emission at night", 2, 1, 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate\windows.data.bluelightreduction.bluelightreductionstate",
     "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate' -Name 'Data' -Value ([byte[]](0x43,0x42,0x01,0x00,0x0A,0x02,0x01,0x00,0x2A,0x06,0x24,0xA0,0x99,0x0E,0x01,0x00))",
     "desk.cpl", 
     "ms-settings:nightlight",
     "",
     "blue light,night mode,eye strain,display,color temperature",
     "reduce blue light,night shift,eye protection,sleep better"),
     
    # Privacy category
    (2, "Disable Advertising ID", "Prevents apps from using advertising ID", 4, 1,
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
     "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo' -Name 'Enabled' -Value 0",
     "",
     "ms-settings:privacy-general",
     "Computer Configuration\\Administrative Templates\\System\\User Profiles\\Turn off the advertising ID",
     "privacy,tracking,personalized ads,marketing",
     "stop ad tracking,disable ads,privacy settings"),
     
    # Performance
    (3, "Adjust for Best Performance", "Optimize visual effects for performance", 1, 1,
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
     "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name 'VisualFXSetting' -Value 2",
     "sysdm.cpl",
     "",
     "",
     "performance,speed,visual effects,animations",
     "speed up windows,faster pc,optimize performance"),
     
    # Network
    (4, "Metered Connection", "Set network connection as metered", 3, 1,
     r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost",
     "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost' -Name '3' -Value 2",
     "",
     "ms-settings:network-wifi",
     "",
     "wifi,data usage,network,bandwidth",
     "limit data usage,save bandwidth,reduce data")
]

# Sample setting actions
SAMPLE_ACTIONS = [
    # Night Light
    (1, 1, "Enable Night Light", "Turn on blue light reduction", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate\windows.data.bluelightreduction.bluelightreductionstate=([byte[]](0x43,0x42,0x01,0x00,0x0A,0x02,0x01,0x00,0x2A,0x06,0x24,0xA0,0x99,0x0E,0x01,0x00))", 
     1),
    (2, 1, "Disable Night Light", "Turn off blue light reduction", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\CloudStore\Store\DefaultAccount\Current\default$windows.data.bluelightreduction.bluelightreductionstate\windows.data.bluelightreduction.bluelightreductionstate=([byte[]](0x43,0x42,0x01,0x00,0x0A,0x02,0x01,0x00,0x22,0x04,0x80,0x99,0x0E,0x00))", 
     0),
    
    # Advertising ID
    (3, 2, "Disable Advertising ID", "Turn off advertising ID", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled=0", 
     1),
    (4, 2, "Enable Advertising ID", "Turn on advertising ID", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled=1", 
     0),
    
    # Performance
    (5, 3, "Best Performance", "Optimize for performance", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects\VisualFXSetting=2", 
     1),
    (6, 3, "Best Appearance", "Optimize for appearance", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects\VisualFXSetting=1", 
     0),
    (7, 3, "Custom", "Custom visual effects settings", "registry", 
     r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects\VisualFXSetting=3", 
     0),
    
    # Metered Connection
    (8, 4, "Enable Metered Connection", "Set connection as metered", "registry", 
     r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost\3=2", 
     1),
    (9, 4, "Disable Metered Connection", "Set connection as non-metered", "registry", 
     r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost\3=1", 
     0)
]