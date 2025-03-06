"""
Commands page for WinRegi application
Allows managing and executing custom commands
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFrame,
    QDialog, QLineEdit, QTextEdit, QComboBox, QFormLayout,
    QMessageBox, QSplitter, QSizePolicy, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

from ..database.db_manager import DatabaseManager
from ..windows_api.command_manager import CommandManager

class CommandDialog(QDialog):
    """Dialog for adding or editing commands"""
    
    def __init__(self, command_manager, command_id=None, parent=None):
        """Initialize command dialog
        
        Args:
            command_manager: Command manager instance
            command_id: ID of command to edit (None for new command)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.command_manager = command_manager
        self.command_id = command_id
        self.db_manager = self.command_manager.db_manager
        
        self.setWindowTitle("Add Command" if not command_id else "Edit Command")
        self.resize(600, 400)
        
        # Create form layout
        form_layout = QFormLayout(self)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        
        # Name field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter command name")
        form_layout.addRow("Name:", self.name_input)
        
        # Description field
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter command description")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        # Command type field
        self.type_combo = QComboBox()
        for cmd_type, cmd_type_name in self.command_manager.get_command_types().items():
            self.type_combo.addItem(cmd_type_name, cmd_type)
        form_layout.addRow("Command Type:", self.type_combo)
        
        # Command value field
        self.value_input = QTextEdit()
        self.value_input.setPlaceholderText("Enter command value")
        form_layout.addRow("Command:", self.value_input)
        
        # Add help text based on selected command type
        self.help_label = QLabel()
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("font-size: 12px; color: gray;")
        form_layout.addRow("", self.help_label)
        
        # Connect type combo to update help text
        self.type_combo.currentIndexChanged.connect(self.update_help_text)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_command)
        buttons_layout.addWidget(self.save_button)
        
        form_layout.addRow("", buttons_layout)
        
        # If editing an existing command, load its data
        if self.command_id:
            self.load_command()
        
        # Update help text for initial command type
        self.update_help_text()
    
    def load_command(self):
        """Load command data for editing"""
        command = self.db_manager.get_command_by_id(self.command_id)
        if command:
            self.name_input.setText(command["name"])
            self.description_input.setText(command["description"])
            
            # Set command type
            cmd_type = command["command_type"]
            index = -1
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == cmd_type:
                    index = i
                    break
            
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            self.value_input.setText(command["command_value"])
    
    def update_help_text(self):
        """Update help text based on selected command type"""
        cmd_type = self.type_combo.currentData()
        
        if cmd_type == "system":
            self.help_label.setText(
                "Enter the path to the program or system command to execute.\n"
                "Example: notepad.exe, calc.exe, explorer.exe"
            )
        elif cmd_type == "powershell":
            self.help_label.setText(
                "Enter a PowerShell command to execute.\n"
                "Example: Get-Process | Where-Object {$_.CPU -gt 10} | Sort-Object CPU -Descending"
            )
        elif cmd_type == "batch":
            self.help_label.setText(
                "Enter batch commands to execute.\n"
                "Example:\n@echo off\ndir\npause"
            )
        elif cmd_type == "registry":
            self.help_label.setText(
                "Enter a registry command in the format 'path=value' or 'path-' (for deletion).\n"
                "Examples:\nHKCU\\Software\\MyApp\\Setting=value\nHKCU\\Software\\MyApp\\Setting-"
            )
    
    def save_command(self):
        """Save the command data"""
        # Get values from form
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        cmd_type = self.type_combo.currentData()
        cmd_value = self.value_input.toPlainText().strip()
        
        # Validate input
        if not name:
            QMessageBox.warning(self, "Validation Error", "Command name is required")
            return
        
        if not cmd_value:
            QMessageBox.warning(self, "Validation Error", "Command value is required")
            return
        
        # Validate command
        valid, error_msg = self.command_manager.validate_command(cmd_type, cmd_value)
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Save to database
        try:
            if self.command_id:
                # Update existing command
                success = self.db_manager.update_command(
                    self.command_id, name, description, cmd_type, cmd_value
                )
                if success:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update command")
            else:
                # Add new command
                new_id = self.db_manager.add_command(
                    name, description, cmd_type, cmd_value
                )
                if new_id:
                    self.command_id = new_id
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add command")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving command: {str(e)}")


