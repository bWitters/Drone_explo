from states.drone import Drone

class Follower(Drone):
    def __init__(self, follower=None, position=None, preceding=None, follower_id=None, preceding_id=None): 
        super().__init__(follower=follower, position=position, preceding=preceding, follower_id=follower_id, preceding_id=preceding_id) 
    
    def follow_agent_in_front(self):
        self.action = [0,0,0,0,0]
        if len(self.message_received) != 0 and self.message_received[-1] == "Come closer":
            print("Come closer received")
            if self.follower != None:
                if self.distance_drone_x(self.follower) > self.distance_max or (len(self.follower.message_received) != 0 and self.follower.message_received[-1] == 'Come closer'):
                    if len(self.follower.message_received) != 0:
                        if self.follower.message_received[-1] != "Come closer":
                            print('Sending message to follower')
                            self.msg_to_follower("Come closer")
                    else:
                        print('Sending message to follower')
                        self.msg_to_follower("Come closer")
                    self.action = [0,0,0,0,0]
                else:
                    self.get_closer()
            else:
                self.get_closer()
                
        
    
    def get_closer(self):
        if self.distance_drone_x(self.preceding) < self.distance_min:
            self.message_received.pop()
            self.action = [0,0,0,0,0]
            print("End of getting closer")
        else:
            print("Getting closer")
            direction = self.direction_drone_x(self.preceding)
            self.action = [direction[0], direction[1], direction[2], float(0.1), 0]

    def run(self, lidar_data, lidar_ray_angles):
        print("Follower is running")
        self.follow_agent_in_front()


        