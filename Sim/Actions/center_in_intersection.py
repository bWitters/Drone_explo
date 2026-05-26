from agents import Drones
from Actions.Action import Action

class CenterInIntersection(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)
    
    @property
    def entrance_position(self):
        return self.agent.situation.intersection_entrance

    def action(self): # TODO : Centrage dans une intersection.
        distance_x = 0
        distance_y = 0
        match self.agent.front:
            case "N":
                distance_x = self.entrance_position[1] + 0.3 - self.agent.position[1]
            case "S":
                distance_x = self.entrance_position[1] - 0.3 - self.agent.position[1]
            case "E":
                distance_y = self.entrance_position[0] + 0.3 - self.agent.position[0]
            case "W":
                distance_y = self.entrance_position[0] - 0.3 - self.agent.position[0]
        self.agent.move_drone[1] += distance_x
        self.agent.move_drone[0] += distance_y