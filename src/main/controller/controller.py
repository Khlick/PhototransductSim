import os
import json
import yaml
import csv
import numpy as np
from PyQt6.QtCore import QObject, QCoreApplication, Qt, QThread, QTimer, pyqtSlot, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import QMessageBox

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

from src.main.app.baseapp import BaseApp
from src.main.utils import StateBuffer, NumpyEncoder, camel_to_title
from src.main.model.simulationworker import SimulationWorker

class Controller(QObject, BaseApp):
    MAX_UNDO = 20
    
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self.param_actions_buffer = StateBuffer(self.MAX_UNDO)
        self.refreshOnExit = False
        
        # Initialize the UI and Model
        self.initModelUi()
        self.updateModelData()
        
        # Be default, set the reset model button to disabled
        self.view.set_sidebar_item_enabled("resetParams",False)
        
        # Load view and settings
        self.load_settings()
        
        # Apply settings related to model
        self.updateModelData()
        
        # Bind ui listeners
        self.bindUi()
        
        # Setup, run simulation
        self.initSimWorker()
        
        # Setup onClose()
        QCoreApplication.instance().aboutToQuit.connect(self.save_settings)

    def bindUi(self):
        # Sidebar and param view toggles
        self.view.sidebar_toggle.toggled.connect(self.on_toggle_sidebar)
        self.view.param_toggle.toggled.connect(self.on_toggle_param)
        
        # Sidebar icons 
        self.view.sidebar_iconList.itemClicked.connect(self.handle_sidebar_click)
        self.view.sidebar_iconList_expanded.itemClicked.connect(self.handle_sidebar_click)
        
        # Axes page events
        self.view.axes.axes_changed.connect(self.on_axes_changed)
        self.view.axes.data_exported.connect(self.on_data_exported)
        
        # Connect the model parameter section listeners
        for _, section in self.view.param_sections.items():
            section.sectionValueChanged.connect(self.handle_section_value_changed)
        
        # Connect the menu actions
        self.view.actionAbout.triggered.connect(self.show_about)
        self.view.actionConfiguration.triggered.connect(self.edit_configuration)
        self.view.actionImport.triggered.connect(self.load_parameters)
        self.view.actionExport.triggered.connect(self.save_parameters)
        self.view.actionQuit.triggered.connect(self.quit_application)
        self.view.actionResetSettings.triggered.connect(self.reset_settings)
        
        # Connect Keyboard Actions
        self.view.requestUndo.connect(self.undo)
        self.view.requestRedo.connect(self.redo)
        self.view.interruptSim.connect(self.onInterruptSim)
        
        # Connect configuration events
        for _, section in self.view.config_sections.items():
            section.sectionValueChanged.connect(self.handle_config_value_changed)
        
        # Connect the configuration page buttons
        self.view.config_defaults_button.clicked.connect(self.on_config_defaults)
        self.view.config_done_button.clicked.connect(lambda: self.view.set_active_page('axes'))
    
    def initModelUi(self):
        self.view.updateAxesOptions(self.model.getLabels())
    
    def updateModelUi(self):
        self.view.set_model_parameters(self.model.getParameters())
        self.view.updateAxesOptions(self.model.getLabels())
        
    def updateModelData(self):
        ui_params = self.view.get_model_parameters()
        # Set model attributes
        for line_item_id, ui_value in ui_params["stimulusConfiguration"].items():
            if hasattr(self.model, line_item_id):
                setattr(self.model, line_item_id, ui_value)
        # Set model parameter values
        self.model.setParam(**ui_params["modelParameters"])
    
    # Callbacks
    def handle_sidebar_click(self, item):
        # Exit early if disabled
        if item.data(Qt.ItemDataRole.UserRole + 1):
            # is disabled
            return
        item_id = item.data(Qt.ItemDataRole.UserRole)
        item_row = self.view.sidebar_iconList_expanded.row(item) if item_id.endswith('-exp') else self.view.sidebar_iconList.row(item)
        
        if item_id.endswith('-exp'):
            item_id = item_id[:-4]  # Remove the '-exp' suffix
            self.view.sidebar_iconList.setCurrentRow(item_row)
        else:
            self.view.sidebar_iconList_expanded.setCurrentRow(item_row)
        
        # Proceed with the trimmed item_id
        if item_id == "simulate":
            self.runSimulation()
        elif item_id == "resetParams":
            self.reset_parameters()
        elif item_id == "loadParams":
            self.load_parameters()
        elif item_id == "saveParams":
            self.save_parameters()
        elif item_id == "exportResults":
            self.export_results()
        elif item_id == "exportFigure":
            self.export_figure()
        elif item_id == "editConfiguration":
            self.edit_configuration()
        elif item_id == "quit":
            self.quit_application()
        else:
            # print(f"Unknown item clicked: {item_id}")
            pass
        # After click, animate a fade off of the item clicked.
        def clear_selection(obj):
            obj.view.sidebar_iconList.clearSelection()
            obj.view.sidebar_iconList_expanded.clearSelection()
        # Set up a QTimer to clear the selection after a delay
        QTimer.singleShot(600, lambda: clear_selection(self))
    
    def save_settings(self):
        settings = {
            "refreshOnExit": self.refreshOnExit,
            "window_geometry": self.view.get_window_geometry(),
            "sidebar_toggle": self.view.get_sidebar_toggle(),
            "param_toggle": self.view.get_param_toggle(),
            "model_parameters": self.view.get_model_parameters(),
            "config_parameters": self.view.get_config_parameters()
        }
        settings_path = self.setUserData("settings.json","cfg")
        try:
            with open(settings_path, "w") as file:
                json.dump(settings, file, indent=4, cls=NumpyEncoder)
        except Exception as e:
            QMessageBox.critical(self.view, "Error Saving Settings", f"Error saving settings: {e}")
    
    def load_settings(self):
        # Notes:
        #  when loading base model for reset, make sure to update the resetParam sidebar
        settings_path = self.getUserData("cfg","settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as file:
                    settings = json.load(file)
                    if settings.get("refreshOnExit", False):
                        return
                    self.view.set_window_geometry(settings.get("window_geometry", {}))
                    self.view.set_sidebar_toggle(settings.get("sidebar_toggle", False))
                    self.on_toggle_sidebar(settings.get("sidebar_toggle", False))
                    self.view.set_param_toggle(settings.get("param_toggle", False))
                    self.on_toggle_param(settings.get("param_toggle", False))
                    self.view.set_model_parameters(settings.get("model_parameters", {}))
                    self.view.set_config_parameters(settings.get("config_parameters", {}))
            except Exception as e:
                QMessageBox.critical(self.view, "Error Loading Settings", f"Error loading settings: {e}")
                pass

    def reset_settings(self):
        self.refreshOnExit = True
        QMessageBox.information(
            self.view, 
            "Reset Settings",
            "Settings reset will take effect on next application run."
            )

    def on_toggle_param(self, status):
        if status:
            self.view.param_toggle.setIcon(QIcon(self.getResource('icons', 'sliders-solid.svg')))
            self.view.param_toggle.setToolTip("Click to show parameters")
            self.view.param_label.hide()
            self.view.param_panel_frame.hide()
            self.view.param_scroll_area.setMaximumWidth(58)  # Shrink the scroll area width
            self.view.param_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.view.param_toggle.setIcon(QIcon(self.getResource('icons', 'ellipsis-vertical-solid.svg')))
            self.view.param_toggle.setToolTip("Click to hide parameters")
            self.view.param_label.show()
            self.view.param_panel_frame.show()
            self.view.param_scroll_area.setMaximumWidth(300)  
            self.view.param_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def on_toggle_sidebar(self, status):
        self.view.sidebar_label.setHidden(status)
        self.view.sidebar_icon.setHidden(status)
        self.view.sidebar_iconList_expanded.setHidden(status)
        self.view.sidebar_iconList.setVisible(status)
        
        if status:
            self.view.sidebar_toggle.setIcon(QIcon(self.getResource('icons', 'bars-solid.svg')))
            self.view.sidebar_toggle.setToolTip("Click to show menu")
        else:
            self.view.sidebar_toggle.setIcon(QIcon(self.getResource('icons', 'ellipsis-vertical-solid.svg')))
            self.view.sidebar_toggle.setToolTip("Click to hide menu")
    
    def on_axes_changed(self, eventData):
        selections = self.view.getAxesSelectedOptions()
        results = self.model.getResult(selections['x'], selections['y'])
        self.view.updatePlot(results)

    def handle_config_value_changed(self):
        # No action for now
        pass
    
    @pyqtSlot(object)
    def on_data_exported(self,data):
        file_name = self.save_file(
            "Export Results Data", 
            "CSV Files (*.csv);;All Files (*.*)",
            os.path.join(self.view.getConfig("directories","saveDir"),"results.csv")
        )
        if file_name:
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data['headers'])
                writer.writerows(data['data'])
            self.save_parameters_as_pdf(file_name)

    def save_parameters_as_pdf(self, csv_file_path):
        params = self.model.getParameters()
        pdf_file_path = os.path.splitext(csv_file_path)[0] + ".pdf"
        
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter

        for root_key, root_value in params.items():
            self.create_pdf_page(c, root_key, root_value, width, height)
            c.showPage()  # Create a new page for each root key
        
        c.save()

    def create_pdf_page(self, c, root_key, data, width, height):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, camel_to_title(root_key))
        
        c.setFont("Helvetica", 10)
        
        # Prepare data for table
        def format_value(value):
            if isinstance(value, (list, np.ndarray, tuple)):
                # Format each element in the array
                formatted_elements = [format_number(element) for element in np.atleast_1d(value)]
                return ", ".join(formatted_elements)
            else:
                return format_number(value)

        def format_number(value):
            try:
                # Format the number to 4 decimal places and remove trailing zeros
                return "{:.4f}".format(float(value)).rstrip('0').rstrip('.')
            except (TypeError, ValueError):
                # If the value cannot be converted to a float, return it as a string
                return str(value)

        def prepare_table_data(data):
            table_data = [["Parameter", "Value"]]
            for key, value in data.items():
                table_data.append([key, format_value(value)])
            return table_data
        
        table_data = prepare_table_data(data)
        
        # Create table
        table = Table(table_data, colWidths=[3 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        # Calculate table position
        table.wrapOn(c, width, height)
        table_height = table._height
        table.drawOn(c, 1 * inch, height - 2 * inch - table_height)
    
    def initSimWorker(self):
        self.simulationThread = None
        selections = self.view.getAxesSelectedOptions()
        self.worker = SimulationWorker(self.model, selections)

    def initSimulation(self):
        self.simulationThread = QThread()
        self.worker.moveToThread(self.simulationThread)
        self.simulationThread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.finished.connect(self.simulationThread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.on_simulation_error)
        self.worker.result.connect(self.on_simulation_result)
        self.worker.progress.connect(self.on_simulation_progress)

    def runSimulation(self):
        # Check if parameters are different?
        # Update status bar
        self.view.setStatus("Simulating...")
        
        # Prepare simulation
        if self.simulationThread is not None:
            try: 
                if self.simulationThread.isRunning():
                    QMessageBox.information(
                        self.view, 
                        "Simulation In Progress",
                        "A simulation is already in progress. Press Ctrl+C (Cmd+C for Mac) to interrupt."
                        )
                    return
            except RuntimeError: 
                return
        
        self.initSimWorker()
        self.initSimulation()
        self.worker.selections = self.view.getAxesSelectedOptions()
        self.simulationThread.start()

    def on_simulation_finished(self):
        self.view.setStatus("Current")

    def on_simulation_error(self, error_message):
        QMessageBox.critical(self.view, "Simulation Error", error_message)
        self.view.updateStatusBarProgress(-1)
        self.view.setStatus("Error")
        self.simulationThread.finished.connect(self.simulationThread.deleteLater)
        self.simulationThread = None

    def on_simulation_result(self, results):
        self.view.updatePlot(results)

    def on_simulation_progress(self, progress):
        self.view.updateStatusBarProgress(progress)

    def onInterruptSim(self):
        if self.simulationThread is not None:
            try:
                if self.simulationThread.isRunning():
                    self.view.updateStatusBarProgress(-1)
                    self.view.setStatus("Terminating...")
                    self.worker.stop()
                    self.simulationThread.quit()
                    self.simulationThread.wait()
                    self.view.setStatus("Awaiting Simulation")
            except RuntimeError:
                self.simulationThread = None
    
    def on_config_defaults(self):
        # loads the getData("configs.yaml") sets the configs values from it
        with open(self.getData('configs.yaml'), 'r') as file:
            config_data = yaml.safe_load(file)
        for section_id, items in config_data.items():
            for line_id, item in items.items():
                self.view.setConfig(section_id,line_id,item.get("default",None))
    
    def reset_parameters(self):
        # finds the corresponding parameters in getData()
        model = self.view.get_param("modelSetup","cellModel")
        if model == "None":
            return
        model_path = self.getData(model.lower().replace(" ", "_") + ".json")
        self.import_model_params(model_path)

    def import_model_params(self,model_path):
        if os.path.exists(model_path):
            with open(model_path, "r") as file:
                    params = json.load(file)
            for param,value in params.items():
                try:
                    self.view.set_param("modelParameters",param,value)
                    self.model.setParam(**{param:value})
                except Exception as e:
                    QMessageBox.information(self.view, "Skipping Parameter", f"Skipping {param} for reason: {e}")
            self.view.setStatus("Parameters imported successfully!")
                    
    def load_parameters(self):
        # allows user defined parameters json
        model_path = self.load_file(
            "Import Model Parameters", 
            "JSON (*.json);",
            os.path.join(self.view.getConfig("directories","loadDir"),"model.json")
            )
        if model_path:
            self.import_model_params(model_path)
        if self.view.getConfig("directories","updateOnSave"):
            self.view.setConfig("directories","loadDir",os.path.dirname(model_path))

    def save_parameters(self):
        save_path = self.save_file(
            "Save Model Parameters",
            "JSON (*.json);",
            os.path.join(self.view.getConfig("directories","saveDir"),"model.json")
            )
        if save_path:
            params = self.model.getParameters()
            with open(save_path, 'w') as json_file:
                json.dump(params["modelParameters"], json_file, indent=4, cls=NumpyEncoder)
                self.view.setStatus("Parameters exported successfully!")
            if self.view.getConfig("directories","updateOnSave"):
                self.view.setConfig("directories","saveDir",os.path.dirname(save_path))

    def export_results(self):
        if self.model.results is None:
            return
        self.view.export_figure_data()

    def export_figure(self):
        root = self.view.getConfig("directories","saveDir")
        fig_path = self.save_file(
            "Save Figure",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;PDF (*.pdf);;SVG (*.svg);;All Files (*)",
            root
            )
        if fig_path:
            if self.view.getConfig("directories","updateOnSave"):
                self.view.setConfig("directories","saveDir",os.path.dirname(fig_path))
            self.view.save_figure(fig_path)

    def edit_configuration(self):
        self.view.set_active_page("config")
    
    def show_about(self):
        github_url = "https://github.com/Khlick/PhototransductSim"
        QDesktopServices.openUrl(QUrl(github_url))
        
    def handle_section_value_changed(self, section_id, old_value, new_value, line_item_id):
        # print(f"Section ID: {section_id}, Line Item ID: {line_item_id}, Old Value: {old_value}, New Value: {new_value} <{type(new_value)}>")
        if section_id == "modelSetup":
            if line_item_id == "cellModel":
                isDefaultModel = new_value != "None"
                self.view.set_sidebar_item_enabled("resetParams",isDefaultModel)
                if isDefaultModel:
                    self.import_model_params(
                        self.getData(new_value.lower().replace(" ", "_") + ".json")
                    )
        elif section_id == "stimulusConfiguration":
            if hasattr(self.model, line_item_id):
                setattr(self.model, line_item_id, new_value)
                # model attributes cause updates to other parameters in stimconfig
                updated_attrs = self.model.getParameters()
                self.view.set_model_parameters({section_id: updated_attrs[section_id].copy()})
                # Update undoable action
                self.appendAction( section_id, old_value, new_value, line_item_id)
            else:
                QMessageBox.warning(self.view, "Invalid Attribute", f"Warning: {line_item_id} is not a valid attribute of the model.")
        elif section_id == "modelParameters":
            self.model.setParam(**{line_item_id: new_value})
            # model attributes cause updates to other parameters in stimconfig
            updated_attrs = self.model.getParameters()
            self.view.set_model_parameters({section_id: updated_attrs[section_id].copy()})
            # Update undoable action
            self.appendAction( section_id, old_value, new_value, line_item_id)
        else:
            QMessageBox.warning(self.view, "Unrecognized Section", f"Warning: {section_id} is not a recognized section.")
        # Any updates here should cause an request for update
        if self.view.getConfig("simulation","doOnChange"):
            
            self.runSimulation()
        else:
            self.view.setStatus("Awaiting Simulation...")

    def updateModel(self, section_id, line_item_id, value):
        if section_id == "modelParameters":
            self.model.setParam(**{line_item_id: value})
            self.view.set_model_parameters(self.model.getParameters())
        elif section_id == "stimulusConfiguration":
            if hasattr(self.model, line_item_id):
                setattr(self.model, line_item_id, value)
                updated_attrs = self.model.getParameters()
                self.view.set_model_parameters({section_id: updated_attrs[section_id].copy()})
        else:
            return
        # update status bar to pending
        self.view.setStatus("Awaiting Simulation")

    def appendAction(self, section_id, old_value, new_value, line_item_id):
        # We always want to track the latest update, but if we don't already have an undo buffer, we need to insert the first old_value in
        if not len(self.param_actions_buffer):
            self.param_actions_buffer.append((section_id, line_item_id, old_value))
        self.param_actions_buffer.append((section_id, line_item_id, new_value))
        
    def undo(self):
        pass
        # if len(self.param_actions_buffer) == 0:
        #     return
        # section_id, line_item_id, last_value = self.param_actions_buffer.previous()
        # if section_id == None:
        #     # Either no more undo steps or none yet
        #     return
        # self.updateModel(section_id,line_item_id,last_value)

    def redo(self):
        pass
        # if len(self.param_actions_buffer.buffer) == 0:
        #     return
        # section_id, line_item_id, next_value = self.param_actions_buffer.previous()
        # if section_id == None:
        #     # Either no more undo steps or none yet
        #     return
        # self.updateModel(section_id,line_item_id,next_value)

    def quit_application(self):
        QCoreApplication.quit()
