from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class ReconfigFollowerCurve(Behavior):
    """State machine for the Curve behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None
        self.waiting_rot = False
        self.change_neighborhood = False
        self.reconfig_sent = False
        self.neighborhood_changed = False
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
        print(self.change_neighborhood)
        print(self.situation[Situation.ROTATION_COMPLETED])
        if ReconfigFollowerCurve.Active.Sub_Stop.Stop in self.configuration:
            self.send("standby_stop")
            self.send("do_RotationReconfigCurve")
            self.change_neighborhood = False
            self.reconfig_sent = False
            self.neighborhood_changed = False
            self.completed = False
            print("ReconfigFollowerCurve : Currently starting rotation")
        elif ReconfigFollowerCurve.Active.Sub_RotationReconfigCurve.RotationReconfigCurve in self.configuration:
            self.send("standby_RotationReconfigCurve")
            self.change_neighborhood = True
            print("ReconfigFollowerCurve : Currently stopping rotation")
        elif self.change_neighborhood and self.situation[Situation.ROTATION_COMPLETED]:
            print("ReconfigFollowerCurve : trying to send reconfig")
            self.send("do_SendReconfig")
            self.reconfig_sent = True
            self.change_neighborhood = False
        elif self.reconfig_sent:
            self.send("standby_SendReconfig")
            print(f"ReconfigFollowerCurve : Old Neighbors : {self.agent.neighboring_agent_list}")
            old_preceding = self.agent.neighboring_agent_list["P"]
            self.agent.neighboring_agent_list["P"] = self.agent.neighboring_agent_list["F"]
            self.agent.neighboring_agent_list["F"] = old_preceding
            self.neighborhood_changed = True
            self.reconfig_sent = False
            print("ReconfigFollowerCurve : should have changed neighbors")
            print(f"ReconfigFollowerCurve : New Nieghbors : {self.agent.neighboring_agent_list}")
        elif self.neighborhood_changed:
            print("ReconfigFollowerCurve : Trying to change role")
            self.send("do_change_role")
            self.neighborhood_changed = False
            self.completed = True
        elif self.completed:
            self.send("standby_change_role")
            print("ReconfigFollowerCurve : Waiting for next command")