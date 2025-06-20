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

        self.add_hardware(AndorCCDHW(self))
        self.add_hardware(AndorShamrockSpecHW(self))
        self.add_hardware(MclXYZStageHW(self))

        # Add measurement

        from measurements.andor_ccd_readout import AndorCCDReadoutMeasure

        self.add_measurement(AndorCCDReadoutMeasure)


if __name__ == "__main__":
    app = FancyApp(sys.argv)
    # app.settings_load_ini("default_settings.ini")
    sys.exit(app.exec_())
