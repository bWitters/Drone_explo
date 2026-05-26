from agents import Drones
from Actions.Action import Action

class HeightControl(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def height(self):
        return self.agent.position[2]

    def action(self):
        self.agent.move_drone[2] += 1 - self.height
        if 1- self.height < 0.01:
            self.agent.move_drone[2] = 0