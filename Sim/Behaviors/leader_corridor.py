from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderCorridor(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    
    def update_action(self): # TODO : ADD A 5m limit
        if LeaderCorridor.Active.Sub_Stop.Stop in self.configuration:
            self.send("standby_stop")
            self.situation[Situation.COME_CLOSER_SENT] = False
            self.send("do_HeightControl")
            self.send("do_RotationControl")
            self.send("do_CenterInCorridor")
            self.send("do_explore")
        elif LeaderCorridor.Active.Sub_Move.Move in self.configuration:
            self.send("standby_GapDirectionDetermination")
            self.send("standby_rotation")
            if self.situation[Situation.CENTERED_IN_CORRIDOR]:
                self.send("standby_CenterInCorridor")