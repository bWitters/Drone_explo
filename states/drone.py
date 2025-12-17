import numpy as np
from sensors_analyzer_simple import SensorsAnalyzer
import math

class Drone():
    def __init__(self, follower, position, preceding): # sensors, 
        self.is_leader = False
        self.is_follower = False
        self.is_reconfig_follower = False
        self.state_commands = None
        self.follower = follower
        self.preceding = preceding
        self.position = position
        self.message_received = []
        self.action = [0, 0, 0, float(0.1), 0]
        print(self.action)
        # self.lidar = sensors["lidar"]
        # self.neighbour_vision = sensors["vision"]
        self.distance_max = 0.5
        self.distance_min = 0.2
        self.is_doing_something = False
        self.sensorsAnalyzer = SensorsAnalyzer()
        self.analyzed_data = []
    
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
        print("Waiting")
    
    # def get_closer(self):
    #     print("getting closer")

    # def centering(self):
    #     print("centering myself")
    
    # def turn_around(self):
    #     print("turning around")
    
    def follow_the_branch(self, gap_analysis, gap_sel):
        # # Pour le moment c'est aller tout droit
        # self.action = [0, 0.5, 0, float(0.1), 0]
        self.action[1] = 0.2 # Forward

        if gap_analysis[gap_sel] > 0:
            self.action[4] = (abs(gap_analysis[gap_sel])/math.pi)*0.7 # Rotation
            self.action[0] = 0.1 # Lateral

        if gap_analysis[gap_sel] < 0:
            self.action[4] = -(abs(gap_analysis[gap_sel])/math.pi)*0.7
            self.action[0] = -0.1

        else:
            pass
        
        print(self.action)
    # def rotation(self):
    #     print("rotating")
    
    # def new_follower(self, follower_drone):
    #     self.follower = follower_drone

    def msg_to_follower(self, type):
        match type:
            case "Come closer":
                self.follower.message_received.append("Come closer")
                print(self.follower.message_received)
                print("Come closer message sent")
            case "Reconfiguration":
                print("Reconfiguration message sent")
            case "Reconfiguration over":
                print("Reconfiguration over message sent")
    
    # def msg_to_preceding(self, type):
    #     match type:
    #         case "Reconfiguration":
    #             print("Reconfiguration message sent")

    