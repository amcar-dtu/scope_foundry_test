# number_gen_readout_extendable_dataset.py
import time

import numpy as np
import pyqtgraph as pg
from qtpy import QtCore, QtWidgets

from ScopeFoundry import Measurement, h5_io


class NumberGenReadoutExtendableDataset(Measurement):

    name = "number_gen_readout_extendable_dataset"

    def setup(self):
        """
        Runs once during app initialization.
        This is the place to load a user interface file,
        define settings, and set up data structures.
        """

        s = self.settings
        s.New("sampling_period", float, initial=0.1, unit="s")
        s.New("N", int, initial=101)
        s.New("save_h5", bool, initial=True)

        # Data structure of the measurement
        self.data = {"y": np.ones(101)}
        self.hw = self.app.hardware["number_gen"]

    def setup_figure(self):
        """Create a figure programmatically."""

        # Create a layout that holds all measurement controls and settings from hardware
        cb_layout = QtWidgets.QHBoxLayout()
        cb_layout.addWidget(self.new_start_stop_button())
        cb_layout.addWidget(
            self.settings.New_UI(
                exclude=("activation", "run_state", "profile", "progress")
            )
        )
        # Add hardware settings to the layout
        cb_layout.addWidget(
            self.hw.settings.New_UI(exclude=("debug_mode", "connected", "port"))
        )
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.addLayout(cb_layout)

        # Create a plot widget containing a single line
        self.graphics_widget = pg.GraphicsLayoutWidget(border=(100, 100, 100))
        self.plot = self.graphics_widget.addPlot(title=self.name)
        self.plot_lines = {}
        self.plot_lines["y"] = self.plot.plot(pen="g")

        # Combine everything
        # ScopeFoundry assumes .ui is the main widget:
        self.ui = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.ui.addWidget(header_widget)
        self.ui.addWidget(self.graphics_widget)

    def update_display(self):
        self.plot_lines["y"].setData(self.data["y"])

    def run(self):
        """
        Runs when the measurement is started. Executes in a separate thread from the GUI.
        It should not update the graphical interface directly and should only
        focus on data acquisition.
        """

        # A buffer in memory for data
        self.data["y"] = np.ones(self.settings["N"])

        if self.settings["save_h5"]:
            self.open_new_h5_file()
            self.h5_y = h5_io.create_extendable_h5_like(
                h5_group=self.h5_meas_group, name="y", arr=self.data["y"], axis=0
            )

        # Use a try/finally block to ensure cleanup, e.g., closing the data file object.
        try:
            i = 0
            i_extended = 0

            # Run indefinitely or until interrupted
            while not self.interrupt_measurement_called:
                i %= self.settings["N"]

                # Update progress bar percentage
                self.set_progress(i * 100.0 / self.settings["N"])

                # Fill the buffer with sine wave readings from the hardware
                val = self.hw.settings.sine_data.read_from_hardware()
                self.data["y"][i] = val

                if self.settings["save_h5"]:
                    # Extend h5 data file if needed.
                    if i_extended >= len(self.h5_y):
                        self.h5_y.resize(i_extended + self.settings["N"], axis=0)

                    self.h5_y[i_extended] = val
                    self.h5_file.flush()

                # Wait between readings
                time.sleep(self.settings["sampling_period"])

                i += 1
                i_extended += 1

        finally:
            print(self.name, "finished")
            if self.settings["save_h5"]:
                # Ensure the data file is closed
                self.close_h5_file()
                print(self.name, "saved")

    # ---------------------------------------------------------------------------
    ## UNCOMMENT IF YOU HAVE SCOPEFOUNDRY 2.0 OR EARLIER
    # ---------------------------------------------------------------------------

    # def open_new_h5_file(self):
    #     """remove me if you have ScopeFoundry 2.1+"""
    #     self.close_h5_file()

    #     self.h5_file = h5_io.h5_base_file(self.app, measurement=self)
    #     self.h5_meas_group = h5_io.h5_create_measurement_group(self, self.h5_file)

    #     return self.h5_meas_group

    # def close_h5_file(self):
    #     if hasattr(self, "h5_file") and self.h5_file.id is not None:
    #         self.h5_file.close()

    # def save_h5(self, data):
    #     self.open_new_h5_file(data)
    #     self.close_h5_file()
