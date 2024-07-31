from PyQt6.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation, pyqtSignal
from PyQt6.QtWidgets import QWidget, QToolButton, QFrame, QScrollArea, QSizePolicy, QVBoxLayout

from src.main.view.components.lineitem import LineItem

class CollapsibleSection(QWidget):
    # section_id, old_value, new_value, line_item_id
    sectionValueChanged = pyqtSignal(str, object, object, str)  

    def __init__(self, id, title="", animationDuration=100, parent=None):
        super().__init__(parent)
        self.id = id
        self.animationDuration = animationDuration
        self.toggleButton = QToolButton(self)
        self.headerLine = QFrame(self)
        self.headerLine.setObjectName("collapsibleSection")
        self.toggleAnimation = QParallelAnimationGroup(self)
        self.contentArea = QScrollArea(self)
        self.contentWidget = QWidget()  
        self.mainLayout = QVBoxLayout(self)

        self.toggleButton.setStyleSheet("QToolButton {border: none;}")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)  # Start closed

        self.headerLine.setFrameShape(QFrame.Shape.HLine)
        self.headerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.contentArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contentArea.setWidgetResizable(True)  # Ensure it resizes with content
        self.contentArea.setWidget(self.contentWidget)  # Set the content widget

        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addWidget(self.headerLine, row + 1)
        self.mainLayout.addWidget(self.contentArea, row + 2)
        self.setLayout(self.mainLayout)

        self.toggleButton.toggled.connect(self.toggle)
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        
        # Start out expanded
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        
        # Storage for line items
        self.line_items = {}

    def setContentLayout(self):        
        self.contentWidget.setLayout(self.contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = self.contentLayout.sizeHint().height() + 5
        for i in range(self.toggleAnimation.animationCount() - 1):
            sectionAnimation = self.toggleAnimation.animationAt(i)
            sectionAnimation.setDuration(self.animationDuration)
            sectionAnimation.setStartValue(collapsedHeight)
            sectionAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)

    def toggle(self, expanded):
        if expanded:
            self.toggleButton.setArrowType(Qt.ArrowType.DownArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Direction.Forward)
            self.contentArea.setMaximumHeight(self.contentLayout.sizeHint().height())
        else:
            self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Direction.Backward)
            self.contentArea.setMaximumHeight(0)
        self.toggleAnimation.start()

    def append(self, id, config):
        line_item = LineItem(id, config, self)
        line_item.valueChanged.connect(self.handle_line_item_value_changed)
        self.contentLayout.addWidget(line_item)
        self.line_items[id] = line_item
        self.setContentLayout()

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

    def setAllValues(self,values):
        for id,value in values.items():
            self.setValue(id,value)