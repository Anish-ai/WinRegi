from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, Qt
import time
import psutil

class PerformanceMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Performance Monitor")
        self.setWindowFlags(Qt.Window | Qt.Tool)
        self.resize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # CPU usage
        self.cpu_label = QLabel("CPU Usage: 0%")
        self.cpu_bar = QProgressBar()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        
        # Memory usage
        self.mem_label = QLabel("Memory Usage: 0 MB")
        self.mem_bar = QProgressBar()
        layout.addWidget(self.mem_label)
        layout.addWidget(self.mem_bar)
        
        # UI responsiveness
        self.fps_label = QLabel("UI Responsiveness: 0 ms")
        layout.addWidget(self.fps_label)
        
        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second
        
        # For measuring UI responsiveness
        self.last_update_time = time.time()
        
    def update_stats(self):
        # Measure time since last update
        current_time = time.time()
        elapsed = (current_time - self.last_update_time) * 1000  # ms
        self.last_update_time = current_time
        
        # Get process info
        process = psutil.Process()
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        self.cpu_label.setText(f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_bar.setValue(int(cpu_percent))
        
        # Memory usage
        mem_info = process.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)  # Convert to MB
        self.mem_label.setText(f"Memory Usage: {mem_mb:.1f} MB")
        self.mem_bar.setValue(int(mem_mb / 10))  # Scale for progress bar
        
        # UI responsiveness
        self.fps_label.setText(f"UI Update Time: {elapsed:.1f} ms")