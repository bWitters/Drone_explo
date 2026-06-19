from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class FollowerCorridor(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        if self.situation[Situation.RECONFIG_RECEIVED]:
            self.situation[Situation.RECONFIG] = True

        if FollowerCorridor.Active.Sub_Stop.Stop in self.configuration:
            self.send("do_CenterInCorridor")
            self.send("do_HeightControl")
            self.send("do_RotationControl")
            self.send("standby_stop")
            self.send("do_ComeCloserDirectionToGo")
            self.send("do_move")
            #self.send("do_rotation")
            #self.send("do_SendCurrentDirection")
            self.situation[Situation.COME_CLOSER_SENT] = False

        elif FollowerCorridor.Active.Sub_Move.Move in self.configuration:
            self.send("standby_ComeCloserDirectionToGo")

            if self.situation[Situation.BACKWARD_TOO_FAR][0]:
                if self.situation[Situation.COME_CLOSER_SENT] == False:
                    self.send("do_send_come_closer")
                if self.situation[Situation.BACKWARD_TOO_FAR][1] == 2:
                    self.send("do_ForcedWaiting")
                    self.send("standby_move")
            
            if self.situation[Situation.FRONT_TOO_CLOSE]:
                self.send("do_ForcedWaiting")


            if not self.situation[Situation.FRONT_TOO_CLOSE] and not self.situation[Situation.BACKWARD_TOO_FAR][0]:
                self.send("standby_ForcedWaiting")        

        elif FollowerCorridor.Active.Sub_ForcedWaiting.ForcedWaiting in self.configuration:
            if self.situation[Situation.BACKWARD_TOO_FAR][0] == False:
                self.send("do_move")
                self.send("standby_ForcedWaiting")
            if self.situation[Situation.BACKWARD_TOO_FAR][1] == 1:
                self.send("do_move")
                self.send("standby_ForcedWaiting")