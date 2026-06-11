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
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils.multiranger import Multiranger
from cflib.crazyflie.swarm import CachedCfFactory, Swarm
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.high_level_commander import HighLevelCommander 

from datetime import datetime
import csv
import os

# === CONFIGURATION ===

URIS = [
    'radio://0/80/2M/1',
    'radio://0/80/2M/2'
]

MAX_X, MIN_X = 1, -1
MAX_Y, MIN_Y= 1, -1
MAX_Z, MIN_Z = 1.5, 0
ZONE = [MIN_X, MAX_X, MIN_Y, MAX_Y, MIN_Z, MAX_Z]

# === GLOBAL STATE ===

pos_dict = {}
vel_dict = {}
running = True
leader_yaw = 0


# For auto landing on pm.state == 3
pm_state_last = {}   # uri -> last pm.state known
state_last = {}
e_stops = {}

def go(queues, queue_etat_reel,queues_position_simu):
    cflib.crtp.init_drivers()

    ### Log files
    directory_name = f"logs/Controleur/Controleur_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    # === LOGGING ===
    log_files = {}
    log_writers = {}
    cmd_dict = {}

    STATE_LOG_PERIOD_MS = 30

    for uri in URIS:
        split_uri = uri.split("/")
        outfile = open(f"{directory_name}/logs_cf_{split_uri[-1]}_{datetime.now().strftime("%Hh%Mm%S")}.csv", "w", newline='')
        writer = csv.writer(outfile)

        writer.writerow(["t", "x", "y", "z", "vx", "vy", "vz", "Vx_cmd", "Vy_cmd", "Vz_cmd"])

        log_files[uri] = outfile
        log_writers[uri] = writer
        cmd_dict[uri] = np.array([0.0, 0.0, 0.0])

    def log_callback_state(uri, timestamp, data, logconf):
        # Update positions/speeds  

        pos_dict[uri] = np.array([data[f'stateEstimate.{axis}'] for axis in 'xyz'])
        vel_dict[uri] = np.array([data[f'stateEstimate.v{axis}'] for axis in 'xyz'])

        cmd = cmd_dict.get(uri, np.array([0.0, 0.0, 0.0]))

        row = [
            timestamp,
            *pos_dict[uri],
            *vel_dict[uri],
            *cmd
        ]
        log_writers[uri].writerow(row)
        log_files[uri].flush()


        # if uri == URI_LEADER:
        #     z = pos_dict[uri][2]
        #     if z > 0.15 and not takeoff_evt.is_set():
        #         print(f"Leader à décollé (z={z:.2f}) -> followers autorisés")
        #         takeoff_evt.set()

    # def log_callback(uri, timestamp, data, logconf):
    #     global running, leader_yaw

    #     # Detection pm.state == 3 -> controlled landing of the drone concerned
    #     pm_state = int(data['pm.state'])

    #     last = pm_state_last.get(uri, None)
    #     pm_state_last[uri] = pm_state

        # if uri == URI_LEADER:
        #     leader_yaw = float(data['stateEstimate.yaw'])
            
        #     if pm_state == 3 and last != 3:
        #         running = False


    def start_states_log(scf):
        log_conf_state = LogConfig(name='States', period_in_ms=STATE_LOG_PERIOD_MS)
        print("call1", flush=True)
        for var in ['x', 'y', 'z']:
            log_conf_state.add_variable(f'stateEstimate.{var}', 'float')
            log_conf_state.add_variable(f'stateEstimate.v{var}', 'float')
        uri = scf.cf.link_uri

        scf.cf.log.add_config(log_conf_state)
        log_conf_state.data_received_cb.add_callback(
            lambda ts, data, logconf: log_callback_state(uri, ts, data, logconf)
        )
        log_conf_state.start()

        # log_conf = LogConfig(name='callback', period_in_ms=STATE_LOG_PERIOD_MS)

        # log_conf.add_variable(f'stateEstimate.yaw', 'float')

        # log_conf.add_variable('pm.state', 'uint8_t')

        # uri = scf.cf.link_uri

        # scf.cf.log.add_config(log_conf)
        # log_conf.data_received_cb.add_callback(
        #     lambda ts, data, logconf: log_callback(uri, ts, data, logconf)
        # )
        # log_conf.start()

    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(URIS, factory=factory) as swarm:
        my_args = {
            URIS[0]: [queues[0], directory_name, queue_etat_reel[0],queues_position_simu[0]],
            URIS[1]: [queues[1], directory_name, queue_etat_reel[1],queues_position_simu[1]],
        }

        swarm.parallel_safe(start_states_log)
        print("Logging started")
        
        swarm.parallel_safe(fly_sequence, args_dict=my_args)
        
def fly_sequence(scf, queue, directory_name, queue_etat_reel,queue_position_simu):
    keep_flying = True

    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    print("Controler running")
    uri = scf.cf.link_uri
    split_uri = uri.split("/")
    nom_fichier = f"{directory_name}/drone_control_{split_uri[-1]}.csv"
    file = open(nom_fichier,"w")
    log_writer = csv.writer(file)
    log_writer.writerow(["vx","vy","vz","speed_frac","v_yaw","keep_flying"])
    file.flush()
    nom_fichier = f"{directory_name}/drone_logs_{split_uri[-1]}.csv"
    file_log = open(nom_fichier,"w")
    log_writer_log = csv.writer(file_log)
    log_writer_log.writerow(["current_pos_x","current_pos_y","current_pos_z","commande_x","commande_y","commande_z","n_direction"])
    file_log.flush()


    keep_flying = True
    time.sleep(1.0)

    while queue_position_simu.empty():
        print("waiting for sim to send positions")
    init_pos = queue_position_simu.get()
    initialised = False

    with MotionCommander(scf) as motion_commander:
        with Multiranger(scf) as multi_ranger:
            compte = 0
            while not initialised:
                commande_init = {"x":.0,"y":.0,"z":.0}
                for direction in "xyz":
                    if abs(pos_dict[scf.cf.link_uri][direction] - init_pos[0]) > 0.1:
                        commande_init[direction] = 0.1
                    else:
                        compte +=1
                    if compte == 3:
                        initialised = True
                motion_commander.start_linear_motion(commande_init["x"],commande_init["y"],commande_init["z"])
                log_writer_log.writerow([pos_dict["x"],pos_dict["y"],pos_dict["z"],commande_init["x"],commande_init["y"],commande_init["z"],compte])
                file_log.flush()
            while keep_flying:
                queue_etat_reel.put([True])
                if not queue.empty():
                    commandes = queue.get()
                    print(f"Consommateur : Liste reçue pour {scf.cf.link_uri}: {commandes}")
                    keep_flying = commandes[5]
                    motion_commander.start_linear_motion(commandes[0],commandes[1],commandes[2],commandes[4])
                    log_writer.writerow(commandes)
                    file.flush()

                    
        

        print('Demo terminated!')

    
