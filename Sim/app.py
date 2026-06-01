import time
import argparse
import numpy as np
import math
import pybullet as p
from datetime import datetime
import csv

from gym_pybullet_drones.utils.enums import DroneModel, Physics
from VelocityAviary import VelocityAviary
from gym_pybullet_drones.utils.utils import sync, str2bool

from agents import Drones
import yaml


import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger

with open("Map/Multiple_corner/Multiple_corner.yaml") as stream: # TODO : Faire les centrages par rapport à la width du fichier de config plutot que pour une width de 1
    try:
        init_conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

DEFAULT_DRONES = DroneModel("cf2x")
DEFAULT_PHYSICS = Physics("pyb")
DEFAULT_GUI = True
DEFAULT_PLOT = True
DEFAULT_USER_DEBUG_GUI = True
DEFAULT_SIMULATION_FREQ_HZ = 60
DEFAULT_CONTROL_FREQ_HZ = 30
DEFAULT_OUTPUT_FOLDER = 'results'
NUM_DRONES = 6
#INIT_XYZ = np.array([[.0, (-init_conf["length"]/2) + 1 + .2*i, .1] for i in range(NUM_DRONES)])
INIT_XYZ = np.array([[.0, 0 -.4*i, 0.3] for i in range(NUM_DRONES)])
STOCKING_AREA = np.array([[0,.5],[0,-1],[-.4,.4]])
INIT_RPY = np.array([[.0, .0, .0] for _ in range(NUM_DRONES)])
RAY_LENGTH = 10
RAY_HIT_COLOR = [1, 0, 0]
RAY_MISS_COLOR = [0, 1, 0]
SHOW_LIDAR = False
print(INIT_XYZ)
URIS = [
    
]

def run(
        queue = None,
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
    
    # Vérifie qu'il y a assez d'URIS associé aux drones simulé
    if len(URIS) != NUM_DRONES and len(URIS) >= 1:
        print("Entrer plus d'URIS pour démarrer")
        return
    else:
        for i in range(NUM_DRONES):
            URIS.append(None)

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

    p.loadURDF("Map/Multiple_corner/Multiple_corner.urdf", useFixedBase=True, physicsClientId=PYB_CLIENT)

    ### Log files 

    files = []
    log_writers = []

    #### ID drones ####
    n = p.getNumBodies(physicsClientId=PYB_CLIENT)
    env_id_drones = {}
    for bid in range(n):
        info = p.getBodyInfo(bid, physicsClientId=PYB_CLIENT)
        pos = p.getBasePositionAndOrientation(bid, physicsClientId=PYB_CLIENT)
        if info[1] == b'cf2' :
            env_id_drones[bid] = {"env_position" : pos, "drone_id" : None}

    #### Run the simulation ####################################
    action = np.zeros((num_drones,5))
    START = time.time()
    running = 5000
    
    debut = time.time()
    rayLen = RAY_LENGTH
    rayHitColor = RAY_HIT_COLOR
    rayMissColor = RAY_MISS_COLOR
    show_lidar = SHOW_LIDAR
    numRays = 181
    drones = []
    for sim_steps in range(running):
        #### Step the simulation ###################################
        obs, reward, terminated, truncated, info = env.step(action)

        if sim_steps == 0: # Découverte des drones et leurs relations
            drones = []
            unique_id = 2
            for drone_i in range(num_drones):
                pos = env.pos[drone_i]
                for key, value in env_id_drones.items():
                    pos_compare = np.array([value["env_position"][0][0], value["env_position"][0][1], value["env_position"][0][2]])
                    truth = 0
                    for i in range(len(pos)):
                        if abs(pos[i] - pos_compare[i]) < 0.2:
                            truth+=1
                    if truth == 3:
                        env_id_drones[key]["drone_id"] = drone_i
                #### Log files

                
                
                if drone_i == 0:
                    drones.append(Drones(1,drones,env_id_drones,STOCKING_AREA,URIS[0]))
                    nom_fichier = f"Sim/logs/drone_velocity_1_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
                    files.append(open(nom_fichier,"w"))
                    log_writers.append(csv.writer(files[-1]))
                    log_writers[-1].writerow(["vx","vy","vz","v_yaw"])
                    files[-1].flush()
                else:
                    drones.append(Drones(unique_id,drones,env_id_drones,STOCKING_AREA,URIS[unique_id-1]))
                    nom_fichier = f"Sim/logs/drone_velocity_{unique_id}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
                    files.append(open(nom_fichier,"w"))
                    log_writers.append(csv.writer(files[-1]))
                    log_writers[-1].writerow(["vx","vy","vz","v_yaw"])
                    files[-1].flush()
                    unique_id +=1

                
                
            
            for i in range(unique_id-1):
                if NUM_DRONES>1:
                    if i == 0:
                        drones[i].neighboring_agent_list["F"] = drones[i+1]
                    elif i == unique_id-2:
                        drones[i].neighboring_agent_list["P"] = drones[i-1]
                    else:
                        drones[i].neighboring_agent_list["F"] = drones[i+1]
                        drones[i].neighboring_agent_list["P"] = drones[i-1]
                    #print(drones[i].neighboring_agent_list)



        p.removeAllUserDebugItems()


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
                mins_ray = [(math.inf,False),(math.inf,False),(math.inf,False),(math.inf,False)]
                for i in range(len(results)):
                    if i < 16 :
                        if results[i][2]*RAY_LENGTH < mins_ray[0][0]:
                            mins_ray[0] = (results[i][2]*RAY_LENGTH,results[i][0])
                    elif i < 32:
                        if results[i][2]*RAY_LENGTH < mins_ray[1][0]:
                            mins_ray[1] = (results[i][2]*RAY_LENGTH,results[i][0])
                    elif i < 48:
                        if results[i][2]*RAY_LENGTH < mins_ray[2][0]:              
                            mins_ray[2] = (results[i][2]*RAY_LENGTH,results[i][0])
                    elif i < 64:
                        if results[i][2]*RAY_LENGTH < mins_ray[3][0]:           
                            mins_ray[3] = (results[i][2]*RAY_LENGTH,results[i][0])

                drones[j].position = env.pos[j]
                drones[j].rpy = env.rpy[j]
                drones[j].step(mins_ray)
                vx_w, vy_w, vz_w, speed_frac, wz = drones[j].move_drone
                v_norm = math.sqrt(vx_w * vx_w + vy_w * vy_w + vz_w * vz_w)
                if v_norm < 1e-3:
                    # No translation; keep yaw rate
                    commande = [0.0, 0.0, 0.0, 0.0, float(wz), True]
                    queue.put(commande)
                    action[j, :] = commande
                else:
                    # Unit direction + speed fraction w.r.t. speed_limit
                    dir_x = vx_w / v_norm
                    dir_y = vy_w / v_norm
                    dir_z = vz_w / v_norm
                    speed_frac = min(1.0, v_norm / max(1e-3, 1.0))
                    commande = [dir_x, dir_y, dir_z, float(speed_frac), float(wz), True]
                    action[j, :] = commande
                    if queue != None:
                        queue.put(commande)
                
                
                
                for key in env_id_drones.keys():
                    if env_id_drones[key]["drone_id"] == j:
                        base_velocity = p.getBaseVelocity(key, physicsClientId=PYB_CLIENT)
                        print(f"Current drone velocity : {base_velocity[0]} \nYaw velocity : {base_velocity[1][2]}")
                        action_to_log = [base_velocity[0][0],base_velocity[0][1],base_velocity[0][2],base_velocity[1][2]]
                        log_writers[j].writerow(action_to_log)
                        files[j].flush()
                
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