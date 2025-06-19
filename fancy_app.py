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
        # from ScopeFoundryHW.random_number_gen import NumberGenHW

        # self.add_hardware(NumberGenHW(self))

        from ScopeFoundryHW.andor_camera import AndorCCDHW

        self.add_hardware(AndorCCDHW(self))

        # Add measurement
        # from measurements.number_gen_readout_simple import NumberGenReadoutSimple

        # self.add_measurement(NumberGenReadoutSimple(self))

        # from measurements.number_gen_readout_qt_creator import NumberGenReadoutQtCreator

        # self.add_measurement(NumberGenReadoutQtCreator(self))

        # from measurements.number_gen_readout_extendable_dataset import (
        #     NumberGenReadoutExtendableDataset,
        # )

        # self.add_measurement(NumberGenReadoutExtendableDataset(self))

        from measurements.andor_ccd_readout import AndorCCDReadoutMeasure

        self.add_measurement(AndorCCDReadoutMeasure)


if __name__ == "__main__":
    app = FancyApp(sys.argv)
    # app.settings_load_ini("default_settings.ini")
    sys.exit(app.exec_())
