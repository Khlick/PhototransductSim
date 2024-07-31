import unittest
from PyQt6.QtWidgets import QApplication
import sys

from src.main.view.components.collapsiblesection import CollapsibleSection

class TestCollapsibleSection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.section = CollapsibleSection(id="section1", title="Test Section", animationDuration=100)
        self.section.show()

    def tearDown(self):
        self.section.close()

    def test_append_and_get_value(self):
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

        self.section.append(id1, config1)
        self.section.append(id2, config2)

        # Test getting values
        self.assertEqual(self.section.getValue(id1), 1.0)
        self.assertEqual(self.section.getValue(id2), "Option 1")

    def test_set_value(self):
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

        self.section.append(id1, config1)
        self.section.append(id2, config2)

        # Test setting values
        self.section.setValue(id1, 2.0)
        self.assertEqual(self.section.getValue(id1), 2.0)

        self.section.setValue(id2, "Option 3")
        self.assertEqual(self.section.getValue(id2), "Option 3")

    def test_invalid_id(self):
        with self.assertRaises(ValueError):
            self.section.getValue("invalid_id")

        with self.assertRaises(ValueError):
            self.section.setValue("invalid_id", "value")


if __name__ == '__main__':
    unittest.main()

