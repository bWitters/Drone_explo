import time
import argparse
import numpy as np
import csv
import math
import pybullet as p
import pybullet_data as pd
import traceback

from gym_pybullet_drones.utils.enums import DroneModel, Physics
from VelocityAviary import VelocityAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync, str2bool

from StateMachines.state_machine import DroneMachine

import yaml

with open("Map/Croix/croix.yaml") as stream:
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
NUM_DRONES = 1
#INIT_XYZ = np.array([[.0, (-init_conf["length"]/2) + 1 + .2*i, .1] for i in range(NUM_DRONES)])
INIT_XYZ = np.array([[.0, -1+ .5*i, .1] for i in range(NUM_DRONES)])
INIT_RPY = np.array([[.0, .0, .0] for _ in range(NUM_DRONES)])
NUM_RAYS = 65
RAY_LENGTH = 10
RAY_HIT_COLOR = [1, 0, 0]
RAY_MISS_COLOR = [0, 1, 0]
SHOW_LIDAR = False
print(INIT_XYZ)

def world_to_object_ref(points, yaw, center=None):
    """
    Rotate `points` (Nx3 or 3,) around Z by `yaw` (radians).
    If center is given, rotate around that 3-vector (world coordinates).
    Returns an array of same shape as input.
    """
    pts = np.asarray(points, dtype=float)
    single = (pts.ndim == 1)
    if single:
        pts = pts.reshape(1, 3)
    if center is not None:
        c = np.asarray(center, dtype=float).reshape(1, 3)
        pts = pts - c
    ca = math.cos(yaw)
    sa = math.sin(yaw)
    R = np.array([[ca, -sa, 0.0],
                  [sa,  ca, 0.0],
                  [0.0, 0.0, 1.0]])
    # rotate points
    rotated = pts.dot(R.T)
    if center is not None:
        rotated = rotated + c
    return rotated.reshape(3,) if single else rotated

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

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()

    p.loadURDF("Map/Croix/croix.urdf", useFixedBase=True, physicsClientId=PYB_CLIENT)

    #### Run the simulation ####################################
    """
    Boucle principale utilisant les State Machines pour le contrôle des drones.
    
    Au lieu d'utiliser des if/else imbriqués, chaque drone a une state machine
    qui gère automatiquement les transitions et les actions correspondantes.
    """
    action = np.zeros((num_drones,5))
    START = time.time()
    running = 2500
    
    debut = time.time()
    numRays = NUM_RAYS
    rayLen = RAY_LENGTH
    rayHitColor = RAY_HIT_COLOR
    rayMissColor = RAY_MISS_COLOR
    show_lidar = SHOW_LIDAR
    angles = np.linspace(-np.pi, np.pi, NUM_RAYS)
    index = np.where(angles == 0)[0][0]
    a = angles[index:]
    b = angles[:index]
    ray_angles = np.concatenate((a,b))
    drones = []
    drones.append(DroneMachine())
    for sim_steps in range(running):
        #### Step the simulation ###################################
        obs, reward, terminated, truncated, info = env.step(action)

        
        #### Exécuter le contrôle pour chaque drone (gérées par State Machines) ####
        for j in range(num_drones):
            try:
                ### LIDAR ###
                # Générer les rayons lidar
                rayFrom = []
                rayTo = []
                rayIds = []

                startOfRays = [-3/40*math.pi, math.pi/2-3/40*math.pi, math.pi-3/40*math.pi, 3*math.pi/2-3/40*math.pi]

                for starts in startOfRays:
                    for i in range(16):
                        rayFrom.append(env.pos[j])
                        rayTo.append([
                            rayFrom[i][0] + rayLen * math.sin((3/20*math.pi * float(i)/15) + starts),
                            rayFrom[i][1] + rayLen * math.cos((3/20*math.pi * float(i)/15) + starts),
                            rayFrom[i][2]
                        ])
                        rayIds.append(-1)
                    

                    
                    #### Debug Lidar ####
                    
                    # results = p.rayTestBatch(rayFrom, rayTo)

                    # # Affichage du lidar (optionnel)
                    # if show_lidar:
                    #     p.removeAllUserDebugItems()
                    #     for i in range(len(results)):
                    #         hitObjectUid = results[i][0]
                    #         if hitObjectUid < 0:
                    #             p.addUserDebugLine(rayFrom[i], rayTo[i], rayMissColor, replaceItemUniqueId=rayIds[i])
                    #         else:
                    #             hitPosition = results[i][3]
                    #             p.addUserDebugLine(rayFrom[i], hitPosition, rayHitColor, replaceItemUniqueId=rayIds[i])

                # Test lidar raycast
                dirs = np.asarray(rayTo) - np.asarray(rayFrom)
                dirs_rot = world_to_object_ref(dirs, env.rpy[j][2], center=None)  # rotate vector around origin
                rayTo_rot = np.asarray(rayFrom) + dirs_rot
                results = p.rayTestBatch(rayFrom, rayTo)

                # Affichage du lidar (optionnel)
                if show_lidar:
                    p.removeAllUserDebugItems()
                    for i in range(len(results)):
                        hitObjectUid = results[i][0]
                        if hitObjectUid < 0:
                            p.addUserDebugLine(rayFrom[i], rayTo[i], rayMissColor, replaceItemUniqueId=rayIds[i])
                        else:
                            hitPosition = results[i][3]
                            p.addUserDebugLine(rayFrom[i], hitPosition, rayHitColor, replaceItemUniqueId=rayIds[i])

                # Extraire les distances lidar depuis les résultats
                lidar_data = [results[i][2]*RAY_LENGTH for i in range(len(results))]  # Distance hit or max_distance
                
                mins_ray = [math.inf,math.inf,math.inf,math.inf]
                for i in range(len(results)):
                    if i < 16 :
                        if results[i][2]*RAY_LENGTH < mins_ray[0]:
                            mins_ray[0] = results[i][2]*RAY_LENGTH
                    elif i < 32:
                        if results[i][2]*RAY_LENGTH < mins_ray[1]:
                            mins_ray[1] = results[i][2]*RAY_LENGTH
                    elif i < 48:
                        if results[i][2]*RAY_LENGTH < mins_ray[2]:
                            mins_ray[2] = results[i][2]*RAY_LENGTH
                    elif i < 64:
                        if results[i][2]*RAY_LENGTH < mins_ray[3]:
                            mins_ray[3] = results[i][2]*RAY_LENGTH
                    
                
                drones[j].position = env.pos[j]
                drones[j].process_lidar(mins_ray)
                drones[j].execute()
                vx_w, vy_w, vz_w, speed_frac, wz = drones[j].action
                v_norm = math.sqrt(vx_w * vx_w + vy_w * vy_w + vz_w * vz_w)
                if v_norm < 1e-6:
                    # No translation; keep yaw rate
                    action[j, :] = [0.0, 0.0, 0.0, 0.0, float(wz)]
                else:
                    # Unit direction + speed fraction w.r.t. speed_limit
                    dir_x = vx_w / v_norm
                    dir_y = vy_w / v_norm
                    dir_z = vz_w / v_norm
                    speed_frac = min(1.0, v_norm / max(1e-6, 1.0))
                    action[j, :] = [dir_x, dir_y, dir_z, float(speed_frac), float(wz)]
                
            except Exception as e:
                print(f"Erreur drone n°{j}: {e}")
                import traceback
                traceback.print_exc()
                break        

        #### Sync the simulation ###################################
        if gui:
            pass
            sync(sim_steps, START, env.CTRL_TIMESTEP)

    fin = time.time()
    print(f"Total duration = {fin-debut}")
    input("Press enter to continue...")
    #### Close the environment #################################
    env.close()

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