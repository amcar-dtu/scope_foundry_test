from ScopeFoundry.hardware import HardwareComponent


class NumberGenHw(HardwareComponent):

    name = "number_gen"

    def setup(self):
        s = self.settings
        s.New("port", str, initial="COM1", description="has no effect for this dummy device")
        s.New("amplitude", float, initial=1.0, ro=False)
        s.New("rand_data", float, initial=0, ro=True)
        s.New("sine_data", float, initial=0, ro=True)

    def connect(self):
        from .number_gen_dev import NumberGenDev

        s = self.settings
        self.dev = NumberGenDev(s["port"], debug=s["debug_mode"])

        # Connect settings to hardware:
        s.get_lq("amplitude").connect_to_hardware(write_func=self.dev.write_amp)
        s.get_lq("rand_data").connect_to_hardware(read_func=self.dev.read_rand_num)
        s.get_lq("sine_data").connect_to_hardware(read_func=self.dev.read_sine_wave)

        # Take an initial sample of the data.
        self.read_from_hardware()

    def disconnect(self):
        if not hasattr(self, "dev"):
            return

        self.settings.disconnect_all_from_hardware()
        del self.dev

    # if you want to continuously update settings implement *run* method
    # def run(self):
    #     self.settings.property_x.read_from_hardware()
    #     time.sleep(0.1)
