from PyQt5.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import sys
import traceback

class ConsoleRedirector(QObject):
    text_written = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
    
    def write(self, text):
        self.original_stdout.write(text)
        self.text_written.emit(text)
    
    def flush(self):
        self.original_stdout.flush()

class DebugConsole(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Debug Console", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        # Create console widget
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            "background-color: #1e1e1e; color: #dcdcdc; font-family: Consolas, monospace;"
        )
        
        # Create control buttons
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.console.clear)
        
        control_layout.addWidget(clear_button)
        control_layout.addStretch()
        
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.console)
        layout.addWidget(control_widget)
        
        self.setWidget(main_widget)
        
        # Set up stdout/stderr redirection
        self.redirector = ConsoleRedirector()
        self.redirector.text_written.connect(self.append_text)
        
    def append_text(self, text):
        self.console.append(text.rstrip('\n'))
        # Auto-scroll to bottom
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )
    
    def install_redirector(self):
        sys.stdout = self.redirector
        sys.stderr = self.redirector
    
    def remove_redirector(self):
        sys.stdout = self.redirector.original_stdout
        sys.stderr = self.redirector.original_stderr