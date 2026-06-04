from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class FollowerIntersection(Behavior):
    """State machine for the Intersection behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.dir_to_follow = None
        super().__init__(name=self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values

    def update_action(self):
        print(f"Follower front direction : {self.agent.front}")
        # 1 : Center
        # 2 : Wait come closer
        # 3 : Select direction + rotate + Send come closer
        # 4 : Stop select direction + Stop come closer
        # 5 : Wait backward close
        # 6 : Go
        if FollowerIntersection.Active.Sub_Stop.Stop in self.configuration:
            if FollowerIntersection.Active.Sub_CenterInIntersection.Idle_CenterInIntersection in self.configuration:
                self.send("do_CenterInIntersection")
        #     if FollowerIntersection.Active.Sub_SendComeCloser.SendComeCloser in self.configuration:
        #         self.send("standby_send_come_closer")
        #     elif self.situation[Situation.COME_CLOSER_SENT]:
        #         self.send("standby_ComeCloserDirectionToGo")
        #         if self.situation[Situation.BACKWARD_TOO_CLOSE]:
        #             #if self.situation[Situation.CLOSE_TO_EXPLORED_BRANCH]:
        #             self.send("standby_CenterInIntersection")
        #             self.send("do_come_closer")
        #     elif self.situation[Situation.COME_CLOSER][0]:
        #         self.dir_to_follow = self.situation[Situation.COME_CLOSER][1]
        #         if self.agent.neighboring_agent_list["F"] != None:
        #             self.send("do_send_come_closer")
        #             #print("trying to get direction")
        #         self.send("do_ComeCloserDirectionToGo")
        # elif FollowerIntersection.Active.Sub_GapDirectionDetermination.GapDirectionDetermination in self.configuration:
        #     self.send("standby_GapDirectionDetermination")
        #     self.send("standby_rotation")
        # elif FollowerIntersection.Active.Sub_Move.Move in self.configuration:
        #     self.entrance = True
        #     pass 