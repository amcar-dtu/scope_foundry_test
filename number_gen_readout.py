# number_gen_readout.py
import time

import numpy as np
import pyqtgraph as pg
from qtpy import QtCore, QtWidgets

from ScopeFoundry import Measurement, h5_io


class NumberGenReadout(Measurement):

    name = "number_gen_readout"

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

        # data structure of the measurement
        self.data = {"y": np.ones(101)}
        self.hw = self.app.hardware["number_gen"]

    def setup_figure(self):
        """create a figure programmatically"""

        # make a layout that holds all measurement controlls and settings from hardware
        cb_layout = QtWidgets.QHBoxLayout()
        cb_layout.addWidget(self.new_start_stop_button())
        cb_layout.addWidget(
            self.settings.New_UI(
                exclude=("activation", "run_state", "profile", "progress")
            )
        )
        # add hardware settings to the layout
        cb_layout.addWidget(
            self.hw.settings.New_UI(exclude=("debug_mode", "connected", "port"))
        )
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QVBoxLayout(header_widget)
        header_layout.addLayout(cb_layout)

        # make a plot widget that containing a one line
        self.graphics_widget = pg.GraphicsLayoutWidget(border=(100, 100, 100))
        self.plot = self.graphics_widget.addPlot(title=self.name)
        self.plot_lines = {}
        self.plot_lines["y"] = self.plot.plot(pen="g")

        # putting everything together
        # ScopeFoundry assumes .ui is the main widget:
        self.ui = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.ui.addWidget(header_widget)
        self.ui.addWidget(self.graphics_widget)

    def update_display(self):
        self.plot_lines["y"].setData(self.data["y"])

    def setup_h5_file(self):
        # This stores all the hardware and app meta-data in the H5 file
        self.h5file = h5_io.h5_base_file(app=self.app, measurement=self)

        # create a measurement H5 group (folder) within self.h5file
        # This stores all the measurement meta-data in this group
        self.h5_group = h5_io.h5_create_measurement_group(
            measurement=self, h5group=self.h5file
        )

        # create an h5 dataset to store the data
        dset = self.data["y"]
        self.h5_y = self.h5_group.create_dataset(
            name="y", shape=dset.shape, dtype=dset.dtype
        )

    def run(self):
        """
        Runs when measurement is started. Runs in a separate thread from GUI.
        It should not update the graphical interface directly, and should only
        focus on data acquisition.
        """

        # a buffer in memory for data
        self.data["y"] = np.ones(self.settings["N"])

        if self.settings["save_h5"]:
            self.setup_h5_file()

        # We use a try/finally block, so that if anything goes wrong during a measurement,
        # the finally block can clean things up, e.g. close the data file object.
        try:
            i = 0

            # Will run forever until interrupt is called.
            while not self.interrupt_measurement_called:
                i %= len(self.h5_y)

                # Set progress bar percentage complete
                self.set_progress(i * 100.0 / self.settings["N"])

                # Fills the buffer with sine wave readings from func_gen Hardware
                self.data["y"][i] = self.hw.settings.sine_data.read_from_hardware()

                if self.settings["save_h5"]:
                    # if we are saving data to disk, copy data to H5 dataset
                    self.h5_y[i] = self.data["y"][i]
                    # flush H5
                    self.h5file.flush()

                # wait between readings.
                # We will use our sampling_period settings to define time
                time.sleep(self.settings["sampling_period"])

                i += 1

                if self.interrupt_measurement_called:
                    # Listen for interrupt_measurement_called flag.
                    # This is critical to do, if you don't the measurement will
                    # never stop.
                    # The interrupt button is a polite request to the
                    # Measurement thread. We must periodically check for
                    # an interrupt request
                    break

        finally:
            print("NumberGenReadout: Finishing")
            if self.settings["save_h5"]:
                # make sure to close the data file
                self.h5file.close()
                print("NumberGenReadout: Finishing")

    # alternative way to set up the figure using the qt creator
    # def setup_figure(self):

    #     # connect ui widgets to measurement/hardware settings or functions
    #     self.ui.start_pushButton.clicked.connect(self.start)
    #     self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
    #     self.settings.save_h5.connect_to_widget(self.ui.save_h5_checkBox)
    #     self.func_gen.settings.amplitude.connect_to_widget(self.ui.amp_doubleSpinBox)

    #     # Set up pyqtgraph graph_layout in the UI
    #     self.graph_layout=pg.GraphicsLayoutWidget()
    #     self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

    #     # Create PlotItem object (a set of axes)
    #     self.plot = self.graph_layout.addPlot(title=self.name)
    #     self.plot_lines = {}
    #     self.plot_lines["y"] = self.plot.plot(pen="g")
