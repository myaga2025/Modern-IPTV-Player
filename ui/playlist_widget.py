from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QAction

from core.language_manager import tr

class PlaylistWidget(QWidget):
    """Widget for displaying and managing channel playlist"""
    
    # Signals
    channel_selected = pyqtSignal(object)  # Emitted when a channel is selected for playback
    
    def __init__(self):
        super().__init__()
        
        self.channels = []
        self.current_displayed = []
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Channel list widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.list_widget)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_channels(self, channels):
        """Set or update channel list"""
        self.channels = channels
        self.current_displayed = channels
        self._update_list()
    
    def search(self, query):
        """Filter channels by search query"""
        if not query:
            self.current_displayed = self.channels
        else:
            query = query.lower()
            self.current_displayed = [ch for ch in self.channels if query in ch.name.lower()]
        
        self._update_list()
    
    def _update_list(self):
        """Update the list widget with current channels"""
        self.list_widget.clear()
        
        for channel in self.current_displayed:
            item = QListWidgetItem(channel.name)
            
            # Set tooltip with more details
            tooltip = f"Group: {channel.group or 'Unknown'}"
            if channel.quality:
                tooltip += f"\nQuality: {channel.quality}"
            item.setToolTip(tooltip)
            
            # Store the channel object in the item
            item.setData(Qt.ItemDataRole.UserRole, channel)
            
            # Add icon if available
            if channel.logo:
                item.setIcon(QIcon(channel.logo))
            
            self.list_widget.addItem(item)
    
    def _on_item_double_clicked(self, item):
        """Handle double click on channel item"""
        channel = item.data(Qt.ItemDataRole.UserRole)
        if channel:
            self.channel_selected.emit(channel)
    
    def _show_context_menu(self, position):
        """Show context menu for channel item"""
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        channel = item.data(Qt.ItemDataRole.UserRole)
        if not channel:
            return
        
        menu = QMenu()
        
        # Add actions
        play_action = QAction(tr("Play"), self)
        play_action.triggered.connect(lambda: self.channel_selected.emit(channel))
        menu.addAction(play_action)
        
        # Add "Add to Playlist" submenu
        from ui.dialogs import AddToPlaylistDialog
        
        add_to_playlist_menu = QMenu(tr("Add to Playlist"), self)
        
        # Get playlist manager from main window
        main_window = self.window()
        if hasattr(main_window, 'playlist_manager'):
            playlist_manager = main_window.playlist_manager
            
            # Add entry for each playlist
            for name in playlist_manager.playlists:
                playlist_action = QAction(name, self)
                playlist_action.triggered.connect(lambda checked, pname=name: self._add_to_playlist(channel, pname))
                add_to_playlist_menu.addAction(playlist_action)
            
            # Add separator and "New Playlist..." option
            if playlist_manager.playlists:
                add_to_playlist_menu.addSeparator()
            
            new_playlist_action = QAction(tr("New Playlist..."), self)
            new_playlist_action.triggered.connect(lambda: self._add_to_new_playlist(channel))
            add_to_playlist_menu.addAction(new_playlist_action)
            
            menu.addMenu(add_to_playlist_menu)
        
        # Display the menu
        menu.exec(self.list_widget.mapToGlobal(position))

    def _add_to_playlist(self, channel, playlist_name):
        """Add a channel to an existing playlist"""
        main_window = self.window()
        if hasattr(main_window, 'playlist_manager'):
            playlist_manager = main_window.playlist_manager
            if playlist_manager.add_channel_to_playlist(playlist_name, channel):
                # Show success message in status bar if available
                if hasattr(main_window, 'statusBar'):
                    main_window.statusBar.showMessage(
                        tr("Added '{channel}' to playlist '{playlist}'").format(
                            channel=channel.name, 
                            playlist=playlist_name
                        ), 
                        3000
                    )

    def _add_to_new_playlist(self, channel):
        """Create a new playlist and add the channel to it"""
        main_window = self.window()
        if hasattr(main_window, 'playlist_manager'):
            from ui.dialogs import AddPlaylistDialog
            
            dialog = AddPlaylistDialog()
            if dialog.exec():
                playlist_name = dialog.get_playlist_name()
                if playlist_name:
                    playlist_manager = main_window.playlist_manager
                    playlist = playlist_manager.create_playlist(playlist_name)
                    
                    if playlist_manager.add_channel_to_playlist(playlist_name, channel):
                        # Show success message in status bar if available
                        if hasattr(main_window, 'statusBar'):
                            main_window.statusBar.showMessage(
                                tr("Created new playlist '{playlist}' with channel '{channel}'").format(
                                    channel=channel.name, 
                                    playlist=playlist_name
                                ), 
                                3000
                            )
                        
                        # Refresh playlist tabs
                        if hasattr(main_window, '_refresh_playlist_tabs'):
                            main_window._refresh_playlist_tabs()
