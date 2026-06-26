from agents import Drones
from Actions.Action import Action

class CenterInDeadEnd(Action):
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
        self.agent.move_drone[i] += k*(self.d_F_wall-0.24)
        self.agent.move_drone[(i+1)%2] += j*(self.d_R_wall-self.d_L_wall)