from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QDialog, QScrollArea, QWidget
from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtGui import QCursor, QKeySequence
import inspect

class WidgetInspector(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active = False
        self.original_cursor = None
        self.parent_window = parent
        
        # Store original event filters
        self.original_event_filter = parent.eventFilter if hasattr(parent, 'eventFilter') else None
        
        # Create info dialog
        self.info_dialog = QDialog(parent)
        self.info_dialog.setWindowTitle("Widget Inspector")
        self.info_dialog.resize(500, 400)
        
        # Create scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.info_content = QLabel()
        self.info_content.setTextFormat(Qt.RichText)
        self.info_content.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.info_content.setWordWrap(True)
        
        scroll.setWidget(self.info_content)
        
        layout = QVBoxLayout(self.info_dialog)
        layout.addWidget(scroll)
    
    def toggle(self):
        self.active = not self.active
        
        if self.active:
            print("Widget inspector activated - click on any widget to inspect")
            self.original_cursor = QApplication.overrideCursor()
            QApplication.setOverrideCursor(Qt.CrossCursor)
            # Install event filter
            self.parent_window.installEventFilter(self)
        else:
            print("Widget inspector deactivated")
            QApplication.restoreOverrideCursor()
            # Remove event filter
            self.parent_window.removeEventFilter(self)
    
    def eventFilter(self, obj, event):
        if self.active and event.type() == QEvent.MouseButtonPress:
            widget = QApplication.widgetAt(QCursor.pos())
            if widget:
                self.inspect_widget(widget)
                return True
        
        # Call original event filter if it exists
        if self.original_event_filter:
            return self.original_event_filter(obj, event)
        
        return super().eventFilter(obj, event)
    
    def inspect_widget(self, widget):
        # Build widget path
        path = []
        parent = widget
        while parent:
            path.append(f"{parent.__class__.__name__}({parent.objectName() or 'unnamed'})")
            parent = parent.parent()
        
        # Get properties
        properties = []
        for name in dir(widget):
            if name.startswith('_') or name in ('parent', 'children'):
                continue
            
            try:
                attr = getattr(widget, name)
                if callable(attr):
                    continue
                    
                value = str(attr)
                if len(value) > 100:
                    value = value[:100] + "..."
                    
                properties.append(f"<b>{name}</b>: {value}")
            except Exception:
                pass
        
        # Build HTML content
        html = f"""<h2>Widget: {widget.__class__.__name__}</h2>
        <p><b>Object Name:</b> {widget.objectName() or 'unnamed'}</p>
        <p><b>Geometry:</b> {widget.geometry().x()}, {widget.geometry().y()}, {widget.geometry().width()}x{widget.geometry().height()}</p>
        <p><b>Visible:</b> {widget.isVisible()}</p>
        <p><b>Enabled:</b> {widget.isEnabled()}</p>
        <p><b>Widget Path:</b> {' → '.join(reversed(path))}</p>
        <h3>Properties:</h3>
        <p>{'<br>'.join(properties)}</p>
        <h3>Style Sheet:</h3>
        <pre>{widget.styleSheet()}</pre>
        """
        
        self.info_content.setText(html)
        self.info_dialog.show()
        self.info_dialog.raise_()