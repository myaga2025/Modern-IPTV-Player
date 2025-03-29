from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QSlider, QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
import os
import sys
from core.language_manager import tr

# Function to get Python architecture
def get_python_arch():
    return "64bit" if sys.maxsize > 2**32 else "32bit"

class PlayerWidget(QWidget):
    """Video player widget"""
    
    def __init__(self):
        super().__init__()
        
        # Setup UI first
        self._setup_ui()
        
        # Initialize player
        self.vlc_available = False
        self.current_channel_name = ""
        
        try:
            from core.player import Player
            self.player = Player()
            
            # Connect signals
            self._connect_signals()
            
            # Check if VLC is available
            try:
                import vlc
                self.vlc_available = True
            except ImportError:
                self.vlc_available = False
                self._show_vlc_warning(tr("VLC not found - Playback unavailable"))
            except OSError as e:
                self.vlc_available = False
                if "[WinError 193]" in str(e):
                    python_arch = get_python_arch()
                    self._show_vlc_warning(tr(f"Architecture mismatch - Your Python is {python_arch} but VLC is not"))
                else:
                    self._show_vlc_warning(tr(f"VLC error: {str(e)}"))
        except Exception as e:
            self._show_vlc_warning(tr(f"Error initializing player: {str(e)}"))
    
    def _show_vlc_warning(self, message):
        """Show warning if VLC is not available"""
        self.channel_label.setText(message)
        self.channel_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff5555;")
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Channel info bar
        info_layout = QHBoxLayout()
        self.channel_label = QLabel(tr("No channel selected"))
        self.channel_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.channel_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Video display area
        self.video_frame = QFrame()
        self.video_frame.setFrameShape(QFrame.Shape.Box)
        self.video_frame.setStyleSheet("background-color: #1e1e1e;")
        layout.addWidget(self.video_frame, 1)
        
        # Controls area
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 5)
        
        # تحسين استدعاء الأيقونات
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
        
        # Play/pause button
        self.play_button = QPushButton()
        play_icon_path = os.path.join(icons_dir, "play.png")
        if os.path.exists(play_icon_path):
            self.play_button.setIcon(QIcon(play_icon_path))
        else:
            self.play_button.setText("▶")
        self.play_button.setToolTip(tr("Play/Pause"))
        self.play_button.setFixedSize(36, 36)
        controls_layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton()
        stop_icon_path = os.path.join(icons_dir, "stop.png")
        if os.path.exists(stop_icon_path):
            self.stop_button.setIcon(QIcon(stop_icon_path))
        else:
            self.stop_button.setText("■")
        self.stop_button.setToolTip(tr("Stop"))
        self.stop_button.setFixedSize(36, 36)
        controls_layout.addWidget(self.stop_button)
        
        controls_layout.addSpacing(20)
        
        # Current time
        self.time_label = QLabel("00:00:00")
        controls_layout.addWidget(self.time_label)
        
        # Progress bar
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setToolTip(tr("Seek"))
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(1000)
        controls_layout.addWidget(self.progress_slider, 1)
        
        # Duration
        self.duration_label = QLabel("00:00:00")
        controls_layout.addWidget(self.duration_label)
        
        controls_layout.addSpacing(20)
        
        # Volume control
        self.volume_label = QLabel()
        volume_icon_path = os.path.join(icons_dir, "volume.png")
        if os.path.exists(volume_icon_path):
            self.volume_label.setPixmap(QIcon(volume_icon_path).pixmap(20, 20))
        else:
            self.volume_label.setText("🔊")
        controls_layout.addWidget(self.volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setToolTip(tr("Volume"))
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addLayout(controls_layout)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        if not hasattr(self, 'player'):
            return
            
        self.play_button.clicked.connect(self.toggle_play)
        self.stop_button.clicked.connect(self.stop)
        
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.progress_slider.sliderMoved.connect(self.seek)
        
        self.player.time_changed.connect(self.update_time)
        self.player.position_changed.connect(self.update_position)
        self.player.error_occurred.connect(self.on_error)
        
        # Set video frame for player now that player is initialized
        if hasattr(self, 'player'):
            self.player.set_widget(self.video_frame)
    
    def play(self, url, name):
        """Play a channel"""
        if not hasattr(self, 'player') or not self.vlc_available:
            self.on_error(tr("VLC is not available. Please install the correct version of VLC media player."))
            return False
            
        self.current_channel_name = name
        self.channel_label.setText(name)
        self.channel_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        success = self.player.play(url)  # Make sure player.py's play() method accepts the URL parameter
        if success:
            icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
            pause_icon_path = os.path.join(icons_dir, "pause.png")
            if os.path.exists(pause_icon_path):
                self.play_button.setIcon(QIcon(pause_icon_path))
            else:
                self.play_button.setText("⏸️")
        
        return success
    
    def toggle_play(self):
        """Toggle play/pause"""
        if not hasattr(self, 'player') or not self.vlc_available:
            self.on_error(tr("VLC is not available. Please install VLC media player."))
            return
            
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
        play_icon_path = os.path.join(icons_dir, "play.png")
        pause_icon_path = os.path.join(icons_dir, "pause.png")
        
        if self.player.is_playing():
            self.player.pause()
            if os.path.exists(play_icon_path):
                self.play_button.setIcon(QIcon(play_icon_path))
            else:
                self.play_button.setText("▶")
        else:
            self.player.pause()  # In VLC, pause toggles play/pause
            if os.path.exists(pause_icon_path):
                self.play_button.setIcon(QIcon(pause_icon_path))
            else:
                self.play_button.setText("⏸️")
    
    def stop(self):
        """Stop playback"""
        if not hasattr(self, 'player') or not self.vlc_available:
            return
            
        self.player.stop()
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
        play_icon_path = os.path.join(icons_dir, "play.png")
        if os.path.exists(play_icon_path):
            self.play_button.setIcon(QIcon(play_icon_path))
        else:
            self.play_button.setText("▶")
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00:00")
    
    def set_volume(self, volume):
        """Set player volume"""
        if not hasattr(self, 'player') or not self.vlc_available:
            return
        self.player.set_volume(volume)
    
    def seek(self, position):
        """Seek to position"""
        if not hasattr(self, 'player') or not self.vlc_available:
            return
        self.player.set_position(position / 1000.0)
    
    @pyqtSlot(int)
    def update_time(self, time_ms):
        """Update current time display"""
        hours = time_ms // (3600 * 1000)
        minutes = (time_ms % (3600 * 1000)) // (60 * 1000)
        seconds = (time_ms % (60 * 1000)) // 1000
        
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update duration if not set
        if self.duration_label.text() == "00:00:00":
            length = self.player.get_length()
            if length > 0:
                hours = length // (3600 * 1000)
                minutes = (length % (3600 * 1000)) // (60 * 1000)
                seconds = (length % (60 * 1000)) // 1000
                self.duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    @pyqtSlot(float)
    def update_position(self, position):
        """Update position slider"""
        # Only update if not being dragged
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(int(position * 1000))
    
    @pyqtSlot(str)
    def on_error(self, message):
        """Handle player errors"""
        self.channel_label.setText(f"Error: {message}")
        self.channel_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff5555;")
