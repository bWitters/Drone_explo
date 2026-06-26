from agents import Drones
from Actions.Action import Action
import math

class CenterInCurve(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def d_F_wall(self):
        return self.agent.sensor_data.dist_F_wall

    @property
    def d_L_wall(self):
        return self.agent.sensor_data.dist_L_wall
    
    @property
    def d_R_wall(self):
        return self.agent.sensor_data.dist_R_wall
    
    def determine_wall_dir(self):
        if self.d_L_wall - self.d_R_wall <0:
            side_wall = "L"
        else:
            side_wall = "R"
        print(f"the side where there is a wall is : {side_wall}")
        return side_wall

    def side_wall_action(self):
        act = 0
        side = self.determine_wall_dir()
        if side == "R":
            act = self.d_R_wall-0.25
        elif side == "L":
            act = 0.25-self.d_L_wall
        print(f"The action to center is : {act}")
        return act

    def action(self):
        #print("coucou")
        if self.agent.front == "N":
            i = 1
            k = 1
            j = 1
        elif self.agent.front == "E":
            i = 0
            k = 1
            j = -1
        elif self.agent.front == "S":
            i = 1
            k = -1
            j = -1
        elif self.agent.front == "W":
            i = 0
            k = -1
            j = 1
        if abs(self.d_F_wall-0.25) < 0.15 :
            self.agent.move_drone[i] += k*(self.d_F_wall-0.25)
        else:
            self.agent.move_drone[i] += math.copysign(0.15,k*(self.d_F_wall-0.25))
        a = self.side_wall_action()
        if abs(a) < 0.15 :
            self.agent.move_drone[(i+1)%2] += j*self.side_wall_action()
        else:
            self.agent.move_drone[(i+1)%2] += math.copysign(0.15,j*self.side_wall_action())