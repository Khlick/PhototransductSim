from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QHBoxLayout, QSizePolicy, QCheckBox, QPushButton, QFileDialog
)
from PyQt6.QtGui import QDoubleValidator, QPixmap
from matplotlib import pyplot as plt
import io
import numpy as np

from src.main.utils import safe_eval, num_to_str

class LineItem(QWidget):
    valueChanged = pyqtSignal(object, object, str)  # old_value, new_value, id
    LineItemError = pyqtSignal(str)
    def __init__(self, id, config, useTex=True, parent=None):
        super().__init__(parent)
        self.id = id
        self.isTex = useTex
        self.old_value = None
        self.setObjectName("LineItem")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 3, 0)
        layout.setSpacing(0)
        self.label = QLabel()
        if useTex:
            self.set_latex_label(config['name'])
        else:
            self.label.setText(str(config['name']))
        if 'tip' in config:
            self.label.setToolTip(config['tip'])
        layout.addWidget(self.label)

        self.input_type = config['type']
        self.default_value = config.get('default', None)
        self.display_format = config.get('display', '')
        self.input_options = config.get('options', [])

        if self.input_type in ["numericInput", "numericArray"]:
            self.input = QLineEdit()
            if self.input_type.endswith("Input"):
                self.input.setValidator(QDoubleValidator())
            self.input.editingFinished.connect(self.emit_value_changed)
        elif self.input_type == "dropdown":
            self.input = QComboBox()
            self.input.addItems(self.input_options)
            self.input.currentTextChanged.connect(self.emit_value_changed)
        elif self.input_type == "checkbox":
            self.input = QCheckBox()
            self.input.setChecked(self.default_value)
            self.input.stateChanged.connect(self.emit_value_changed)
            layout.addStretch()
        elif self.input_type == "folderInput":
            self.input = QWidget()
            folder_layout = QHBoxLayout(self.input)
            folder_layout.setContentsMargins(5, 0, 0, 0)
            folder_layout.setSpacing(5)
            self.folder_edit = QLineEdit()
            self.folder_edit.setText(self.default_value)
            self.folder_edit.setReadOnly(True)
            self.folder_button = QPushButton("...")
            self.folder_button.setFixedWidth(30)
            self.folder_button.clicked.connect(self.open_folder_dialog)
            folder_layout.addWidget(self.folder_edit)
            folder_layout.addWidget(self.folder_button)
        else:
            self.LineItemError.emit(f"Warning: Unsupported input type '{self.input_type}' for LineItem with id '{id}'")
            return  # Skip unsupported types

        self.setValue(self.default_value)
        self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.input)
        self.setLayout(layout)
        self.setPreviousValue(self.default_value)

    def setPreviousValue(self, value):
        if self.input_type in ["numericInput", "numericArray"]:
            if isinstance(value, str):
                value = safe_eval(value)
            self.old_value = value
        elif self.input_type == "dropdown":
            if value in [self.input.itemText(i) for i in range(self.input.count())]:
                self.old_value = value

    @pyqtSlot()
    def emit_value_changed(self):
        old_value = self.old_value
        new_value = self.getValue()

        if self.input_type == "numericInput":
            old_value = float(old_value) if old_value else 0.0
            new_value = float(new_value) if new_value else 0.0
        elif self.input_type == "numericArray":
            if isinstance(old_value, str):
                old_value = safe_eval(old_value)
            if isinstance(new_value, str):
                new_value = safe_eval(new_value)

        # Check for changes and emit signal if necessary
        if self.input_type in ["numericInput", "numericArray"]:
            # cast to 1d numpy array and compare equality
            check_old = np.atleast_1d(old_value)
            check_new = np.atleast_1d(new_value)
            if not np.array_equal(check_old, check_new):
                self.old_value = new_value
                self.setValue(new_value)
                self.valueChanged.emit(old_value, new_value, self.id)
        elif old_value != new_value:
            self.old_value = new_value
            self.valueChanged.emit(old_value, new_value, self.id)

    @pyqtSlot()
    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory", self.folder_edit.text())
        if folder_path:
            old_value = self.old_value
            new_value = folder_path
            self.folder_edit.setText(new_value)
            self.old_value = new_value
            self.valueChanged.emit(old_value, new_value, self.id)

    def set_latex_label(self, latex_text):
        plt.figure(figsize=(0.01, 0.01))
        plt.text(0.5, 0.5, latex_text, horizontalalignment='center', verticalalignment='center', fontsize=9)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.05, transparent=True)
        plt.close()
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue(), "PNG")
        self.label.setPixmap(pixmap)

    def getValue(self):
        if self.input_type in ["numericInput", "numericArray"]:
            return safe_eval(self.input.text())
        elif self.input_type == "dropdown":
            return self.input.currentText()
        elif self.input_type == "checkbox":
            return self.input.isChecked()
        elif self.input_type == "folderInput":
            return self.folder_edit.text()

    def setValue(self, value):
        if self.input_type in ["numericInput", "numericArray"]:
            self.input.setText(
                num_to_str(value, self.display_format)
            )
        elif self.input_type == "dropdown":
            if value in [self.input.itemText(i) for i in range(self.input.count())]:
                self.input.setCurrentText(value)
            else:
                self.LineItemError.emit(f"Warning: '{value}' is not a valid option for the dropdown with id '{self.id}'")
                self.input.setCurrentText(self.input.itemText(0))
        elif self.input_type == "checkbox":
            self.input.setChecked(bool(value))
        elif self.input_type == "folderInput":
            self.folder_edit.setText(str(value))

    def setClass(self, class_name):
        self.setProperty("class", class_name)
        self.input.setProperty("class", class_name)
        self.label.setProperty("class", class_name)
        if self.input_type == "folderInput":
            self.folder_edit.setProperty("class", class_name)
            self.folder_button.setProperty("class", class_name)
        self.style().unpolish(self)
        self.style().polish(self)