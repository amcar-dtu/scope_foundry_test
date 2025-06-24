# fancy_app.py
import sys

from ScopeFoundry import BaseMicroscopeApp


class FancyApp(BaseMicroscopeApp):

    name = "fancy app"

    def setup(self):
        """
        Runs once during app initialization. This is where you add hardware
        and measurements to the app.
        """
        # Add hardware

        from ScopeFoundryHW.andor_camera import AndorCCDHW
        from ScopeFoundryHW.andor_spec import AndorShamrockSpecHW
        from ScopeFoundryHW.mcl_stage import MclXYZStageHW
        from ScopeFoundryHW.mcl_stage import MclXYStageHW

        self.add_hardware(AndorCCDHW(self))
        self.add_hardware(AndorShamrockSpecHW(self))
        self.add_hardware(MclXYZStageHW(self))
        self.add_hardware(MclXYStageHW(self))

        # Add measurement

        from measurements.andor_ccd_readout import AndorCCDReadoutMeasure
        from measurements.example_2d_slowscan_measure import Example2DSlowScanMeasure

        self.add_measurement(AndorCCDReadoutMeasure)
        self.add_measurement(Example2DSlowScanMeasure(self))


if __name__ == "__main__":
    app = FancyApp(sys.argv)
    # app.settings_load_ini("default_settings.ini")
    sys.exit(app.exec_())
