#!/usr/bin/env python3
"""
Database migration script for WinRegi
Fixes PowerShell commands for settings actions
"""
import os
import sqlite3
import sys
from pathlib import Path

def get_db_path():
    """Get database path"""
    # Use the same path logic as the main application
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        print(f"Creating data directory: {data_dir}")
        data_dir.mkdir(exist_ok=True)
    
    return str(data_dir / "winregi.db")

def migrate_database():
    """Perform database migration"""
    db_path = get_db_path()
    
    print(f"Updating PowerShell commands in database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist. Nothing to migrate.")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Updated PowerShell commands
        updated_commands = [
            # Night Light - Enable
            (1, """
# Enable Night Light
try {
    # Method 1: Using the Settings URI (most reliable)
    Start-Process "ms-settings:nightlight"
    Start-Sleep -Seconds 1
    
    # Method 2: Using registry (alternative approach)
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate" -Force | Out-Null
    }
    
    # Set registry value for Night Light enabled
    $NightLightData = [byte[]](0x43,0x42,0x01,0x00,0x0A,0x02,0x01,0x00,0x2A,0x06,0x24,0xA0,0x99,0x0E,0x01,0x00)
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate" -Name "Data" -Value $NightLightData -Type Binary -Force
    
    # Also try the settings path
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings" -Name "Data" -Value ([byte[]](0x02,0x00,0x00,0x00,0x12,0x66,0x72,0x00,0x00)) -Type Binary -Force
    
    # Method 3: Using the Windows API (most direct)
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    
    public class NightLight {
        [DllImport("user32.dll")]
        public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
        
        [DllImport("user32.dll")]
        public static extern IntPtr FindWindowW(string lpClassName, string lpWindowName);
        
        public static void Enable() {
            IntPtr hWnd = FindWindowW("Windows.UI.Core.CoreWindow", "Windows Shell Experience Host");
            if (hWnd != IntPtr.Zero) {
                SendMessageW(hWnd, 0x0112, new IntPtr(0xF170), new IntPtr(1));
            }
        }
    }
"@
    
    # Try to use the Windows API method
    try {
        [NightLight]::Enable()
    } catch {
        # Ignore errors with this method
    }
    
    Write-Output "Night Light has been enabled. You may need to restart the Windows Explorer process for changes to take effect."
} catch {
    Write-Error "Failed to enable Night Light: $_"
    exit 1
}
            """),
            
            # Night Light - Disable
            (2, """
# Disable Night Light
try {
    # Method 1: Using the Settings URI (most reliable)
    Start-Process "ms-settings:nightlight"
    Start-Sleep -Seconds 1
    
    # Method 2: Using registry (alternative approach)
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate" -Force | Out-Null
    }
    
    # Set registry value for Night Light disabled
    $NightLightData = [byte[]](0x43,0x42,0x01,0x00,0x0A,0x02,0x01,0x00,0x22,0x04,0x80,0x99,0x0E,0x00)
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.bluelightreductionstate" -Name "Data" -Value $NightLightData -Type Binary -Force
    
    # Also try the settings path
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default`$windows.data.bluelightreduction.settings" -Name "Data" -Value ([byte[]](0x02,0x00,0x00,0x00,0x10,0x66,0x72,0x00,0x00)) -Type Binary -Force
    
    # Method 3: Using the Windows API (most direct)
    Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    
    public class NightLight {
        [DllImport("user32.dll")]
        public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
        
        [DllImport("user32.dll")]
        public static extern IntPtr FindWindowW(string lpClassName, string lpWindowName);
        
        public static void Disable() {
            IntPtr hWnd = FindWindowW("Windows.UI.Core.CoreWindow", "Windows Shell Experience Host");
            if (hWnd != IntPtr.Zero) {
                SendMessageW(hWnd, 0x0112, new IntPtr(0xF170), new IntPtr(0));
            }
        }
    }
"@
    
    # Try to use the Windows API method
    try {
        [NightLight]::Disable()
    } catch {
        # Ignore errors with this method
    }
    
    Write-Output "Night Light has been disabled. You may need to restart the Windows Explorer process for changes to take effect."
} catch {
    Write-Error "Failed to disable Night Light: $_"
    exit 1
}
            """),
            
            # Advertising ID - Disable
            (3, """
# Disable Advertising ID
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" -Name "Enabled" -Value 0 -Type DWord -Force
    Write-Output "Advertising ID has been disabled successfully."
} catch {
    Write-Error "Failed to disable Advertising ID: $_"
    exit 1
}
            """),
            
            # Advertising ID - Enable
            (4, """
# Enable Advertising ID
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" -Name "Enabled" -Value 1 -Type DWord -Force
    Write-Output "Advertising ID has been enabled successfully."
} catch {
    Write-Error "Failed to enable Advertising ID: $_"
    exit 1
}
            """),
            
            # Visual Effects - Best Performance
            (5, """
# Set Visual Effects to Best Performance
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name "VisualFXSetting" -Value 2 -Type DWord -Force
    Write-Output "Visual Effects set to Best Performance successfully."
} catch {
    Write-Error "Failed to set Visual Effects to Best Performance: $_"
    exit 1
}
            """),
            
            # Visual Effects - Best Appearance
            (6, """
# Set Visual Effects to Best Appearance
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name "VisualFXSetting" -Value 1 -Type DWord -Force
    Write-Output "Visual Effects set to Best Appearance successfully."
} catch {
    Write-Error "Failed to set Visual Effects to Best Appearance: $_"
    exit 1
}
            """),
            
            # Visual Effects - Custom
            (7, """
# Set Visual Effects to Custom
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name "VisualFXSetting" -Value 3 -Type DWord -Force
    Write-Output "Visual Effects set to Custom successfully."
} catch {
    Write-Error "Failed to set Visual Effects to Custom: $_"
    exit 1
}
            """),
            
            # Metered Connection - Enable
            (8, """
# Enable Metered Connection
try {
    if (!(Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost")) {
        # This requires admin privileges
        New-Item -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" -Name "3" -Value 2 -Type DWord -Force
    Write-Output "Metered Connection has been enabled successfully."
} catch {
    Write-Error "Failed to enable Metered Connection: $_"
    exit 1
}
            """),
            
            # Metered Connection - Disable
            (9, """
# Disable Metered Connection
try {
    if (!(Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost")) {
        # This requires admin privileges
        New-Item -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\NetworkList\\DefaultMediaCost" -Name "3" -Value 1 -Type DWord -Force
    Write-Output "Metered Connection has been disabled successfully."
} catch {
    Write-Error "Failed to disable Metered Connection: $_"
    exit 1
}
            """),
            
            # Dark Mode - Enable
            (10, """
# Enable Dark Mode
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "AppsUseLightTheme" -Value 0 -Type DWord -Force
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "SystemUsesLightTheme" -Value 0 -Type DWord -Force
    Write-Output "Dark Mode has been enabled successfully."
} catch {
    Write-Error "Failed to enable Dark Mode: $_"
    exit 1
}
            """),
            
            # Light Mode - Enable
            (11, """
# Enable Light Mode
try {
    if (!(Test-Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")) {
        New-Item -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Force | Out-Null
    }
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "AppsUseLightTheme" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "SystemUsesLightTheme" -Value 1 -Type DWord -Force
    Write-Output "Light Mode has been enabled successfully."
} catch {
    Write-Error "Failed to enable Light Mode: $_"
    exit 1
}
            """)
        ]
        
        # Update each command
        for action_id, command in updated_commands:
            cursor.execute(
                "UPDATE setting_actions SET powershell_command = ? WHERE id = ?",
                (command.strip(), action_id)
            )
            print(f"Updated command for action ID {action_id}")
        
        # Commit transaction
        conn.commit()
        print("PowerShell commands updated successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("WinRegi PowerShell Command Fix Tool")
    print("==================================")
    
    success = migrate_database()
    
    if success:
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1) 