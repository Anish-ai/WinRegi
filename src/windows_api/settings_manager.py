"""
Windows Settings manager for WinRegi application
Orchestrates registry, PowerShell, and direct settings modifications
"""
from typing import Dict, Any, List, Tuple, Optional
from .registry_manager import RegistryManager
from .powershell_manager import PowerShellManager

class SettingsManager:
    """Manages Windows settings operations"""
    
    def __init__(self):
        """Initialize Settings Manager"""
        self.registry_manager = RegistryManager()
        self.powershell_manager = PowerShellManager()
    
    def apply_setting_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a setting action
        
        Args:
            action: Setting action dictionary
            
        Returns:
            Result dictionary with status and message
        """
        action_type = action.get('action_type', '').lower()
        action_value = action.get('action_value', '')
        
        try:
            if action_type == 'registry':
                # Execute registry action
                result = self.registry_manager.execute_registry_action(action_value)
                
                # Check if admin rights are required
                if result.get('requires_admin', False):
                    return {
                        'success': False,
                        'message': result.get('message', 'Administrator privileges required'),
                        'requires_admin': True
                    }
                    
                return {
                    'success': result.get('success', False),
                    'message': result.get('message', 'Registry modification completed'),
                    'requires_admin': False
                }
                
            elif action_type == 'powershell':
                # Check if PowerShell command needs admin privileges
                if 'runas' in action_value.lower() or any(cmd in action_value.lower() for cmd in ['restart-service', 'stop-service', 'start-service']):
                    if not self.registry_manager.is_admin:
                        return {
                            'success': False,
                            'message': 'Administrator privileges required for this PowerShell command',
                            'requires_admin': True
                        }
                
                # Execute PowerShell command
                success, stdout, stderr = self.powershell_manager.execute_command(action_value)
                
                return {
                    'success': success,
                    'message': stdout if success else stderr,
                    'requires_admin': False
                }
                
            elif action_type == 'control_panel':
                # Open Control Panel applet
                success = self.powershell_manager.open_control_panel_item(action_value)
                
                return {
                    'success': success,
                    'message': f'Opened Control Panel: {action_value}' if success else f'Failed to open Control Panel: {action_value}',
                    'requires_admin': False
                }
                
            elif action_type == 'ms_settings':
                # Open Settings app page
                success = self.powershell_manager.open_settings_page(action_value)
                
                return {
                    'success': success,
                    'message': f'Opened Settings: {action_value}' if success else f'Failed to open Settings: {action_value}',
                    'requires_admin': False
                }
                
            elif action_type == 'group_policy':
                # Check for admin privileges as Group Policy Editor requires them
                if not self.registry_manager.is_admin:
                    return {
                        'success': False,
                        'message': 'Administrator privileges required to open Group Policy Editor',
                        'requires_admin': True
                    }
                    
                # Not directly implemented due to Group Policy API complexity
                # Instead, open Group Policy Editor
                success = self.powershell_manager.execute_command(f"Start-Process gpedit.msc")
                
                return {
                    'success': success,
                    'message': 'Opened Group Policy Editor' if success else 'Failed to open Group Policy Editor',
                    'requires_admin': False
                }
                
            else:
                return {
                    'success': False,
                    'message': f'Unsupported action type: {action_type}',
                    'requires_admin': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error applying setting: {str(e)}',
                'requires_admin': False
            }
    
    def get_setting_status(self, setting: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current status of a setting
        
        Args:
            setting: Setting dictionary
            
        Returns:
            Status dictionary with current value and state
        """
        try:
            # Try to determine the current state based on access method
            access_method = setting.get('access_method_id')
            
            if access_method == 1:  # Registry
                registry_path = setting.get('registry_path')
                if registry_path:
                    # Parse the registry path to extract value name
                    root_key, subkey_path, value_name = self.registry_manager.parse_registry_path(registry_path)
                    
                    if value_name:
                        # Read the registry value
                        value = self.registry_manager.read_registry_value(registry_path)
                        
                        if value:
                            return {
                                'current_value': value[0],
                                'value_type': value[1],
                                'exists': True,
                                'message': 'Registry value exists'
                            }
                        else:
                            return {
                                'current_value': None,
                                'value_type': None,
                                'exists': False,
                                'message': 'Registry value does not exist'
                            }
            
            elif access_method == 2:  # PowerShell
                # For PowerShell-based settings, we need a specific command to check status
                # This is a simplified implementation
                powershell_command = setting.get('powershell_command')
                if powershell_command and 'Get-' in powershell_command:
                    success, output, _ = self.powershell_manager.execute_command(powershell_command)
                    
                    if success:
                        return {
                            'current_value': output.strip(),
                            'exists': True,
                            'message': 'PowerShell command executed successfully'
                        }
                    else:
                        return {
                            'current_value': None,
                            'exists': False,
                            'message': 'PowerShell command failed'
                        }
            
            # For other access methods, we can't easily determine status
            return {
                'current_value': None,
                'exists': None,
                'message': 'Status determination not supported for this setting'
            }
            
        except Exception as e:
            return {
                'current_value': None,
                'exists': None,
                'error': True,
                'message': f'Error checking setting status: {str(e)}'
            }
    
    def get_recommended_actions(self, setting_id: int, db_manager) -> List[Dict[str, Any]]:
        """Get recommended actions for a setting
        
        Args:
            setting_id: Setting ID
            db_manager: Database manager instance
            
        Returns:
            List of recommended actions
        """
        # Get all actions for the setting
        all_actions = db_manager.get_actions_for_setting(setting_id)
        
        # Get default action if available
        default_actions = [action for action in all_actions if action.get('is_default', 0) == 1]
        
        if default_actions:
            return default_actions
        
        # If no default action, return all actions
        return all_actions
    
    def set_windows_theme(self, theme: str) -> Dict[str, Any]:
        """Set Windows theme to light or dark
        
        Args:
            theme: Theme to set ('light' or 'dark')
            
        Returns:
            Dictionary with status and message
        """
        if theme not in ['light', 'dark']:
            return {
                'success': False,
                'message': f'Invalid theme: {theme}. Must be "light" or "dark"',
                'requires_admin': False
            }
        
        # Check if admin is required to restart explorer
        requires_admin = False
        
        # Apply the theme change
        success, stdout, stderr = self.powershell_manager.set_windows_theme(theme)
        
        if not success and "Access is denied" in stderr:
            requires_admin = True
            return {
                'success': False,
                'message': 'Administrator privileges required to restart Explorer',
                'requires_admin': requires_admin
            }
        
        return {
            'success': success,
            'message': f'Windows {theme} theme applied successfully' if success else f'Failed to apply {theme} theme: {stderr}',
            'requires_admin': requires_admin
        }
    
    def analyze_system_settings(self) -> Dict[str, Any]:
        """Analyze system settings to provide optimization recommendations
        
        Returns:
            Dictionary with analysis results
        """
        recommendations = []
        
        # Check performance settings
        success, stdout, _ = self.powershell_manager.execute_command(
            "(Get-CimInstance -ClassName Win32_OperatingSystem).Name"
        )
        
        if success:
            windows_version = stdout.strip()
            
            # Add system info
            recommendations.append({
                'category': 'System',
                'name': 'Windows Version',
                'value': windows_version,
                'recommendation': None
            })
        
        # Check visual effects setting
        try:
            visual_fx = self.registry_manager.read_registry_value(
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects:VisualFXSetting"
            )
            
            if visual_fx:
                value, _ = visual_fx
                if value != 2:  # 2 is best performance
                    recommendations.append({
                        'category': 'Performance',
                        'name': 'Visual Effects',
                        'value': 'Not optimized for performance',
                        'recommendation': 'Set visual effects to "Best performance" to improve system responsiveness'
                    })
        except:
            pass
        
        # Check startup programs
        success, stdout, _ = self.powershell_manager.execute_command(
            "Get-CimInstance -ClassName Win32_StartupCommand | Measure-Object | Select-Object -ExpandProperty Count"
        )
        
        if success:
            try:
                startup_count = int(stdout.strip())
                if startup_count > 10:
                    recommendations.append({
                        'category': 'Performance',
                        'name': 'Startup Programs',
                        'value': f'{startup_count} programs',
                        'recommendation': 'Reduce the number of startup programs to improve boot time'
                    })
            except:
                pass
        
        # Check power plan
        success, stdout, _ = self.powershell_manager.execute_command(
            "powercfg /getactivescheme"
        )
        
        if success:
            if "Power saver" in stdout:
                recommendations.append({
                    'category': 'Power',
                    'name': 'Power Plan',
                    'value': 'Power saver',
                    'recommendation': 'Switch to "Balanced" or "High performance" power plan for better performance'
                })
        
        # Check theme settings
        success, value_data = self.powershell_manager.get_registry_value(
            "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            "AppsUseLightTheme"
        )
        
        if success:
            try:
                light_theme = int(value_data.strip()) == 1
                recommendations.append({
                    'category': 'Display',
                    'name': 'Theme',
                    'value': 'Light theme' if light_theme else 'Dark theme',
                    'recommendation': 'Consider using dark theme to reduce eye strain and save battery on OLED displays' if light_theme else None
                })
            except:
                pass
        
        return {
            'recommendations': recommendations,
            'analyzed_at': '2023-01-01 00:00:00'  # This would be current time in a real app
        }