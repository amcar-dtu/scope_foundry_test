# number_gen_readout_simple.py
import time

import numpy as np
import pyqtgraph as pg
from qtpy import QtCore, QtWidgets

from ScopeFoundry import Measurement, h5_io


class NumberGenReadoutSimple(Measurement):

    name = "number_gen_readout_simple"

    def setup(self):
        """
        Runs once during app initialization.
        This is where you define your settings and set up data structures.
        """

        s = self.settings
        s.New("sampling_period", float, initial=0.1, unit="s")
        s.New("N", int, initial=101)
        s.New("save_h5", bool, initial=True)
        self.data = {"y": np.ones(self.settings["N"])}

    def run(self):
        """
        Runs when the measurement starts. Executes in a separate thread from the GUI.
        It should not update the graphical interface directly and should focus only
        on data acquisition.
        """
        # Prepare an array for data in memory.
        y = self.data["y"] = np.ones(self.settings["N"])

        # Get a reference to the hardware
        hw = self.app.hardware["number_gen"]

        # Sample the hardware for values N times
        for i in range(self.settings["N"]):

            # read data from device.
            y[i] = hw.settings.get_lq("sine_data").read_from_hardware()

            # wait for the sampling period.
            time.sleep(self.settings["sampling_period"])

            self.set_progress(i * 100.0 / self.settings["N"])

            # break the loop if user desires.
            if self.interrupt_measurement_called:
                break

        if self.settings["save_h5"]:
            # saves data, closes file,
            self.save_h5(data=self.data)

            # ScopeFoundry 2.1 and later
            # self.save_h5 also sets self.dataset_metadata
            # which allows to save data in other formats
            import matplotlib.pyplot as plt

            plt.figure()
            plt.plot(y)
            plt.savefig(self.dataset_metadata.get_file_path(".png"))
            plt.close()

    def setup_figure(self):
        """
        Runs once during App initialization and is responsible
        to create widget self.ui.
        Create plots, controls widgets and buttons here.
        """
        self.ui = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout()
        self.ui.setLayout(layout)
        layout.addWidget(
            self.settings.New_UI(include=("sampling_period", "N", "save_h5"))
        )
        layout.addWidget(self.new_start_stop_button())
        self.graphics_widget = pg.GraphicsLayoutWidget(border=(100, 100, 100))
        self.plot = self.graphics_widget.addPlot(title=self.name)
        self.plot_lines = {"y": self.plot.plot(pen="g")}
        layout.addWidget(self.graphics_widget)

    def update_display(self):
        self.plot_lines["y"].setData(self.data["y"])

    # ---------------------------------------------------------------------------
    # # UNCOMMENT IF YOU HAVE SCOPEFOUNDRY 2.0 OR EARLIER
    # ---------------------------------------------------------------------------

    # def open_new_h5_file(self):
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
