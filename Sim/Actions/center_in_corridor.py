from agents import Drones
from Actions.Action import Action
import math
class CenterInCorridor(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def d_L_wall(self):
        return self.agent.sensor_data.dist_L_wall
    
    @property
    def d_R_wall(self):
        return self.agent.sensor_data.dist_R_wall

    def action(self):
        if self.agent.front == "N":
            i = 0
            k = 1
        elif self.agent.front == "E":
            i = 1
            k = -1
        elif self.agent.front == "S":
            i = 0
            k = -1
        elif self.agent.front == "W":
            i = 1
            k = 1
        if abs(self.d_L_wall-self.d_R_wall) <0.15:
            self.agent.move_drone[i] += k*-(self.d_L_wall-self.d_R_wall)
        else:
            self.agent.move_drone[i] += math.copysign(0.15,k*-(self.d_L_wall-self.d_R_wall))