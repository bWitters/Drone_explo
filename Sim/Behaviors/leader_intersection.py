from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderIntersection(Behavior):
    """State machine for the Intersection behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values
    
    def update_action(self):
        print(f"Leader front direction : {self.agent.front}")
        if LeaderIntersection.Active.Sub_Stop.Stop in self.configuration:
            if LeaderIntersection.Active.Sub_ChangeRole.ChangeRole in self.configuration:
                self.send("standby_change_role")
            else:
                if "leader" not in self.role:
                    self.send("do_change_role")
            if LeaderIntersection.Active.Sub_CenterInIntersection.Idle_CenterInIntersection in self.configuration:
                self.send("do_CenterInIntersection")
            if LeaderIntersection.Active.Sub_SendComeCloser.SendComeCloser in self.configuration:
                self.send("standby_send_come_closer")
            elif self.situation[Situation.COME_CLOSER_SENT]:
                if self.situation[Situation.BACKWARD_TOO_CLOSE]:
                    #if self.situation[Situation.CLOSE_TO_EXPLORED_BRANCH]:
                    self.send("standby_stop")
                    self.send("do_explore")
            elif LeaderIntersection.Active.Sub_SendComeCloser.Idle_SendComeCloser in self.configuration:
                self.send("do_send_come_closer")
        elif LeaderIntersection.Active.Sub_GapDirectionDetermination.GapDirectionDetermination in self.configuration:
            self.send("standby_GapDirectionDetermination")
            self.send("standby_rotation")
        elif LeaderIntersection.Active.Sub_Move.Move in self.configuration:
            self.entrance = True
            pass 
