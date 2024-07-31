from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.main.app.baseapp import BaseApp
from src.main.view.components import CollapsibleContainer
from .axestoolbar import AxesToolbar

class Axes(QWidget,BaseApp):
    axes_changed = pyqtSignal(dict)
    data_exported = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.previous_selection = {"x": None, "y": None}
        self.max_legend_width = 10
        self.legend_items = []
        self.setupUi()
        self.bindUi()

    def bindUi(self):
        self.x_axis_dropdown.currentTextChanged.connect(
            lambda: self.on_axis_changed("x")
        )
        self.y_axis_dropdown.currentTextChanged.connect(
            lambda: self.on_axis_changed("y")
        )
        self.toolbar.dataExported.connect(self.handle_data_exported)
        
    def setupUi(self):
        self.setObjectName("plot_page")
        plot_layout = QVBoxLayout(self)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar = AxesToolbar(self.canvas,self)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")

        # Add the toolbar and canvas to a container
        plot_container = QVBoxLayout()
        plot_container.addWidget(self.toolbar)
        plot_container.addWidget(self.canvas)
        plot_container.setStretch(0, 0)
        plot_container.setStretch(1, 1)  # Make the canvas stretchable

        # Create the axis selection layout
        axis_layout = QHBoxLayout()
        axis_layout.setSpacing(5)
        axis_layout.setContentsMargins(10, 0, 10, 0)
        
        # Y-Axis selection
        y_label = QLabel("Y-Axis:")
        self.y_axis_dropdown = QComboBox()
        self.y_axis_dropdown.addItem("Option 1")
        self.y_axis_dropdown.addItem("Option 2")
        y_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.y_axis_dropdown.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        
        # X-Axis selection
        x_label = QLabel("X-Axis:")
        self.x_axis_dropdown = QComboBox()
        self.x_axis_dropdown.addItem("Option 1")
        self.x_axis_dropdown.addItem("Option 2")
        x_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.x_axis_dropdown.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        
        # Add contents to layout
        # Y-Axis
        axis_layout.addWidget(y_label)
        axis_layout.addWidget(self.y_axis_dropdown)
        # Expanding space
        axis_layout.addStretch()
        # X-Axis
        axis_layout.addWidget(x_label)
        axis_layout.addWidget(self.x_axis_dropdown)

        # Create the collapsible legend container
        self.legend_container = CollapsibleContainer(title="Legend")
        # legend_layout = QHBoxLayout()  # Set as horizontal layout
        legend_layout = QGridLayout()
        legend_layout.setContentsMargins(2, 3, 2, 3)  # Add some padding
        legend_layout.setSpacing(2)
        self.legend_container.setContentLayout(legend_layout)
        legendObjs = [
            "collapsibleContainer", "collapsibleToggleButton", "collapsibleHeaderLine", "collapsibleContentArea", "collapsibleContentWidget"
            ]
        for obj in legendObjs:
            self.legend_container.setClassName(obj,"legend")
        
        # Add everything to the main layout
        plot_layout.addLayout(plot_container)
        plot_layout.addLayout(axis_layout)
        plot_layout.addWidget(self.legend_container)

        # Set stretch factors to ensure proper resizing
        plot_layout.setStretch(0, 1)  # Make the plot container stretchable
        plot_layout.setStretch(1, 0)  # Fixed height for axis selection
        plot_layout.setStretch(2, 0)  # Fixed height for legend

    def update_axes_options(self, opts, xSelection, ySelection):
        self.x_axis_dropdown.blockSignals(True)
        self.y_axis_dropdown.blockSignals(True)

        self.x_axis_dropdown.clear()
        self.y_axis_dropdown.clear()

        self.x_axis_dropdown.addItems(opts)
        self.y_axis_dropdown.addItems(opts)

        if xSelection in opts:
            self.x_axis_dropdown.setCurrentText(xSelection)
        if ySelection in opts:
            self.y_axis_dropdown.setCurrentText(ySelection)

        self.previous_selection["x"] = xSelection
        self.previous_selection["y"] = ySelection

        self.x_axis_dropdown.blockSignals(False)
        self.y_axis_dropdown.blockSignals(False)

        self.axes_changed.emit(self.previous_selection.copy())

    @pyqtSlot(str)
    def on_axis_changed(self, axis):
        dropdown = self.sender()
        old_value = self.previous_selection.get(axis, None)
        new_value = dropdown.currentText()
        if new_value != old_value:
            # update previous selection and then send a copy (prevent unwanted mutations)
            self.previous_selection[axis] = new_value
            self.axes_changed.emit(self.previous_selection.copy())

    @pyqtSlot(object)
    def handle_data_exported(self, data):
        self.data_exported.emit(data)
    
    def add_legend_item(self, label, color):
        legend_layout = self.legend_container.contentLayout
        count = legend_layout.count()
          # Set your desired max columns
        row = count // self.max_legend_width
        column = count % self.max_legend_width
        legend_label = QLabel(f'<font color="{color}"><b>{label}</b></font>')
        legend_label.setStyleSheet("padding: 2px;")
        legend_layout.addWidget(legend_label, row, column)
        self.legend_items.append(legend_label)
    
    def clear(self):
        self.axes.clear()
        self.legend_container.clear()
        self.legend_items = []
        self.canvas.draw()

    def append(self, result):
        line, = self.axes.plot(result['x'], result['y'], label=result['label'])
        color = line.get_color()
        self.add_legend_item(result['label'],color)
        # Check the toolbar's status for grid lines and apply them
        if self.toolbar.is_h_grid_enabled():
            self.axes.yaxis.grid(True)
        if self.toolbar.is_v_grid_enabled():
            self.axes.xaxis.grid(True)
        # update view
        self.canvas.draw()

    def setAxesLabels(self, labels):
        self.axes.set_xlabel(labels['x'])
        self.axes.set_ylabel(labels['y'])
        self.canvas.draw()

    def getAxesDataLabels(self):
        return {"x": self.x_axis_dropdown.currentText(), "y": self.y_axis_dropdown.currentText()}
