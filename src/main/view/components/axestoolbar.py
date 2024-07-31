from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QAction
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from src.main.app.baseapp import BaseApp

class AxesToolbar(NavigationToolbar, BaseApp):
    dataExported = pyqtSignal(object)
    
    def __init__(self, canvas, parent=None):
        super().__init__(canvas, parent)

        # Icons
        pop_icon = QIcon(self.getResource('icons', 'up-right-from-square-solid.svg'))
        hgrid_icon = QIcon(self.getResource('icons', 'horz-grid-lines.svg'))
        vgrid_icon = QIcon(self.getResource('icons', 'vert-grid-lines.svg'))
        export_icon = QIcon(self.getResource('icons', 'share-from-square-solid-padded.svg'))
        
        # Create custom buttons
        self.pop_figure_action = QAction(self)
        self.pop_figure_action.setIcon(pop_icon)
        self.pop_figure_action.setToolTip('Pop figure')
        self.pop_figure_action.triggered.connect(self.pop_figure)

        self.toggle_h_grid_action = QAction(self)
        self.toggle_h_grid_action.setIcon(hgrid_icon)
        self.toggle_h_grid_action.setToolTip('Toggle horizontal grid')
        self.toggle_h_grid_action.setCheckable(True)
        self.toggle_h_grid_action.toggled.connect(self.toggle_h_grid)

        self.toggle_v_grid_action = QAction(self)
        self.toggle_v_grid_action.setIcon(vgrid_icon)
        self.toggle_v_grid_action.setToolTip('Toggle vertical grid')
        self.toggle_v_grid_action.setCheckable(True)
        self.toggle_v_grid_action.toggled.connect(self.toggle_v_grid)
        
        self.export_data_action = QAction(self)
        self.export_data_action.setIcon(export_icon)
        self.export_data_action.setToolTip('Export figure data')
        self.export_data_action.triggered.connect(self.pop_data)

        # Add custom buttons to the toolbar
        self.addAction(self.toggle_h_grid_action)
        self.addAction(self.toggle_v_grid_action)
        self.addSeparator()
        self.addAction(self.export_data_action)
        self.addAction(self.pop_figure_action)

    def pop_figure(self):
        original_axes = self.canvas.figure.get_axes()[0]
        new_fig, new_axes = plt.subplots()

        for line in original_axes.lines:
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            label = line.get_label()
            new_axes.plot(x_data, y_data, label=label)
        
        new_axes.set_title(original_axes.get_title())
        new_axes.set_xlabel(original_axes.get_xlabel())
        new_axes.set_ylabel(original_axes.get_ylabel())
        new_axes.yaxis.grid(self.is_h_grid_enabled())
        new_axes.xaxis.grid(self.is_v_grid_enabled())

        new_fig.show()
    
    def pop_data(self):
        # Get the current axes
        original_axes = self.canvas.figure.get_axes()[0]

        # Prepare data for export
        data = []
        headers = []
        for line in original_axes.lines:
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            label = line.get_label()
            headers.append(f'X-{label}')
            headers.append(f'Y-{label}')
            if len(data) == 0:
                data = list(zip(x_data, y_data))
            else:
                new_data = list(zip(x_data, y_data))
                data = [(*d, *n) for d, n in zip(data, new_data)]
        # Emit the data
        self.dataExported.emit({'headers':headers,'data': data})
        
        # # Save to CSV
        # file_name = self.save_file("CSV Files (*.csv);;All Files (*.*)")
        # if file_name:
        #     with open(file_name, 'w', newline='') as csvfile:
        #         writer = csv.writer(csvfile)
        #         writer.writerow(headers)
        #         writer.writerows(data)
        #     print(f"Data exported to {file_name}")

    def toggle_h_grid(self, checked):
        self.canvas.figure.gca().yaxis.grid(checked)
        self.canvas.draw()

    def toggle_v_grid(self, checked):
        self.canvas.figure.gca().xaxis.grid(checked)
        self.canvas.draw()

    def is_h_grid_enabled(self):
        return self.toggle_h_grid_action.isChecked()

    def is_v_grid_enabled(self):
        return self.toggle_v_grid_action.isChecked()