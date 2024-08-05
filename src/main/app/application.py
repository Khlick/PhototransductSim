import sys
import threading

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QElapsedTimer, QTimer

from src.main.app.splash import PhototransducSimSplash
from src.main.app.version import __version__, __author__, __year__

class PhototransductSimApp:
    MIN_SPLASH_DELAY = 3000
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        splash_text = f"PhototransductSim v{__version__}"
        splash_by = f"{__author__} ({__year__})"
        self.splash = PhototransducSimSplash("psim_image.png", splash_text, splash_by)
        self.splash.show()
        
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        
        self.initialization_done = False

        # Start the initialization in the main thread
        QTimer.singleShot(0, self.initializeApp)

        # Check the initialization status periodically
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.checkInit)
        self.check_timer.start(100)

    def initializeApp(self):
        from src.main.model.phototransduction import Phototransduction
        from src.main.view.ui import MainView
        from src.main.controller.controller import Controller

        self.model = Phototransduction()
        self.view = MainView()
        self.controller = Controller(self.model, self.view)
        
        self.initialization_done = True

    def checkInit(self):
        if self.initialization_done and self.elapsed_timer.elapsed() >= self.MIN_SPLASH_DELAY:
            self.check_timer.stop()
            self.splash.close()
            self.view.show()
    
    def run(self):
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = PhototransductSimApp()
    app.run()
