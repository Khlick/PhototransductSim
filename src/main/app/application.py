import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QElapsedTimer

from src.main.model.phototransduction import Phototransduction
from src.main.view.ui import MainView
from src.main.controller.controller import Controller
from src.main.app.splash import PhototransducSimSplash
from src.main.app.version import __version__, __author__, __year__

class PhototransductSimApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        splash_text = f"PhototransductSim v{__version__}"
        splash__by = f"{__author__} ({__year__})"
        self.splash = PhototransducSimSplash("psim_image.png", splash_text, splash__by)
        self.splash.show()
        self.splash_timer = QElapsedTimer()
        self.splash_timer.start()
        
        self.model = Phototransduction()
        self.view = MainView()
        self.controller = Controller(self.model, self.view)

    def run(self):
        while self.splash_timer.elapsed() < 3000:
            pass
        self.splash.close()
        self.view.show()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = PhototransductSimApp()
    app.run()
