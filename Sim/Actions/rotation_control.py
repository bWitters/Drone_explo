from agents import Drones
from math import pi
from Actions.Action import Action

class RotationControl(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def yaw_angle(self):
        return self.agent.rpy[2]

    def action(self): #FIXME
        print(f"Current yaw angale : {self.yaw_angle}")
        match self.agent.front:
            case "N":
                angle = pi/2
            case "S":
                angle = -pi/2
            case "E":
                angle = 0
            case "W":
                if self.yaw_angle < 0:
                    angle = -pi
                else:
                    angle = pi
        print(f"Angle decided : {angle}")
        self.agent.move_drone[4] += angle - self.yaw_angle