import asyncio
import numpy as np
from datetime import datetime
import os
import csv
import pygame

from cflib2 import Crazyflie, LinkContext
from cflib2.toc_cache import FileTocCache

# === CONFIGURATION ===

URIS = [
    # 'radio://0/20/2M/1',
    # 'radio://0/20/2M/2',
    'radio://0/20/2M/4',

    # 'radio://0/60/2M/10',
    # 'radio://0/60/2M/7',

    # 'radio://1/80/2M/6',

    # 'radio://1/100/2M/11',
    # 'radio://1/100/2M/12',
    'radio://0/100/2M/14',
]

STATE_LOG_PERIOD_MS = 100
CTRL_FREQ = 30

FRONT = 'range.front'
BACK = 'range.back'
LEFT = 'range.left'
RIGHT = 'range.right'
UP = 'range.up'
DOWN = 'range.zrange'
# === GLOBAL STATE ===

pos_dict: dict[str, np.ndarray] = {}
filtered_pos_dict: dict[str, np.ndarray] = {}
vel_dict: dict[str, np.ndarray] = {}
ranger_dict: dict[str, np.ndarray] = {}
pm_state_last: dict[str, int] = {}
cmd_dict: dict[str, np.ndarray] = {}
e_stops: dict[str, bool] = {}

running = True

log_files = {}
log_writers = {}

ranger_file = {}
ranger_writers = {}


# === LOGGING FILES ===

flight_log_dir: str | None = None


def init_csv_logs() -> None:
    global flight_log_dir

    # Un dossier par vol
    flight_id = datetime.now().strftime("logs/Controleur/Controleur_%m-%d_%Hh%Mm%S%f")
    flight_log_dir = flight_id
    os.makedirs(flight_log_dir, exist_ok=True)

    print(f"[LOG] Flight logs directory: {flight_log_dir}")

    for uri in URIS:
        split_uri = uri.split("/")
        filename = flight_log_dir + "/" + f"{split_uri[-1]}.csv"
        filename_ranger = flight_log_dir + "/" + "ranger_" + f"{split_uri[-1]}.csv"

        outfile = open(filename, "w", newline="")
        outfile_ranger = open(filename_ranger, "w", newline="")
        writer = csv.writer(outfile)
        writer_ranger = csv.writer(outfile_ranger)

        writer.writerow([
            "t",
            "x", "y", "z",
            "vx", "vy", "vz",
            "Vx_cmd", "Vy_cmd", "Vz_cmd"
        ])

        writer_ranger.writerow([
            "timestamp", "Ranger_left", "Ranger_front", "Ranger_right", "Ranger_back"
        ])

        log_files[uri] = outfile
        log_writers[uri] = writer
        ranger_file[uri] = outfile_ranger
        ranger_writers[uri] = writer_ranger
        cmd_dict[uri] = np.array([0.0, 0.0, 0.0])
        e_stops[uri] = False
        pm_state_last[uri] = -1

        outfile.flush()
        outfile_ranger.flush()


def close_csv_logs() -> None:
    for f in log_files.values():
        f.close()

def wrapper_sync(queues, queues_etat_reel, queues_lidar):
    asyncio.run(go(queues, queues_etat_reel,queues_lidar))

async def go(queues, queues_etat_reel,queues_lidar):
    global running
    context = LinkContext()
    cache = FileTocCache("./cache")
    running = True

    init_csv_logs()

    print(f"Connecting to {len(URIS)} Crazyflies...")

    cfs = await asyncio.gather(
        *[
            Crazyflie.connect_from_uri(context, uri, cache)
            for uri in URIS
        ]
    )

    print("Connected to Crazyflies")
    if queues_lidar != None:
        log_tasks = [
                asyncio.create_task(start_states_log(cfs[i],queues_lidar[i]))
                for i in range(len(cfs))
            ]
    else:
        log_tasks = [
                asyncio.create_task(start_states_log(cfs[i],None))
                for i in range(len(cfs))
            ]
    
    try:
        await asyncio.sleep(0.5)

        flight_tasks = [
            asyncio.create_task(fly_sequence(cfs[i], queues[i], queues_etat_reel[i]))
            for i in range(len(cfs))
        ]

        await asyncio.gather(*flight_tasks)

    finally:
        running = False
        for task in log_tasks:
            task.cancel()

        await asyncio.gather(*log_tasks, return_exceptions=True)

        print("Disconnecting...")

        await asyncio.gather(
            *[
                cf.disconnect()
                for cf in cfs
            ],
            return_exceptions=True,
        )
        
        close_csv_logs()
        print("Done")
        
