from agents import Drones
from situation_dict import Situation

from Actions.Action import Action

class ChangeRole(Action):
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
    
    def new_role(self):
        if "Stock" in self.state:
            if "stock" in self.role:
                if self.agent.unique_id == 1:
                    return "leader"
                else:
                    return "follower"
        elif "LeaderIntersection" in self.state:
            if "follower" in self.role:
                return "leader"
        print("Trying to get new role")
        if "ReconfigFollower" in self.state or "ReconfigFollowerCurve" in self.state:
            if self.agent.neighboring_agent_list["P"] == None:
                return "reconfig_leader"
            else:
                return "reconfig_follower"

    def action(self):
        print("Changing Role")
        new_role = self.new_role()
        if new_role == "leader":
            self.agent.role.become_leader()
        elif new_role == "follower":
            self.agent.role.become_follower()
        elif new_role == "reconfig_follower":
            self.agent.role.become_reconfig_follower()
        elif new_role == "reconfig_leader":
            self.agent.role.become_reconfig_leader()
