from agents import Drones
from situation_dict import Situation

from Actions.Action import Action

class Reconfig(Action):
    def __init__(self, agent):
        self.agent:Drones = agent

        super().__init__(self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    
    @property
    def role(self):
        return self.agent.role.configuration_values
    
    @property
    def state(self):
        return self.agent.state.configuration_values

    def action(self):
        pass
