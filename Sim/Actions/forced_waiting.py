from agents import Drones

from Actions.Action import Action

class ForcedWaiting(Action):

    def __init__(self, agent):
        self.agent: Drones = agent

        super().__init__(self.name)

    def action(self):
        self.agent.move_drone[0] = 0
        self.agent.move_drone[1] = 0

