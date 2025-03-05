"""
Windows Registry manager for WinRegi application
Handles Windows Registry operations
"""
import winreg
import sys
import ctypes
from typing import Any, Tuple, Dict, List, Optional, Union

class RegistryManager:
    """Manages Windows Registry operations"""
    
    # Registry root keys mapping
    ROOT_KEYS = {
        "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_USERS": winreg.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKU": winreg.HKEY_USERS,
        "HKCC": winreg.HKEY_CURRENT_CONFIG
    }
    
    # Registry value types mapping
    VALUE_TYPES = {
        "REG_SZ": winreg.REG_SZ,
        "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
        "REG_DWORD": winreg.REG_DWORD,
        "REG_QWORD": winreg.REG_QWORD,
        "REG_BINARY": winreg.REG_BINARY,
        "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ
    }
    
    def __init__(self):
        """Initialize Registry Manager"""
        self.is_admin = self._is_admin()
    
    def _is_admin(self) -> bool:
        """Check if the application is running with admin privileges
        
        Returns:
            True if running as admin, False otherwise
        """
        try:
            if sys.platform == 'win32':
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return False
        except:
            return False
    
    def parse_registry_path(self, path: str) -> Tuple[int, str, Optional[str]]:
        """Parse a registry path string into components
        
        Args:
            path: Registry path string (e.g., "HKCU\\Software\\Microsoft\\Windows")
            
        Returns:
            Tuple of (root_key_handle, subkey_path, value_name)
        """
        # Split the path into parts
        parts = path.split("\\")
        
        # Extract the root key
        root_key_str = parts[0]
        if root_key_str not in self.ROOT_KEYS:
            raise ValueError(f"Invalid registry root key: {root_key_str}")
        
        root_key = self.ROOT_KEYS[root_key_str]
        
        # Check if the path contains a value name
        value_name = None
        subkey_parts = parts[1:]
        
        if ":" in path:
            # If path contains a colon, the part after the last colon is the value name
            path_without_root = "\\".join(subkey_parts)
            key_path, value_name = path_without_root.rsplit(":", 1)
            subkey_parts = key_path.split("\\")
        
        subkey_path = "\\".join(subkey_parts)
        
        return root_key, subkey_path, value_name
    
    def read_registry_value(self, path: str) -> Optional[Tuple[Any, str]]:
        """Read a value from the Windows Registry
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft\\Windows:DisplayVersion")
            
        Returns:
            Tuple of (value_data, value_type) or None if not found
        """
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is None:
            raise ValueError("Registry path must include a value name")
        
        try:
            # Open the registry key
            key = winreg.OpenKey(root_key, subkey_path)
            
            # Read the value
            value_data, value_type_id = winreg.QueryValueEx(key, value_name)
            
            # Get the value type name
            value_type = None
            for type_name, type_id in self.VALUE_TYPES.items():
                if type_id == value_type_id:
                    value_type = type_name
                    break
            
            # Close the key
            winreg.CloseKey(key)
            
            return value_data, value_type
            
        except FileNotFoundError:
            return None
        except Exception as e:
            raise e
    
    def write_registry_value(self, path: str, value: Any, value_type: str = "REG_SZ") -> Dict[str, Any]:
        """Write a value to the Windows Registry
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft\\Windows:DisplayVersion")
            value: The value to write
            value_type: Registry value type (e.g., "REG_SZ", "REG_DWORD")
            
        Returns:
            Dict with success status and message
        """
        # Check if admin is required for HKLM or HKCR
        root_key_str = path.split("\\")[0].upper()
        needs_admin = root_key_str in ["HKEY_LOCAL_MACHINE", "HKLM", "HKEY_CLASSES_ROOT", "HKCR"]
        
        if needs_admin and not self.is_admin:
            return {
                "success": False,
                "message": "Administrator privileges required for this operation",
                "requires_admin": True
            }
            
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is None:
            return {
                "success": False,
                "message": "Registry path must include a value name",
                "requires_admin": False
            }
        
        if value_type not in self.VALUE_TYPES:
            return {
                "success": False,
                "message": f"Invalid registry value type: {value_type}",
                "requires_admin": False
            }
        
        value_type_id = self.VALUE_TYPES[value_type]
        
        try:
            # Ensure the key exists by creating it if necessary
            key = winreg.CreateKeyEx(root_key, subkey_path)
            
            # Write the value
            winreg.SetValueEx(key, value_name, 0, value_type_id, value)
            
            # Close the key
            winreg.CloseKey(key)
            
            return {
                "success": True,
                "message": "Registry value written successfully",
                "requires_admin": False
            }
            
        except PermissionError:
            return {
                "success": False,
                "message": "Permission denied. Administrator privileges may be required.",
                "requires_admin": True
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error writing registry value: {str(e)}",
                "requires_admin": False
            }
    
    def delete_registry_value(self, path: str) -> bool:
        """Delete a value from the Windows Registry
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft\\Windows:DisplayVersion")
            
        Returns:
            True if successful, False otherwise
        """
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is None:
            raise ValueError("Registry path must include a value name")
        
        try:
            # Open the registry key
            key = winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_SET_VALUE)
            
            # Delete the value
            winreg.DeleteValue(key, value_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
            raise e
    
    def delete_registry_key(self, path: str) -> bool:
        """Delete a key from the Windows Registry
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft\\Windows")
            
        Returns:
            True if successful, False otherwise
        """
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is not None:
            # Remove the value name from the path
            subkey_path = subkey_path + "\\" + value_name
        
        # Split the path to get parent key and subkey name
        parent_path, subkey_name = "\\".join(subkey_path.split("\\")[:-1]), subkey_path.split("\\")[-1]
        
        try:
            # Open the parent key
            parent_key = winreg.OpenKey(root_key, parent_path, 0, winreg.KEY_ALL_ACCESS)
            
            # Delete the subkey
            winreg.DeleteKey(parent_key, subkey_name)
            
            # Close the key
            winreg.CloseKey(parent_key)
            
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
            raise e
    
    def create_registry_key(self, path: str) -> Dict[str, Any]:
        """Create a key in the Windows Registry
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\MyApp")
            
        Returns:
            Dictionary with success status and message
        """
        # Check if admin is required for HKLM or HKCR
        root_key_str = path.split("\\")[0].upper()
        needs_admin = root_key_str in ["HKEY_LOCAL_MACHINE", "HKLM", "HKEY_CLASSES_ROOT", "HKCR"]
        
        if needs_admin and not self.is_admin:
            return {
                "success": False,
                "message": "Administrator privileges required for this operation",
                "requires_admin": True
            }
            
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is not None:
            # Ignore value name for key creation
            subkey_path = subkey_path + "\\" + value_name
        
        try:
            # Create the key
            key = winreg.CreateKey(root_key, subkey_path)
            
            # Close the key
            winreg.CloseKey(key)
            
            return {
                "success": True,
                "message": "Registry key created successfully",
                "requires_admin": False
            }
            
        except PermissionError:
            return {
                "success": False,
                "message": "Permission denied. Administrator privileges may be required.",
                "requires_admin": True
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating registry key: {str(e)}",
                "requires_admin": False
            }
    
    def list_registry_values(self, path: str) -> List[Dict[str, Any]]:
        """List all values in a registry key
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft\\Windows")
            
        Returns:
            List of dictionaries containing value information
        """
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is not None:
            # Ignore value name for key enumeration
            subkey_path = subkey_path + "\\" + value_name
        
        try:
            # Open the registry key
            key = winreg.OpenKey(root_key, subkey_path)
            
            # Get the number of values
            value_count = winreg.QueryInfoKey(key)[1]
            
            values = []
            
            # Enumerate all values
            for i in range(value_count):
                try:
                    name, data, type_id = winreg.EnumValue(key, i)
                    
                    # Get the value type name
                    value_type = None
                    for type_name, tid in self.VALUE_TYPES.items():
                        if tid == type_id:
                            value_type = type_name
                            break
                    
                    values.append({
                        "name": name,
                        "data": data,
                        "type": value_type
                    })
                except OSError:
                    continue
            
            # Close the key
            winreg.CloseKey(key)
            
            return values
            
        except FileNotFoundError:
            return []
        except Exception as e:
            raise e
    
    def list_registry_keys(self, path: str) -> List[str]:
        """List all subkeys in a registry key
        
        Args:
            path: Registry path (e.g., "HKCU\\Software\\Microsoft")
            
        Returns:
            List of subkey names
        """
        root_key, subkey_path, value_name = self.parse_registry_path(path)
        
        if value_name is not None:
            # Ignore value name for key enumeration
            subkey_path = subkey_path + "\\" + value_name
        
        try:
            # Open the registry key
            key = winreg.OpenKey(root_key, subkey_path)
            
            # Get the number of subkeys
            subkey_count = winreg.QueryInfoKey(key)[0]
            
            subkeys = []
            
            # Enumerate all subkeys
            for i in range(subkey_count):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkeys.append(subkey_name)
                except OSError:
                    continue
            
            # Close the key
            winreg.CloseKey(key)
            
            return subkeys
            
        except FileNotFoundError:
            return []
        except Exception as e:
            raise e
    
    def parse_registry_action(self, action_value: str) -> Tuple[str, Any, Optional[str]]:
        """Parse a registry action string
        
        Args:
            action_value: Registry action string (e.g., "HKCU\\Path:ValueName=Data")
            
        Returns:
            Tuple of (path, data, value_type)
        """
        # Split by equals sign to separate path and data
        if "=" in action_value:
            path, data_str = action_value.split("=", 1)
            
            # Determine data type and parse
            if data_str.startswith("dword:"):
                data = int(data_str[6:], 16)
                value_type = "REG_DWORD"
            elif data_str.startswith("qword:"):
                data = int(data_str[6:], 16)
                value_type = "REG_QWORD"
            elif data_str.startswith("hex:"):
                # Convert hex string to bytes
                hex_values = data_str[4:].split(",")
                data = bytes([int(x, 16) for x in hex_values])
                value_type = "REG_BINARY"
            elif data_str.startswith("([byte[]])"):
                # Parse byte array notation
                byte_array_str = data_str.replace("([byte[]])(", "").replace(")", "")
                hex_values = [x.strip() for x in byte_array_str.split(",")]
                data = bytes([int(x.replace("0x", ""), 16) for x in hex_values])
                value_type = "REG_BINARY"
            elif data_str.startswith('"') and data_str.endswith('"'):
                # String value
                data = data_str[1:-1]
                value_type = "REG_SZ"
            else:
                # Default to string
                data = data_str
                value_type = "REG_SZ"
        else:
            # If no equals sign, assume it's a key creation
            path = action_value
            data = None
            value_type = None
        
        return path, data, value_type
    
    def execute_registry_action(self, action_value: str) -> Dict[str, Any]:
        """Execute a registry action
        
        Args:
            action_value: Registry action string (e.g., "HKCU\\Path:ValueName=Data")
            
        Returns:
            Dictionary with success status and message
        """
        path, data, value_type = self.parse_registry_action(action_value)
        
        if data is None:
            # Create key
            result = self.create_registry_key(path)
            if isinstance(result, bool):
                return {
                    "success": result,
                    "message": "Registry key created successfully" if result else "Failed to create registry key",
                    "requires_admin": False
                }
            return result
        else:
            # Write value
            return self.write_registry_value(path, data, value_type)