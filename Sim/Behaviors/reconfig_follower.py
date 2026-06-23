from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class ReconfigFollower(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.rotate = True
        self.change_neighborhood = True
        self.neighborhood_changed = False
        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        print(self.role)
        if "leader" in self.role:
            if ReconfigFollower.Active.Sub_Stop.Stop in self.configuration:
                self.send("standby_stop")
                self.change_neighborhood = True
            elif self.change_neighborhood:
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = None
                self.rotate = False
                self.change_neighborhood = False
            print(self.agent.neighboring_agent_list)
        else:
            if ReconfigFollower.Active.Sub_Stop.Stop in self.configuration:
                self.rotate = True
                self.change_neighborhood = False
                self.neighborhood_changed = False
                self.send("standby_stop")
            elif self.rotate:
                self.send("do_turn_around")
                self.send("do_rotation")
                self.rotate = False
                self.change_neighborhood = True
            elif self.change_neighborhood and self.situation[Situation.ROTATION_COMPLETED]:
                self.send("standby_turn_around")
                self.send("standby_rotate")
                old_preceding = self.agent.neighboring_agent_list["P"]
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = old_preceding
                self.change_neighborhood = False
                self.neighborhood_changed = True
            elif self.neighborhood_changed:
                self.send("do_SendReconfig")
                print("Reconfig done")