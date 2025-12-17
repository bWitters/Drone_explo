from states.drone import Drone
import numpy as np

class Leader(Drone):
    def __init__(self, follower, position, preceding): # sensors, 
        super().__init__(follower=follower, position=position, preceding=preceding) # sensors=sensors, 

    def run(self, lidar_data, lidar_ray_angles):
        print("Leader is running")
        self.sensorsAnalyzer.analyze(lidar_data, lidar_ray_angles)
        self.move_forward_in_branch()

    def move_forward_in_branch(self):
        # while not self.lidar.loop and not self.lidar.dead_end and not self.lidar.intersection:
        if self.follower != None and ((self.distance_drone_x(self.follower) > self.distance_max) or (len(self.follower.message_received) != 0 and self.follower.message_received[-1] == 'Come closer')):
            if len(self.follower.message_received) != 0:
                if self.follower.message_received[-1] != "Come closer":
                    print('Sending message to follower')
                    self.msg_to_follower("Come closer")
            else:
                print('Sending message to follower')
                self.msg_to_follower("Come closer")
            self.action = [0,0,0,float(0.1),0]
        else:
            print("Bonne distance")
            self.follow_the_branch(self.sensorsAnalyzer.analyzed_data["positive gap direction"],0)

        # if self.lidar.loop :
        #     print("Loop management begin")
        #     self.loop_management()
        # elif self.lidar.dead_end :
        #     print("Dead end management begin")
        #     self.dead_end_management()
        # elif self.lidar.intersaction:
        #     print("Intersection management begin")
        #     self.intersection_management()
        

    # def loop_management(self):
    #     self.msg_to_follower("Reconfiguration")
    #     self.turn_around()
    #     self.

    # def dead_end_management(self):
    #     self.msg_to_follower("Reconfiguration")
    #     self.turn_around()
    
    # def intersection_management(self):
    #     self.msg_to_follower("Come closer")
    #     self.centering()
    #     self.rotation()
    #     while np.linalg.norm(np.array(self.position)-np.array(self.follower.position)) > self.distance_max:
    #         self.wait()
    #     else:
    #         self.move_forward_in_branch()
