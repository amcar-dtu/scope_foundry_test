# fancy_app.py
import sys

from ScopeFoundry import BaseMicroscopeApp


class FancyApp(BaseMicroscopeApp):

    name = "fancy app"

    def setup(self):

        from ScopeFoundryHW.random_number_gen import NumberGenHW, NumberGenReadout

        self.add_hardware(NumberGenHW(self))
        # self.add_measurement(NumberGenReadout(self))

        # from number_gen_readout_simple import NumberGenReadoutSimple
        # self.add_measurement(NumberGenReadoutSimple(self))

        from number_gen_readout_qt_creator import NumberGenReadoutQtCreator
        self.add_measurement(NumberGenReadoutQtCreator(self))
        ## spatial scanning example

        # from ScopeFoundry.sequencer import Sequencer

        # self.add_measurement(Sequencer)

        # from ScopeFoundryHW.simulon_xyz_stage import SimulonXYZStageHW
        # from ScopeFoundryHW.bsinc_noiser200 import Noiser200HW

        # self.add_hardware(SimulonXYZStageHW(self))
        # self.add_hardware(Noiser200HW(self))

        # # Define the actuators for the scans
        # # Each actuator can be defined with a tuple of settings paths. The following formats are supported:
        # # 1. (name, position_path, target_position_path)
        # # 2. (name, target_position_path) -> position_path=target_position_path
        # # 3. (position_path, target_position_path) -> name=position_path
        # # 4. (target_position_path) -> name=target_position_path=position_path
        # actuators = (
        #     (
        #         "x_position",
        #         "hw/simulon_xyz_stage/x_position",
        #         "hw/simulon_xyz_stage/x_target_position",
        #     ),
        #     (
        #         "y_position",
        #         "hw/simulon_xyz_stage/y_position",
        #         "hw/simulon_xyz_stage/y_target_position",
        #     ),
        #     (
        #         "z_position",
        #         "hw/simulon_xyz_stage/z_position",
        #         "hw/simulon_xyz_stage/z_target_position",
        #     ),
        # )

        # from example_2d_slowscan_measure import Example2DSlowScanMeasure
        # from example_3d_slowscan_measure import Example3DSlowScanMeasure

        # self.add_measurement(Example2DSlowScanMeasure(self, actuators=actuators))
        # self.add_measurement(Example3DSlowScanMeasure(self, actuators=actuators))


if __name__ == "__main__":
    app = FancyApp(sys.argv)
    # app.settings_load_ini("default_settings.ini")
    sys.exit(app.exec_())
