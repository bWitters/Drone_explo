from agents import Drones

from Actions.Action import Action

class Takeoff(Action):

    def __init__(self, agent):
        self.agent: Drones = agent

        super().__init__(self.name)
    
    @property
    def position(self):
        return self.agent.position

    def distance(self):
        return 0.45 - self.position[2]
    
    def action(self):
        self.agent.move_drone[2] = self.distance()
        #print("Increasing height")