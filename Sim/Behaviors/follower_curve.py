from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class FollowerCurve(Behavior):
    """State machine for the curve behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.dir_to_follow = None
        self.ready_to_continue = False
        super().__init__(name=self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 


    def update_action(self):
        if self.situation[Situation.RECONFIG_RECEIVED]:
            print("Reconfig received")
            print("Sending Reconfig")
            self.send("do_SendReconfig")            

        if FollowerCurve.Active.Sub_Stop.Stop in self.configuration:
            self.ready_to_continue = False
            self.dir_to_follow = None
            self.send("do_CenterInCurve")
            self.send("do_HeightControl")
            self.send("do_RotationControl")
            if self.agent.sensor_data.centered_in_corner:
                self.ready_to_continue = True
                self.send("standby_stop")
        
        elif self.ready_to_continue:
            if self.situation[Situation.COME_CLOSER][0]:
                self.dir_to_follow = self.situation[Situation.COME_CLOSER][1]
                if self.agent.neighboring_agent_list["F"] != None:
                    self.send("do_send_come_closer")
                self.send("do_ComeCloserDirectionToGo")
                self.ready_to_continue = False

        elif FollowerCurve.Active.Sub_Move.Move in self.configuration:
            self.send("standby_ComeCloserDirectionToGo")
            if self.situation[Situation.FRONT_TOO_CLOSE]:
                self.send("do_stop")
                pass

        elif FollowerCurve.Active.Sub_Rotation.Rotation in self.configuration:
            if self.situation[Situation.ROTATION_COMPLETED]:
                self.send("standby_CenterInCurve")
                self.send("do_move")

        elif self.situation[Situation.COME_CLOSER_SENT] or self.agent.neighboring_agent_list["F"] == None:
            self.send("standby_send_come_closer")
            self.send("standby_ComeCloserDirectionToGo")
            if self.situation[Situation.BACKWARD_TOO_CLOSE] or self.agent.neighboring_agent_list["F"] == None:
                self.send("standby_CenterInCurve")
                self.send("do_rotation")
        