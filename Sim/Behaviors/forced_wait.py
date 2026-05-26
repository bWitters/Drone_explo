from agents import Drones
from Behaviors.Behavior import Behavior

class ForcedWait(Behavior):
    """State machine for the Pebble behavior of Drones"""

    def __init__(self, agent):
            self.agent:Drones = agent
            self.all_branch_explored = False

            super().__init__(name=self.name)


    def update_action(self, state):
        pass
