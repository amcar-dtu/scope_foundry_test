# fancy_app.py
import sys

from ScopeFoundry import BaseMicroscopeApp

class FancyApp(BaseMicroscopeApp):

    name = "fancy app"

    def setup(self):


        from ScopeFoundryHW.random_number_gen import NumberGenHw
        self.add_hardware(NumberGenHw(self))

        # from number_gen_readout_simple import NumberGenReadoutSimple
        # self.add_measurement(NumberGenReadoutSimple(self))

        # from number_gen_readout import NumberGenReadout
        # self.add_measurement(NumberGenReadout(self))

        from number_gen_readout_qt_creator import NumberGenReadoutQtCreator
        self.add_measurement(NumberGenReadoutQtCreator(self))



if __name__ == "__main__":
    app = FancyApp(sys.argv)
    # app.settings_load_ini("default_settings.ini")
    sys.exit(app.exec_())
