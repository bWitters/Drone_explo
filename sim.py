import time
import argparse
import numpy as np
import csv
import math
import pybullet as p
import pybullet_data as pd
import traceback
from transforms3d.quaternions import rotate_vector, qconjugate, mat2quat, qmult
from transforms3d.utils import normalized_vector

from gym_pybullet_drones.utils.enums import DroneModel, Physics
from VelocityAviary import VelocityAviary
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl
from gym_pybullet_drones.utils.Logger import Logger
from gym_pybullet_drones.utils.utils import sync, str2bool

from state_machine import DroneMachine

import yaml

with open("croix.yaml") as stream:
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
INIT_XYZ = np.array([[.0, -0.5+ .5*i, .1] for i in range(NUM_DRONES)])
INIT_RPY = np.array([[.0, .0, .0] for _ in range(NUM_DRONES)])
NUM_RAYS = 181
RAY_LENGTH = 1.5
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
    # ctrl = CTBRControl(drone_model=drone)

    #### Obtain the PyBullet Client ID from the environment ####
    PYB_CLIENT = env.getPyBulletClient()
    #p.loadURDF("corridor.urdf", useFixedBase=True, physicsClientId=PYB_CLIENT)
    p.loadURDF("croix.urdf", useFixedBase=True, physicsClientId=PYB_CLIENT)

    n = p.getNumBodies(physicsClientId=PYB_CLIENT)
    env_id_drones = {}
    for bid in range(n):
        info = p.getBodyInfo(bid, physicsClientId=PYB_CLIENT)
        pos = p.getBasePositionAndOrientation(bid, physicsClientId=PYB_CLIENT)
        if info[1] == b'cf2' :
            env_id_drones[bid] = {"env_position" : pos, "drone_id" : None}

    #### Initialize the logger #################################
    # logger = Logger(logging_freq_hz=control_freq_hz,
    #                 num_drones=NUM_DRONES,
    #                 output_folder=output_folder,
    #                 )

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
    for sim_steps in range(running):
        #### Step the simulation ###################################
        obs, reward, terminated, truncated, info = env.step(action)

        if sim_steps == 0: # Découverte des drones et leurs relations
            drones = []
            for drone_i in range(num_drones):
                pos = env.pos[drone_i]
                for key, value in env_id_drones.items():
                    pos_compare = np.array([value["env_position"][0][0], value["env_position"][0][1], value["env_position"][0][2]])
                    truth = 0
                    for i in range(len(pos)):
                        if pos[i] == pos_compare[i]:
                            truth+=1
                    if truth == 3:
                        value["drone_id"] = drone_i
                if drone_i == num_drones-1:
                    drones.append(Leader(position = INIT_XYZ[drone_i]))
                    drones[-1].is_leader = True
                else:
                    drones.append(Follower(position = INIT_XYZ[drone_i]))
                    drones[-1].is_follower = True

            for drone_i in range(num_drones):
                rayFrom = []
                rayTo = []
                rayIds = []

                for rays in range(numRays):
                    rayFrom.append(env.pos[drone_i])
                    rayTo.append([
                        rayFrom[rays][0] + rayLen * math.sin(2. * math.pi * float(rays) / numRays),
                        rayFrom[rays][1] + rayLen * math.cos(2. * math.pi * float(rays) / numRays), rayFrom[rays][2]
                    ])
                    rayIds.append(-1)

                results = p.rayTestBatch(rayFrom, rayTo)
                p.removeAllUserDebugItems()
                for i in range(numRays):
                    hitObjectUid = results[i][0]

                    if (hitObjectUid < 0):
                        hitPosition = [0, 0, 0]
                        p.addUserDebugLine(rayFrom[i], rayTo[i], rayMissColor, replaceItemUniqueId=rayIds[i])
                    else:
                        hitPosition = results[i][3]
                        p.addUserDebugLine(rayFrom[i], hitPosition, rayHitColor, replaceItemUniqueId=rayIds[i])
                        
                ids = [(t[0],t[3]) for t in results]

                for id in ids:
                    if id[0] in env_id_drones.keys():
                        if id[1][1] > env.pos[drone_i][1]:
                            drones[drone_i].preceding = drones[env_id_drones[id[0]]["drone_id"]]
                            drones[drone_i].preceding_id = id[0]
                        elif id[1][1] < env.pos[drone_i][1]:
                            drones[drone_i].follower = drones[env_id_drones[id[0]]["drone_id"]]
                            drones[drone_i].follower_id = id[0]

        p.removeAllUserDebugItems()

        #### Exécuter le contrôle pour chaque drone (gérées par State Machines) ####
        for j in range(num_drones):
            try:
                # Générer les rayons lidar
                rayFrom = []
                rayTo = []
                rayIds = []

                for i in range(numRays):
                    rayFrom.append(env.pos[j])
                    rayTo.append([
                        rayFrom[i][0] + rayLen * math.sin(2. * math.pi * float(i) / numRays),
                        rayFrom[i][1] + rayLen * math.cos(2. * math.pi * float(i) / numRays), rayFrom[i][2]
                    ])
                    rayIds.append(-1)

                # Test lidar raycast
                dirs = np.asarray(rayTo) - np.asarray(rayFrom)
                dirs_rot = world_to_object_ref(dirs, env.rpy[j][2], center=None)  # rotate vector around origin
                rayTo_rot = np.asarray(rayFrom) + dirs_rot
                results = p.rayTestBatch(rayFrom, rayTo_rot.tolist())

                # Affichage du lidar (optionnel)
                if show_lidar:
                    p.removeAllUserDebugItems()
                    for i in range(0, numRays, numRays//4):
                        hitObjectUid = results[i][0]
                        if hitObjectUid < 0:
                            p.addUserDebugLine(rayFrom[i], rayTo[i], rayMissColor, replaceItemUniqueId=rayIds[i])
                        else:
                            hitPosition = results[i][3]
                            p.addUserDebugLine(rayFrom[i], hitPosition, rayHitColor, replaceItemUniqueId=rayIds[i])

                # Extraire les distances lidar depuis les résultats
                lidar_data = [results[i][2]*RAY_LENGTH for i in range(numRays)]  # Distance hit or max_distance
                
                # Mettre à jour la position du drone
                drones[j].position = env.pos[j]
                
                # =========== APPELER LE STATE MACHINE DU DRONE ===========
                # C'est ICI que toute la logique de contrôle se fait maintenant !
                # Plus de if/else imbriqués, tout est géré par la state machine.
                if drones[j].is_leader:
                    drones[j].run(lidar_data, ray_angles, sim_steps)
                elif drones[j].is_follower:
                    drones[j].run(lidar_data, ray_angles, sim_steps)
                
                print(world_to_object_ref(drones[j].action[0:3], env.rpy[j][2]))
                new_action = world_to_object_ref(drones[j].action[0:3], env.rpy[j][2])
                action_to_send = [new_action[0], new_action[1], new_action[2], drones[j].action[3], drones[j].action[4]]
                vx_w, vy_w, vz_w, speed_frac, wz = action_to_send
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
            sync(sim_steps, START, env.CTRL_TIMESTEP)

    fin = time.time()
    print(f"Total duration = {fin-debut}")
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