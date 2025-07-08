'''
Created on Jul 27, 2014

@author: Edward Barnard
'''
from __future__ import absolute_import, print_function, division
from ScopeFoundry import HardwareComponent
try:
    from .mcl_microdrive import MCLMicroDrive
except Exception as err:
    print("Cannot load required modules for MclXYStage:", err)
from qtpy import QtCore
import time


class MclXYStageHW(HardwareComponent):
    
    def setup(self):
        self.name = 'mcl_xy_stage'

        
        # Created logged quantities
        lq_params = dict(  dtype=float, ro=True,
                           initial = -1,
                           spinbox_decimals=3,
                           vmin=-1e3,
                           vmax=1e3,
                           si = False,
                           unit='um')
        self.x_position = self.add_logged_quantity("x_position", **lq_params)
        self.y_position = self.add_logged_quantity("y_position", **lq_params)       
        
        lq_params = dict(  dtype=float, ro=False,
                           initial = -1,
                           spinbox_decimals=3,
                           vmin=-1e3,
                           vmax=1e3,
                           unit='um')
        self.x_target = self.add_logged_quantity("x_target", **lq_params)
        self.y_target = self.add_logged_quantity("y_target", **lq_params)       
        
        
        lq_params = dict(unit="um", dtype=float, ro=True, initial=300, 
                         spinbox_decimals=3,
                         si=False)
        self.x_max = self.add_logged_quantity("x_max", **lq_params)
        self.y_max = self.add_logged_quantity("y_max", **lq_params)

        lq_params = dict(dtype=str, choices=[("X","X"), ("Y","Y")])
        self.h_axis = self.add_logged_quantity("h_axis", initial="X", **lq_params)
        self.v_axis = self.add_logged_quantity("v_axis", initial="Y", **lq_params)
        
        self.MCL_AXIS_ID = dict(X = 2, Y = 1)
        self.xy_axis_map = self.add_logged_quantity('xy_axis_map', dtype=str, initial='21')
        self.xy_axis_map.updated_value.connect(self.on_update_xy_axis_map)
        
        
        self.move_speed = self.add_logged_quantity(name='move_speed',
                                                             initial = 100.0,
                                                             unit = "um/s",
                                                             vmin = 1e-4,
                                                             vmax = 1000,
                                                             si = False,
                                                             dtype=float)        
        
        # TODO: check if this is needed
        # # connect logged quantities together
        # self.x_target.updated_value[()].connect(self.read_pos)
        # self.y_target.updated_value[()].connect(self.read_pos)
        
        # Actions
        self.add_operation('GOTO_Center_XY', self.go_to_center_xy)
        self.add_operation('Set_Current_Position_As_Zero', self.set_current_position_as_zero)
        
    def on_update_xy_axis_map(self):
        print("on_update_xy_axis_map")
        map_str = self.xy_axis_map.val
        self.MCL_AXIS_ID['X'] = int(map_str[0])
        self.MCL_AXIS_ID['Y'] = int(map_str[1])
    
    def move_pos_slow(self, x=None,y=None):
        # move slowly to new position
        new_pos = [None, None]
        new_pos[self.MCL_AXIS_ID['X']-1] = x
        new_pos[self.MCL_AXIS_ID['Y']-1] = y
        if self.microdrive.num_axes < 2:
            new_pos[1] = None
        self.microdrive.set_pos_slow(*new_pos)

        if x is not None: 
            self.settings.x_target.update_value(x, update_hardware=False)
        if y is not None:
            self.settings.y_target.update_value(y, update_hardware=False)

        self.read_pos()
        
    def move_pos_fast(self, x=None,y=None):
        new_pos = [None, None]
        new_pos[self.MCL_AXIS_ID['X']-1] = x
        new_pos[self.MCL_AXIS_ID['Y']-1] = y
        if self.microdrive.num_axes < 2:
            new_pos[1] = None
        self.microdrive.set_pos(*new_pos)
        

    
    @QtCore.Slot()
    def read_pos(self):
        if self.settings['debug_mode']: self.log.debug("read_pos")
        if self.settings['connected']:
            self.x_position.read_from_hardware()
            self.y_position.read_from_hardware()
        
    def connect(self):
        if self.debug_mode.val: print("connecting to mcl_xy_stage")
        
        # Open connection to hardware
        self.microdrive = MCLMicroDrive(debug=self.debug_mode.val)
        
        # connect logged quantities
        self.x_target.hardware_set_func  = \
            lambda x: self.microdrive.set_pos_ax(x, self.MCL_AXIS_ID["X"])
        self.y_target.hardware_set_func  = \
            lambda y: self.microdrive.set_pos_ax(y, self.MCL_AXIS_ID["Y"])

        self.x_position.hardware_read_func = \
            lambda: self.microdrive.get_pos_ax(int(self.MCL_AXIS_ID["X"]))
        self.y_position.hardware_read_func = \
            lambda: self.microdrive.get_pos_ax(int(self.MCL_AXIS_ID["Y"]))


        ##TODO: add set functions, note the microdrive does not have a set_min_position_x/y function
        self.x_max.hardware_read_func = self.microdrive.get_max_position_x
        self.y_max.hardware_read_func = self.microdrive.get_max_position_y
        ##TODO: at some point one wants to have also min functions (not present in original code)
        # self.x_min.hardware_read_func = self.microdrive.get_min_position_x
        # self.y_min.hardware_read_func = self.microdrive.get_min_position_y

        self.move_speed.hardware_read_func = self.microdrive.get_max_speed
        self.move_speed.hardware_set_func =  self.microdrive.set_max_speed
        self.move_speed.write_to_hardware()
        
        self.read_from_hardware()
        

        self.settings.x_target.change_min_max(self.microdrive.min_xposition, self.microdrive.max_xposition)
        self.settings.y_target.change_min_max(self.microdrive.min_yposition, self.microdrive.max_yposition)
        
        self.settings.x_target.update_value(self.settings['x_position'], update_hardware=False)
        self.settings.y_target.update_value(self.settings['y_position'], update_hardware=False)

        

    def disconnect(self):
        #disconnect logged quantities from hardware
        self.settings.disconnect_all_from_hardware()

        #disconnect hardware
        if hasattr(self, 'microdrive'):
            self.microdrive.close()
            # clean up hardware object
            del self.microdrive
        
    @property
    def v_axis_id(self):
        return self.MCL_AXIS_ID[self.v_axis.val]
    
    @property
    def h_axis_id(self):
        return self.MCL_AXIS_ID[self.h_axis.val]
    
    @property
    def x_axis_id(self):
        return self.MCL_AXIS_ID["X"]
    
    @property
    def y_axis_id(self):
        return self.MCL_AXIS_ID["Y"]
    
    
    def go_to_center_xy(self):
        self.settings['x_target'] = self.settings['x_max']*0.0
        self.settings['y_target'] = self.settings['y_max']*0.0

    def set_current_position_as_zero(self):
        """
        Set the current position as zero.
        """
        
        # Update the logged quantities
        self.microdrive.x_pos = 0
        self.microdrive.y_pos = 0

    def backlash_correction(self, axis, steps=300):
        """
        Perform backlash correction for the specified axis.
        The correction assumes first a negative step, then a positive step of 30 micron be taken
        """
        if axis == 'X':
            self.microdrive.move_relative_steps(-steps, self.MCL_AXIS_ID['X']) #TODO change function steps
            self.microdrive.move_relative_steps(steps, self.MCL_AXIS_ID['X'])
        elif axis == 'Y':
            self.microdrive.move_relative_steps(-steps, self.MCL_AXIS_ID['Y'])
            self.microdrive.move_relative_steps(steps, self.MCL_AXIS_ID['Y'])
        else:
            raise ValueError("Invalid axis specified for backlash correction.")
        
        
    def threaded_update(self):
        self.x_position.read_from_hardware()
        self.y_position.read_from_hardware()
        time.sleep(0.1)
