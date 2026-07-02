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
        self.stop_rotation_command = False
        self.reconfig_sent = False
        self.completed = False
        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        if self.situation[Situation.STOP_RECONFIG]:
            print("Stop reconfig received")
        print(self.role)
        if "leader" in self.role:
            if ReconfigFollower.Active.Sub_Stop.Stop in self.configuration:
                self.send("standby_stop")
                self.change_neighborhood = True
                self.completed = False
            elif self.change_neighborhood:
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = None
                self.rotate = False
                self.change_neighborhood = False
                self.send("do_change_role")
                self.completed = True
            elif self.completed:
                self.send("standby_change_role")
                print("Waiting for next command")
        else:
            if ReconfigFollower.Active.Sub_Stop.Stop in self.configuration:
                self.rotate = True
                self.change_neighborhood = False
                self.neighborhood_changed = False
                self.reconfig_sent = False
                self.stop_rotation_command = False
                self.completed = False
                self.send("standby_stop")
            elif self.rotate:
                self.send("do_turn_around")
                self.send("do_rotation")
                self.rotate = False
                self.stop_rotation_command = True
            elif self.stop_rotation_command:
                self.send("standby_turn_around")
                self.send("standby_rotation")
                self.stop_rotation_command = False
                self.change_neighborhood = True
            elif self.change_neighborhood and self.situation[Situation.ROTATION_COMPLETED]:
                self.send("do_SendReconfig")
                self.reconfig_sent = True
                self.change_neighborhood = False
            elif self.reconfig_sent:
                self.send("standby_SendReconfig")
                self.send("standby_turn_around")
                self.send("standby_rotate")
                old_preceding = self.agent.neighboring_agent_list["P"]
                self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
                self.agent.neighboring_agent_list["F"] = old_preceding
                self.neighborhood_changed = True
                self.reconfig_sent = False
            elif self.neighborhood_changed:
                self.send("do_change_role")
                self.neighborhood_changed = False
                self.completed = True
            elif self.completed:
                self.send("standby_change_role")
                print("Waiting for next command")