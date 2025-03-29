import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QPushButton, QLineEdit, QComboBox,
                           QLabel, QToolBar, QMenu, QMenuBar, QStatusBar,
                           QMessageBox, QFileDialog)
from PyQt6.QtGui import QIcon, QAction, QActionGroup
from PyQt6.QtCore import Qt, QSize, QTranslator, QEvent

from ui.player_widget import PlayerWidget
from ui.playlist_widget import PlaylistWidget
from ui.dialogs import AddPlaylistDialog, AboutDialog, URLInputDialog
from core.m3u_parser import M3UParser
from core.playlist import PlaylistManager
from core.language_manager import LanguageManager, tr
from core.url_history import PlaylistURLManager  # إضافة استيراد مدير سجل الروابط

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.m3u_parser = M3UParser()
        self.playlist_manager = PlaylistManager()
        self.language_manager = LanguageManager()
        self.url_manager = PlaylistURLManager()  # إنشاء مدير سجل الروابط
        
        # تعيين أيقونة النافذة
        app_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "resources", "icons", "app_icon.png")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        # Setup UI
        self.setWindowTitle(tr("Modern IPTV Player"))
        self.setMinimumSize(1200, 800)
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QHBoxLayout(self.central_widget)
        
        # Create left panel (playlists and channels)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Search channels..."))
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Tabs for different playlists
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Main playlists tab
        self.all_channels_widget = PlaylistWidget()
        self.tabs.addTab(self.all_channels_widget, tr("All Channels"))
        
        # Add playlists from playlist manager
        for name, playlist in self.playlist_manager.playlists.items():
            playlist_widget = PlaylistWidget()
            playlist_widget.set_channels(playlist.channels)
            self.tabs.addTab(playlist_widget, name)
        
        # Add tab for adding new playlists
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFlat(True)
        self.add_tab_button.setMaximumWidth(30)
        self.tabs.setCornerWidget(self.add_tab_button)
        
        left_layout.addWidget(self.tabs)
        
        # Filter UI
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(tr("Category:")))
        self.category_combo = QComboBox()
        self.category_combo.addItem(tr("All"))
        filter_layout.addWidget(self.category_combo)
        left_layout.addLayout(filter_layout)
        
        main_layout.addWidget(left_panel, 1)
        
        # Create right panel (player)
        self.player_widget = PlayerWidget()
        main_layout.addWidget(self.player_widget, 2)
        
        # Setup menu bar
        self._setup_menu_bar()
        
        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(tr("Ready"))
    
    def _setup_menu_bar(self):
        """Setup menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu(tr("&File"))
        
        open_action = QAction(tr("&Open Playlist..."), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_playlist)
        file_menu.addAction(open_action)
        
        open_url_action = QAction(tr("Open Playlist from &URL..."), self)
        open_url_action.triggered.connect(self.open_playlist_url)
        file_menu.addAction(open_url_action)
        
        # إضافة خيار Xtream (Soon)
        xtream_action = QAction(tr("Xtream (Soon)"), self)
        xtream_action.setEnabled(False)  # تعطيل هذا الخيار لأنه قادم قريباً
        file_menu.addAction(xtream_action)
        
        # Add Playlist Management menu
        manage_playlists_action = QAction(tr("&Manage Playlists..."), self)
        manage_playlists_action.triggered.connect(self.show_playlist_manager)
        file_menu.addAction(manage_playlists_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(tr("E&xit"), self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Playback menu
        playback_menu = menu_bar.addMenu(tr("&Playback"))
        
        play_action = QAction(tr("&Play/Pause"), self)
        play_action.setShortcut("Space")
        play_action.triggered.connect(self.player_widget.toggle_play)
        playback_menu.addAction(play_action)
        
        stop_action = QAction(tr("&Stop"), self)
        stop_action.triggered.connect(self.player_widget.stop)
        playback_menu.addAction(stop_action)
        
        # Settings menu
        settings_menu = menu_bar.addMenu(tr("&Settings"))
        
        # إضافة خيار لإدارة شعار التطبيق
        logo_action = QAction(tr("App Logo"), self)
        logo_action.triggered.connect(self.manage_app_logo)
        settings_menu.addAction(logo_action)
        
        # إضافة خيار لإدارة الإعدادات
        manage_settings_action = QAction(tr("Manage Settings"), self)
        manage_settings_action.triggered.connect(self.manage_settings)
        settings_menu.addAction(manage_settings_action)
        
        # Language submenu
        language_menu = settings_menu.addMenu(tr("Language"))
        
        # Create action group for languages to make them exclusive
        lang_action_group = QActionGroup(self)
        lang_action_group.setExclusive(True)
        
        # Add language options
        english_action = QAction(tr("English"), self)
        english_action.setCheckable(True)
        english_action.setChecked(self.language_manager.current_language == "en")
        english_action.triggered.connect(lambda: self.change_language("en"))
        lang_action_group.addAction(english_action)
        language_menu.addAction(english_action)
        
        arabic_action = QAction(tr("العربية"), self)
        arabic_action.setCheckable(True)
        arabic_action.setChecked(self.language_manager.current_language == "ar")
        arabic_action.triggered.connect(lambda: self.change_language("ar"))
        lang_action_group.addAction(arabic_action)
        language_menu.addAction(arabic_action)
        
        # Help menu
        help_menu = menu_bar.addMenu(tr("&Help"))
        
        # إضافة عناصر القائمة مباشرة إلى قائمة المساعدة
        about_app_action = QAction(tr("About App"), self)
        about_app_action.triggered.connect(self.show_about_app)
        help_menu.addAction(about_app_action)
        
        about_developer_action = QAction(tr("About Developer"), self)
        about_developer_action.triggered.connect(self.show_about_developer)
        help_menu.addAction(about_developer_action)
        
        check_updates_action = QAction(tr("Check for Updates"), self)
        check_updates_action.triggered.connect(self.check_updates)
        help_menu.addAction(check_updates_action)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        self.add_tab_button.clicked.connect(self.add_new_playlist)
        self.search_input.textChanged.connect(self.search_channels)
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        self.all_channels_widget.channel_selected.connect(self.play_channel)
    
    def change_language(self, language):
        """Change application language"""
        self.language_manager.change_language(language)
        
        # Show a message to inform the user
        QMessageBox.information(
            self, 
            tr("Language Changed"),
            tr("The language has been changed. Please restart the application for the changes to take effect."),
            QMessageBox.StandardButton.Ok
        )
    
    def open_playlist(self):
        """Open M3U playlist from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("Open Playlist"), "", tr("M3U Playlists (*.m3u *.m3u8);;JSON Playlists (*.json);;All Files (*)")
        )
        
        if file_path:
            self.statusBar.showMessage(tr("Loading playlist: {file_path}...").format(file_path=file_path))
            try:
                success = self.m3u_parser.load_from_file(file_path)
                
                if success:
                    self._update_after_playlist_load()
                else:
                    QMessageBox.critical(self, tr("Error"), tr("Failed to load playlist: {file_path}").format(file_path=file_path))
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    tr("Error"), 
                    tr("Error loading playlist {file_path}: {error}").format(file_path=file_path, error=str(e))
                )
                print(f"Detailed error loading playlist: {e}")
    
    def open_playlist_url(self):
        """Open M3U playlist from URL"""
        dialog = URLInputDialog(self.url_manager.get_urls(), tr("Open Playlist URL"), tr("Enter playlist URL:"), self)
        if dialog.exec():
            url = dialog.get_input()
            if url:
                # إضافة الرابط إلى السجل
                self.url_manager.add_url(url)
                
                self.statusBar.showMessage(tr("Loading playlist from URL..."))
                try:
                    success = self.m3u_parser.load_from_url(url)
                    
                    if success:
                        self._update_after_playlist_load()
                    else:
                        QMessageBox.critical(self, tr("Error"), tr("Failed to load playlist from URL"))
                except Exception as e:
                    QMessageBox.critical(
                        self, 
                        tr("Error"), 
                        tr("Error loading playlist from URL: {error}").format(error=str(e))
                    )
                    print(f"Detailed error loading URL playlist: {e}")
    
    def _update_after_playlist_load(self):
        """Update UI after loading a playlist"""
        # Update channels list
        self.all_channels_widget.set_channels(self.m3u_parser.channels)
        
        # Update categories filter
        self.category_combo.clear()
        self.category_combo.addItem(tr("All"))
        for group in sorted(self.m3u_parser.groups):
            self.category_combo.addItem(group)
        
        self.statusBar.showMessage(tr("Loaded {count} channels").format(count=len(self.m3u_parser.channels)))
    
    def search_channels(self, query):
        """Search channels by name"""
        self.all_channels_widget.search(query)
    
    def filter_by_category(self, category):
        """Filter channels by category/group"""
        if category == tr("All"):
            self.all_channels_widget.set_channels(self.m3u_parser.channels)
        else:
            filtered = self.m3u_parser.get_channels_by_group(category)
            self.all_channels_widget.set_channels(filtered)
    
    def add_new_playlist(self):
        """Add new custom playlist"""
        dialog = AddPlaylistDialog()
        if dialog.exec():
            name = dialog.get_playlist_name()
            if name:
                playlist = self.playlist_manager.create_playlist(name)
                
                # Add new tab for playlist
                playlist_widget = PlaylistWidget()
                new_tab_index = self.tabs.addTab(playlist_widget, name)
                self.tabs.setCurrentIndex(new_tab_index)
    
    def play_channel(self, channel):
        """Play selected channel"""
        if channel:
            self.statusBar.showMessage(tr("Playing: {channel_name}").format(channel_name=channel.name))
            self.player_widget.play(channel.url, channel.name)
    
    def show_about_app(self):
        """Show information about the app"""
        content = ""
        if self.language_manager.current_language == "ar":
            content = "Modern IPTV Player v1.0\n\n" \
                      "مشغل IPTV حديث ومتطور يدعم قوائم تشغيل M3U وبواجهة رسومية جذابة.\n\n" \
                      "الميزات:\n" \
                      "- دعم قوائم تشغيل M3U المحلية وعبر الإنترنت\n" \
                      "- البحث والتصنيف بالمجموعات\n" \
                      "- إنشاء وإدارة قوائم تشغيل مخصصة\n" \
                      "- واجهة مستخدم عصرية وسهلة الاستخدام\n\n" \
                      "© 2023-2024 جميع الحقوق محفوظة."
        else:
            content = "Modern IPTV Player v1.0\n\n" \
                      "A modern IPTV player supporting M3U playlists with an elegant graphical interface.\n\n" \
                      "Features:\n" \
                      "- Support for local and remote M3U playlists\n" \
                      "- Search and categorization by groups\n" \
                      "- Create and manage custom playlists\n" \
                      "- Modern and user-friendly interface\n\n" \
                      "© 2023-2024 All Rights Reserved."
                      
        dialog = AboutDialog(
            title=tr("About App"),
            content=content
        )
        dialog.exec()
    
    def show_about_developer(self):
        """Show information about the developer"""
        content = ""
        if self.language_manager.current_language == "ar":
            content = "تم تطوير هذا البرنامج بواسطة:\n\n" \
                      " تطوير Mu Dev \n\n" \
                      "للتواصل والدعم الفني:\n" \
                      "البريد الإلكتروني: admin@aljup.com\n" \
                      "الموقع الإلكتروني: www.aljup.com\n\n" \
                      "نرحب بملاحظاتكم واقتراحاتكم لتطوير البرنامج!"
        else:
            content = "This program was developed by:\n\n" \
                      "IPTV Player Development Team\n\n" \
                      "Contact and support information:\n" \
                      "Email: admin@aljup.com\n" \
                      "Website: www.aljup.com\n" \
                      "We welcome your feedback and suggestions!"
                      
        dialog = AboutDialog(
            title=tr("About Developer"),
            content=content
        )
        dialog.exec()
    
    def check_updates(self):
        """Check for application updates"""
        message = tr("You are using the latest version (1.0).\nNo updates are currently available.") if self.language_manager.current_language == "en" else "أنت تستخدم أحدث إصدار من البرنامج (1.0).\nلا توجد تحديثات متوفرة حاليًا."
        
        QMessageBox.information(
            self,
            tr("Updates"),
            message
        )
    
    def show_about(self):
        """Show about dialog - for backwards compatibility"""
        self.show_about_app()
    
    def show_playlist_manager(self):
        """Show the playlist manager dialog"""
        from ui.dialogs import PlaylistManagerDialog
        dialog = PlaylistManagerDialog(self.playlist_manager, self)
        if dialog.exec():
            # Refresh tabs if changes made
            self._refresh_playlist_tabs()
    
    def _refresh_playlist_tabs(self):
        """Refresh playlist tabs"""
        # Get current tab index
        current_index = self.tabs.currentIndex()
        
        # Delete all tabs except the first one (All Channels)
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        
        # Re-add all playlists
        for name, playlist in self.playlist_manager.playlists.items():
            playlist_widget = PlaylistWidget()
            playlist_widget.set_channels(playlist.channels)
            playlist_widget.channel_selected.connect(self.play_channel)
            self.tabs.addTab(playlist_widget, name)
        
        # Try to restore the selected tab
        if current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)
    
    def manage_app_logo(self):
        """فتح نافذة إدارة شعار التطبيق"""
        try:
            # استدعاء مدير الشعار
            from logo_manager import LogoManagerWindow
            self.logo_manager = LogoManagerWindow()
            self.logo_manager.show()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح مدير الشعار: {str(e)}")

    def manage_settings(self):
        """فتح نافذة إدارة الإعدادات"""
        try:
            # استدعاء مدير الإعدادات
            from settings_manager import SettingsManager
            self.settings_manager = SettingsManager()
            self.settings_manager.show()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح مدير الإعدادات: {str(e)}")
