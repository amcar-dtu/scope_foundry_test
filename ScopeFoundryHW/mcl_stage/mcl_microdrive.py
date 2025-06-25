# Adapted from the original Scopefoundry Plugin for MCL NanoDrive
# Source: https://github.com/ScopeFoundry/HW_mcl_stage.git

from __future__ import division, print_function, absolute_import
import ctypes
from ctypes import c_int, c_byte, c_ubyte, c_short, c_double, cdll, pointer, byref
import time
import numpy as np
import threading


# tested with 64bit windows
madlib_path = r"C:\Program Files\Mad City Labs\MicroDrive\MicroDrive.dll"

print("loading DLL:", repr(madlib_path))

## Load DLL
madlib = cdll.LoadLibrary(madlib_path)

# set return types of certain function
# madlib.MCL_SingleReadN.restype = c_double
# madlib.MCL_MonitorN.restype = c_double

# madlib.MCL_GetCalibration.restype = c_double
#more...
MCL_ERROR_CODES = {
   0: "MCL_SUCCESS",
   -1: "MCL_GENERAL_ERROR",
    -2: "MCL_DEV_ERROR",
    -3: "MCL_DEV_NOT_ATTACHED",
    -4: "MCL_USAGE_ERROR",
    -5: "MCL_DEV_NOT_READY",
    -6: "MCL_ARGUMENT_ERROR",
    -7: "MCL_INVALID_AXIS",
    -8: "MCL_INVALID_HANDLE"
}

SLOW_STEP_PERIOD = 0.050  #units are seconds

STEP_SIZE = 0.095 # units are microns, this is the step size of the MCL MicroDrive

class MCLProductInformation(ctypes.Structure):
    _fields_ = [
        ("axis_bitmap",     c_byte),    #//bitmap of available axis
        ("ADC_resolution",  c_short), #//# of bits of resolution
        #("pad", c_byte),
        ("DAC_resolution",  c_short), #//# of bits of resolution
        ("Product_id",      c_short),   
        ("FirmwareVersion", c_short),
        ("FirmwareProfile", c_short),]
        
    _pack_ = 1 # important for field alignment
    
    def print_info(self):
        print("MCL Product Information")
        for fieldname, fieldtype in self._fields_:
            fieldval = self.__getattribute__(fieldname)
            print("\t", fieldname, "\t\t", fieldval, "\t\t", bin(fieldval))
        
        

