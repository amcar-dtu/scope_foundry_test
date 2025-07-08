import time
from ScopeFoundry import HardwareComponent
from ScopeFoundry.scanning import BaseRaster2DSlowScan
import numpy as np

from ScopeFoundry import h5_io
import traceback


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

    def move_position_start(self, h, v):  ##H and V axes are now always X and Y axes
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def move_position_slow(self, h, v, dh, dv):
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def move_position_fast(self, h, v, dh, dv):
        self.stage.settings.x_target.update_value(h)
        self.stage.settings.y_target.update_value(v)

    def backlash_correction_h(self):
        self.stage.backlash_correction('X')

    def backlash_correction_v(self):
        self.stage.backlash_correction('Y')


    def collect_pixel(self, pixel_num, k, j, i):
        ccd_hw = self.detector
        ccd_dev = ccd_hw.ccd_dev

        width_px = ccd_dev.Nx_ro
        
        try:
            self.log.info("starting acq")
            ccd_dev.start_acquisition()

            while not self.interrupt_measurement_called:

                stat = ccd_hw.settings.ccd_status.read_from_hardware()
                
                if stat == 'IDLE':
                    # grab data
                    buffer_ = ccd_hw.get_acquired_data()


                    bg = ccd_hw.background
                    if bg is not None:
                        if bg.shape == buffer_.shape:
                            buffer_ = buffer_ - bg
                        else:
                            self.log.warning("Background not the correct shape {} != {}".format( self.buffer_.shape, bg.shape))
                    else:
                        self.log.warning( "No Background available, raw data shown")

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


    def run(self):
            '''Overwrite scan to implement backlash correction'''
            S = self.settings

            # Hardware
            # self.apd_counter_hc = self.app.hardware_components['apd_counter']
            # self.apd_count_rate = self.apd_counter_hc.apd_count_rate
            # self.stage = self.app.hardware_components['dummy_xy_stage']

            # Data File
            # H5

            # Compute data arrays
            self.compute_scan_arrays()

            self.initial_scan_setup_plotting = True

            # Fill display image with nan
            # this allows for pyqtgraph histogram to ignore unfilled data
            # pyqtgraph ImageItem also keeps unfilled data pixels transparent
            self.display_image_map = np.nan * np.zeros(self.scan_shape, dtype=float)

            while not self.interrupt_measurement_called:
                try:
                    # h5 data file setup
                    self.t0 = time.time()

                    if self.settings["save_h5"]:
                        self.h5_file = h5_io.h5_base_file(self.app, measurement=self)
                        self.h5_filename = self.h5_file.filename

                        self.h5_file.attrs["time_id"] = self.t0
                        H = self.h5_meas_group = h5_io.h5_create_measurement_group(
                            self, self.h5_file
                        )

                        # create h5 data arrays
                        H["h_array"] = self.h_array
                        H["v_array"] = self.v_array
                        H["range_extent"] = self.range_extent
                        H["corners"] = self.corners
                        H["imshow_extent"] = self.imshow_extent
                        H["scan_h_positions"] = self.scan_h_positions
                        H["scan_v_positions"] = self.scan_v_positions
                        H["scan_slow_move"] = self.scan_slow_move
                        H["scan_index_array"] = self.scan_index_array

                    # start scan
                    self.pixel_i = 0
                    self.current_scan_index = self.scan_index_array[0]

                    self.pixel_time = np.zeros(self.scan_shape, dtype=float)
                    if self.settings["save_h5"]:
                        self.pixel_time_h5 = H.create_dataset(
                            name="pixel_time", shape=self.scan_shape, dtype=float
                        )

                    self.pre_scan_setup()

                    self.move_position_start(
                        self.scan_h_positions[0], self.scan_v_positions[0]
                    )

                    self.backlash_correction_v() #backlash on slow axis is done only once

                    for self.pixel_i in range(self.Npixels):
                        if self.interrupt_measurement_called:
                            break

                        i = self.pixel_i

                        self.current_scan_index = self.scan_index_array[i]
                        kk, jj, ii = self.current_scan_index

                        h, v = self.scan_h_positions[i], self.scan_v_positions[i]

                        if self.pixel_i == 0:
                            dh = 0
                            dv = 0
                        else:
                            dh = self.scan_h_positions[i] - self.scan_h_positions[i - 1]
                            dv = self.scan_v_positions[i] - self.scan_v_positions[i - 1]

                        if self.scan_slow_move[i]:
                            if self.interrupt_measurement_called:
                                break
                            self.move_position_slow(h, v, dh, dv)

                            if ii==0:   # backlash correction on fast axis
                                print("backlash correction on fast axis")
                                time.sleep(0.1)  # wait for slow move to finish
                                self.backlash_correction_h()

                            if self.settings["save_h5"]:
                                self.h5_file.flush()  # flush data to file every slow move
                            # self.app.qtapp.ProcessEvents()
                            time.sleep(0.01)
                        else:
                            self.move_position_fast(h, v, dh, dv)

                        self.pos = (h, v)
                        # each pixel:
                        # acquire signal and save to data array
                        pixel_t0 = time.time()
                        self.pixel_time[kk, jj, ii] = pixel_t0
                        if self.settings["save_h5"]:
                            self.pixel_time_h5[kk, jj, ii] = pixel_t0
                        self.collect_pixel(self.pixel_i, kk, jj, ii)
                        self.set_progress(100.0 * self.pixel_i / (self.Npixels))
                except Exception as err:
                    self.last_err = err
                    self.log.error("Failed to Scan {}".format(repr(err)))
                    traceback.print_exc()
                    # raise(err)
                finally:
                    self.post_scan_cleanup()
                    if hasattr(self, "h5_file"):
                        print("h5_file", self.h5_file)
                        try:
                            self.h5_file.close()
                        except ValueError as err:
                            self.log.warning("failed to close h5_file: {}".format(err))
                    if not self.settings["continuous_scan"]:
                        break
            print(self.name, "done")