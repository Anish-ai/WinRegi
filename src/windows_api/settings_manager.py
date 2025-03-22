"""
Windows Settings manager for WinRegi application
Orchestrates PowerShell commands for settings modifications
"""
from typing import Dict, Any, List, Tuple, Optional
from .powershell_manager import PowerShellManager

class SettingsManager:
    """Manages Windows settings operations"""
    
    def __init__(self):
        """Initialize Settings Manager"""
        self.powershell_manager = PowerShellManager()
    
    def apply_setting_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a setting action
        
        Args:
            action: Setting action dictionary
            
        Returns:
            Result dictionary with status and message
        """
        powershell_command = action.get('powershell_command', '')
        
        if not powershell_command:
            print(f"No PowerShell command provided for action: {action.get('name', 'Unknown')}")
            return {
                'success': False,
                'message': 'No PowerShell command provided for this action',
                'requires_admin': False
            }
        
        try:
            print(f"Executing action: {action.get('name', 'Unknown')}")
            print(f"PowerShell command: {powershell_command}")
            
            # Check if PowerShell command needs admin privileges
            if any(cmd in powershell_command.lower() for cmd in ['hklm:', 'restart-service', 'stop-service', 'start-service']):
                if not self.is_admin():
                    print("Admin privileges required but not available")
                    return {
                        'success': False,
                        'message': 'Administrator privileges required for this PowerShell command',
                        'requires_admin': True
                    }
            
            # Execute PowerShell command
            success, stdout, stderr = self.powershell_manager.execute_command(powershell_command)
            
            # Log the result
            print(f"Command execution result: {'Success' if success else 'Failed'}")
            if stdout:
                print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
            
            return {
                'success': success,
                'message': stdout if success else stderr,
                'requires_admin': False
            }
                
        except Exception as e:
            print(f"Error applying setting: {str(e)}")
            import traceback
            traceback.print_exc()
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
            # Get the PowerShell command to check status
            powershell_get_command = setting.get('powershell_get_command')
            
            if not powershell_get_command:
                return {
                    'current_value': None,
                    'exists': None,
                    'message': 'No PowerShell command available to check status'
                }
            
            # Execute the PowerShell command
            success, stdout, stderr = self.powershell_manager.execute_command(powershell_get_command)
            
            if success:
                return {
                    'current_value': stdout.strip(),
                    'exists': True,
                    'message': 'PowerShell command executed successfully'
                }
            else:
                return {
                    'current_value': None,
                    'exists': False,
                    'message': f'PowerShell command failed: {stderr}'
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
    
    def is_admin(self) -> bool:
        """Check if the application is running with administrator privileges
        
        Returns:
            True if running as administrator, False otherwise
        """
        return self.powershell_manager.is_admin()
    
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
        
        # Create PowerShell command to set theme
        theme_value = 1 if theme == 'light' else 0
        powershell_command = f"""
        # Set app theme
        Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "AppsUseLightTheme" -Value {theme_value} -Type DWord
        
        # Set system theme
        Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "SystemUsesLightTheme" -Value {theme_value} -Type DWord
        """
        
        # Execute PowerShell command
        success, stdout, stderr = self.powershell_manager.execute_command(powershell_command)
        
        if not success and "Access is denied" in stderr:
            return {
                'success': False,
                'message': 'Administrator privileges required to set theme',
                'requires_admin': True
            }
        
        return {
            'success': success,
            'message': f'Windows {theme} theme applied successfully' if success else f'Failed to apply {theme} theme: {stderr}',
            'requires_admin': False
        }
    
    def toggle_night_light(self, enable: bool) -> Dict[str, Any]:
        """Toggle Night Light feature
        
        Args:
            enable: True to enable Night Light, False to disable
            
        Returns:
            Dictionary with status and message
        """
        try:
            # The most reliable way is to use the Settings app
            import subprocess
            
            # Open Night Light settings
            subprocess.Popen(["explorer.exe", "ms-settings:nightlight"])
            
            # Inform the user what to do
            return {
                'success': True,
                'message': f"The Night Light settings page has been opened. Please {'enable' if enable else 'disable'} Night Light manually.",
                'requires_manual_action': True
            }
        except Exception as e:
            print(f"Error toggling Night Light: {e}")
            return {
                'success': False,
                'message': f"Failed to toggle Night Light: {str(e)}",
                'requires_admin': False
            }