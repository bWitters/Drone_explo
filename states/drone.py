import numpy as np
from sensors_analyzer_simple import SensorsAnalyzer
import math

class Drone():
    def __init__(self, follower=None, position=None, preceding=None, follower_id=None, preceding_id=None):
        self.is_leader = False
        self.is_follower = False
        self.is_reconfig_follower = False
        self.state_commands = None
        self.follower = follower
        self.follower_id = follower_id
        self.preceding_id = preceding_id
        self.preceding = preceding
        self.position = position
        self.message_received = []
        self.action = [0, 0, 0, float(0.1), 0]
        self.distance_max = 0.5
        self.distance_min = 0.2
        self.is_doing_something = False
        self.sensorsAnalyzer = SensorsAnalyzer()
        self.analyzed_data = []
        self.prev_angle_error = 0.0  # for derivative term
        self.yaw_rate_controller = {"Kp": 0.8, "Kd": 0.1}  # PD gains
    
    # def state_change(self, new_state):
    #     match new_state:
    #         case "Leader":
    #             self.is_leader = True
    #             self.state_commands = 

    def distance_drone_x(self, drone_x):
        return np.linalg.norm(np.array(self.position)-np.array(drone_x.position))

    def direction_drone_x(self, drone_x):
        return -np.array(self.position)+np.array(drone_x.position)

    def wait(self):
        #print("Waiting")
        return None
    
    # def get_closer(self):
    #     print("getting closer")

    # def centering(self):
    #     print("centering myself")
    
    # def turn_around(self):
    #     print("turning around")
    
    def follow_the_branch(self, gap_analysis, gap_sel, nb_gap):
        """
        gap_analysis: list of angle errors (rad) to each gap
        gap_sel: index of selected gap to follow
        nb_gap: number of gaps detected
        """
        angle_error = gap_analysis[gap_sel]  # écart angulaire en radians
        
        # Proportional controller: convert angle error to angular velocity command
        # Tune Kp based on your drone dynamics (start with 0.5-1.0)
        Kp = self.yaw_rate_controller["Kp"]
        Kd = self.yaw_rate_controller["Kd"]
        
        # Calculate angular velocity command
        yaw_rate_cmd = np.clip(
            - Kp * angle_error + Kd * (angle_error - self.prev_angle_error),
            -2.0, 2.0
        )
        self.prev_angle_error = angle_error
        
        # Check if drone is roughly aligned (within ~10 degrees tolerance)
        angle_tolerance = 0.174  # ~10 degrees in radians
        
        if abs(angle_error) > angle_tolerance:
            self.action[1] = 0.1
            self.action[4] = yaw_rate_cmd
            print(f"Aligning to gap: angle_error={np.degrees(angle_error):.1f}°, yaw_rate={yaw_rate_cmd:.2f} rad/s")
        else:
            self.action[1] = 0.2
            self.action[4] = yaw_rate_cmd * 0.3
            print(f"Aligned! Moving forward. Fine correction: {yaw_rate_cmd*0.3:.2f} rad/s")

    
    # def rotation(self):
    #     print("rotating")
    
    # def new_follower(self, follower_drone):
    #     self.follower = follower_drone

    def msg_to_follower(self, type):
        match type:
            case "Come closer":
                self.follower.message_received.append("Come closer")
                #print(self.follower.message_received)
                #print("Come closer message sent")
            case "Reconfiguration":
                print("Reconfiguration message sent")
            case "Reconfiguration over":
                print("Reconfiguration over message sent")
    
    # def msg_to_preceding(self, type):
    #     match type:
    #         case "Reconfiguration":
    #             print("Reconfiguration message sent")

    