class MCLMicroDrive(object):

    def __init__(self, debug=False):
        
        self.lock = threading.Lock()
        
        self.debug = debug
        
        self.MCL_ERROR_CODES = MCL_ERROR_CODES
        
        ver = c_short()
        rev = c_short()
        madlib.MCL_DLLVersion(byref(ver), byref(rev))
        if self.debug:
            print("MCL_DLLVersion", ver.value, rev.value)
            print("madlib.MCL_CorrectDriverVersion():", madlib.MCL_CorrectDriverVersion())
        if not madlib.MCL_CorrectDriverVersion():
            print("MCL_CorrectDriverVersion is False")
        
        handle = self._handle = madlib.MCL_InitHandle()
        assert handle > 0

        dev_attached = madlib.MCL_DeviceAttached(2000, handle)
        print("dev_attached", dev_attached)

        if self.debug: print("handle:", hex(handle))

        if not handle:
            print("MCLMicroDrive failed to grab device handle ", hex(handle))

        #self.prodinfo = MCLProductInformation()
        #madlib.MCL_GetProductInfo(byref(self.prodinfo), handle)
        #if self.debug: self.prodinfo.print_info()
        
        self.device_serial_number = madlib.MCL_GetSerialNumber(handle)
        if self.debug: print("MCL_GetSerialNumber", self.device_serial_number)


        #safety for it not to go to too big range, TODO: make adjustable in mcl_xy_stage.py
        self.min_xposition = -100 # minimum x position in microns
        self.min_yposition = -100 # minimum y position in microns
        self.max_xposition = 100 # maximum x position in microns
        self.max_yposition = 100 # maximum y position in microns

        self.num_axes = 0
    
        self.cal = dict()
        for axname, axnum, axbitmap in [('X', 1, 0b001), ('Y', 2, 0b010)]:
            axvalid = bool(not madlib.MCL_GetAxisInfo(bin(axbitmap), handle))
            if debug: print(axname, axnum, "axbitmap:", bin(axbitmap), "axvalid", axvalid)
            
            if not axvalid:
                if debug: print("No %s axis, skipping" % axname)
                continue
            
            self.num_axes += 1
            
            # cal = madlib.MCL_GetCalibration(axnum, handle)

            # setattr(self, 'cal_%s' % axname, cal)
            # self.cal[axnum] = cal
            # if debug: print("cal_%s: %g" % (axname, cal))
        
        self.set_max_speed(100)  # default speed for slow movement is 100 microns/second
        #self.get_pos()
        
        self.lock 

        self.velocity = 0.1905  # default velocity, found by trial and error, can be adjusted if needed
        if self.debug: print("default velocity:", self.velocity)

        #positions set to zero upon initialization
        self.x_pos = 0 
        self.y_pos = 0

    def set_max_speed(self, max_speed):
        '''
        Units are in microns/second
        '''
        self.max_speed = float(max_speed)
    
    def get_max_speed(self):
        return self.max_speed
    
    def set_pos_slow(self, x=None, y=None):
        '''
        x -> axis 1
        y -> axis 2
        '''
        
        x_start, y_start = self.get_pos()
        
        if x is not None:
            dx = x - x_start
        else:
            dx = 0
        if y is not None:            
            dy = y - y_start
        else:
            dy = 0
        
        # Compute the amount of time that will be needed to make the movement.
        dt = np.sqrt(dx**2 + dy**2)/self.max_speed
            
        # Assume dt is in ms; divide the movement into SLOW_STEP_PERIOD chunks
        steps = int( np.ceil(dt/SLOW_STEP_PERIOD))
        x_step = dx/steps
        y_step = dy/steps
        
        for i in range(1,steps+1):
            t1 = time.time()
            self.set_pos(x_start+i*x_step, y_start+i*y_step)
            t2 = time.time()
            
            if (t2-t1) < SLOW_STEP_PERIOD:
                time.sleep(SLOW_STEP_PERIOD - (t2-t1))
        
        # Update internal variables with current position
        self.get_pos()
        
        
    def __del__(self):
        self.close()
        
    def close(self):
        madlib.MCL_ReleaseHandle(self._handle)
        
    def move_rel(self, dx, dy):
        pass
        #TODO

    def set_pos(self, x=None, y=None):
        if x is not None:
            assert self.min_xposition <= x <= self.max_xposition
            self.set_pos_ax(x, 1)
        if y is not None:
            assert self.min_yposition <= y <= self.max_yposition
            self.set_pos_ax(y, 2)
        
        #madlib.MCL_DeviceAttached(200, self._handle)
        # MCL_DeviceAttached can be used as a simple wait function. In this case
        # it is being used to allow the nanopositioner to finish its motion before 
        # reading its position. (standard 200)
        #madlib.MCL_DeviceAttached(100, self._handle)
        
    def set_pos_ax(self, pos, axis):
        if self.debug: print("set_pos_ax ", pos, axis)
        assert 1 <= axis <= self.num_axes
        # assert 0 <= pos <= self.cal[axis]

        rel_steps = int( (pos - self.get_pos_ax(axis)) // STEP_SIZE )  # convert to relative steps, where STEP_SIZE is the step size in microns
        self.handle_err(madlib.MCL_MDMoveM(axis, c_double(self.velocity), rel_steps, self._handle))
        self.handle_err(madlib.MCL_MicroDriveWait(self._handle))

        # Update internal variables with current position
        if self.debug: print("set_pos_ax: setting pos to ", pos, " for axis ", axis, 'relative steps:', rel_steps)
        if axis == 1:
            self.x_pos = pos
        elif axis == 2:
            self.y_pos = pos

    def get_pos_ax(self, axis):
        if self.debug: print("get_pos_ax", axis)
        return self.x_pos if axis == 1 else self.y_pos
    
    def get_pos(self):
        self.x_pos = self.get_pos_ax(1)
        self.y_pos = self.get_pos_ax(2)
            
        return (self.x_pos, self.y_pos)
            
    
    def set_pos_ax_slow(self, pos, axis):
        if self.debug: print("set_pos_slow_ax ", pos, axis)
        assert 1 <= axis <= self.num_axes
        #assert 0 <= pos <= self.cal[axis]
        pos = np.clip(pos, 0, self.cal[axis])
        
        start = self.get_pos_ax(axis)
        
        dl = pos - start
        dt = abs(dl) / self.max_speed
        
        # Assume dt is in ms; divide the movement into SLOW_STEP_PERIOD chunks
        steps = int(np.ceil(dt/SLOW_STEP_PERIOD))
        l_step = dl/steps
        
        print("\t", steps, l_step, dl, dt, start)        
        
        for i in range(1,steps+1):
            t1 = time.time()         
            self.set_pos_ax(start+i*l_step, axis)
            t2 = time.time()
            
            if (t2-t1) < SLOW_STEP_PERIOD:
                time.sleep(SLOW_STEP_PERIOD - (t2-t1))
        # Update internal variables with current position
        self.get_pos()
        
    def handle_err(self, retcode):
        if retcode < 0:
            raise IOError(self.MCL_ERROR_CODES[retcode])
        return retcode
        
if __name__ == '__main__':
    print("MCL microdrive test")
    
    microdrive = MCLMicroDrive(debug=True)
    # print(microdrive.getCommandedPosition())
    #print microdrive.monitorN(0, 1)

    microdrive.set_pos(10, 0)
    
    #for x,y in [ (0,0), (10,10), (30,30), (50,50), (50,25), (50,0)]:
    """for x,y in [ (30,0), (30,10), (30,30), (30,50), (30,25), (30,0)]:
        print "moving to ", x,y
        microdrive.set_pos(x,y)
        x1,y1 = microdrive.get_pos()
        print "moved to ", x1, y1
        time.sleep(1)"""
    
    microdrive.close()
    
