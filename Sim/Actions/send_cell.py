from agents import Drones
from communication import Com
from Actions.Action import Action

class SendCell(Com, Action):
    def __init__(self, agent):
        super().__init__(agent = agent, name = self.name)
        self.agent:Drones = agent

    @property
    def cell(self):
        return self.agent.cell
    
    def action(self):
        self.send_com("Cell to follow", self.cell)