class CommandItem(QWidget):
    """Custom widget for displaying a command in the list"""
    
    def __init__(self, command, parent=None):
        """Initialize command item
        
        Args:
            command: Command dictionary
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.command = command
        self.command_id = command["id"]
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Top row with name and command type
        top_row = QHBoxLayout()
        
        # Command name
        self.name_label = QLabel(command["name"])
        self.name_label.setObjectName("command-name")
        font = QFont()
        font.setBold(True)
        self.name_label.setFont(font)
        top_row.addWidget(self.name_label)
        
        # Spacer
        top_row.addStretch()
        
        # Command type badge
        cmd_type_map = {
            "system": "System",
            "powershell": "PowerShell",
            "batch": "Batch",
            "registry": "Registry"
        }
        cmd_type = cmd_type_map.get(command["command_type"], command["command_type"])
        type_badge = QLabel(cmd_type)
        type_badge.setObjectName("command-type-badge")
        type_badge.setStyleSheet("background-color: #e3f2fd; color: #1565c0; padding: 3px 6px; border-radius: 10px;")
        top_row.addWidget(type_badge)
        
        layout.addLayout(top_row)
        
        # Description
        if command["description"]:
            description = QLabel(command["description"])
            description.setObjectName("command-description")
            description.setWordWrap(True)
            layout.addWidget(description)
        
        # Command value
        value_label = QLabel(command["command_value"])
        value_label.setObjectName("command-value")
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(value_label)
        
        # Set object name for styling
        self.setObjectName("command-list-item")


class CommandsPage(QWidget):
    """Commands page with custom commands management"""
    
    def __init__(self, db_manager=None, parent=None):
        """Initialize commands page
        
        Args:
            db_manager: Database manager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store managers
        self.db_manager = db_manager or DatabaseManager()
        self.command_manager = CommandManager(self.db_manager)
        
        # Set up UI
        self.init_ui()
        
        # Load commands
        self.load_commands()
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Create header
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Custom Commands")
        title.setObjectName("commands-title")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Spacer
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("Add Command")
        self.add_button.setObjectName("add-command-button")
        self.add_button.setFixedSize(150, 36)
        self.add_button.clicked.connect(self.add_command)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Create description
        description = QLabel("Create and manage custom commands to run Windows applications, PowerShell scripts, batch files, or registry edits.")
        description.setWordWrap(True)
        description.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Create separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #dddddd; margin: 10px 0;")
        layout.addWidget(separator)
        
        # Create commands list
        self.commands_list = QListWidget()
        self.commands_list.setObjectName("command-list")
        self.commands_list.setStyleSheet("QListWidget::item { border-bottom: 1px solid #eeeeee; }")
        self.commands_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.commands_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.commands_list)
        
        # Create empty state message
        self.empty_label = QLabel("No commands found. Add a command to get started.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #999999; margin: 20px 0;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)
    
    def load_commands(self):
        """Load commands from database"""
        # Clear current commands
        self.commands_list.clear()
        
        # Get commands from database
        commands = self.db_manager.get_all_commands()
        
        if not commands:
            self.empty_label.setVisible(True)
            return
        
        self.empty_label.setVisible(False)
        
        # Add commands to list
        for command in commands:
            item = QListWidgetItem(self.commands_list)
            command_widget = CommandItem(command)
            item.setSizeHint(command_widget.sizeHint())
            item.setData(Qt.UserRole, command["id"])
            self.commands_list.setItemWidget(item, command_widget)
    
    def add_command(self):
        """Add a new command"""
        dialog = CommandDialog(self.command_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_commands()
    
    def edit_command(self, command_id):
        """Edit an existing command
        
        Args:
            command_id: ID of the command to edit
        """
        dialog = CommandDialog(self.command_manager, command_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_commands()
    
    def delete_command(self, command_id):
        """Delete a command
        
        Args:
            command_id: ID of the command to delete
        """
        # Get command details
        command = self.db_manager.get_command_by_id(command_id)
        if not command:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the command '{command['name']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete command
            success = self.db_manager.delete_command(command_id)
            
            if success:
                self.load_commands()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete command")
    
    def execute_command(self, command_id):
        """Execute a command
        
        Args:
            command_id: ID of the command to execute
        """
        # Get command details
        command = self.db_manager.get_command_by_id(command_id)
        if not command:
            return
        
        # Execute command
        success, output = self.command_manager.execute_command(command_id)
        
        # Show result based on command type
        if command["command_type"] in ["powershell", "batch"]:
            # These command types can produce output that's useful to show
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Command Execution Result")
            
            if success:
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText(f"Command '{command['name']}' executed successfully.")
                if output:
                    msg_box.setDetailedText(output)
            else:
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText(f"Command '{command['name']}' failed to execute.")
                msg_box.setDetailedText(output)
            
            msg_box.exec_()
        else:
            # Other command types may not produce useful output
            if not success:
                QMessageBox.warning(
                    self,
                    "Command Failed",
                    f"Command '{command['name']}' failed to execute:\n{output}"
                )
    
    def show_context_menu(self, position):
        """Show context menu for a command item
        
        Args:
            position: Position where the context menu should be shown
        """
        # Get the list item at the position
        item = self.commands_list.itemAt(position)
        if not item:
            return
        
        # Get command ID
        command_id = item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu(self)
        
        # Add actions
        execute_action = QAction("Execute", self)
        execute_action.triggered.connect(lambda: self.execute_command(command_id))
        menu.addAction(execute_action)
        
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.edit_command(command_id))
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_command(command_id))
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(self.commands_list.mapToGlobal(position))