"""
Voice Visualizer Component for Heystive Desktop
Simple audio level visualization widget
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
import random

class VoiceVisualizer(QWidget):
    """
    Simple voice level visualizer
    """
    
    # Signals
    level_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # State
        self.current_level = 0.0
        self.is_listening = False
        
        # Initialize UI
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("سطح صدا")
        title_label.setFont(QFont("Vazir", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Level display
        self.level_label = QLabel("0%")
        self.level_label.setFont(QFont("Vazir", 12, QFont.Bold))
        self.level_label.setAlignment(Qt.AlignCenter)
        self.level_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self.level_label)
        
        # Progress bar
        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setMaximumHeight(20)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                text-align: center;
                font-family: 'Vazir';
                font-size: 9pt;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 9px;
            }
        """)
        layout.addWidget(self.level_bar)
        
        # Status
        self.status_label = QLabel("آماده")
        self.status_label.setFont(QFont("Vazir", 9))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)
        
    def setup_timer(self):
        """Setup update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_level)
        self.update_timer.setInterval(100)  # Update every 100ms
        
    def start_listening(self):
        """Start voice level monitoring"""
        self.is_listening = True
        self.status_label.setText("در حال گوش دادن...")
        self.status_label.setStyleSheet("color: #FF9800;")
        self.update_timer.start()
        
    def stop_listening(self):
        """Stop voice level monitoring"""
        self.is_listening = False
        self.status_label.setText("متوقف شد")
        self.status_label.setStyleSheet("color: #666666;")
        self.update_timer.stop()
        self.set_level(0)
        
    def set_level(self, level: float):
        """Set voice level (0.0 to 1.0)"""
        self.current_level = max(0.0, min(1.0, level))
        percentage = int(self.current_level * 100)
        
        self.level_bar.setValue(percentage)
        self.level_label.setText(f"{percentage}%")
        
        # Update color based on level
        if percentage > 80:
            color = "#F44336"  # Red
        elif percentage > 50:
            color = "#FF9800"  # Orange
        else:
            color = "#4CAF50"  # Green
            
        self.level_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                text-align: center;
                font-family: 'Vazir';
                font-size: 9pt;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 9px;
            }}
        """)
        
        self.level_label.setStyleSheet(f"color: {color};")
        self.level_changed.emit(self.current_level)
        
    def update_level(self):
        """Update voice level (simulated for demo)"""
        if self.is_listening:
            # Simulate voice level changes
            base_level = random.uniform(0.1, 0.3)
            noise = random.uniform(-0.1, 0.1)
            new_level = max(0.0, min(1.0, base_level + noise))
            self.set_level(new_level)
            
    def reset(self):
        """Reset visualizer to initial state"""
        self.set_level(0)
        self.status_label.setText("آماده")
        self.status_label.setStyleSheet("color: #666666;")