import time

import numpy as np

class NumberGenDev:

    """
    This is the low level dummy device object.
    Typically when instantiated it will connect to the real-world
    Methods allow for device read and write functions
    """
        
    def __init__(self, port=None, debug=False):
        """We would connect to the real-world here
        if this were a real device
        """
        self.port = port
        self.debug = debug
        print("NumberGenDev: Connecting to port", port)
        self.write_amp(1)

    
    def write_amp(self, amplitude):
        """
        A write function to change the device's amplitude
        normally this would talk to the real-world to change
        a setting on the device
        """
        self._amplitude = amplitude
            
    def read_rand_num(self):
        """
        Read function to access a Random number generator. 
        Acts as our scientific device picking up a lot of noise.
        """
        rand_data = np.random.ranf() * self._amplitude
        return rand_data
    
    def read_sine_wave(self):
        """
        Read function to access a sine wave.
        Acts like the device is generating a 1Hz sine wave
        with an amplitude set by write_amp
        """
        sine_data = np.sin(time.time()) * self._amplitude
        return sine_data

if __name__ == '__main__':
    print('start')
    dev = NumberGenDev(port="COM1", debug=True)
    print(dev.read_sine_wave())
    print('done')
