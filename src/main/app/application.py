import sys
import os

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from PyQt6.QtWidgets import QApplication
from src.main.model import Phototransduction
from src.main.view.ui import MainView
from src.main.controller import Controller

class PhototransductSimApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.model = Phototransduction()
        self.view = MainView()
        self.controller = Controller(self.model, self.view)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = PhototransductSimApp()
    app.run()
