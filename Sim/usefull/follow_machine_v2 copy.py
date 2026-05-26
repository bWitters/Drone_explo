#Imports
from statemachine import StateChart, State
from statemachine.contrib.diagram import DotGraphMachine
import time
#Const
GENRERATE_DIAGRAM = True

#Classes
class FollowerMachine(StateChart):
    position = [0,0,0]
    is_centered = True
    current_active_direction = None
    previous_active_direction = None
    gaps_dir = []
    previous_gap_dir = []
    dist_wall = 0
    rays = None
    front = "North"
    action = [0,0,0,0,0]
    number_of_gaps = 0
    is_centered_east_west = False
    is_centered_north_south = False
    intersection_visited = []
    current_intersection = None
    begin_entering_gap = True
    inital_position = []
    preceding = None
    follower = None
    maybe_corner = False
    come_closer_sent = False
    leader_message = []
    centered_in_corner = False
    close_to_leader = False

    def __init__(self):
        super().__init__()
        self.add_listener(MyListener())
            
    done_state_takeoff = takeoff.to(mission)

    def checkHeight(self):
        return abs(self.position[2] - 1) < 0.05

    def moreThanTwoGaps(self):
        return self.number_of_gaps > 2 and not self.maybe_corner

    def centered(self):
        return FollowerMachine.mission.movements.centerInIntersection.centered in self.configuration

    # def goodDirection(self):
    #     return self.yaw == self.gap_direction

    # def directionChanged(self):
    #     return self.gap_direction != self.previous_gap_direction

    # def oneGap(self):
    #     return self.number_of_gaps == 1

    # def followerClose(self):
    #     return self.followerIsClose

class MyListener:
    def on_transition(self, source, target, transition):
        print(f"Transition de {source.name} vers {target.name} via {transition}")

if __name__ == "__main__":
    #Init Machine
    drone = FollowerMachine()
    print('coucou')

    #Generate diagram
    if GENRERATE_DIAGRAM:
        open(f"Images/order_control_machine_initial_{time.strftime("%d%m%Y_%H%M%S")}.png","w")
        graph = DotGraphMachine(FollowerMachine)
        dot = graph()
        dot.to_string()
        dot.write_png(f"Images/order_control_machine_initial_{time.strftime("%d%m%Y_%H%M%S")}.png")

    # #Run
    # for i in range(10):
    #     drone.execute()