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

def run(queue):
    keep_flying = True
    URI = ""
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    cf = Crazyflie(rw_cache='./cache')
    with SyncCrazyflie(URI, cf=cf) as scf:
        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        with MotionCommander as motion_commander:
            with Multiranger(scf) as multi_ranger:

                while keep_flying:
                    if not queue.empty():
                        commandes = queue.get()
                        print("Consommateur : Liste reçue :", commandes)
                        keep_flying = queue[5]
                        motion_commander.start_linear_motion(
                            queue[0], queue[1], queue[2])
            

            print('Demo terminated!')