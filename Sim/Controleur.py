"""
Example script that allows a user to "push" the Crazyflie 2.x around
using your hands while it's hovering.

This examples uses the Flow and Multi-ranger decks to measure distances
in all directions and tries to keep away from anything that comes closer
than 0.2m by setting a velocity in the opposite direction.

The demo is ended by either pressing Ctrl-C or by holding your hand above the
Crazyflie.
"""
import logging
import sys
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger

class Controleur:
    def __init__(self,uri, agent):
        self.URI = uri
        self.agent = agent
        cflib.crtp.init_drivers(enable_debug_driver=False)
        self.cf = Crazyflie(rw_cache='./cache')
        print(self.URI)
        self.scf = SyncCrazyflie(self.URI, cf=self.cf)
        self.motion_commander = MotionCommander(self.scf)
        self.multi_ranger = Multiranger(self.scf)
        self.scf.cf.platform.send_arming_request(True)
        

        while self.scf.cf.is_connected() != True:
            print("waiting connection")
    
    @property
    def velocity_x(self):
        self.agent.move_drone[0]
    
    @property
    def velocity_y(self):
        self.agent.move_drone[1]

    @property
    def velocity_z(self):
        self.agent.move_drone[2]

    def run(self):
        self.motion_commander.start_linear_motion(
            self.velocity_x, self.velocity_y, self.velocity_z)

        time.sleep(0.1)