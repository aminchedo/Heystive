"""
Voice Control Widget for Heystive Desktop
Advanced voice recording and processing interface
"""

import sys
import numpy as np
from pathlib import Path
from typing import Optional, Callable
import tempfile
import wave

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QSlider, QGroupBox, QComboBox, QCheckBox,
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import (
    Qt, Signal, QTimer, QThread, QMutex, QWaitCondition,
    QPropertyAnimation, QEasingCurve, QRect
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QPainter, QColor, QBrush
from PySide6.QtMultimedia import QAudioInput, QAudioFormat, QMediaDevices

try:
    import pyaudio
    import audioop
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio not available. Voice recording may be limited.")

class VoiceControlWidget(QWidget):
    """
    Advanced voice control widget with real-time visualization
    """
    
    # Signals
    voice_recorded = Signal(bytes)
    recording_started = Signal()
    recording_stopped = Signal()
    error_occurred = Signal(str)
    volume_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Audio configuration
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        
        # Recording state
        self.is_recording = False
        self.is_processing = False
        self.audio_data = []
        self.volume_threshold = 30
        self.silence_threshold = 10
        self.silence_timeout = 2000  # ms
        
        # Audio components
        self.audio = None
        self.stream = None
        self.recording_thread = None
        
        # UI components
        self.record_button = None
        self.volume_bar = None
        self.status_label = None
        self.settings_group = None
        
        # Timers
        self.silence_timer = QTimer()
        self.volume_timer = QTimer()
        
        # Animations
        self.button_animation = None
        
        # Initialize
        self.init_ui()
        self.init_audio()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("کنترل صوتی")
        title_label.setFont(QFont("Vazir", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Record button container
        button_container = self.create_record_button()
        layout.addWidget(button_container)
        
        # Status label
        self.status_label = QLabel("آماده برای ضبط")
        self.status_label.setFont(QFont("Vazir", 11))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #718096; margin: 10px 0;")
        layout.addWidget(self.status_label)
        
        # Volume visualization
        volume_group = self.create_volume_visualization()
        layout.addWidget(volume_group)
        
        # Voice settings
        settings_group = self.create_voice_settings()
        layout.addWidget(settings_group)
        
        # Control buttons
        controls_layout = self.create_control_buttons()
        layout.addLayout(controls_layout)
        
        layout.addStretch()
        
    def create_record_button(self):
        """Create main record button with animation"""
        container = QFrame()
        container.setMinimumHeight(200)
        container.setMaximumHeight(200)
        
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        
        # Main record button
        self.record_button = QPushButton()
        self.record_button.setFixedSize(120, 120)
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        
        # Style the button
        self.update_record_button_style()
        
        # Button animation
        self.button_animation = QPropertyAnimation(self.record_button, b"geometry")
        self.button_animation.setDuration(300)
        self.button_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        layout.addWidget(self.record_button, 0, Qt.AlignCenter)
        
        # Shortcut hint
        hint_label = QLabel("فضا یا کلیک برای ضبط")
        hint_label.setFont(QFont("Vazir", 9))
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #A0AEC0; margin-top: 10px;")
        layout.addWidget(hint_label)
        
        return container
        
    def create_volume_visualization(self):
        """Create volume level visualization"""
        group = QGroupBox("سطح صوت")
        group.setFont(QFont("Vazir", 10, QFont.Bold))
        
        layout = QVBoxLayout(group)
        
        # Volume progress bar
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)
        self.volume_bar.setTextVisible(True)
        self.volume_bar.setFormat("%p%")
        
        # Custom styling for volume bar
        self.volume_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                text-align: center;
                font-family: 'Vazir';
                font-size: 10pt;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4CAF50, stop: 0.5 #FF9800, stop: 1 #F44336);
                border-radius: 6px;
                margin: 2px;
            }
        """)
        
        layout.addWidget(self.volume_bar)
        
        # Volume level indicator
        level_layout = QHBoxLayout()
        
        level_layout.addWidget(QLabel("آرام"))
        level_layout.addStretch()
        level_layout.addWidget(QLabel("متوسط"))
        level_layout.addStretch()
        level_layout.addWidget(QLabel("بلند"))
        
        for label in [level_layout.itemAt(i).widget() for i in range(level_layout.count()) if level_layout.itemAt(i).widget()]:
            if isinstance(label, QLabel):
                label.setFont(QFont("Vazir", 8))
                label.setStyleSheet("color: #718096;")
        
        layout.addLayout(level_layout)
        
        return group
        
    def create_voice_settings(self):
        """Create voice settings panel"""
        group = QGroupBox("تنظیمات صوتی")
        group.setFont(QFont("Vazir", 10, QFont.Bold))
        
        layout = QVBoxLayout(group)
        
        # Volume threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("آستانه صدا:"))
        
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(10, 80)
        self.threshold_slider.setValue(self.volume_threshold)
        self.threshold_slider.valueChanged.connect(self.on_threshold_changed)
        
        self.threshold_label = QLabel(f"{self.volume_threshold}")
        self.threshold_label.setMinimumWidth(30)
        self.threshold_label.setAlignment(Qt.AlignCenter)
        
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_label)
        
        layout.addLayout(threshold_layout)
        
        # Silence timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("مهلت سکوت (ثانیه):"))
        
        self.timeout_slider = QSlider(Qt.Horizontal)
        self.timeout_slider.setRange(1, 10)
        self.timeout_slider.setValue(self.silence_timeout // 1000)
        self.timeout_slider.valueChanged.connect(self.on_timeout_changed)
        
        self.timeout_label = QLabel(f"{self.silence_timeout // 1000}")
        self.timeout_label.setMinimumWidth(30)
        self.timeout_label.setAlignment(Qt.AlignCenter)
        
        timeout_layout.addWidget(self.timeout_slider)
        timeout_layout.addWidget(self.timeout_label)
        
        layout.addLayout(timeout_layout)
        
        # Auto-stop checkbox
        self.auto_stop_checkbox = QCheckBox("توقف خودکار پس از سکوت")
        self.auto_stop_checkbox.setChecked(True)
        self.auto_stop_checkbox.setFont(QFont("Vazir", 9))
        layout.addWidget(self.auto_stop_checkbox)
        
        return group
        
    def create_control_buttons(self):
        """Create control buttons layout"""
        layout = QHBoxLayout()
        
        # Test microphone button
        test_button = QPushButton("🎤 تست میکروفن")
        test_button.clicked.connect(self.test_microphone)
        test_button.setFont(QFont("Vazir", 9))
        
        # Settings button
        settings_button = QPushButton("⚙️ تنظیمات")
        settings_button.clicked.connect(self.show_advanced_settings)
        settings_button.setFont(QFont("Vazir", 9))
        
        layout.addWidget(test_button)
        layout.addWidget(settings_button)
        layout.addStretch()
        
        return layout
        
    def init_audio(self):
        """Initialize audio system"""
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio در دسترس نیست")
            return
            
        try:
            self.audio = pyaudio.PyAudio()
            
            # Get default input device
            default_device = self.audio.get_default_input_device_info()
            print(f"🎤 Default input device: {default_device['name']}")
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در راه‌اندازی صوت: {str(e)}")
            
    def connect_signals(self):
        """Connect signals and slots"""
        # Timer connections
        self.silence_timer.setSingleShot(True)
        self.silence_timer.timeout.connect(self.on_silence_timeout)
        
        self.volume_timer.timeout.connect(self.update_volume_display)
        
    def toggle_recording(self):
        """Toggle voice recording"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Start voice recording"""
        if self.is_recording or not PYAUDIO_AVAILABLE:
            return
            
        try:
            self.is_recording = True
            self.audio_data = []
            
            # Update UI
            self.update_recording_ui(True)
            
            # Start recording thread
            self.recording_thread = VoiceRecordingThread(
                self.audio, self.sample_rate, self.channels, 
                self.chunk_size, self.audio_format
            )
            
            self.recording_thread.audio_chunk.connect(self.on_audio_chunk)
            self.recording_thread.error_occurred.connect(self.on_recording_error)
            self.recording_thread.start()
            
            # Start silence timer if auto-stop is enabled
            if self.auto_stop_checkbox.isChecked():
                self.silence_timer.start(self.silence_timeout)
                
            # Start volume monitoring
            self.volume_timer.start(50)  # Update every 50ms
            
            self.recording_started.emit()
            
        except Exception as e:
            self.is_recording = False
            self.error_occurred.emit(f"خطا در شروع ضبط: {str(e)}")
            
    def stop_recording(self):
        """Stop voice recording"""
        if not self.is_recording:
            return
            
        try:
            self.is_recording = False
            
            # Stop timers
            self.silence_timer.stop()
            self.volume_timer.stop()
            
            # Stop recording thread
            if self.recording_thread:
                self.recording_thread.stop()
                self.recording_thread.wait(3000)  # Wait max 3 seconds
                
            # Update UI
            self.update_recording_ui(False)
            
            # Process recorded audio
            if self.audio_data:
                self.process_audio_data()
            
            self.recording_stopped.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در توقف ضبط: {str(e)}")
            
    def process_audio_data(self):
        """Process recorded audio data"""
        if not self.audio_data:
            return
            
        try:
            self.is_processing = True
            self.status_label.setText("در حال پردازش...")
            
            # Combine audio chunks
            audio_bytes = b''.join(self.audio_data)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(self.channels)
                    wav_file.setsampwidth(self.audio.get_sample_size(self.audio_format))
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_bytes)
                
                # Read back as bytes for processing
                temp_file.seek(0)
                processed_audio = temp_file.read()
                
            self.voice_recorded.emit(processed_audio)
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در پردازش صوت: {str(e)}")
        finally:
            self.is_processing = False
            self.status_label.setText("آماده برای ضبط")
            
    def on_audio_chunk(self, chunk_data: bytes):
        """Handle incoming audio chunk"""
        self.audio_data.append(chunk_data)
        
        # Calculate volume level
        try:
            rms = audioop.rms(chunk_data, 2)  # 2 bytes per sample for paInt16
            volume = min(100, rms // 100)  # Scale to 0-100
            
            self.volume_changed.emit(volume)
            
            # Reset silence timer if volume is above threshold
            if volume > self.volume_threshold:
                if self.auto_stop_checkbox.isChecked():
                    self.silence_timer.start(self.silence_timeout)
                    
        except Exception as e:
            print(f"Volume calculation error: {e}")
            
    def on_recording_error(self, error_msg: str):
        """Handle recording thread error"""
        self.is_recording = False
        self.update_recording_ui(False)
        self.error_occurred.emit(error_msg)
        
    def on_silence_timeout(self):
        """Handle silence timeout"""
        if self.is_recording:
            self.stop_recording()
            
    def update_volume_display(self):
        """Update volume level display"""
        # This will be updated by volume_changed signal
        pass
        
    def update_recording_ui(self, recording: bool):
        """Update UI for recording state"""
        if recording:
            self.record_button.setChecked(True)
            self.status_label.setText("در حال ضبط...")
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            self.record_button.setChecked(False)
            self.status_label.setText("آماده برای ضبط")
            self.status_label.setStyleSheet("color: #718096;")
            
        self.update_record_button_style()
        
    def update_record_button_style(self):
        """Update record button styling"""
        if self.is_recording:
            style = """
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #F44336, stop:1 #D32F2F);
                    border: 3px solid #FFCDD2;
                    border-radius: 60px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #E53935, stop:1 #C62828);
                }
            """
            self.record_button.setText("⏹️")
        else:
            style = """
                QPushButton {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #1565C0, stop:1 #0D47A1);
                    border: 3px solid #BBDEFB;
                    border-radius: 60px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #1976D2, stop:1 #1565C0);
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        fx:0.5, fy:0.5, stop:0 #0D47A1, stop:1 #01579B);
                }
            """
            self.record_button.setText("🎤")
            
        self.record_button.setStyleSheet(style)
        
    # Slot methods
    def on_threshold_changed(self, value: int):
        """Handle threshold slider change"""
        self.volume_threshold = value
        self.threshold_label.setText(str(value))
        
    def on_timeout_changed(self, value: int):
        """Handle timeout slider change"""
        self.silence_timeout = value * 1000  # Convert to milliseconds
        self.timeout_label.setText(str(value))
        
    def test_microphone(self):
        """Test microphone functionality"""
        if not PYAUDIO_AVAILABLE:
            self.error_occurred.emit("PyAudio در دسترس نیست")
            return
            
        try:
            # Quick recording test
            test_stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            # Record for 1 second
            test_data = []
            for _ in range(int(self.sample_rate / self.chunk_size)):
                chunk = test_stream.read(self.chunk_size)
                test_data.append(chunk)
                
            test_stream.stop_stream()
            test_stream.close()
            
            # Calculate average volume
            combined_data = b''.join(test_data)
            rms = audioop.rms(combined_data, 2)
            volume = min(100, rms // 100)
            
            if volume > 5:
                self.status_label.setText(f"میکروفن کار می‌کند - سطح صوت: {volume}%")
                self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            else:
                self.status_label.setText("میکروفن شناسایی نشد یا صدایی وجود ندارد")
                self.status_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                
            # Reset status after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText("آماده برای ضبط"))
            QTimer.singleShot(3000, lambda: self.status_label.setStyleSheet("color: #718096;"))
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در تست میکروفن: {str(e)}")
            
    def show_advanced_settings(self):
        """Show advanced settings dialog"""
        # This would open a more detailed settings dialog
        pass
        
    def send_text_command(self, command: str):
        """Send text command (for quick commands)"""
        # Convert text to audio and process
        # This is a placeholder - in real implementation, this would
        # send the command directly to the backend
        self.status_label.setText(f"ارسال دستور: {command}")
        
        # Reset after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_label.setText("آماده برای ضبط"))
        
    def play_audio_response(self, audio_url: str):
        """Play audio response"""
        # This would play the audio response
        # Placeholder implementation
        self.status_label.setText("پخش پاسخ صوتی...")
        QTimer.singleShot(2000, lambda: self.status_label.setText("آماده برای ضبط"))
        
    def play_last_audio(self):
        """Play last audio response"""
        # Placeholder for playing last response
        self.status_label.setText("پخش آخرین پاسخ...")
        QTimer.singleShot(2000, lambda: self.status_label.setText("آماده برای ضبط"))
        
    # Property methods
    def set_volume_threshold(self, threshold: int):
        """Set volume threshold"""
        self.volume_threshold = threshold
        if hasattr(self, 'threshold_slider'):
            self.threshold_slider.setValue(threshold)
            
    def get_volume_threshold(self) -> int:
        """Get current volume threshold"""
        return self.volume_threshold
        
    def set_silence_timeout(self, timeout: int):
        """Set silence timeout in milliseconds"""
        self.silence_timeout = timeout
        if hasattr(self, 'timeout_slider'):
            self.timeout_slider.setValue(timeout // 1000)
            
    def get_silence_timeout(self) -> int:
        """Get current silence timeout"""
        return self.silence_timeout


class VoiceRecordingThread(QThread):
    """
    Background thread for voice recording
    """
    
    audio_chunk = Signal(bytes)
    error_occurred = Signal(str)
    
    def __init__(self, audio, sample_rate, channels, chunk_size, audio_format):
        super().__init__()
        
        self.audio = audio
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_format = audio_format
        
        self.running = False
        self.stream = None
        
    def run(self):
        """Run recording thread"""
        try:
            self.running = True
            
            # Open audio stream
            self.stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            while self.running:
                try:
                    chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    self.audio_chunk.emit(chunk)
                except Exception as e:
                    if self.running:  # Only emit error if we're still supposed to be running
                        self.error_occurred.emit(f"خطا در خواندن صوت: {str(e)}")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"خطا در شروع ضبط: {str(e)}")
        finally:
            self.cleanup()
            
    def stop(self):
        """Stop recording"""
        self.running = False
        
    def cleanup(self):
        """Cleanup audio resources"""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None