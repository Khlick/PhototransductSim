# NOTES:
# Need to set up a configuration yaml to populate configuration page

import os
import yaml
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QListWidget, QListWidgetItem, QStackedWidget, QWidget, QGridLayout, QMenuBar, QMenu, QStatusBar, QScrollArea, QSizePolicy, QSpacerItem, QProgressBar
)
from PyQt6.QtGui import (
    QFontDatabase, QIcon, QPixmap, QFont, QAction, QKeySequence, QShortcut
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRect

# local imports
from src.main.app.baseapp import BaseApp
from src.main.view.components import CollapsibleSection, Axes

# utilities
from src.main.utils import camel_to_title

class MainView(QMainWindow, BaseApp):
    requestUndo = pyqtSignal()
    requestRedo = pyqtSignal()
    interruptSim = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.initUi()
        self.bindKeyboard()
    
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1200, 700)
        
        with open(self.getData('aes.yaml'), 'r') as file:
            aes =  yaml.safe_load(file)

        # load app icon
        app_icon_path = self.getResource('icons', aes.get('appIcon'))
        self.setWindowIcon(QIcon(app_icon_path))
        
        # Load and apply the Playfair Display font
        playfair_font_path = self.getResource('fonts', aes.get('defaultFont'))
        QFontDatabase.addApplicationFont(playfair_font_path)
        self.setFont(QFont("Playfair Display"))

        # Load the Playwrite HR font for sidebar label
        playwrite_font_path = self.getResource('fonts', aes.get('titleFont'))
        QFontDatabase.addApplicationFont(playwrite_font_path)
        
        # Load and apply QSS styles
        style_path = self.getResource('styles', 'ui.qss')
        with open(style_path, 'r') as file:
            self.setStyleSheet(file.read())

        # Main layout
        self.main_gridLayout = QWidget(parent=self)
        self.main_gridLayout.setObjectName("main_gridLayout")
        self.gridLayout = QGridLayout(self.main_gridLayout)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        # Sidebar frame
        self.sidebar_frame = QFrame(parent=self.main_gridLayout)
        self.sidebar_frame.setFrameShape(QFrame.Shape.Box)
        self.sidebar_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.sidebar_frame.setObjectName("sidebar_frame")
        self.horizontalLayout = QHBoxLayout(self.sidebar_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Sidebar icon
        self.sidebar_icon = QLabel(parent=self.sidebar_frame)
        self.sidebar_icon.setPixmap(QPixmap(app_icon_path))
        self.sidebar_icon.setObjectName("sidebar_icon")
        self.sidebar_icon.setScaledContents(True)
        self.horizontalLayout.addWidget(self.sidebar_icon)

        # Sidebar label
        self.sidebar_label = QLabel(parent=self.sidebar_frame)
        self.sidebar_label.setText("PhototransductSim")
        self.sidebar_label.setObjectName("sidebar_label")
        self.horizontalLayout.addWidget(self.sidebar_label)

        # Sidebar Toggle
        isopen_icon = QIcon(self.getResource('icons', 'ellipsis-vertical-solid.svg'))
        self.sidebar_toggle = QPushButton(parent=self.sidebar_frame)
        self.sidebar_toggle.setObjectName("sidebar_toggle")
        self.sidebar_toggle.setText("")
        self.sidebar_toggle.setIcon(isopen_icon)
        self.sidebar_toggle.setIconSize(QSize(20, 20))
        self.sidebar_toggle.setCheckable(True)
        self.sidebar_toggle.setChecked(False)
        self.sidebar_toggle.setToolTip("Click to hide menu")
        self.sidebar_toggle.setFixedSize(35, 40)
        self.horizontalLayout.addWidget(self.sidebar_toggle)
        self.gridLayout.addWidget(self.sidebar_frame, 0, 0, 1, 2)

        # Sidebar icon list
        self.sidebar_iconList = QListWidget(parent=self.main_gridLayout)
        self.sidebar_iconList.setMaximumSize(QtCore.QSize(58, 16777215))
        self.sidebar_iconList.setObjectName("sidebar_iconList")
        self.gridLayout.addWidget(self.sidebar_iconList, 1, 0, 1, 1)
        self.sidebar_iconList.hide()

        # Expanded sidebar icon list
        self.sidebar_iconList_expanded = QListWidget(parent=self.main_gridLayout)
        self.sidebar_iconList_expanded.setMaximumSize(QtCore.QSize(255, 16777215))
        self.sidebar_iconList_expanded.setObjectName("sidebar_iconList_expanded")
        self.gridLayout.addWidget(self.sidebar_iconList_expanded, 1, 1, 1, 1)

        # Parameter frame
        self.param_frame = QFrame(parent=self.main_gridLayout)
        self.param_frame.setFrameShape(QFrame.Shape.Box)
        self.param_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.param_frame.setObjectName("param_frame")
        self.horizontalLayout_2 = QHBoxLayout(self.param_frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.param_label = QLabel(parent=self.param_frame)
        self.param_label.setObjectName("param_label")
        self.param_label.setText("Model Parameters")
        self.horizontalLayout_2.addWidget(self.param_label)
        self.param_toggle = QPushButton(parent=self.param_frame)
        self.param_toggle.setObjectName("param_toggle")
        self.param_toggle.setText('')
        self.param_toggle.setToolTip("Click to hide parameters")
        self.param_toggle.setIcon(isopen_icon)
        self.param_toggle.setIconSize(QSize(20, 20))
        self.param_toggle.setCheckable(True)
        self.param_toggle.setChecked(False)
        self.param_toggle.setFixedSize(35, 40)
        self.horizontalLayout_2.addWidget(self.param_toggle)
        self.gridLayout.addWidget(self.param_frame, 0, 2, 1, 1)

        # Parameter panel frame
        self.param_panel_frame = QFrame(parent=self.main_gridLayout)
        self.param_panel_frame.setFrameShape(QFrame.Shape.Box)
        self.param_panel_frame.setFrameShadow(QFrame.Shadow.Plain)
        self.param_panel_frame.setObjectName("param_panel_frame")
        self.param_panel_frame.setMaximumWidth(300)

        # Create a QScrollArea
        self.param_scroll_area = QScrollArea(parent=self.main_gridLayout)
        self.param_scroll_area.setWidgetResizable(True)
        self.param_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.param_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.param_scroll_area.setWidget(self.param_panel_frame)
        self.param_scroll_area.setObjectName("param_scroll_area")
        self.param_scroll_area.setMaximumWidth(300)

        # Ensure the scroll area can expand
        self.param_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Use QVBoxLayout for the param_panel_frame
        self.param_panel_layout = QVBoxLayout(self.param_panel_frame)
        self.param_panel_layout.setSpacing(0)
        self.param_panel_layout.setObjectName("param_panel_layout")
        self.param_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add the QScrollArea to the main layout
        self.gridLayout.addWidget(self.param_scroll_area, 1, 2, 1, 1)

        # Content container
        self.content_container = QStackedWidget(parent=self.main_gridLayout)
        self.content_container.setObjectName("content_container")
        self.content_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gridLayout.addWidget(self.content_container, 0, 3, 2, 1)        
        
        # Add main grid layout to the window
        self.setCentralWidget(self.main_gridLayout)

        # Menu bar
        self.menubar = QMenuBar(parent=self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1078, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QMenu(parent=self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(parent=self)
        self.statusbar.setObjectName("statusbar")
        
        # statusbar container
        status_container = QWidget()
        # statusbar layout
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0,0,0,0)
        status_layout.setSpacing(5)
        
        # add spacer to statusbar layout
        status_spacer = QSpacerItem(40,20,QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        status_layout.addItem(status_spacer)
        
        # Add the status bar text
        self.statustext = QLabel("Welcome")
        self.statustext.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.statustext.setObjectName("statusbar_label")
        # add text to the statusbar layout
        status_layout.addWidget(self.statustext)
        
        # Add a QProgressBar as a progress indicator
        self.statusProgressBar = QProgressBar()
        self.statusProgressBar.setRange(0, 100)
        self.statusProgressBar.setValue(0)
        self.statusProgressBar.setFixedSize(100, 16)
        self.statusProgressBar.setVisible(False)
        status_layout.addWidget(self.statusProgressBar)
        
        self.statusbar.addPermanentWidget(status_container)
        
        # Add statusbar to menu
        self.setStatusBar(self.statusbar)

        # Actions
        self.actionAbout = QAction(parent=self)
        self.actionAbout.setObjectName("actionAbout")
        self.actionConfiguration = QAction(parent=self)
        self.actionConfiguration.setObjectName("actionConfiguration")
        self.actionImport = QAction(parent=self)
        self.actionImport.setObjectName("actionImport")
        self.actionParameters = QAction(parent=self)
        self.actionParameters.setObjectName("actionParameters")
        self.actionSolution = QAction(parent=self)
        self.actionSolution.setObjectName("actionSolution")
        self.actionFigures = QAction(parent=self)
        self.actionFigures.setObjectName("actionFigures")
        self.actionExport = QAction(parent=self)
        self.actionExport.setObjectName("actionExport")
        self.actionQuit = QAction(parent=self)
        self.actionQuit.setObjectName("actionQuit")
        self.actionResetSettings = QAction(parent=self)
        self.actionResetSettings.setObjectName("actionResetSettings")

        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionConfiguration)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionResetSettings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        # Create the data viz page (Axes)
        self.axes = Axes(self.content_container)
        self.content_container.addWidget(self.axes)

        # Config page setup
        self.config_page = QWidget()
        self.config_page.setObjectName("config_page")
        config_layout = QVBoxLayout(self.config_page)
        
        # Build the config container
        # Create the top bar layout
        top_bar = QWidget(self.config_page)
        top_bar.setObjectName("config_top_bar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(5, 2, 5, 2)
        top_bar_layout.setSpacing(5)
        
        # Add icon
        icon_label = QLabel()
        icon_path = self.getResource('icons', 'gear-solid.svg')
        icon_label.setPixmap(QPixmap(icon_path).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        top_bar_layout.addWidget(icon_label)
        
        # Add styled text
        config_label = QLabel("Configuration")
        config_label.setObjectName("config_label")
        config_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        top_bar_layout.addWidget(config_label)

        # Add horizontal spacer
        top_bar_layout.addStretch()

        # Add buttons
        self.config_defaults_button = QPushButton("Defaults")
        self.config_done_button = QPushButton("Done")
        top_bar_layout.addWidget(self.config_defaults_button)
        top_bar_layout.addWidget(self.config_done_button)
        
        # Add top bar to the layout
        config_layout.addWidget(top_bar)
        
        # Create the scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Create a container for the scroll area content
        self.config_scroll_content = QWidget()
        self.config_scroll_layout = QVBoxLayout(self.config_scroll_content)
        self.config_scroll_layout.setSpacing(0)
        self.config_scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Add the scroll content to the scroll area
        scroll_area.setWidget(self.config_scroll_content)
        config_layout.addWidget(scroll_area)
        self.config_scroll_content.setObjectName("config_contents")
        
        # Initialize the dynamic sections storage
        self.param_sections = {}
        self.config_sections = {}

        # Append page to stacked widget
        self.content_container.addWidget(self.config_page)
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "PhototransductSim"))
        self.sidebar_icon.setText(_translate("MainWindow", ""))
        self.sidebar_label.setText(_translate("MainWindow", "PhototransductSim"))
        self.sidebar_toggle.setText(_translate("MainWindow", ""))
        self.param_label.setText(_translate("MainWindow", "Model Parameters"))
        self.param_toggle.setText(_translate("MainWindow", ""))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionResetSettings.setText(_translate("MainWindow", "Reset Settings"))
        self.actionConfiguration.setText(_translate("MainWindow", "Configuration"))
        self.actionImport.setText(_translate("MainWindow", "Import..."))
        self.actionParameters.setText(_translate("MainWindow", "Parameters"))
        self.actionSolution.setText(_translate("MainWindow", "Solution"))
        self.actionFigures.setText(_translate("MainWindow", "Figures"))
        self.actionExport.setText(_translate("MainWindow", "Export..."))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        

    def initUi(self):
        self.init_sidebar()
        self.init_model_parameters()
        self.init_config_page()
    
    def init_sidebar(self):
        self.sidebar_iconList.clear()
        self.sidebar_iconList_expanded.clear()
        
        # Load and parse the YAML configuration
        with open(self.getData("ui_menu.yaml"), 'r') as file:
            menu_data = yaml.safe_load(file)

        # Populate the icon lists
        for key, item in menu_data.items():
            label = item['label']
            icon_path = self.getResource('icons', item['icon'])

            # Create custom widget for unexpanded list
            std_item = QListWidgetItem(self.sidebar_iconList)
            std_item.setIcon(QIcon(icon_path))
            std_item.setSizeHint(QSize(40,40))
            std_item.setToolTip(label)
            std_item.setData(Qt.ItemDataRole.UserRole, key)
            std_item.setData(Qt.ItemDataRole.UserRole + 1 , False) # isDisabled
            self.sidebar_iconList.addItem(std_item)
            
            # Create custom widget for expanded list
            exp_item = QListWidgetItem(self.sidebar_iconList_expanded)
            exp_item.setIcon(QIcon(icon_path))
            exp_item.setText(label)
            exp_item.setData(Qt.ItemDataRole.UserRole, key + "-exp")
            exp_item.setData(Qt.ItemDataRole.UserRole + 1, False) # isDisabled
            self.sidebar_iconList_expanded.addItem(exp_item)

        # Add the Quit item
        quit_label = "Quit"
        quit_icon_path = self.getResource('icons', 'circle-xmark-solid.svg')

        quit_std_item = QListWidgetItem(self.sidebar_iconList)
        quit_std_item.setIcon(QIcon(quit_icon_path))
        quit_std_item.setSizeHint(QSize(40,40))
        quit_std_item.setData(Qt.ItemDataRole.UserRole, "quit")
        quit_std_item.setData(Qt.ItemDataRole.UserRole + 1, False) # isDisabled
        quit_std_item.setToolTip("Close")
        self.sidebar_iconList.addItem(quit_std_item)

        quit_exp_item = QListWidgetItem(self.sidebar_iconList_expanded)
        quit_exp_item.setIcon(QIcon(quit_icon_path))
        quit_exp_item.setText(quit_label)
        quit_exp_item.setData(Qt.ItemDataRole.UserRole, "quit-exp")
        quit_exp_item.setData(Qt.ItemDataRole.UserRole + 1, False)
        self.sidebar_iconList_expanded.addItem(quit_exp_item)
    
    def init_model_parameters(self):
        with open(self.getData('model_inputs.yaml'), 'r') as file:
            model_inputs = yaml.safe_load(file)
        styleObjs = [
            "collapsibleContainer", "collapsibleToggleButton", "collapsibleHeaderLine", "collapsibleContentArea", "collapsibleContentWidget"
            ]
        for section_id, items in model_inputs.items():
            section_title = camel_to_title(section_id)
            section = CollapsibleSection(id=section_id, title=section_title, animationDuration=100, parent=self.param_panel_frame)
            for item_id, config in items.items():
                section.append(item_id, config)
                for obj in styleObjs:
                    section.setClassName(obj,"param")
            self.param_sections[section_id] = section
            self.param_panel_layout.addWidget(section)
            section.toggle(False)
        self.param_panel_layout.addStretch()
    
    def init_config_page(self):
        with open(self.getData('configs.yaml'), 'r') as file:
            config_data = yaml.safe_load(file)
        styleObjs = [
            "collapsibleContainer", "collapsibleToggleButton", "collapsibleHeaderLine", "collapsibleContentArea", "collapsibleContentWidget"
            ]
        for section_id, items in config_data.items():
            section_title = camel_to_title(section_id)
            section = CollapsibleSection(id=section_id, title=section_title, animationDuration=100, parent=self.config_scroll_content)
            for item_id, config in items.items():
                section.append(item_id, config, False)
                for obj in styleObjs:
                    section.setClassName(obj,"config")
                section.setClassName("LineItem", "config")
            self.config_sections[section_id] = section
            self.config_scroll_layout.addWidget(section)
            section.toggle(False)

        self.config_scroll_layout.addStretch()
    
    def updateAxesOptions(self,labels):
        self.axes.update_axes_options(labels, 'time', 'intracellularCurrentNorm')
        
    def getAxesSelectedOptions(self):
        return self.axes.getAxesDataLabels()
    
    def clearPlot(self):
        self.axes.clear()
    
    def updatePlot(self,results):
        # Results are in the format:
        # {
            # label:{x:label (unit), y: label (unit)}, 
            # data: [{x:data,y:data,label:stim R*}]
        # }
        self.clearPlot()
        self.axes.setAxesLabels(results['label'])
        for result in results['data']:
            self.axes.append(result)
    
    def get_param(self, section_id, line_item_id):
        section = self.param_sections.get(section_id)
        if section:
            return section.getValue(line_item_id)
        return None

    def set_param(self, section_id, line_item_id, value):
        section = self.param_sections.get(section_id)
        if section:
            section.setValue(line_item_id, value)
            
    def setStatus(self,message):
        self.statustext.setText(message)
    
    def updateStatusBarProgress(self, progress):
        if progress < 0:
            self.statusProgressBar.hide()
            self.statusProgressBar.setValue(0)
        elif progress == 100:
            self.statustext.setText("Simulation Complete")
            self.statusProgressBar.setValue(0)
            self.statusProgressBar.hide()
        else:
            self.statusProgressBar.setValue(progress)
            if self.statusProgressBar.isHidden():
                self.statusProgressBar.show()
    
    def set_sidebar_item_enabled(self, item_id, enabled=True):
        sidebar_items = self.get_sidebar_item(item_id)
        for item in sidebar_items:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled) if enabled else item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            item.setData(Qt.ItemDataRole.UserRole + 1, not enabled)
    
    def bindKeyboard(self):
        # Add shortcuts
        undoShortcut = QShortcut(QKeySequence("ctrl+z"), self)
        undoShortcut.activated.connect(self.requestUndo.emit)

        redoShortcut = QShortcut(QKeySequence("ctrl+y"), self)
        redoShortcut.activated.connect(self.requestRedo.emit)
        
        interruptSim = QShortcut(QKeySequence("ctrl+c"),self)
        interruptSim.activated.connect(self.interruptSim.emit)
    
    def set_active_page(self,page_name):
        if page_name == "config":
            self.content_container.setCurrentWidget(self.config_page)
        else:
            self.content_container.setCurrentWidget(self.axes)

    def get_sidebar_item(self,id):
        items = []
        for index in range(self.sidebar_iconList.count()):
            item = self.sidebar_iconList.item(index)
            item_exp = self.sidebar_iconList_expanded.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == id:
                items.append(item)
                items.append(item_exp)
                break
        return items
        
    def getConfig(self,section_id,line_id):
        for id, section in self.config_sections.items():
            if id == section_id:
                return section.getValue(line_id)
    
    def setConfig(self,section_id,line_id,value):
        for id, section in self.config_sections.items():
            if id == section_id:
                section.setValue(line_id,value)

    def save_figure(self, file_path):
        self.axes.figure.savefig(file_path)

    def export_figure_data(self):
        self.axes.toolbar.pop_data()

    #--------------- GET AND SET METHODS FOR SETTINGS ---------------#
    
    # MODEL PARAMETERS
    def get_model_parameters(self):
        return {
            id: section.getAllValues() for id, section in self.param_sections.items()
            }
    
    def set_model_parameters(self,paramObj):
        for section_id, value_obj in paramObj.items():
            if section_id in self.param_sections:
                self.param_sections[section_id].setAllValues(value_obj)

    # CONFIGURATIONS
    def get_config_parameters(self):
        return {
            id: section.getAllValues() for id, section in self.config_sections.items()
        }

    def set_config_parameters(self, paramObj):
        for section_id, value_obj in paramObj.items():
            if section_id in self.config_sections:
                self.config_sections[section_id].setAllValues(value_obj)
    
    # SIDEBAR
    def get_sidebar_toggle(self):
        return self.sidebar_toggle.isChecked()
    
    def set_sidebar_toggle(self,visible):
        self.sidebar_toggle.setChecked(visible)
    
    # PARAMETERS
    def get_param_toggle(self):
        return self.param_toggle.isChecked()
    
    def set_param_toggle(self,visible):
        self.param_toggle.setChecked(visible)
    
    def get_param_section_visible(self):
        return {
            section_id: section.toggleButton.isChecked()
            for section_id, section in self.param_sections.items()
        }
    
    def set_param_section_visible(self,paramVisObj):
        if not self.get_param_toggle():
            return
        for section_id, section in self.param_sections.items():
            setVisible = paramVisObj.get(section_id, None)
            if setVisible is not None:
                section.toggle(setVisible)

    # MAIN VIEW
    def get_window_geometry(self):
        geometry = self.geometry()
        return {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        }

    def set_window_geometry(self, geometry):
        if all(key in geometry for key in ("x", "y", "width", "height")):
            primary_screen = QApplication.primaryScreen()
            available_geometry = primary_screen.availableGeometry()
            total_geometry = QRect()
            for screen in QApplication.screens():
                total_geometry = total_geometry.united(screen.availableGeometry())

            screen_rect = QRect(
                geometry["x"],
                geometry["y"],
                geometry["width"],
                geometry["height"]
            )

            if total_geometry.contains(screen_rect):
                self.setGeometry(screen_rect)
            else:
                # Center the window on the primary monitor
                width = min(geometry["width"], available_geometry.width())
                height = min(geometry["height"], available_geometry.height())
                x = available_geometry.left() + (available_geometry.width() - width) / 2
                y = available_geometry.top() + (available_geometry.height() - height) / 2
                self.setGeometry(x, y, width, height)
