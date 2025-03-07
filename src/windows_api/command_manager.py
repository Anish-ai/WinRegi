"""
Command manager for WinRegi application
Handles execution of custom commands
"""
import os
import subprocess
import tempfile
import sys
import re
import winreg

class CommandManager:
    """Manages execution of custom commands"""
    
    def __init__(self, db_manager):
        """Initialize command manager
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        
        # Define available command types
        self._command_types = {
            "system": "System Command",
            "powershell": "PowerShell Script",
            "batch": "Batch Script",
            "registry": "Registry Edit"
        }
    
    def get_command_types(self):
        """Get available command types
        
        Returns:
            Dictionary of command types
        """
        return self._command_types
    
    def execute_command(self, command_id):
        """Execute a command by ID
        
        Args:
            command_id: ID of the command to execute
            
        Returns:
            Tuple of (success, output)
        """
        # Get command from database
        command = self.db_manager.get_command_by_id(command_id)
        if not command:
            return False, "Command not found"
        
        # Update last used timestamp
        try:
            self.db_manager.update_command_usage(command_id)
        except Exception as e:
            # Non-critical error, can continue
            print(f"Failed to update command usage: {e}")
        
        # Dispatch to appropriate handler
        cmd_type = command["command_type"]
        cmd_value = command["command_value"]
        
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
    
    def validate_command(self, cmd_type, cmd_value):
        """Validate a command
        
        Args:
            cmd_type: Command type
            cmd_value: Command value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if cmd_type == "system":
            # Basic validation for system commands
            if not cmd_value.strip():
                return False, "Command cannot be empty"
                
            # Check for potentially dangerous commands
            dangerous_commands = ["format", "rm -rf", "deltree", "del /s", "del /q"]
            for dangerous in dangerous_commands:
                if dangerous in cmd_value.lower():
                    return False, f"Command contains potentially dangerous operation: {dangerous}"
                    
            return True, ""
            
        elif cmd_type == "powershell":
            # Basic validation for PowerShell scripts
            if not cmd_value.strip():
                return False, "PowerShell script cannot be empty"
                
            # Check for potentially dangerous commands
            dangerous_commands = ["Remove-Item -Recurse -Force", "Format-Volume", "Clear-"]
            for dangerous in dangerous_commands:
                if dangerous in cmd_value:
                    return False, f"Script contains potentially dangerous operation: {dangerous}"
                    
            return True, ""
            
        elif cmd_type == "batch":
            # Basic validation for batch scripts
            if not cmd_value.strip():
                return False, "Batch script cannot be empty"
                
            # Check for potentially dangerous commands
            dangerous_commands = ["format", "rmdir /s", "del /s", "del /q", "rd /s"]
            for dangerous in dangerous_commands:
                if dangerous in cmd_value.lower():
                    return False, f"Script contains potentially dangerous operation: {dangerous}"
                    
            return True, ""
            
        elif cmd_type == "registry":
            # Validate registry command format
            if not cmd_value.strip():
                return False, "Registry command cannot be empty"
                
            # Check format: path=value or path-
            if not re.match(r"^[A-Za-z0-9\\:_]+[=\\-].*$", cmd_value):
                return False, "Invalid registry command format. Should be 'path=value' or 'path-'"
                
            # Check if registry path starts with a valid root key
            valid_roots = ["HKCU", "HKLM", "HKCR", "HKU", "HKCC"]
            if not any(cmd_value.startswith(root) for root in valid_roots):
                return False, "Registry path must start with a valid root key (HKCU, HKLM, HKCR, HKU, HKCC)"
                
            return True, ""
            
        else:
            return False, f"Unsupported command type: {cmd_type}"
    
    def _execute_system_command(self, command):
        """Execute a system command
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # Run the command
            process = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Combine stdout and stderr
            output = process.stdout
            if process.stderr:
                if output:
                    output += "\n" + process.stderr
                else:
                    output = process.stderr
            
            return process.returncode == 0, output
        except Exception as e:
            return False, str(e)
    
    def _execute_powershell_command(self, command):
        """Execute a PowerShell command
        
        Args:
            command: PowerShell command to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # Run PowerShell with the command
            process = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Combine stdout and stderr
            output = process.stdout
            if process.stderr:
                if output:
                    output += "\n" + process.stderr
                else:
                    output = process.stderr
            
            return process.returncode == 0, output
        except Exception as e:
            return False, str(e)
    
    def _execute_batch_command(self, command):
        """Execute a batch command
        
        Args:
            command: Batch commands to execute
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # Create a temporary batch file
            with tempfile.NamedTemporaryFile(suffix=".bat", delete=False, mode="w") as batch_file:
                batch_file.write(command)
                batch_file_path = batch_file.name
            
            # Run the batch file
            try:
                process = subprocess.run(
                    batch_file_path,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Combine stdout and stderr
                output = process.stdout
                if process.stderr:
                    if output:
                        output += "\n" + process.stderr
                    else:
                        output = process.stderr
                
                return process.returncode == 0, output
            finally:
                # Clean up the temporary file
                try:
                    os.remove(batch_file_path)
                except:
                    pass
        except Exception as e:
            return False, str(e)
    
    def _execute_registry_command(self, command):
        """Execute a registry command
        
        Args:
            command: Registry command to execute (path=value or path-)
            
        Returns:
            Tuple of (success, output)
        """
        try:
            # Parse command
            if "=" in command:
                # Set value
                path, value = command.split("=", 1)
                delete = False
            elif command.endswith("-"):
                # Delete value
                path = command[:-1]
                value = None
                delete = True
            else:
                return False, "Invalid registry command format"
            
            # Parse registry path
            root_key_str, subkey_path = path.split("\\", 1)
            
            # Map root key string to actual key
            root_keys = {
                "HKCU": winreg.HKEY_CURRENT_USER,
                "HKLM": winreg.HKEY_LOCAL_MACHINE,
                "HKCR": winreg.HKEY_CLASSES_ROOT,
                "HKU": winreg.HKEY_USERS,
                "HKCC": winreg.HKEY_CURRENT_CONFIG
            }
            
            if root_key_str not in root_keys:
                return False, f"Invalid root key: {root_key_str}"
            
            root_key = root_keys[root_key_str]
            
            # Get value name (if any)
            value_name = None
            if "\\" in subkey_path:
                # The last element might be a value name
                *subkey_parts, last_part = subkey_path.split("\\")
                
                # If the last part contains non-path characters, it's likely a value name
                if re.search(r'[^A-Za-z0-9_\-]', last_part):
                    value_name = last_part
                    subkey_path = "\\".join(subkey_parts)
            
            # Open the key
            try:
                key = winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                # Create the key if it doesn't exist
                key = winreg.CreateKey(root_key, subkey_path)
            
            # Perform the requested operation
            if delete:
                # Delete the value
                if value_name:
                    winreg.DeleteValue(key, value_name)
                else:
                    # If no value name is specified, delete the key
                    winreg.DeleteKey(root_key, subkey_path)
                
                return True, f"Deleted {path}"
            else:
                # Set the value
                # Determine value type (simple heuristic)
                if value.isdigit():
                    # Integer
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, int(value))
                elif value.startswith("0x"):
                    # Hex value
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, int(value, 16))
                else:
                    # String
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)
                
                return True, f"Set {path} = {value}"
        
        except FileNotFoundError:
            return False, f"Registry key not found: {path}"
        except PermissionError:
            return False, "Permission denied. Try running as administrator."
        except Exception as e:
            return False, str(e)