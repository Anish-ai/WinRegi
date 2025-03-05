"""
Category list widget for WinRegi application
"""
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QLabel, 
    QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

class CategoryItem(QFrame):
    """Category item for category list"""
    
    def __init__(self, category_id, name, description=None, icon=None, parent=None):
        """Initialize category item
        
        Args:
            category_id: Category ID
            name: Category name
            description: Category description (optional)
            icon: Category icon (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store category data
        self.category_id = category_id
        self.category_name = name
        self.category_description = description
        self.category_icon = icon
        
        # Set up UI
        self.init_ui()
        
        # Set frame properties
        self.setFrameShape(QFrame.NoFrame)
        self.setProperty("class", "category-item")
    
    def init_ui(self):
        """Initialize user interface"""
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add icon if available
        if self.category_icon:
            # Create icon label
            icon_label = QLabel()
            icon_label.setFixedSize(24, 24)
            
            # Set icon
            if isinstance(self.category_icon, str):
                # Icon is a path or name
                pixmap = QPixmap(self.category_icon)
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    # Use default icon or text
                    icon_label.setText(self.category_name[0])
                    icon_label.setAlignment(Qt.AlignCenter)
                    icon_label.setStyleSheet("background-color: #2979ff; color: white; border-radius: 12px;")
            else:
                # Icon is a QIcon or QPixmap
                if isinstance(self.category_icon, QIcon):
                    pixmap = self.category_icon.pixmap(24, 24)
                    icon_label.setPixmap(pixmap)
                elif isinstance(self.category_icon, QPixmap):
                    icon_label.setPixmap(self.category_icon.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            layout.addWidget(icon_label)
        
        # Create text area
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        # Category name
        name_label = QLabel(self.category_name)
        name_label.setObjectName("category-name")
        name_label.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(name_label)
        
        # Category description
        if self.category_description:
            description_label = QLabel(self.category_description)
            description_label.setObjectName("category-description")
            description_label.setStyleSheet("color: #777; font-size: 11px;")
            text_layout.addWidget(description_label)
        
        # Add text layout to main layout
        layout.addLayout(text_layout, 1)

class CategoryList(QListWidget):
    """List widget displaying setting categories"""
    
    # Signal emitted when a category is selected
    category_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize category list widget
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        # Set list properties
        self.setFrameShape(QFrame.NoFrame)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
    
    def add_category(self, category_id, name, description=None, icon=None):
        """Add a category to the list
        
        Args:
            category_id: Category ID
            name: Category name
            description: Category description (optional)
            icon: Category icon (optional)
            
        Returns:
            Created list item
        """
        # Create list item
        item = QListWidgetItem(self)
        
        # Create category widget
        category_widget = CategoryItem(category_id, name, description, icon)
        
        # Set item properties
        item.setSizeHint(category_widget.sizeHint())
        item.setData(Qt.UserRole, category_id)
        
        # Add item to list
        self.addItem(item)
        self.setItemWidget(item, category_widget)
        
        return item
    
    def clear_categories(self):
        """Clear all categories from the list"""
        self.clear()
    
    def on_item_clicked(self, item):
        """Handle item click
        
        Args:
            item: Clicked list item
        """
        # Get category ID
        category_id = item.data(Qt.UserRole)
        
        # Emit signal
        self.category_selected.emit(category_id)