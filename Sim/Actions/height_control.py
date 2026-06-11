from agents import Drones
from Actions.Action import Action

class HeightControl(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def height(self):
        return self.agent.position[2]

    def action(self): #FIXME
        self.agent.move_drone[2] += 0.45 - self.height
        print(f"Current height : {self.height}")
        if abs(0.45 - self.height) < 0.01:
            self.agent.move_drone[2] = 0