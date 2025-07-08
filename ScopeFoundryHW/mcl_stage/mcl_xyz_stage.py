'''
Created on Jul 27, 2014

@author: Edward Barnard
'''
from __future__ import absolute_import, print_function, division
from ScopeFoundry import HardwareComponent
try:
    from .mcl_nanodrive import MCLNanoDrive
except Exception as err:
    print("Cannot load required modules for MclXYZStage:", err)
from qtpy import QtCore
import time


class MclXYZStageHW(HardwareComponent):
    
    def setup(self):
        self.name = 'mcl_z_stage'

        
        # Created logged quantities
        lq_params = dict(  dtype=float, ro=True,
                           initial = -1,
                           spinbox_decimals=3,
                           vmin=-1,
                           vmax=300,
                           si = False,
                           unit='um')    
        self.z_position = self.add_logged_quantity("z_position", **lq_params)
        
        lq_params = dict(  dtype=float, ro=False,
                           initial = -1,
                           spinbox_decimals=3,
                           vmin=-1,
                           vmax=300,
                           unit='um')  
        self.z_target = self.add_logged_quantity("z_target", **lq_params)        
        
        
        lq_params = dict(unit="um", dtype=float, ro=True, initial=300, 
                         spinbox_decimals=3,
                         si=False)
        self.z_max = self.add_logged_quantity("z_max", **lq_params)

        lq_params = dict(dtype=str, choices=[("Z","Z")])
        
        self.MCL_AXIS_ID = dict(Z = 3)
        self.xyz_axis_map = self.add_logged_quantity('xyz_axis_map', dtype=str, initial='213')
        self.xyz_axis_map.updated_value.connect(self.on_update_xyz_axis_map)
        
        
        self.move_speed = self.add_logged_quantity(name='move_speed',
                                                             initial = 100.0,
                                                             unit = "um/s",
                                                             vmin = 1e-4,
                                                             vmax = 1000,
                                                             si = False,
                                                             dtype=float)        
        
        # TODO: check if this is needed
        # # connect logged quantities together
        # self.z_target.updated_value[()].connect(self.read_pos)
        
        # Actions
        # self.add_operation('GOTO_Center_XY', self.go_to_center_xy)
        
    def on_update_xyz_axis_map(self):
        print("on_update_xyz_axis_map")
        map_str = self.xyz_axis_map.val
        self.MCL_AXIS_ID['Z'] = int(map_str[2])
    
    def move_pos_slow(self, x=None,y=None,z=None):
        # move slowly to new position
        new_pos = [None]
        new_pos[self.MCL_AXIS_ID['Z']-1] = z
        # if self.nanodrive.num_axes < 3:
        #     new_pos[2] = None
        self.nanodrive.set_pos_slow(*new_pos)

        if z is not None:
            self.settings.z_target.update_value(z, update_hardware=False)

        self.read_pos()
        
    def move_pos_fast(self,  x=None,y=None,z=None):
        new_pos = [None]
        new_pos[self.MCL_AXIS_ID['Z']-1] = z
        if self.nanodrive.num_axes < 3:
            new_pos[2] = None
        self.nanodrive.set_pos(*new_pos)
        

    
    @QtCore.Slot()
    def read_pos(self):
        if self.settings['debug_mode']: self.log.debug("read_pos")
        if self.settings['connected']:
            self.x_position.read_from_hardware()
            self.y_position.read_from_hardware()
            if self.nanodrive.num_axes > 2:
                self.z_position.read_from_hardware()
        
    def connect(self):
        if self.debug_mode.val: print("connecting to mcl_xyz_stage")
        
        # Open connection to hardware
        self.nanodrive = MCLNanoDrive(debug=self.debug_mode.val)
        
        self.z_target.change_readonly(False)
        self.z_target.hardware_set_func  = \
            lambda z: self.nanodrive.set_pos_ax_slow(z, self.MCL_AXIS_ID["Z"])

        self.z_position.hardware_read_func = \
            lambda: self.nanodrive.get_pos_ax(self.MCL_AXIS_ID["Z"])
            
            
        # if self.nanodrive.num_axes > 2:
        self.z_max.hardware_read_func = lambda: self.nanodrive.cal[self.MCL_AXIS_ID["Z"]]
        
        self.move_speed.hardware_read_func = self.nanodrive.get_max_speed
        self.move_speed.hardware_set_func =  self.nanodrive.set_max_speed
        self.move_speed.write_to_hardware()
        
        self.read_from_hardware()
        
        self.settings.z_target.change_min_max(0.1, self.z_max.value-0.1)
        self.settings.z_target.update_value(self.settings['z_position'], update_hardware=False)

        

    def disconnect(self):
        #disconnect logged quantities from hardware
        self.settings.disconnect_all_from_hardware()

        #disconnect hardware
        if hasattr(self, 'nanodrive'):
            self.nanodrive.close()
            # clean up hardware object
            del self.nanodrive
        
    
    @property
    def z_axis_id(self):
        return self.MCL_AXIS_ID["Z"]
     
        
    def threaded_update(self):
        self.z_position.read_from_hardware()
        time.sleep(0.1)    