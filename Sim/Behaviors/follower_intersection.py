from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class FollowerIntersection(Behavior):
    """State machine for the Intersection behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.dir_to_follow = None
        self.waiting_come_closer = True
        self.centered = False
        self.need_standby = False
        self.waiting_rot = False
        self.come_closer_received = False
        super().__init__(name=self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values

    @property
    def centered_in_intersection(self):
        return self.agent.sensor_data.centered_in_intersection

    def update_action(self):
        print(f"Follower front direction : {self.agent.front}")
        # 1 : Center
        # 2 : Wait come closer
        # 3 : Select direction + rotate + Send come closer
        # 4 : Stop select direction + Stop come closer
        # 5 : Wait backward close
        # 6 : Go
        if self.situation[Situation.RECONFIG_RECEIVED]:
            self.situation[Situation.RECONFIG]

        if FollowerIntersection.Active.Sub_Stop.Stop in self.configuration:
                self.need_standby = False
                self.centered = False
                self.waiting_come_closer = True
                self.dir_to_follow = None
                self.waiting_rot = False
                self.come_closer_received = False
                self.send("do_CenterInIntersection")
                self.send("standby_stop")

        if FollowerIntersection.Active.Sub_SendComeCloser.SendComeCloser in self.configuration:
            self.send("standby_send_come_closer")

        elif self.situation[Situation.COME_CLOSER][0] and self.waiting_come_closer:
            self.come_closer_received = True
            self.dir_to_follow = self.situation[Situation.COME_CLOSER][1]
            self.waiting_come_closer = False
            if self.agent.neighboring_agent_list["F"] != None:
                self.send("do_send_come_closer")
                #print("trying to get direction")
            self.send("do_ComeCloserDirectionToGo")
            
        elif self.come_closer_received:
            if self.situation[Situation.COME_CLOSER_SENT] or self.agent.neighboring_agent_list["F"] == None:
                self.send("standby_ComeCloserDirectionToGo")
                if self.need_standby:
                    self.send("standby_GapDirectionDetermination")
                    self.send("standby_rotation")
                    self.waiting_rot = True
                if self.centered_in_intersection:
                    self.send("standby_CenterInIntersection")
                    self.send("do_GapDirectionDetermination")
                    self.send("do_rotation")
                    self.need_standby = True
                if self.situation[Situation.BACKWARD_TOO_CLOSE] or self.agent.neighboring_agent_list["F"] == None:
                    #if self.situation[Situation.CLOSE_TO_EXPLORED_BRANCH]:
                    if self.waiting_rot and self.situation[Situation.ROTATION_COMPLETED]:
                        self.send("do_move")