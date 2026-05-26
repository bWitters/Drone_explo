from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderCurve(Behavior):
    """State machine for the Curve behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.current_state.id 
    
    def update_action(self): # FIXME
        if LeaderCurve.Active.Sub_Stop.Stop in self.configuration:
            self.send("standby_stop")
            self.send("do_send_come_closer")
            self.send("do_CenterInCurve")
            #print("step 1 Stop")
        elif LeaderCurve.Active.Sub_Move.Move in self.configuration:
            self.send("standby_GapDirectionDetermination")
            self.send("standby_rotation")
            #print("Step 5 going to next environnement")
        elif LeaderCurve.Active.Sub_SendComeCloser.SendComeCloser in self.configuration:
            self.send("standby_send_come_closer")
            #print("Step 2 send message")
        elif LeaderCurve.Active.Sub_SendComeCloser.Idle_SendComeCloser in self.configuration:
            #print("Step 3 Wait")
            if self.situation[Situation.BACKWARD_TOO_CLOSE]:
                #print("Step 4 move")
                self.send("standby_stop")
                self.send("do_GapDirectionDetermination")
                self.send("do_rotation")
                self.send("do_move")