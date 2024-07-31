import os
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import QStandardPaths
from appdirs import AppDirs

class BaseApp:
    # Initialize AppDirs with your application name and author
    app_dirs = AppDirs("PhototransductSim", "DrG")

    @staticmethod
    def getResource(*args):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', *args)

    @staticmethod
    def getData(file_name):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', file_name)

    @staticmethod
    def save_file(id="Save File", filters="All Files (*.*)", root=None):
        if root is None or root == "/":
            root = BaseApp.app_dirs.user_documents_dir
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        file_dialog.setNameFilters([filters])
        file_name, _ = file_dialog.getSaveFileName(None, id, root, filters)
        return file_name

    @staticmethod
    def load_file(id="Load File", filters="All Files (*.*)", default_dir=None):
        if default_dir is None or default_dir == "/":
            default_dir = BaseApp.app_dirs.user_documents_dir
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        file_name, _ = file_dialog.getOpenFileName(None, id, default_dir, filters)
        return file_name

    @staticmethod
    def get_directory(id="Select Directory", default_dir=None):
        if default_dir is None or default_dir == "/":
            default_dir = BaseApp.app_dirs.user_documents_dir
        file_dialog = QFileDialog()
        file_dialog.setWindowTitle(id)
        directory = file_dialog.getExistingDirectory(None, id, default_dir)
        return directory
