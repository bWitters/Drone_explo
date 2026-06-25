from agents import Drones
from Behaviors.Behavior import Behavior
from situation_dict import Situation

class ForcedWait(Behavior):
    """State machine for the Pebble behavior of Drones"""

    def __init__(self, agent):
            self.agent:Drones = agent
            self.all_branch_explored = False
            self.has_receive_reconfig = False

            super().__init__(name=self.name)

    @property
    def situation(self):
        return self.agent.situation.situation

    def update_action(self, state):
        if self.situation[Situation.RECONFIG_RECEIVED]:
            self.situation[Situation.RECONFIG] = True
            self.has_receive_reconfig = True
        if self.has_receive_reconfig:
            print("I have received reconfig message")

