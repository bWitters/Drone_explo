from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class ReconfigCorridor(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    
    def update_action(self):
        if self.situation[Situation.STOP_RECONFIG]:
            print("Stop reconfig received")
        if ReconfigCorridor.Active.Sub_Stop.Stop in self.configuration:
            self.send("standby_stop")
            self.situation[Situation.COME_CLOSER_SENT] = False
            self.send("do_HeightControl")
            self.send("do_RotationControl")
            self.send("do_CenterInCorridor")
            self.send("do_explore")
            #self.send("do_SendCurrentDirection")

        elif ReconfigCorridor.Active.Sub_Move.Move in self.configuration:
            self.send("standby_GapDirectionDetermination")
            self.send("standby_rotation")
            if self.situation[Situation.BACKWARD_TOO_FAR][0]:
                if not self.situation[Situation.COME_CLOSER_SENT]:
                    self.send("do_send_come_closer")
                if self.situation[Situation.BACKWARD_TOO_FAR][1] == 2:
                    self.send("do_send_come_closer")
                    self.send("do_ForcedWaiting")
                    self.send("standby_move")
                
        elif ReconfigCorridor.Active.Sub_ForcedWaiting.ForcedWaiting in self.configuration:
            if self.situation[Situation.BACKWARD_TOO_FAR][0] == False:
                self.send("do_move")
                self.send("standby_ForcedWaiting")
            if self.situation[Situation.BACKWARD_TOO_FAR][1] == 1:
                self.send("do_move")
                self.send("standby_ForcedWaiting")