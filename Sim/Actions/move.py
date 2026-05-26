from agents import Drones

from Actions.Action import Action

class Move(Action):
    def __init__(self, agent):
        self.agent:Drones = agent

        super().__init__(self.name)

    @property
    def front(self):
        return self.agent.front
        
    def action(self):
        #print(self.front)
        #print(self.agent.move_drone)
        if self.front == "E":
            self.agent.move_drone[0] = 0.5
        elif self.front == "N":
            self.agent.move_drone[1] = 0.5
        elif self.front == "W":
            self.agent.move_drone[0] = -0.5
        elif self.front == "S":
            self.agent.move_drone[1] = -0.5


