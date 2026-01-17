import os
import numpy as np
from gymnasium import spaces

from gym_pybullet_drones.envs.BaseAviary import BaseAviary
from gym_pybullet_drones.utils.enums import DroneModel, Physics
from gym_pybullet_drones.control.DSLPIDControl import DSLPIDControl


class VelocityAviary(BaseAviary):
    """Multi-drone environment class for high-level planning with velocity control in WORLD frame."""

    ################################################################################

    def __init__(self,
                 drone_model: DroneModel = DroneModel.CF2X,
                 num_drones: int = 1,
                 neighbourhood_radius: float = np.inf,
                 initial_xyzs=None,
                 initial_rpys=None,
                 physics: Physics = Physics.PYB,
                 pyb_freq: int = 240,
                 ctrl_freq: int = 240,
                 gui=False,
                 record=False,
                 obstacles=False,
                 user_debug_gui=True,
                 output_folder='results'
                 ):
        """Initialization of an aviary environment for high-level planning."""
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
        if drone_model in [DroneModel.CF2X, DroneModel.CF2P]:
            self.ctrl = [DSLPIDControl(drone_model=DroneModel.CF2X) for _ in range(num_drones)]
        super().__init__(drone_model=drone_model,
                         num_drones=num_drones,
                         neighbourhood_radius=neighbourhood_radius,
                         initial_xyzs=initial_xyzs,
                         initial_rpys=initial_rpys,
                         physics=physics,
                         pyb_freq=pyb_freq,
                         ctrl_freq=ctrl_freq,
                         gui=gui,
                         record=record,
                         obstacles=obstacles,
                         user_debug_gui=user_debug_gui,
                         output_folder=output_folder
                         )
        #### Limit on the maximum target speed (m/s) in WORLD frame ####
        self.SPEED_LIMIT = 1.0

    ################################################################################

    def _actionSpace(self):
        # [dir_x, dir_y, dir_z, speed_frac, yaw_rate]
        act_lower_bound = np.array([[-1, -1, -1, 0, -2.0] for _ in range(self.NUM_DRONES)], dtype=np.float32)
        act_upper_bound = np.array([[1,  1,  1, 1,  2.0] for _ in range(self.NUM_DRONES)], dtype=np.float32)
        return spaces.Box(low=act_lower_bound, high=act_upper_bound, dtype=np.float32)

    ################################################################################

    def _observationSpace(self):
        #### Observation vector ### X Y Z Q1 Q2 Q3 Q4 R P Y VX VY VZ WX WY WZ P0 P1 P2 P3
        obs_lower_bound = np.array([[-np.inf, -np.inf, 0.,
                                     -1., -1., -1., -1.,
                                     -np.pi, -np.pi, -np.pi,
                                     -np.inf, -np.inf, -np.inf,
                                     -np.inf, -np.inf, -np.inf,
                                     0., 0., 0., 0.] for _ in range(self.NUM_DRONES)])
        obs_upper_bound = np.array([[np.inf,  np.inf,  np.inf,
                                     1.,  1.,  1.,  1.,
                                     np.pi,  np.pi,  np.pi,
                                     np.inf,  np.inf,  np.inf,
                                     np.inf,  np.inf,  np.inf,
                                     self.MAX_RPM, self.MAX_RPM, self.MAX_RPM, self.MAX_RPM]
                                    for _ in range(self.NUM_DRONES)])
        return spaces.Box(low=obs_lower_bound, high=obs_upper_bound, dtype=np.float32)

    ################################################################################

    def _computeObs(self):
        return np.array([self._getDroneStateVector(i) for i in range(self.NUM_DRONES)])

    ################################################################################

    def _preprocessAction(self, action):
        """Map high-level velocity command in WORLD frame to motor RPMs."""
        rpm = np.zeros((self.NUM_DRONES, 4))
        for k in range(action.shape[0]):
            state = self._getDroneStateVector(k)
            a = action[k, :]

            dir_xyz    = a[0:3]                  # direction in WORLD frame
            speed_frac = float(np.clip(a[3], 0.0, 1.0))  #norm des vitesses
            yaw_rate   = float(a[4]) if a.shape[0] >= 5 else 0.0  # rad/s

            if np.linalg.norm(dir_xyz) > 1e-6:
                v_unit = dir_xyz / np.linalg.norm(dir_xyz)
            else:
                v_unit = np.zeros(3, dtype=np.float32)

            target_vel = self.SPEED_LIMIT * speed_frac * v_unit  # WORLD frame

            temp, _, _ = self.ctrl[k].computeControl(
                control_timestep=self.CTRL_TIMESTEP,
                cur_pos=state[0:3],
                cur_quat=state[3:7],
                cur_vel=state[10:13],
                cur_ang_vel=state[13:16],
                target_pos=state[0:3],                           # no position control
                target_rpy=np.array([0, 0, state[9]]),           # keep current yaw angle
                target_vel=target_vel,
                target_rpy_rates=np.array([0.0, 0.0, yaw_rate])  # yaw rate command
            )
            rpm[k, :] = temp
        return rpm

    ################################################################################

    def _computeReward(self):
        return -1

    def _computeTerminated(self):
        return False

    def _computeTruncated(self):
        return False

    def _computeInfo(self):
        return {"answer": 42}
