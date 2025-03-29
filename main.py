#!/usr/bin/env python3
import sys
import os
import platform
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon

def get_python_arch():
    """Returns the Python architecture (32bit or 64bit)"""
    return "64bit" if sys.maxsize > 2**32 else "32bit"

def setup_vlc_path():
    """Setup VLC library path based on platform"""
    system = platform.system()
    python_arch = get_python_arch()
    
    print(f"Python architecture: {python_arch}")
    
    if system == "Windows":
        # Check if we have a saved VLC path from previous runs
        if os.path.exists("vlc_path.txt"):
            with open("vlc_path.txt", "r") as f:
                custom_path = f.read().strip()
                if custom_path and os.path.exists(custom_path):
                    print(f"استخدام مسار VLC من ملف التكوين: {custom_path}")
                    
                    # Validate that the architecture matches
                    libvlc_path = os.path.join(custom_path, 'libvlc.dll')
                    if os.path.exists(libvlc_path):
                        try:
                            # Try to load the DLL directly to make sure it works with this Python
                            ctypes.CDLL(libvlc_path)
                            print(f"تم تحميل libvlc.dll بنجاح من المسار المخصص")
                            
                            # Add VLC directory to PATH and Python path
                            if custom_path not in sys.path:
                                sys.path.append(custom_path)
                            
                            os.environ['PATH'] = custom_path + os.pathsep + os.environ.get('PATH', '')
                            
                            # Remove problematic environment variables
                            if 'PYTHON_VLC_MODULE_PATH' in os.environ:
                                del os.environ['PYTHON_VLC_MODULE_PATH']
                            if 'PYTHON_VLC_LIB_PATH' in os.environ:
                                del os.environ['PYTHON_VLC_LIB_PATH']
                                
                            return custom_path
                        except Exception as e:
                            print(f"خطأ في تحميل libvlc.dll من المسار المخصص: {e}")
                            # Continue to try other paths if custom path fails
        
        # Define VLC paths based on Python architecture
        vlc_paths = []
        
        # Always try the architecture that matches Python first
        if python_arch == "64bit":
            vlc_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
                # Fallback to 32-bit as last resort
                r"C:\Program Files (x86)\VideoLAN\VLC",
            ]
        else:  # 32-bit Python
            vlc_paths = [
                r"C:\Program Files (x86)\VideoLAN\VLC",
                # Fallback to 64-bit as last resort (but unlikely to work)
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
            ]
        
        for path in vlc_paths:
            if os.path.exists(path):
                print(f"تم العثور على VLC في: {path}")
                
                # Try to load the DLL directly
                libvlc_path = os.path.join(path, 'libvlc.dll')
                if os.path.exists(libvlc_path):
                    try:
                        # Try to load the DLL directly to make sure it works
                        ctypes.CDLL(libvlc_path)
                        print("تم تحميل libvlc.dll بنجاح")
                        
                        # Add VLC directory to PATH and Python path
                        if path not in sys.path:
                            sys.path.append(path)
                        
                        os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                        
                        # Remove problematic environment variables
                        if 'PYTHON_VLC_MODULE_PATH' in os.environ:
                            del os.environ['PYTHON_VLC_MODULE_PATH']
                        if 'PYTHON_VLC_LIB_PATH' in os.environ:
                            del os.environ['PYTHON_VLC_LIB_PATH']
                            
                        # Save this as our preferred path for future runs
                        with open("vlc_path.txt", "w") as f:
                            f.write(path)
                            
                        return path
                    except Exception as e:
                        print(f"خطأ في تحميل libvlc.dll: {e}")
        
        print("تحذير: لم يتم العثور على تثبيت VLC متوافق.")
        return None
    
    elif system == "Darwin":  # macOS
        vlc_paths = [
            '/Applications/VLC.app/Contents/MacOS/',
            '/Applications/VLC.app/Contents/MacOS/lib',
        ]
        
        for path in vlc_paths:
            if os.path.exists(path):
                print(f"Found VLC at: {path}")
                if path not in sys.path:
                    sys.path.append(path)
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                os.environ['DYLD_LIBRARY_PATH'] = path + os.pathsep + os.environ.get('DYLD_LIBRARY_PATH', '')
                return path
        
        print("Warning: Could not find VLC installation path.")
        return None
    
    # Linux doesn't need path setup as libraries should be in system paths
    return None

