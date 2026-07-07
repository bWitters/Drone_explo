from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class ReconfigIntersection(Behavior):
    """State machine for the Intersection behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.new_cell = None
        self.waiting_rot = False
        self.stop_centering = False

        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values
    
    def update_action(self): #TODO : Aller dans la direction où il y a un drone qui est resté
        if self.situation[Situation.STOP_RECONFIG]:
            print("Stop reconfig received")
        # print(f"Leader front direction : {self.agent.front}")
        # if LeaderIntersection.Active.Sub_Stop.Stop in self.configuration:
        #     self.send("standby_stop")
        #     self.situation[Situation.COME_CLOSER_SENT] = False

        # if LeaderIntersection.Active.Sub_ChangeRole.ChangeRole in self.configuration:
        #     self.send("standby_change_role")
        # else:
        #     if "leader" not in self.role:
        #         self.send("do_change_role")

        # if LeaderIntersection.Active.Sub_CenterInIntersection.Idle_CenterInIntersection in self.configuration and not self.stop_centering:
        #     self.send("do_CenterInIntersection")

        # if LeaderIntersection.Active.Sub_GapDirectionDetermination.GapDirectionDetermination in self.configuration:
        #     self.send("standby_GapDirectionDetermination")
        #     self.send("standby_rotation")
        
        # elif LeaderIntersection.Active.Sub_Move.Move in self.configuration:
        #     pass

        # elif self.waiting_rot:
        #     if self.situation[Situation.ROTATION_COMPLETED]:
        #         self.send("standby_GapDirectionDetermination")
        #         self.send("standby_rotation")
        #         self.send("do_move")
        #         self.waiting_rot = False

        # elif LeaderIntersection.Active.Sub_SendComeCloser.SendComeCloser in self.configuration or self.agent.neighboring_agent_list["F"] == None:
        #     self.send("standby_send_come_closer")

        # elif self.situation[Situation.COME_CLOSER_SENT] or self.agent.neighboring_agent_list["F"] == None:
        #     if self.situation[Situation.BACKWARD_TOO_CLOSE] or self.agent.neighboring_agent_list["F"] == None:
        #         #if self.situation[Situation.CLOSE_TO_EXPLORED_BRANCH]:
        #         self.send("standby_CenterInIntersection")
        #         self.send("do_GapDirectionDetermination")
        #         self.send("do_rotation")
        #         self.waiting_rot = True
        #         self.stop_centering = True

        # elif LeaderIntersection.Active.Sub_SendComeCloser.Idle_SendComeCloser in self.configuration:
        #     self.send("do_send_come_closer")