async def fly_sequence(cf: Crazyflie, queue, queue_etat_reel):
    global running

    try:
        await fly(cf, queue, queue_etat_reel)
        print("Sequence ended")

    except asyncio.CancelledError:
        raise

    except Exception as e:
        print(f"Error in fly_sequence for {cf.uri}: {e}")
        e_stops[cf.uri] = True
        await emergency_stop(cf)

async def fly(cf: Crazyflie, queue, queue_etat_reel) -> None:
    global running

    print(f"Voici la queue : {queue_etat_reel}")

    platform = cf.platform()
    hlc = cf.high_level_commander()
    if cf.uri == 'radio://0/100/2M/14':
        pygame.init()
        pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Leader Control - AZER / U/P (W = EMERGENCY STOP)")
        clock = pygame.time.Clock()

    await platform.send_arming_request(do_arm=True)
    y = 0
    if cf.uri == 'radio://0/100/2M/14':
        y = 0.5

    try:
        print("taking off...")
        await hlc.take_off(0.70, None, 3.0, None)
        await asyncio.sleep(3.0)

        await hlc.go_to(
                    float(y),
                    float(0),
                    float(0.70),
                    0,
                    2,
                    False,
                    False,
                    0
                )
        await asyncio.sleep(2)

        await hlc.go_to(
                    float(y),
                    float(0),
                    float(0.45),
                    0,
                    1,
                    False,
                    False,
                    0
                )
        await asyncio.sleep(1)

        print_running = True
        while running:
            if print_running:
                print("running")
            if cf.uri == 'radio://0/100/2M/14':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    running = False

            queue_etat_reel.put([True])
            if print_running:
                print(f"Voici la queue apres le lancement : {queue_etat_reel}")
                print(queue_etat_reel.empty())
                print_running = False
            if not queue.empty():
                commandes = queue.get()
                x_world, y_world, z, yaw = commandes[0], commandes[1], commandes[2], commandes[3]

                await hlc.go_to(
                    float(x_world),
                    float(y_world),
                    float(z),
                    yaw,
                    1/30,
                    False,
                    False,
                    0
                )

                print(f"Ranger data {ranger_dict[cf.uri]}")

            await asyncio.sleep(0)
            if cf.uri == 'radio://0/20/2M/1':
                clock.tick(CTRL_FREQ)
    
    except Exception as e:
        print(f"[EMERGENCY] failed: {e}")
        await emergency_stop(cf)

    finally:
        print(f"Drone : {cf.uri}, controlled landing.")
        await land_drone_velocity(cf, cf.uri)

async def emergency_stop(cf: Crazyflie) -> None:
    global running

    try:
        print(f"[EMERGENCY] Stopping and disarming {cf.uri}")
    except Exception:
        pass

    commander = cf.commander()
    platform = cf.platform()

    try:
        await commander.send_stop_setpoint()
    except Exception as e:
        print(f"[EMERGENCY] send_stop_setpoint failed: {e}")

    try:
        await commander.send_notify_setpoint_stop(0)
    except Exception as e:
        print(f"[EMERGENCY] send_notify_setpoint_stop failed: {e}")

    try:
        await platform.send_arming_request(do_arm=False)
    except Exception as e:
        print(f"[EMERGENCY] send_arming_request(False) failed: {e}")

