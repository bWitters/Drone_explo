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
            if self.situation[Situation.BACKWARD_TOO_FAR][0]: # FIXME
                if self.situation[Situation.COME_CLOSER_SENT] == False:
                    self.send("do_send_come_closer")
                if self.situation[Situation.BACKWARD_TOO_FAR][1] == 2:
                    self.send("do_forced_waiting")
                    self.send("standby_move")
                if self.situation[Situation.BACKWARD_TOO_FAR][1] == 1:
                    self.send("standby_force_waiting")
                    self.send("do_move")
            if LeaderCorridor.Active.Sub_ForcedWaiting.ForcedWaiting in self.configuration:
                if self.situation[Situation.BACKWARD_TOO_FAR][0] == False:
                    self.send("standby_force_waiting")
                    self.send("do_move")
            if self.situation[Situation.CENTERED_IN_CORRIDOR]:
                self.send("standby_CenterInCorridor")