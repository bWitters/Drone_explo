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
    'radio://0/20/2M/1',
    'radio://0/20/2M/2',
    'radio://0/20/2M/4',

    #'radio://1/80/2M/5',
    #'radio://1/80/2M/6',

    'radio://0/60/2M/7',
    'radio://1/60/2M/10',


    'radio://1/100/2M/11',
    'radio://1/100/2M/12',
    'radio://1/100/2M/14',
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


# === LOGGING FILES ===

flight_log_dir: str | None = None

def wrapper_sync(queues, queue_etat_reel):
    asyncio.run(go(queues, queue_etat_reel))

async def go(queues, queue_etat_reel):
    global running
    context = LinkContext()
    cache = FileTocCache("./cache")
    running = True

    print(f"Connecting to {len(URIS)} Crazyflies...")

    cfs = await asyncio.gather(
        *[
            Crazyflie.connect_from_uri(context, uri, cache)
            for uri in URIS
        ]
    )

    print("Connected to Crazyflies")
    
    try:
        await asyncio.sleep(0.5)

        flight_tasks = [
            asyncio.create_task(fly_sequence(cfs[i], queues[i], queue_etat_reel[i]))
            for i in range(len(cfs))
        ]

        await asyncio.gather(*flight_tasks)

    finally:
        running = False

        print("Disconnecting...")

        await asyncio.gather(
            *[
                cf.disconnect()
                for cf in cfs
            ],
            return_exceptions=True,
        )

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

    platform = cf.platform()
    hlc = cf.high_level_commander()
    if cf.uri == 'radio://0/20/2M/1':
        pygame.init()
        pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Leader Control - AZER / U/P (W = EMERGENCY STOP)")
        clock = pygame.time.Clock()

    await platform.send_arming_request(do_arm=True)

    try:
        print("taking off...")
        await hlc.take_off(0.45, None, 3.0, None)
        await asyncio.sleep(3.0)
        
        while running:
            if cf.uri == 'radio://0/20/2M/1':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    running = False

            queue_etat_reel.put([True])
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

            await asyncio.sleep(0)
            if cf.uri == 'radio://0/20/2M/1':
                clock.tick(CTRL_FREQ)
    
    except Exception as e:
        print(f"[EMERGENCY] failed: {e}")
        await emergency_stop(cf)

    finally:
        print("Leader controlled landing.")
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