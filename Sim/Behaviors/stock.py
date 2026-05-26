from situation_dict import Situation
from agents import Drones

from Behaviors.Behavior import Behavior

class Stock(Behavior):
    """State machine for the Stock behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        
        super().__init__(self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    
    @property
    def role(self):
        return self.agent.role.current_state.id
    
    @property
    def new_role(self):
        return self.agent.new_role
    
    def update_action(self):
        if Stock.Active.Sub_Stop.Stop in self.configuration:
            if self.role == "stock":
                if self.agent.unique_id == 1:
                    self.send("standby_stop")
                    self.send("do_change_role")
                else:
                    self.send("standby_stop")
                    self.send("do_change_role")