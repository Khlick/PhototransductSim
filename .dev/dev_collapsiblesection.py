import os
import sys
# Ensure the src directory is in the Python path
# Adjust this as it was expected to be in src/main/test
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from src.main.view.components import CollapsibleSection

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Collapsible Section Example")
        self.setGeometry(100, 100, 800, 600)

        section = CollapsibleSection(id="section1", title="Section", animationDuration=100, parent=self)

        # Add labels and input fields in 2 columns
        id1 = 'betadark'
        config1 = {
            'name': r"$\beta_{\text{dark}}$",
            'type': "numericInput",
            'default': 1.0,
            'display': ".5g",
            'tip': "Beta dark parameter"
        }

        id2 = 'gammadark'
        config2 = {
            'name': r"$\gamma_{\text{dark}}$",
            'type': "dropdown",
            'default': "Option 1",
            'options': ["Option 1", "Option 2", "Option 3"],
            'tip': "Gamma dark parameter"
        }

        section.append(id1, config1)
        section.append(id2, config2)

        # Connect the section's valueChanged signal to the callback
        section.sectionValueChanged.connect(self.handle_section_value_changed)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(section)
        main_layout.addStretch(1)

    def handle_section_value_changed(self, section_id, old_value, new_value, line_item_id):
        print(f"Section ID: {section_id}, Line Item ID: {line_item_id}, Old Value: {old_value}, New Value: {new_value}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())