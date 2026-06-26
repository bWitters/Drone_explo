from agents import Drones
from Actions.Action import Action
import math

class CenterInIntersection(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)
    
    @property
    def entrance_position(self):
        return self.agent.situation.intersection_entrance

    def action(self):
        distance_x = 0
        distance_y = 0
        match self.agent.front:
            case "N":
                distance_x = self.entrance_position[1] + 0.2 - self.agent.position[1]
            case "S":
                distance_x = self.entrance_position[1] - 0.2 - self.agent.position[1]
            case "E":
                distance_y = self.entrance_position[0] + 0.2 - self.agent.position[0]
            case "W":
                distance_y = self.entrance_position[0] - 0.2 - self.agent.position[0]
        if abs(distance_x)<0.15:
            self.agent.move_drone[1] += distance_x
        else:
            self.agent.move_drone[1] += math.copysign(0.15,distance_x)
        if abs(distance_y)<0.15:
            self.agent.move_drone[0] += distance_y
        else:
            self.agent.move_drone[0] += math.copysign(0.15,distance_y)