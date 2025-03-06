"""
Command manager for WinRegi application
Handles execution of custom commands
"""
import os
import subprocess
import sys
from typing import Dict, Any, Tuple, List

from ..database.db_manager import DatabaseManager

class CommandManager:
    """Manages custom commands and their execution"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize command manager
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()
        
        # Define supported command types
        self.command_types = {
            "system": "System/Program",
            "powershell": "PowerShell",
            "batch": "Batch File",
            "registry": "Registry Edit"
        }
    
    def get_command_types(self) -> Dict[str, str]:
        """Get supported command types
        
        Returns:
            Dictionary of command types (key: type_id, value: type_name)
        """
        return self.command_types
    
    def execute_command(self, command_id: int) -> Tuple[bool, str]:
        """Execute a command by ID
        
        Args:
            command_id: ID of the command to execute
            
        Returns:
            Tuple containing success status and output message
        """
        # Get command details
        command = self.db_manager.get_command_by_id(command_id)
        
        if not command:
            return False, "Command not found"
        
        # Update command usage timestamp
        self.db_manager.update_command_usage(command_id)
        
        # Execute based on command type
        cmd_type = command["command_type"]
        cmd_value = command["command_value"]
        
        try:
            if cmd_type == "system":
                return self._execute_system_command(cmd_value)
            elif cmd_type == "powershell":
                return self._execute_powershell_command(cmd_value)
            elif cmd_type == "batch":
                return self._execute_batch_command(cmd_value)
            elif cmd_type == "registry":
                return self._execute_registry_command(cmd_value)
            else:
                return False, f"Unsupported command type: {cmd_type}"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"
    
    def _execute_system_command(self, cmd_value: str) -> Tuple[bool, str]:
        """Execute a system/program command
        
        Args:
            cmd_value: Command to execute
            
        Returns:
            Tuple containing success status and output message
        """
        try:
            # For system commands, use a detached process that won't block
            if sys.platform == "win32":
                # Windows
                subprocess.Popen(cmd_value, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return True, f"Executed system command: {cmd_value}"
            else:
                # Non-Windows (for testing)
                subprocess.Popen(cmd_value, shell=True)
                return True, f"Executed system command: {cmd_value}"
        except Exception as e:
            return False, f"Error executing system command: {str(e)}"
    
    def _execute_powershell_command(self, cmd_value: str) -> Tuple[bool, str]:
        """Execute a PowerShell command
        
        Args:
            cmd_value: PowerShell command to execute
            
        Returns:
            Tuple containing success status and output message
        """
        try:
            if sys.platform == "win32":
                # For PowerShell commands, we can capture output
                # Create a process with PowerShell and execute the command
                process = subprocess.Popen(
                    ["powershell", "-Command", cmd_value],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    return True, stdout
                else:
                    return False, f"PowerShell error: {stderr}"
            else:
                # Non-Windows (for testing)
                return True, f"PowerShell command would execute on Windows: {cmd_value}"
        except Exception as e:
            return False, f"Error executing PowerShell command: {str(e)}"
    
    def _execute_batch_command(self, cmd_value: str) -> Tuple[bool, str]:
        """Execute a batch command
        
        Args:
            cmd_value: Batch command to execute
            
        Returns:
            Tuple containing success status and output message
        """
        try:
            if sys.platform == "win32":
                # For batch files, we need to create a temporary file
                temp_batch_file = os.path.join(os.environ['TEMP'], 'winregi_temp.bat')
                
                with open(temp_batch_file, 'w') as f:
                    f.write(cmd_value)
                
                # Run the batch file
                process = subprocess.Popen(
                    [temp_batch_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                stdout, stderr = process.communicate()
                
                # Clean up the temporary file
                try:
                    os.remove(temp_batch_file)
                except:
                    pass
                
                if process.returncode == 0:
                    return True, stdout
                else:
                    return False, f"Batch error: {stderr}"
            else:
                # Non-Windows (for testing)
                return True, f"Batch command would execute on Windows: {cmd_value}"
        except Exception as e:
            return False, f"Error executing batch command: {str(e)}"
    
    def _execute_registry_command(self, cmd_value: str) -> Tuple[bool, str]:
        """Execute a registry command
        
        Args:
            cmd_value: Registry command in format "path=value" or "path-" (delete)
            
        Returns:
            Tuple containing success status and output message
        """
        try:
            if sys.platform == "win32":
                # For registry commands, we'll use reg.exe
                import winreg
                
                # Check if it's a deletion command (ends with -)
                if cmd_value.endswith('-'):
                    # Delete registry key or value
                    reg_path = cmd_value[:-1]
                    parts = reg_path.split('\\')
                    
                    # Get hive
                    hive_str = parts[0]
                    reg_path = '\\'.join(parts[1:])
                    
                    # Map string hive to winreg constant
                    hive_map = {
                        'HKCU': winreg.HKEY_CURRENT_USER,
                        'HKLM': winreg.HKEY_LOCAL_MACHINE,
                        'HKCR': winreg.HKEY_CLASSES_ROOT,
                        'HKU': winreg.HKEY_USERS,
                        'HKCC': winreg.HKEY_CURRENT_CONFIG
                    }
                    
                    hive = hive_map.get(hive_str)
                    if not hive:
                        return False, f"Invalid registry hive: {hive_str}"
                    
                    # Try to delete the key
                    try:
                        winreg.DeleteKey(hive, reg_path)
                        return True, f"Deleted registry key: {cmd_value}"
                    except WindowsError:
                        # Key might not exist or might have subkeys
                        # Let's try to delete a value instead
                        last_slash = reg_path.rfind('\\')
                        if last_slash > 0:
                            key_path = reg_path[:last_slash]
                            value_name = reg_path[last_slash+1:]
                            
                            try:
                                key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE)
                                winreg.DeleteValue(key, value_name)
                                winreg.CloseKey(key)
                                return True, f"Deleted registry value: {cmd_value}"
                            except WindowsError as e:
                                return False, f"Could not delete registry value: {str(e)}"
                        else:
                            return False, f"Invalid registry path format: {reg_path}"
                else:
                    # Set registry value
                    parts = cmd_value.split('=')
                    if len(parts) != 2:
                        return False, "Invalid registry command format. Expected: path=value"
                    
                    reg_path, reg_value = parts
                    
                    # Split path into components
                    path_parts = reg_path.split('\\')
                    
                    # Get hive
                    hive_str = path_parts[0]
                    
                    # Map string hive to winreg constant
                    hive_map = {
                        'HKCU': winreg.HKEY_CURRENT_USER,
                        'HKLM': winreg.HKEY_LOCAL_MACHINE,
                        'HKCR': winreg.HKEY_CLASSES_ROOT,
                        'HKU': winreg.HKEY_USERS,
                        'HKCC': winreg.HKEY_CURRENT_CONFIG
                    }
                    
                    hive = hive_map.get(hive_str)
                    if not hive:
                        return False, f"Invalid registry hive: {hive_str}"
                    
                    # Key path is everything except the last part (which is the value name)
                    key_path = '\\'.join(path_parts[1:-1])
                    value_name = path_parts[-1]
                    
                    # Determine value type and parse value
                    if reg_value.startswith('dword:'):
                        value_type = winreg.REG_DWORD
                        try:
                            reg_value = int(reg_value[6:], 16)
                        except ValueError:
                            return False, f"Invalid DWORD value: {reg_value}"
                    elif reg_value.startswith('qword:'):
                        value_type = winreg.REG_QWORD
                        try:
                            reg_value = int(reg_value[6:], 16)
                        except ValueError:
                            return False, f"Invalid QWORD value: {reg_value}"
                    elif reg_value.startswith('hex:'):
                        value_type = winreg.REG_BINARY
                        try:
                            hex_values = reg_value[4:].split(',')
                            reg_value = bytes([int(x, 16) for x in hex_values])
                        except ValueError:
                            return False, f"Invalid binary value: {reg_value}"
                    else:
                        # Assume string value
                        value_type = winreg.REG_SZ
                    
                    try:
                        # Create or open the key
                        key = winreg.CreateKeyEx(hive, key_path, 0, winreg.KEY_WRITE)
                        
                        # Set the value
                        winreg.SetValueEx(key, value_name, 0, value_type, reg_value)
                        
                        # Close the key
                        winreg.CloseKey(key)
                        
                        return True, f"Set registry value: {cmd_value}"
                    except Exception as e:
                        return False, f"Error setting registry value: {str(e)}"
            else:
                # Non-Windows (for testing)
                return True, f"Registry command would execute on Windows: {cmd_value}"
        except Exception as e:
            return False, f"Error executing registry command: {str(e)}"
    
    def validate_command(self, cmd_type: str, cmd_value: str) -> Tuple[bool, str]:
        """Validate a command before adding it
        
        Args:
            cmd_type: Command type
            cmd_value: Command value
            
        Returns:
            Tuple containing validation status and error message (if any)
        """
        # Check if command type is supported
        if cmd_type not in self.command_types:
            return False, f"Unsupported command type: {cmd_type}"
        
        # Basic validation based on command type
        if not cmd_value or not cmd_value.strip():
            return False, "Command value cannot be empty"
        
        if cmd_type == "system":
            # Basic validation for system commands
            # We can't really validate much for system commands
            return True, ""
        
        elif cmd_type == "powershell":
            # Basic validation for PowerShell commands
            # We'll just check if it looks like PowerShell
            if not any(keyword in cmd_value.lower() for keyword in 
                      ["get-", "set-", "new-", "remove-", "$", "-command", 
                       "write-", "read-", "start-", "stop-", "out-", "invoke-"]):
                return False, "Command doesn't look like valid PowerShell. Please check your syntax."
            return True, ""
        
        elif cmd_type == "batch":
            # Basic validation for batch commands
            # We'll just check if it looks like a batch file
            if not any(keyword in cmd_value.lower() for keyword in 
                      ["@echo", "call", "cd", "cls", "cmd", "color", "date", "dir",
                       "echo", "exit", "find", "findstr", "for", "goto", "if", "md",
                       "mkdir", "pause", "rd", "rem", "rmdir", "set", "setlocal",
                       "start", "title", "type", "ver", "vol"]):
                return False, "Command doesn't look like a valid batch file. Please check your syntax."
            return True, ""
        
        elif cmd_type == "registry":
            # Validate registry commands
            # Format should be path=value or path- (for deletion)
            if cmd_value.endswith('-'):
                # Deletion - just check the path format
                reg_path = cmd_value[:-1]
                if not reg_path.startswith(('HKCU\\', 'HKLM\\', 'HKCR\\', 'HKU\\', 'HKCC\\')):
                    return False, "Registry path must start with a valid hive (HKCU, HKLM, HKCR, HKU, HKCC)"
                if not '\\' in reg_path or len(reg_path.split('\\')) < 2:
                    return False, "Invalid registry path format"
            else:
                # Setting a value
                parts = cmd_value.split('=')
                if len(parts) != 2:
                    return False, "Invalid registry command format. Expected: path=value"
                
                reg_path, reg_value = parts
                
                if not reg_path.startswith(('HKCU\\', 'HKLM\\', 'HKCR\\', 'HKU\\', 'HKCC\\')):
                    return False, "Registry path must start with a valid hive (HKCU, HKLM, HKCR, HKU, HKCC)"
                if not '\\' in reg_path or len(reg_path.split('\\')) < 2:
                    return False, "Invalid registry path format"
                
                # Validate the value format
                if reg_value.startswith('dword:'):
                    try:
                        int(reg_value[6:], 16)
                    except ValueError:
                        return False, "Invalid DWORD value format. Expected: dword:00000000"
                elif reg_value.startswith('qword:'):
                    try:
                        int(reg_value[6:], 16)
                    except ValueError:
                        return False, "Invalid QWORD value format. Expected: qword:0000000000000000"
                elif reg_value.startswith('hex:'):
                    try:
                        hex_values = reg_value[4:].split(',')
                        [int(x, 16) for x in hex_values]
                    except ValueError:
                        return False, "Invalid binary value format. Expected: hex:00,01,02,..."
            
            return True, ""
        
        return False, "Invalid command type"