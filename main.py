#Imports
from transitions import Machine
from transitions.extensions.diagrams import HierarchicalGraphMachine
import pyperclip

#Const
COPY_DIAGRAM = True

#Classes
class DroneMachine():
    states = ['takeoff', 'scanGaps', 'followTheGap', 'centerInIntersection', 'failed', "callFollower", "alignWithGap", 'deadEnd']
    transitions = [
        ['goodHeight', 'takeoff', 'scanGaps'],
        ["goodDirection", "scanGaps", "followTheGap"],
        ["twoLongSum", "followTheGap", "scanGaps"],
        ["twoGaps", "scanGaps", "followTheGap"],
        ["moreThanTwoGaps", "scanGaps", "centerInIntersection"],
        ["goodDirection", "centerInIntersection", "alignWithGap"],
        ["directionChanged", "followTheGap", "callFollower"],
        ["directionChanged", "alignWithGap", "callFollower"],
        ["currentDirectionLow", "followTheGap", "deadEnd"]
    ]
    def __init__(self,name):
        self.name = name

        self.machine = Machine(model=self, states=DroneMachine.states, initial='takeoff')

        self.count_fail = 0

#Init Machine
drone = DroneMachine("test")

#Run
if COPY_DIAGRAM:
    m = HierarchicalGraphMachine(states=drone.states, transitions=drone.transitions, initial="takeoff")

    pyperclip.copy(m.get_graph().draw(None))