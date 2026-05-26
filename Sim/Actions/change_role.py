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
        return self.agent.role.current_state.id
    @property
    def state(self):
        return self.agent.state.configuration_values
    
    def new_role(self):
        if "Stock" in self.state:
            if self.role == "stock":
                if self.agent.unique_id == 1:
                    return "leader"
                else:
                    return "follower"
        elif "LeaderIntersection" in self.state:
            if self.role == "follower":
                return "leader"

    def action(self):
        new_role = self.new_role()
        if new_role == "leader":
            self.agent.role.become_leader()
        elif new_role == "follower":
            self.agent.role.become_follower()
