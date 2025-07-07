import time
from ScopeFoundry import HardwareComponent
from ScopeFoundry.scanning import BaseRaster2DSlowScan
import numpy as np


class Example2DSlowScanMeasure(BaseRaster2DSlowScan):

    name = "example_2d_scan"

    def scan_specific_setup(self):
        self.detector: HardwareComponent = self.app.hardware["andor_ccd"]
        self.stage: HardwareComponent = self.app.hardware["mcl_xy_stage"]

    def pre_scan_setup(self):
        self.scan_shape = (1, self.Nv.val, self.Nh.val, 1600)  # _, Nv, Nh, signal length
        if self.settings["save_h5"]:
            self.signal_map = self.h5_meas_group.create_dataset(
                name="signal_map", shape=self.scan_shape, dtype=float
            )

    def setup_figure(self):
        super().setup_figure()
        self.ui.details_layout.addWidget(
            self.settings.New_UI(include=("h_axis", "v_axis"))
        )

    def move_position_start(self, h, v):
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def move_position_slow(self, h, v, dh, dv):
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def move_position_fast(self, h, v, dh, dv):
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def collect_pixel(self, pixel_num, k, j, i):
        ccd_hw = self.detector
        ccd_dev = ccd_hw.ccd_dev
        try:
            self.log.info("starting acq")
            ccd_dev.start_acquisition()

            while not self.interrupt_measurement_called:
                stat = ccd_hw.settings.ccd_status.read_from_hardware()
                
                if stat == 'IDLE':
                    # grab data
                    buffer_ = ccd_hw.get_acquired_data()
                    signal = np.average(buffer_, axis=0)

                    break # end the while loop for non-continuous scans
                else:
                    time.sleep(0.01)
        finally:            
            # while-loop is complete
            ccd_hw.interrupt_acquisition()

        self.display_image_map[k, j, i] = np.sum(signal, axis=0)
        if self.settings["save_h5"]:
            self.signal_map[k, j, i] = signal
