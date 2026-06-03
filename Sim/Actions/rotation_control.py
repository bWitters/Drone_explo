from agents import Drones
from math import pi
from Actions.Action import Action
import math
class RotationControl(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def yaw_angle(self):
        return self.agent.rpy[2]

    def action(self): #FIXME
        print(f"Current yaw angle : {self.yaw_angle}")
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
        if abs(angle - self.yaw_angle) > pi:
            self.agent.move_drone[4] += -1*math.copysign(1, angle - self.yaw_angle)*(2*pi-abs(angle - self.yaw_angle))
        else:
            self.agent.move_drone[4] += angle - self.yaw_angle