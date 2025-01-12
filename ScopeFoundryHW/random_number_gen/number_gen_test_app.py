'''
Created on Jan 11, 2025

@author: Benedikt Ursprung
'''

from ScopeFoundry.base_app import BaseMicroscopeApp


class TestApp(BaseMicroscopeApp):

    name = "number_gen_test_app"

    def setup(self):
        
        from ScopeFoundryHW.random_number_gen import NumberGenHw, NumberGenReadout
        self.add_hardware(NumberGenHw(self))
        self.add_measurement(NumberGenReadout(self))



if __name__ == '__main__':
    import sys
    app = TestApp(sys.argv)
    sys.exit(app.exec_())
