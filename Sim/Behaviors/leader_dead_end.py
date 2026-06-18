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
            self.send("do_SendReconfig")
            self.send("do_turn_around")
            self.send("do_rotation")
            self.send("standby_stop")
        else:
            self.situation[Situation.RECONFIG] = True