async def land_drone_velocity(cf: Crazyflie, uri: str) -> None:
    commander = cf.commander()

    print(f"[LAND] Controlled velocity landing for {uri}")

    landing_time = 3.0
    dt = 1/CTRL_FREQ

    pos = pos_dict.get(uri, np.array([0.0, 0.0, 0.45]))
    z = max(float(pos[2]), 0.05)

    vz = -z / landing_time
    steps = int(landing_time / dt)

    for _ in range(steps):
        await commander.send_setpoint_velocity_world(0.0, 0.0, vz, 0.0)
        await asyncio.sleep(dt)

    await commander.send_stop_setpoint()
    await commander.send_notify_setpoint_stop(0)

    try:
        await cf.platform().send_arming_request(do_arm=False)
    except Exception as e:
        print(f"[LAND] disarm failed for {uri}: {e}")


# === CRAZYFLIE LOG STREAM ===

async def read_state_log(uri: str, stream) -> None:
    while running and not e_stops.get(uri, False):
        sample = await stream.next()
        data = sample.data
        timestamp = sample.timestamp

        pos_dict[uri] = np.array(
            [
                data["stateEstimate.x"],
                data["stateEstimate.y"],
                data["stateEstimate.z"],
            ],
            dtype=float,
        )

        vel_dict[uri] = np.array(
            [
                data["stateEstimate.vx"],
                data["stateEstimate.vy"],
                data["stateEstimate.vz"],
            ],
            dtype=float,
        )

        cmd = cmd_dict.get(uri, np.array([0.0, 0.0, 0.0]))
        row = [timestamp, *pos_dict[uri], *vel_dict[uri], *cmd]
        log_writers[uri].writerow(row)
        log_files[uri].flush()

async def read_ranger_log(uri: str, stream,queue_lidar) -> None:
    while running and not e_stops.get(uri, False):
        sample = await stream.next()
        data = sample.data
        timestamp = sample.timestamp

        ranger_dict[uri] = np.array(
            [
                data[LEFT]/1000,
                data[FRONT]/1000,
                data[RIGHT]/1000,
                data[BACK]/1000,
            ],
            dtype=float,
        )

        row = [timestamp, *ranger_dict[uri]]
        if queue_lidar != None:
            queue_lidar.put([timestamp, *ranger_dict[uri]])
        ranger_writers[uri].writerow(row)
        ranger_file[uri].flush()

async def read_status_log(uri: str, stream) -> None:
    global running

    while running and not e_stops.get(uri, False):
        sample = await stream.next()
        data = sample.data

        pm_state = int(data["pm.state"])
        last = pm_state_last.get(uri)
        pm_state_last[uri] = pm_state


def convert_log_to_distance(data):
        if data >= 8000:
            return None
        else:
            return data / 1000.0
        
async def start_states_log(cf: Crazyflie, queue_lidar) -> None:
    uri = cf.uri
    log = cf.log()

    # Bloc 1 : 6 variables max
    state_block = await log.create_block()
    for var in [
        "stateEstimate.x",
        "stateEstimate.y",
        "stateEstimate.z",
        "stateEstimate.vx",
        "stateEstimate.vy",
        "stateEstimate.vz",
    ]:
        await state_block.add_variable(var)

    ranger_block = await log.create_block()
    await ranger_block.add_variable(FRONT)
    await ranger_block.add_variable(BACK)
    await ranger_block.add_variable(LEFT)
    await ranger_block.add_variable(RIGHT)

    status_block = await log.create_block()
    for var in [
        "stateEstimate.yaw",
        "pm.state",
    ]:
        await status_block.add_variable(var)

    ranger_stream = await ranger_block.start(STATE_LOG_PERIOD_MS)
    state_stream = await state_block.start(STATE_LOG_PERIOD_MS)
    status_stream = await status_block.start(STATE_LOG_PERIOD_MS)

    print(f"[{uri}] Logging started with split blocks")

    try:
        await asyncio.gather(
            read_state_log(uri, state_stream),
            read_ranger_log(uri,ranger_stream,queue_lidar),
            read_status_log(uri, status_stream),
        )
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print(f"[{uri}] log task error: {e}")
    finally:
        for stream in [state_stream, status_stream, ranger_stream]:
            try:
                await stream.stop()
            except Exception:
                pass