def check_vlc():
    """Check if VLC is available on the system"""
    # First try to set up the path
    vlc_path = setup_vlc_path()
    
    # Remove problematic environment variables
    if 'PYTHON_VLC_MODULE_PATH' in os.environ:
        del os.environ['PYTHON_VLC_MODULE_PATH']
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        del os.environ['PYTHON_VLC_LIB_PATH']
    
    try:
        # Try to import the VLC module
        import vlc
        return True, vlc_path
    except (ImportError, OSError, FileNotFoundError) as e:
        print(f"Error importing VLC: {e}")
        return False, vlc_path

def find_vlc_install():
    """Try to find VLC installation"""
    system = platform.system()
    python_arch = get_python_arch()
    paths = []
    
    if system == "Windows":
        if python_arch == "64bit":
            paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
            ]
        else:
            paths = [
                r"C:\Program Files (x86)\VideoLAN\VLC",
            ]
    elif system == "Darwin":  # macOS
        paths = ['/Applications/VLC.app/Contents/MacOS/']
    else:  # Linux
        # VLC is typically in the PATH on Linux if installed
        return "Please install VLC using your package manager."
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    # Suggest download link if not found
    return f"https://www.videolan.org/vlc/ (Please download the {'64-bit' if python_arch == '64bit' else '32-bit'} version)"

def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    
    # تعيين أيقونة التطبيق إذا كانت متاحة
    app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "resources", "icons", "app_icon.png")
    
    if os.path.exists(app_icon_path):
        app_icon = QIcon(app_icon_path)
        app.setWindowIcon(app_icon)
        # تعيين الأيقونة للاستخدام في شريط المهام في ويندوز
        if platform.system() == "Windows":
            import ctypes
            myappid = 'mycompany.iptvplayer.v1.0'  # أي معرف فريد
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Set application style
    try:
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "resources", "styles", "dark_theme.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                app.setStyleSheet(f.read())
        else:
            print(f"Style file not found: {style_path}")
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
    
    # Check for VLC
    vlc_available, vlc_path = check_vlc()
    if not vlc_available:
        python_arch = get_python_arch()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("VLC Not Found")
        msg.setText("VLC media player appears to be missing or not properly configured.")
        
        # Add detailed instructions
        details = ("The application will start, but video playback will not be available.\n\n"
                  "To fix this issue:\n"
                  f"1. Make sure VLC media player ({python_arch}) is installed\n"
                  f"2. Your Python is {python_arch}, so you need the {python_arch} version of VLC\n"
                  "3. If VLC is already installed, it might be the wrong architecture\n\n")
        if vlc_path:
            details += f"VLC was found at: {vlc_path} but there may be architecture mismatch issues."
        else:
            vlc_path = find_vlc_install()
            if "http" in vlc_path:
                details += f"Download VLC from: {vlc_path}"
            else:
                details += f"VLC should be installed at: {vlc_path}"
        
        msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    # Import MainWindow here to avoid potential import errors with VLC
    from ui.main_window import MainWindow
    
    # Create main window
    window = MainWindow()
    
    # عرض الملاحظة إذا كان التطبيق يُفتح لأول مرة - قبل إظهار النافذة الرئيسية
    try:
        from core.first_run_notice import NoticeManager
        notice_manager = NoticeManager()
        notice_manager.show_notice_if_needed(window)
    except Exception as e:
        print(f"خطأ في عرض الملاحظة: {e}")
    
    # Show the main window
    window.showMaximized()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
