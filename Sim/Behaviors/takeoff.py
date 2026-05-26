from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class Takeoff(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    
    @property
    def role(self):
        return self.agent.role.current_state.id 

    def update_action(self):
        if Takeoff.Active.Sub_Stop.Stop in self.configuration:
            if not self.situation[Situation.GOOD_HEIGHT]:
                self.send("standby_stop")
                self.send("do_takeoff")