from PyQt6.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation, pyqtSignal
from PyQt6.QtWidgets import QWidget, QToolButton, QFrame, QScrollArea, QSizePolicy, QVBoxLayout
from src.main.view.components import CollapsibleContainer
# from src.main.view.components.lineitem import LineItem
from .lineitem import LineItem

class CollapsibleSection(CollapsibleContainer):
    # section_id, old_value, new_value, line_item_id
    sectionValueChanged = pyqtSignal(str, object, object, str)  

    def __init__(self, id, title="", animationDuration=100, parent=None):
        super().__init__(title=title, animationDuration=animationDuration, parent=parent)
        self.id = id
        self.line_items = {}

        # Initialize the content layout
        contentLayout = QVBoxLayout()
        contentLayout.setObjectName("collapsibleSectionLayout")
        contentLayout.setContentsMargins(0, 0, 0, 0)
        contentLayout.setSpacing(0)
        self.setContentLayout(contentLayout)

    def append(self, id, config, useTex=True):
        line_item = LineItem(id, config, useTex, self)
        line_item.valueChanged.connect(self.handle_line_item_value_changed)
        self.contentLayout.addWidget(line_item)
        self.updateAnimations()
        self.line_items[id] = line_item

    def handle_line_item_value_changed(self, old_value, new_value, line_item_id):
        self.sectionValueChanged.emit(self.id, old_value, new_value, line_item_id)

    def getValue(self, id):
        if id in self.line_items:
            return self.line_items[id].getValue()
        else:
            return None

    def setValue(self, id, value):
        if id in self.line_items:
            self.line_items[id].setValue(value)

    def getAllValues(self):
        return {id: item.getValue() for id, item in self.line_items.items()}

    def setAllValues(self, values):
        for id, value in values.items():
            self.setValue(id, value)

    def setClassName(self, object_name, class_name):
        valid_objects = {
            "collapsibleContainer": self,
            "collapsibleToggleButton": self.toggleButton,
            "collapsibleHeaderLine": self.headerLine,
            "collapsibleContentArea": self.contentArea,
            "collapsibleContentWidget": self.contentWidget,
        }

        if object_name in valid_objects:
            valid_objects[object_name].setProperty("class", class_name)
            valid_objects[object_name].style().unpolish(valid_objects[object_name])
            valid_objects[object_name].style().polish(valid_objects[object_name])
        elif object_name == "LineItem":
            for _, item in self.line_items.items():
                item.setClass(class_name)
        else:
            raise ValueError(f"{object_name} is not a valid object name.")