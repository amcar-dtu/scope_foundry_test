# viewers/images.py
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from matplotlib.pyplot import imread

from ScopeFoundry.data_browser import DataBrowserView


class MatplotlibImreadView(DataBrowserView):

    # This name is used in the GUI for the DataBrowser
    name = "matplot_imread_view"

    def setup(self):
        # create the GUI and viewer settings, runs once at program start up
        # self.ui should be a QWidget of some sort, here we use a pyqtgraph ImageView
        self.ui = self.imview = pg.ImageView()

    def is_file_supported(self, fname) -> bool:
        # Tells the DataBrowser whether this plug-in would likely be able
        # to read the given file name
        # here we are using the file extension to make a guess
        return Path(fname).suffix.lower() in (".png", ".tif", ".tiff", ".jpg")

    def on_change_data_filename(self, fname):
        #  A new file has been selected by the user, load and display it
        try:
            self.data = imread(fname)
            self.imview.setImage(self.data.swapaxes(0, 1))
        except Exception as err:
            # When a failure to load occurs, zero out image
            # and show error message
            self.imview.setImage(np.zeros((10, 10)))
            self.databrowser.ui.statusbar.showMessage(f"failed to load {fname}:\n{err}")
            raise (err)
