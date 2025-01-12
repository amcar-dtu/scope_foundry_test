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
        Runs once during App initialization.
        This is the place to load a user interface file,
        define settings, and set up data structures.
        """

        s = self.settings
        s.New("sampling_period", float, initial=0.1, unit="s")
        s.New("N", int, initial=101)
        s.New("save_h5", bool, initial=True)

    def run(self):
        """
        Runs when measurement is started. Runs in a separate thread from GUI.
        It should not update the graphical interface directly, and should only
        focus on data acquisition.
        """

      	# prepare an array for data in memory.
        self.data = np.ones(self.settings["N"])
        
        # get a reference to the hardware
        self.hw = self.app.hardware["number_gen"]
        
        # N-times sampling the hardware for values
        for i in range(self.settings["N"]):
          self.data[i] = self.hw.settings.sine_data.read_from_hardware()
          time.sleep(self.settings["sampling_period"])
          self.set_progress(i * 100.0 / self.settings["N"])
          if self.interrupt_measurement_called:
            break
                        
        if self.settings["save_h5"]:
            # open a file
            self.h5_file = h5_io.h5_base_file(app=self.app, measurement=self)

            # create a measurement H5 group (folder) within self.h5file
            # This stores all the measurement meta-data in this group
            self.h5_group = h5_io.h5_create_measurement_group(
                measurement=self, h5group=self.h5_file
            )

            # dump the data set and close the file
            self.h5_group.create_dataset(name="y", data=self.data)
            self.h5_file.close()
        
    def setup_figure(self):
        """
        Runs once during App initialization and is responsible
        to create widget self.ui.        
        """
        self.ui = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout()
        self.ui.setLayout(layout)
        layout.addWidget(self.settings.New_UI(include=("sampling_period", "N", "save_h5")))
        layout.addWidget(self.new_start_stop_button())
        self.graphics_widget = pg.GraphicsLayoutWidget(border=(100, 100, 100))
        self.plot = self.graphics_widget.addPlot(title=self.name)
        self.plot_lines = {"y": self.plot.plot(pen="g")}
        layout.addWidget(self.graphics_widget)

    def update_display(self):
        self.plot_lines["y"].setData(self.data)
