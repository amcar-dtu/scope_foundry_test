# example that overrides the setup_figure method of the NumberGenReadout class to show usage with Qt Creator generated ui file.
import pyqtgraph as pg

from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

from .number_gen_readout_simple import NumberGenReadoutSimple


class NumberGenReadoutQtCreator(NumberGenReadoutSimple):

    name = "number_gen_readout_qt_creator"

    def setup_figure(self):
        ui_filename = sibling_path(__file__, "number_gen_readout.ui")
        self.ui = load_qt_ui_file(ui_filename)
        self.hw = self.app.hardware["number_gen"]

        # connect ui widgets to measurement/hardware settings or functions
        self.settings.activation.connect_to_pushButton(self.ui.start_pushButton)
        self.settings.save_h5.connect_to_widget(self.ui.save_h5_checkBox)

        self.hw.settings.amplitude.connect_to_widget(self.ui.amp_doubleSpinBox)

        # Set up pyqtgraph graph_layout in the UI
        self.graph_layout = pg.GraphicsLayoutWidget()
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

        # Create PlotItem object (a set of axes)
        self.plot = self.graph_layout.addPlot(title=self.name)
        # Create PlotDataItem object ( a scatter plot on the axes )
        self.plot_lines = {"y": self.plot.plot(pen="g")}
