from PyQt6.QtCore import Qt, QParallelAnimationGroup, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtWidgets import QWidget, QToolButton, QFrame, QScrollArea, QSizePolicy, QVBoxLayout

class CollapsibleContainer(QWidget):
    def __init__(self, title="", animationDuration=100, parent=None):
        super().__init__(parent)
        self.animationDuration = animationDuration
        
        self.setObjectName("collapsibleContainer")
        self.toggleButton = QToolButton(self)
        self.toggleButton.setObjectName("collapsibleToggleButton")
        self.headerLine = QFrame(self)
        self.headerLine.setObjectName("collapsibleHeaderLine")
        self.toggleAnimation = QParallelAnimationGroup(self)
        self.contentArea = QScrollArea(self)
        self.contentArea.setObjectName("collapsibleContentArea")
        self.contentWidget = QWidget()
        self.contentWidget.setObjectName("collapsibleContentWidget")
        self.mainLayout = QVBoxLayout(self)

        self.toggleButton.setStyleSheet("#collapsibleToggleButton {border: none;}")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)  # Start closed

        self.headerLine.setFrameShape(QFrame.Shape.HLine)
        self.headerLine.setFrameShadow(QFrame.Shadow.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.contentArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contentArea.setWidgetResizable(True)
        self.contentArea.setWidget(self.contentWidget)

        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.mainLayout.addWidget(self.toggleButton)
        self.mainLayout.addWidget(self.headerLine)
        self.mainLayout.addWidget(self.contentArea)
        self.setLayout(self.mainLayout)

        self.toggleButton.toggled.connect(self.toggle)
        self.contentLayout = None
        
        # Start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

    def setContentLayout(self, layout):
        if self.contentLayout is None:
            self.contentLayout = layout
            self.contentWidget.setLayout(self.contentLayout)
            self.updateAnimations()

    def updateAnimations(self):
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = self.contentLayout.sizeHint().height() + 20
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
            self.updateAnimations()  # Ensure animations are updated before expanding
            self.contentArea.setMaximumHeight(self.contentLayout.sizeHint().height())
        else:
            self.toggleButton.setArrowType(Qt.ArrowType.RightArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Direction.Backward)
            self.contentArea.setMaximumHeight(0)
        self.toggleAnimation.start()
    
    def addWidget(self, widget):
        if self.contentLayout is None:
            return
        self.contentLayout.addWidget(widget)
        self.updateAnimations()

    def clear(self):
        if self.contentLayout is None:
            return
        while self.contentLayout.count():
            child = self.contentLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.updateAnimations()

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
        else:
            raise ValueError(f"{object_name} is not a valid object name.")
