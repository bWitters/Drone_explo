from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderDeadEnd(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        if LeaderDeadEnd.Active.Sub_Stop.Stop in self.configuration:
            print("Reached a dead end")