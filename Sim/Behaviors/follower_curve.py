from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class FollowerCurve(Behavior):
    """State machine for the curve behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.dir_to_follow = None
        super().__init__(name=self.name)

    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.current_state.id 


    def update_action(self):
        #print(f"Front : {self.agent.front}")
        if FollowerCurve.Active.Sub_Stop.Stop in self.configuration:
            #print(self.agent.sensor_data.com_stack.queue)
            #print("coucou je suis stopé")
            #print(f"Front : {self.agent.front}")
            self.send("do_CenterInCurve")
            if self.situation[Situation.COME_CLOSER][0]:
                self.dir_to_follow = self.situation[Situation.COME_CLOSER][1]
                #print("coucou j'ai recu un come closer")
                self.send("standby_stop")
                if self.agent.neighboring_agent_list["F"] != None:
                    self.send("do_send_come_closer")
                    #print("trying to get direction")
                self.send("do_ComeCloserDirectionToGo")
        elif FollowerCurve.Active.Sub_Move.Move in self.configuration:
            self.send("standby_ComeCloserDirectionToGo")
        elif self.situation[Situation.COME_CLOSER_SENT] or self.agent.neighboring_agent_list["F"] == None:
            self.send("standby_send_come_closer")
            self.send("standby_ComeCloserDirectionToGo")
            if self.situation[Situation.BACKWARD_TOO_CLOSE] or self.agent.neighboring_agent_list["F"] == None:
                self.send("standby_CenterInCurve")
                self.send("do_come_closer")
        