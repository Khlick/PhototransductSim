# src/main/app/splash.py

import yaml
from PyQt6.QtCore import Qt, QTimer, QElapsedTimer
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QFontDatabase

from .baseapp import BaseApp

class PhototransducSimSplash(QWidget, BaseApp):
    def __init__(self, image_name, label, byline="", timeout=5000):
        super().__init__()

        with open(self.getData('aes.yaml'), 'r') as file:
            aes =  yaml.safe_load(file)
        
        playfair_font_path = self.getResource('fonts', aes.get('defaultFont'))
        playwrite_font_path = self.getResource('fonts', aes.get('titleFont'))

        # Load the fonts
        playfair_font_id = QFontDatabase.addApplicationFont(playfair_font_path)
        playfair_font_family = QFontDatabase.applicationFontFamilies(playfair_font_id)[0]

        playwrite_font_id = QFontDatabase.addApplicationFont(playwrite_font_path)
        playwrite_font_family = QFontDatabase.applicationFontFamilies(playwrite_font_id)[0]

        image_path = self.getResource("img", image_name)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Image
        self.image_label = QLabel()
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Text container with black background
        text_container = QWidget()
        text_container.setStyleSheet("background-color: black; border-radius: 10px;")
        text_container_layout = QVBoxLayout()
        text_container.setLayout(text_container_layout)
        text_container_layout.setContentsMargins(20, 10, 20, 10)
        text_container_layout.setSpacing(5)

        # label
        self.text_label = QLabel(label)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(f"color: white; font-size: 16px; font-family: {playwrite_font_family};")
        text_container_layout.addWidget(self.text_label)

        # byline
        self.text_byline = QLabel(byline)
        self.text_byline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_byline.setStyleSheet(f"color: white; font-size: 16px; font-family: {playfair_font_family};")
        text_container_layout.addWidget(self.text_byline)

        layout.addWidget(text_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.timer = QTimer(self)
        self.timer.setInterval(timeout)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start()

    def update_text(self, text):
        self.text_byline.setText(text)

