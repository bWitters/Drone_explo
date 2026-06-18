from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class ReconfigFollower(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.rotate = True
        self.change_neighborhood = True
        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        if self.role == "leader":
            if self.change_neighborhood:
                self.send("standby_turn_around")
                self.send("standby_rotate")
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = None
                self.rotate = False
                self.change_neighborhood = False
        else:
            if self.rotate:
                self.send("do_turn_around")
                self.send("do_rotate")
                self.rotate = False
            if self.change_neighborhood:
                self.send("standby_turn_around")
                self.send("standby_rotate")
                old_preceding = self.agent.neighboring_agent_list["P"]
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = old_preceding
                self.change_neighborhood = False