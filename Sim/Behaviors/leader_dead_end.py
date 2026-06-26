from situation_dict import Situation
from agents import Drones
from Behaviors.Behavior import Behavior

class LeaderDeadEnd(Behavior):
    """State machine for the Corridor behavior of Drones"""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.stop_centering = False
        self.doing_rotation = False
        self.turn_around_ready = False
        self.come_closer_sent = False
        super().__init__(name = self.name)
    
    @property
    def situation(self):
        return self.agent.situation.situation
    @property
    def role(self):
        return self.agent.role.configuration_values 

    def update_action(self):
        if LeaderDeadEnd.Active.Sub_Stop.Stop in self.configuration:
            self.send("do_CenterInDeadEnd")
            self.send("do_SendCurrentDirection")
            self.send("standby_stop")
            self.doing_rotation = False
            self.turn_around_ready = False
        elif self.agent.sensor_data.centered_in_corner and (not self.doing_rotation) and self.turn_around_ready:
            self.send("standby_CenterInDeadEnd")
            self.send("do_turn_around")
            self.send("do_rotation")
            self.doing_rotation = True
        elif self.doing_rotation and self.situation[Situation.ROTATION_COMPLETED]:
            self.send("standby_turn_around")
            self.send("standby_rotation")
            self.send("do_SendReconfig")
            self.situation[Situation.RECONFIG] = True
            self.turn_around_ready = True