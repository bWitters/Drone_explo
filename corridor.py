import time
import argparse
import numpy as np
import csv
import pybullet as p
import pybullet_data as pd
from transforms3d.quaternions import rotate_vector, qconjugate, mat2quat, qmult
from transforms3d.utils import normalized_vector
#from states.drone import Drone

from gym_pybullet_drones.utils.enums import DroneModel, Physics
from VelocityAviary import VelocityAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync, str2bool

from states.leader import Leader
from states.follower import Follower

import yaml

with open("corridor.yaml") as stream:
    try:
        init_conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

DEFAULT_DRONES = DroneModel("cf2x")
DEFAULT_PHYSICS = Physics("pyb")
DEFAULT_GUI = True
DEFAULT_PLOT = True
DEFAULT_USER_DEBUG_GUI = True
DEFAULT_SIMULATION_FREQ_HZ = 500
DEFAULT_CONTROL_FREQ_HZ = 25
DEFAULT_OUTPUT_FOLDER = 'results'
NUM_DRONES = 5
INIT_XYZ = np.array([[.0, (-init_conf["length"]/2) + 1 + .5*i, .1] for i in range(NUM_DRONES)])
INIT_RPY = np.array([[.0, .0, .0] for _ in range(NUM_DRONES)])

print(INIT_XYZ)
input()
def run(
        drone=DEFAULT_DRONES,
        physics=DEFAULT_PHYSICS,
        gui=DEFAULT_GUI,
        plot=DEFAULT_PLOT,
        user_debug_gui=DEFAULT_USER_DEBUG_GUI,
        simulation_freq_hz=DEFAULT_SIMULATION_FREQ_HZ,
        control_freq_hz=DEFAULT_CONTROL_FREQ_HZ,
        num_drones=NUM_DRONES,
        output_folder=DEFAULT_OUTPUT_FOLDER,
        ):
    #### Create the environment with or without video capture ##
    env = VelocityAviary(drone_model=drone,
                        num_drones=num_drones,
                        initial_xyzs=INIT_XYZ,
                        initial_rpys=INIT_RPY,
                        physics=physics,
                        pyb_freq=simulation_freq_hz,
                        ctrl_freq=control_freq_hz,
                        gui=gui,
                        user_debug_gui=user_debug_gui
                        )
    # ctrl = CTBRControl(drone_model=drone)

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()
    p.loadURDF("corridor.urdf", useFixedBase=True, physicsClientId=PYB_CLIENT)
    drones = []
    for i in range(num_drones):
        if i == num_drones-1:
            drones.append(Leader(drones[i-1],position = INIT_XYZ[i], preceding=None))
            drones[i-1].preceding = drones[i]
        else:
            if i != 0:
                drones.append(Follower(drones[i-1],position = INIT_XYZ[i], preceding=None))
                drones[i-1].preceding = drones[i]
            else:
                drones.append(Follower(None,position = INIT_XYZ[i], preceding=None))

    #### Initialize the logger #################################
    # logger = Logger(logging_freq_hz=control_freq_hz,
    #                 num_drones=NUM_DRONES,
    #                 output_folder=output_folder,
    #                 )

    #### Run the simulation ####################################
    delta = 150 # 3s @ 25hz control loop 
    take_off_trajectory = [[0,0,1] for i in range(100)]
    action = np.zeros((num_drones,5))
    START = time.time()
    running = 1000
    skip = False
    takeoff = True
    for i in range(running):
        # t = i/env.ctrl_freq
        #### Step the simulation ###################################
        obs, reward, terminated, truncated, info = env.step(action)
        print("Etape ", i)
        print(num_drones, "drones chargé")

        if takeoff:
            for j in range(num_drones):
                    print("Drone n°",j)
                    try:
                        action[j, :] = [take_off_trajectory[i][0],take_off_trajectory[i][1],take_off_trajectory[i][2], float(0.1),0]
                        drones[j].position = env.pos[j]
                        print(drones[j].position)
                    except:
                        print("Erreur, boucle stoppé")
                        break
            if i == 99:
                takeoff = False
        else:
            for j in range(num_drones):
                print("Drone n°",j)
                try:
                    drones[j].run()
                    action[j, :] = drones[j].action
                    drones[j].position = env.pos[j]
                    print(drones[j].position)
                except:
                    print("Erreur, boucle stoppé")
                    break

        #### Log the simulation ####################################
        # for j in range(NUM_DRONES):
        #     logger.log(drone=j,
        #                 timestamp=i/env.CTRL_FREQ,
        #                 state=obs[j]
        #                 )

        #### Printout ##############################################
        # env.render()

        

        #### Sync the simulation ###################################
        if gui:
            pass
            sync(i, START, env.CTRL_TIMESTEP)

    input("Press enter to continue...")
    #### Close the environment #################################
    env.close()

    #### Save the simulation results ###########################
    # logger.save()
    # logger.save_as_csv("beta") # Optional CSV save

    # #### Plot the simulation results ###########################
    # if plot:
    #     logger.plot()


if __name__ == "__main__":
    #### Define and parse (optional) arguments for the script ##
    parser = argparse.ArgumentParser(description='Test flight script using SITL Betaflight')
    parser.add_argument('--drone',              default=DEFAULT_DRONES,     type=DroneModel,    help='Drone model (default: BETA)', metavar='', choices=DroneModel)
    parser.add_argument('--physics',            default=DEFAULT_PHYSICS,      type=Physics,       help='Physics updates (default: PYB)', metavar='', choices=Physics)
    parser.add_argument('--gui',                default=DEFAULT_GUI,       type=str2bool,      help='Whether to use PyBullet GUI (default: True)', metavar='')
    parser.add_argument('--plot',               default=DEFAULT_PLOT,       type=str2bool,      help='Whether to plot the simulation results (default: True)', metavar='')
    parser.add_argument('--user_debug_gui',     default=DEFAULT_USER_DEBUG_GUI,      type=str2bool,      help='Whether to add debug lines and parameters to the GUI (default: False)', metavar='')
    parser.add_argument('--simulation_freq_hz', default=DEFAULT_SIMULATION_FREQ_HZ,        type=int,           help='Simulation frequency in Hz (default: 500)', metavar='')
    parser.add_argument('--control_freq_hz',    default=DEFAULT_CONTROL_FREQ_HZ,         type=int,           help='Control frequency in Hz (default: 25)', metavar='')
    parser.add_argument('--num_drones',         default=NUM_DRONES, type=int,           help='Number of drones in the simulation', metavar='')
    parser.add_argument('--output_folder',      default=DEFAULT_OUTPUT_FOLDER, type=str,           help='Folder where to save logs (default: "results")', metavar='')
    ARGS = parser.parse_args()

    run(**vars(ARGS))