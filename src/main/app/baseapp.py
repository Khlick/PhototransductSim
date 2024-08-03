import os
import sys
from PyQt6.QtWidgets import QFileDialog
from appdirs import AppDirs

from .version import __version__

class BaseApp:
    # Initialize AppDirs with your application name and author
    app_dirs = AppDirs("PhototransductSim", "DrG", version=__version__)

    @staticmethod
    def get_user_documents_dir(*pathArgs):
        """Get the user's documents directory in an OS-independent way."""
        home_dir = os.path.expanduser("~")
        if pathArgs:
            home_dir = os.path.join(home_dir, *pathArgs)
        return home_dir
            
        
    @staticmethod
    def source_path(*args):
        """ This is for app-install directory locations """
        try:
            # For PyInstaller
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath("./src")

        return os.path.join(base_path, *args)

    @staticmethod
    def getResource(*args):
        return BaseApp.source_path('resources', *args)

    @staticmethod
    def getData(file_name):
        return BaseApp.source_path('data', file_name)

    @staticmethod
    def getUserData(*pathArgs):
        user_data_dir = BaseApp.app_dirs.user_data_dir
        return os.path.join(user_data_dir, *pathArgs)

    @staticmethod
    def setUserData(file_name, *pathArgs):
        full_path = BaseApp.getUserData(*pathArgs)
        os.makedirs(full_path, exist_ok=True)
        return os.path.join(full_path, file_name)
    
    @staticmethod
    def save_file(id="Save File", filters="All Files (*.*)", root=None):
        if root is None or root == "/":
            root = BaseApp.get_user_documents_dir()
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        file_dialog.setNameFilters([filters])
        file_name, _ = file_dialog.getSaveFileName(None, id, root, filters)
        return file_name

    @staticmethod
    def load_file(id="Load File", filters="All Files (*.*)", default_dir=None):
        if default_dir is None or default_dir == "/":
            root = BaseApp.get_user_documents_dir()
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        file_name, _ = file_dialog.getOpenFileName(None, id, default_dir, filters)
        return file_name

    @staticmethod
    def get_directory(id="Select Directory", default_dir=None):
        if default_dir is None or default_dir == "/":
            root = BaseApp.get_user_documents_dir()
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        directory = file_dialog.getExistingDirectory(None, id, default_dir)
        return directory
