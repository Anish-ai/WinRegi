"""
PowerShell manager for WinRegi application
Handles PowerShell command execution
"""
import subprocess
import os
import tempfile
from typing import Tuple, Optional, List, Dict, Any

class PowerShellManager:
    """Manages PowerShell command execution"""
    
    def __init__(self):
        """Initialize PowerShell Manager"""
        self.powershell_path = "powershell.exe"
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute a PowerShell command
        
        Args:
            command: PowerShell command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Log the command for debugging
            print(f"Executing PowerShell command: {command}")
            
            # Create a process to execute the PowerShell command
            process = subprocess.Popen(
                [self.powershell_path, "-ExecutionPolicy", "Bypass", "-NoProfile", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for the process to complete with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            
            # Check if the command was successful
            success = process.returncode == 0
            
            # Log the command and result for debugging
            print(f"PowerShell command result: {'Success' if success else 'Failed'}")
            if stdout:
                print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            process.kill()
            stdout, stderr = process.communicate()
            print(f"PowerShell command timed out after {timeout} seconds")
            return False, stdout, f"Command timed out after {timeout} seconds"
        
        except Exception as e:
            print(f"Exception executing PowerShell command: {str(e)}")
            return False, "", str(e)
    
    def execute_script(self, script_content: str, timeout: int = 60) -> Tuple[bool, str, str]:
        """Execute a PowerShell script
        
        Args:
            script_content: Content of the PowerShell script
            timeout: Script timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Create a temporary file for the script
            with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="w") as temp_file:
                temp_file.write(script_content)
                script_path = temp_file.name
            
            # Execute the script
            process = subprocess.Popen(
                [self.powershell_path, "-ExecutionPolicy", "Bypass", "-File", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for the process to complete with timeout
            stdout, stderr = process.communicate(timeout=timeout)
            
            # Check if the script was successful
            success = process.returncode == 0
            
            # Clean up the temporary file
            os.unlink(script_path)
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            # Kill the process if it times out
            process.kill()
            stdout, stderr = process.communicate()
            # Clean up the temporary file
            os.unlink(script_path)
            return False, stdout, f"Script execution timed out after {timeout} seconds"
        
        except Exception as e:
            # Clean up the temporary file
            if 'script_path' in locals():
                os.unlink(script_path)
            return False, "", str(e)
    
    def get_process_output(self, command: str) -> Tuple[bool, Any]:
        """Execute a PowerShell command and parse the output
        
        Args:
            command: PowerShell command to execute
            
        Returns:
            Tuple of (success, parsed_output)
        """
        # Execute the command with ConvertTo-Json to get structured output
        full_command = f"{command} | ConvertTo-Json -Depth 5 -Compress"
        success, stdout, stderr = self.execute_command(full_command)
        
        if not success:
            return False, stderr
        
        try:
            # Parse the JSON output
            import json
            parsed_output = json.loads(stdout)
            return True, parsed_output
        except json.JSONDecodeError:
            # If the output is not valid JSON, return the raw output
            return True, stdout
    
    def is_admin(self) -> bool:
        """Check if the current process has administrator privileges
        
        Returns:
            True if running as administrator, False otherwise
        """
        command = "[Security.Principal.WindowsIdentity]::GetCurrent() | "
        command += "ForEach-Object { ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) }"
        
        success, stdout, _ = self.execute_command(command)
        
        if success and stdout.strip().lower() == "true":
            return True
        
        return False
    
    def open_settings_page(self, settings_uri: str) -> bool:
        """Open a Windows Settings page using ms-settings URI
        
        Args:
            settings_uri: Settings URI (e.g., "ms-settings:display")
            
        Returns:
            True if successful, False otherwise
        """
        command = f"Start-Process '{settings_uri}'"
        success, _, _ = self.execute_command(command)
        return success
    
    def open_control_panel_item(self, control_panel_path: str) -> bool:
        """Open a Control Panel applet
        
        Args:
            control_panel_path: Control Panel applet path (e.g., "desk.cpl")
            
        Returns:
            True if successful, False otherwise
        """
        command = f"Start-Process control -ArgumentList '{control_panel_path}'"
        success, _, _ = self.execute_command(command)
        return success
    
    def get_registry_value(self, path: str, name: str) -> Tuple[bool, Any]:
        """Get a registry value using PowerShell
        
        Args:
            path: Registry path (e.g., "HKCU:\\Software\\Microsoft\\Windows")
            name: Value name
            
        Returns:
            Tuple of (success, value)
        """
        command = f"Get-ItemProperty -Path '{path}' -Name '{name}' | Select-Object -ExpandProperty '{name}'"
        success, stdout, _ = self.execute_command(command)
        
        if success:
            return True, stdout.strip()
        else:
            return False, None
    
    def set_registry_value(self, path: str, name: str, value: Any, type_name: str = "String") -> bool:
        """Set a registry value using PowerShell
        
        Args:
            path: Registry path (e.g., "HKCU:\\Software\\Microsoft\\Windows")
            name: Value name
            value: Value to set
            type_name: Registry value type
            
        Returns:
            True if successful, False otherwise
        """
        # Format the value based on type
        if type_name == "String":
            formatted_value = f"'{value}'"
        elif type_name == "DWord" or type_name == "QWord":
            formatted_value = str(value)
        elif type_name == "Binary":
            if isinstance(value, bytes):
                # Convert bytes to byte array string
                formatted_value = "([byte[]]@(" + ",".join([str(b) for b in value]) + "))"
            else:
                formatted_value = value
        else:
            formatted_value = f"'{value}'"
        
        # Create the command
        command = f"New-Item -Path '{path}' -Force | Out-Null; "
        command += f"Set-ItemProperty -Path '{path}' -Name '{name}' -Value {formatted_value} -Type {type_name}"
        
        success, _, _ = self.execute_command(command)
        return success
        
    def set_windows_theme(self, theme: str) -> Tuple[bool, str, str]:
        """Set Windows theme (light/dark)
        
        Args:
            theme: Theme to set ('light' or 'dark')
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        theme_value = 1 if theme.lower() == 'light' else 0
        
        script = f"""
        # Set app theme
        New-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "AppsUseLightTheme" -Value {theme_value} -PropertyType DWord -Force
        
        # Set system theme
        New-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "SystemUsesLightTheme" -Value {theme_value} -PropertyType DWord -Force
        
        # Restart Explorer to apply changes
        Stop-Process -Name explorer -Force
        """
        
        return self.execute_script(script)