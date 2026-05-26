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
        return self.agent.role.current_state.id 

    def update_action(self):
        if FollowerCorridor.Active.Sub_Stop.Stop in self.configuration:
            self.send("do_CenterInCorridor")
            self.send("do_HeightControl")
            self.send("do_RotationControl")
            self.send("standby_stop")
            self.send("do_ComeCloserDirectionToGo")
            self.send("do_come_closer")
            self.situation[Situation.COME_CLOSER_SENT] = False

        elif FollowerCorridor.Active.Sub_Move.Move in self.configuration:
            self.send("standby_ComeCloserDirectionToGo")
            if self.situation[Situation.CENTERED_IN_CORRIDOR]:
                self.send("standby_CenterInCorridor")