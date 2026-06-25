from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderCurve(Behavior):
    """State machine for the Curve behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None
        self.waiting_rot = False

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values
    
    def update_action(self):
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
            if self.situation[Situation.BACKWARD_TOO_CLOSE]:
                #print("Step 4 move")
                self.send("standby_send_come_closer")
                self.send("standby_stop")
                self.send("standby_CenterInCurve")
                self.send("do_GapDirectionDetermination")
                self.send("do_rotation")
                self.waiting_rot = True
                #print("Step 2 send message")
        
        elif LeaderCurve.Active.Sub_Rotation.Rotation in self.configuration:
            self.send("standby_rotation")
        
        elif self.waiting_rot:
            if self.situation[Situation.ROTATION_COMPLETED]:
                self.send("do_move")
                self.waiting_rot = False
            
