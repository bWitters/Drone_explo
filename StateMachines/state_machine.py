#Imports
from statemachine import StateChart, State
from statemachine.contrib.diagram import DotGraphMachine
import time
#Const
GENRERATE_DIAGRAM = True

#Classes
class DroneMachine(StateChart):
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

    class takeoff(State.Compound):
        stoped = State(initial=True)
        goingUp = State()
        top = State(final=True)

        takingoff = stoped.to(goingUp)
        
        flying = goingUp.to.itself(internal=True, on="do_goingUp")
        
        goingUp.to(top, cond='topHeight')
        
        def do_goingUp(self):
            self.action = [0,0,0.5,0,0]
        
        def topHeight(self):
            return self.position[2] > 1
    

    class followTheGap(State.Parallel):
        class aligning(State.Compound):
            correctingNothing = State(initial=True)
            correctingNorthSouth = State()
            correctingEastWest = State()

            

            correctingNorthSouth.to(correctingNothing, cond='centered')
            correctingEastWest.to(correctingNothing, cond='centered')

            correctingNothing.to(correctingNorthSouth, cond=['not_centered', 'dirEastWest'])
            correctingNothing.to(correctingEastWest, cond=['not_centered', 'dirNorthSouth'])

            def centered(self):
                return self.is_centered

            def not_centered(self):
                return not self.is_centered
            
            def dirNorthSouth(self):
                return self.current_active_direction in ["North", "South"]

            def dirEastWest(self):
                return self.current_active_direction in ["East", "West"]

        class movingForward(State.Compound):
            moving = State(initial = True)
            # stopped = State()
            # #waiting_follower = State()

            # stop = moving.to(stopped)

            # continue_moving = stopped.to(moving)
            

    class centerInIntersection(State.Compound):
        enteringIntersection = State(initial=True)
        centered = State(final=True)
    
        class aligningEastWest(State.Compound):
            goingEastWest = State()
            centeredEastWest = State(final=True)

            goingEastWest.to(centeredEastWest, cond='centered_EastWest')

            def centered_EastWest(self):
                return self.is_centered_east_west

        class aligningNorthSouth(State.Compound):
            goingNorthSouth = State()
            centeredNorthSouth = State(final=True)

            goingNorthSouth.to(centeredNorthSouth, cond='centered_NorthSouth')

            def centered_NorthSouth(self):
                return self.is_centered_north_south
    
        center_east_west_from_start = enteringIntersection.to(aligningEastWest.goingEastWest)
        center_north_south_from_start = enteringIntersection.to(aligningNorthSouth.goingNorthSouth) 

        center_east_west_after = aligningNorthSouth.centeredNorthSouth.to(aligningEastWest.goingEastWest)
        center_north_south_after = aligningEastWest.centeredEastWest.to(aligningNorthSouth.goingNorthSouth)

        centered.from_(aligningEastWest.centeredEastWest,aligningNorthSouth.centeredNorthSouth)
        
    alignWithGap = State()
    enteringGap = State()

    # class callFollower(State.Compound):
    #     sendingMessage = State()
    #     waiting = State()
    #     followerNearby = State()

    # class deadEnd(State.Compound):
    #     #Je rotationne pas pour le moment
    #     print("Aligned due to no rotation")

    # class failure(State.Compound):
    #     sendingData = State()
    #     goingDown = State()

    takeoff.to(followTheGap, cond="checkTop")
    followTheGap.to(centerInIntersection, cond="moreThanTwoGaps")
    align = centerInIntersection.to(alignWithGap)
    gap_chose = alignWithGap.to(enteringGap)
    follow = enteringGap.to(followTheGap)
    # alignWithGap.to(callFollower, cond="directionChanged")
    # followTheGap.to(callFollower, cond="directionChanged")
    # callFollower.to(followTheGap, cond="followerClose")
    # followTheGap.to(deadEnd, cond="oneGap")
    tick = (
        takeoff.to.itself(internal=True)
        | followTheGap.to.itself(internal=True)
    ) 


    def checkTop(self):
        return DroneMachine.takeoff.top in self.configuration
    
    # def goodDirection(self):
    #     return self.yaw == self.gap_direction
    
    def moreThanTwoGaps(self):
        return self.number_of_gaps > 2
    
    # def directionChanged(self):
    #     return self.gap_direction != self.previous_gap_direction
    
    # def oneGap(self):
    #     return self.number_of_gaps == 1
    
    def centered(self):
        return DroneMachine.centerInIntersection.centered in self.configuration

    # def followerClose(self):
    #     return self.followerIsClose
    
    def execute(self):
        self.send("tick")
        print(self.configuration)
        self.action = [0,0,0,0,0]


        ### Takeoff ###
        if DroneMachine.takeoff.stoped in self.configuration:
            self.send('takingoff')
            print("Takingoff")
        if DroneMachine.takeoff.goingUp in self.configuration:
            self.send("flying")
            print(self.position)
            print("Increasing height")
        if DroneMachine.takeoff.top in self.configuration:
            self.action = [0,0,0,0,0]
            print("Reached the top !")
        


        ### Follow the gap ###
        if DroneMachine.followTheGap.movingForward.moving in self.configuration:
            if self.current_active_direction != None:
                self.front = self.current_active_direction
            dir = ["West","North","East","South"]
            print(self.front)
            if self.front == "North":
                i = 0
            elif self.front == "East":
                i = 1
            elif self.front == "South":
                i = 2
            elif self.front == "West":
                i = 3
            action_dir = {"West":[-0.5,0,0,0,0],"North":[0,0.5,0,0,0],"East":[0.5,0,0,0,0],"South":[0,-0.5,0,0,0]}
            #print("Moving")
            self.previous_active_direction = self.current_active_direction
            print(dir[i%4])
            print(dir[i%4] in self.gaps_dir)
            if dir[i%4] in self.gaps_dir:
                for j in range(len(self.action)):
                    self.action[j] += action_dir[dir[i%4]][j]
                self.current_active_direction = dir[i%4]
                print(self.current_active_direction)
                print(self.action)
            elif dir[(i+1)%4] in self.gaps_dir:
                for j in range(len(self.action)):
                    self.action[j] += action_dir[dir[(i+1)%4]][j]
                self.current_active_direction = dir[(i+1)%4]
            elif dir[(i+2)%4] in self.gaps_dir:
                for j in range(len(self.action)):
                    self.action[j] += action_dir[dir[(i+2)%4]][j]
                self.current_active_direction = dir[(i+2)%4]
            elif dir[(i+3)%4] in self.gaps_dir:
                for j in range(len(self.action)):
                    self.action[j] += action_dir[dir[(i+3)%4]][j]
                self.current_active_direction = dir[(i+3)%4]
        
        if DroneMachine.followTheGap.aligning.correctingEastWest in self.configuration:
            self.action[0] += self.dist_wall/10
            print("Correcting East/West center")
        
        if DroneMachine.followTheGap.aligning.correctingNorthSouth in self.configuration:
            self.action[1] += self.dist_wall/10
            print("Correcting North/South center")
        
        # if DroneMachine.followTheGap.movingForward.stopped in self.configuration:
        #     print("Stopped")
        #     self.action = [0,0,0,0,0]
        #     self.send("continue_moving")



        ### Center in intersection ###
        if DroneMachine.centerInIntersection.enteringIntersection in self.configuration:
            self.is_centered_east_west = False
            self.is_centered_north_south = False
            self.intersection_start = []
            for val in self.position:
                self.intersection_start.append(val)
            print(self.current_active_direction)
            match self.current_active_direction:
                case w if w in ["North", "South"]:
                    self.send("center_north_south_from_start")
                case w if w in ["East", "West"]:
                    self.send("center_east_west_from_start")
            

        if DroneMachine.centerInIntersection.aligningEastWest.goingEastWest in self.configuration:
            if self.current_active_direction == "East":
                center = -0.6
            elif self.current_active_direction == "West":
                center = 0.6
            distance = self.position[0] - self.intersection_start[0] + center
            if distance > 0.1 or distance < -0.1:
                self.action = [-distance,0,0,0,0]
                self.is_centered_east_west = False
            else:
                self.is_centered_east_west = True
                self.action = [0,0,0,0,0]
                if not self.is_centered_north_south:
                    self.send("center_north_south_after")
        
        if DroneMachine.centerInIntersection.aligningNorthSouth.goingNorthSouth in self.configuration:
            if self.current_active_direction == "North":
                center = -0.6
            elif self.current_active_direction == "South":
                center = 0.6
            print("Center : " + str(center))
            distance = self.position[1] - self.intersection_start[1] + center
            print("Distance : " + str(distance))
            if distance > 0.1 or distance < -0.1:
                self.action = [0,-distance,0,0,0]
                self.is_centered_north_south = False
            else:
                self.is_centered_north_south = True
                self.action = [0,0,0,0,0]
                if not self.is_centered_east_west:
                    self.send("center_east_west_after")
        
        if DroneMachine.centerInIntersection.centered in self.configuration:
            self.action = [0,0,0,0,0]
            already_visited = False
            for i in range(len(self.intersection_visited)):
                intersection = self.intersection_visited[i]
                if self.position[0]<intersection["Area"]["x"][1] and self.position[0]>intersection["Area"]["x"][0] and self.position[1]<intersection["Area"]["y"][1] and self.position[1]>intersection["Area"]["y"][0]:
                    already_visited = True
                    id_intersection = i
            if already_visited:
                match self.current_active_direction:
                    case "North":
                        self.intersection_visited[id_intersection]["Visited"][0] = 1
                    case "East":
                        self.intersection_visited[id_intersection]["Visited"][1] = 1
                    case "South":
                        self.intersection_visited[id_intersection]["Visited"][2] = 1
                    case "West":
                        self.intersection_visited[id_intersection]["Visited"][3] = 1
                self.current_intersection = self.intersection_visited[id_intersection]
            elif not already_visited:
                self.intersection_visited.append({"Area" : {"x":[self.position[0]-0.8,self.position[0]+0.8],"y":[self.position[1]-0.8,self.position[1]+0.8]}, "Visited" : {"North":False,"South":False,"East":False,"West":False}})
                match self.current_active_direction:
                    case "North":
                        self.intersection_visited[-1]["Visited"][0] = 1
                    case "East":
                        self.intersection_visited[-1]["Visited"][1] = 1
                    case "South":
                        self.intersection_visited[-1]["Visited"][2] = 1
                    case "West":
                        self.intersection_visited[-1]["Visited"][3] = 1
                self.current_intersection = self.intersection_visited[-1]
            self.send("align")
        
        if DroneMachine.alignWithGap in self.configuration:
            print("AligningGap")
            if self.current_active_direction != None:
                self.front = self.current_active_direction
            print(self.front)
            dir = ["West","North","East","South"]
            if self.front == "North":
                i = 0
            elif self.front == "East":
                i = 1
            elif self.front == "South":
                i = 2
            elif self.front == "West":
                i = 3
            if dir[i%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[i%4]]:
                self.current_active_direction = dir[i%4]
            elif dir[(i+1)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+1)%4]]:
                self.current_active_direction = dir[(i+1)%4]
            elif dir[(i+2)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+2)%4]]:
                self.current_active_direction = dir[(i+2)%4]
            elif dir[(i+3)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+3)%4]]:
                self.current_active_direction = dir[(i+3)%4]
            print(self.current_active_direction)
            self.send("gap_chose")
        
        if DroneMachine.enteringGap in self.configuration:
            # if self.begin_entering_gap:
            #     self.begin_entering_gap = False
            #     self.inital_position = []
            #     for val in self.position:
            #         self.inital_position.append(val)
            action_dir = {"West":[-0.5,0,0,0,0],"North":[0,0.5,0,0,0],"East":[0.5,0,0,0,0],"South":[0,-0.5,0,0,0]}
            self.action = action_dir[self.current_active_direction]
            # if self.current_active_direction in ["North", "East"]:
            #     direction = -1.2
            # elif self.current_active_direction in ["South", "West"]:
            #     direction = 1.2
            # if self.current_active_direction in ["North", "South"]:
            #     distance = self.position[1] - self.inital_position[1] + direction
            # if self.current_active_direction in ["East", "West"]:
            #     distance = self.position[0] - self.inital_position[0] + direction
            # if abs(distance) < 0.1:
            #     self.begin_entering_gap = True
            if self.number_of_gaps <= 2:
                self.send("follow")

            
        # print(self.configuration)
        # if DroneMachine.followTheGap in self.configuration:
        #     print(self.gaps_dir)
        #     print(self.is_centered)
        #     print(self.rays)
        #     print(self.current_active_direction)

        print(self.action)

        # if self.centerInIntersection.is_active:
        #     #Soit utiliser le cone pour et dire que si la distance minimale est >2 mètres on est centré
        #     #Soit la technique de mettre le drone de travers pour faire correspondre les distances minimales avec les angles
        #     self.action

        # if self.alignWithGap.is_active:
        #     while self.yaw != self.gap_direction:
        #         if self.yaw < self.gap_direction:
        #             self.yaw += self.gap_direction-self.yaw
        #         else:
        #             self.yaw += self.yaw - self.gap_direction
        
        # if self.deadEnd.is_active:
        #     init_yaw = self.yaw
        #     while self.yaw != init_yaw -180:
        #         self.yaw += 10

    def process_lidar(self,rays):
        #### Centered ####
        
        #Follow the gap
        if DroneMachine.followTheGap.aligning in self.configuration:
            match self.current_active_direction:
                case w if w in ["North", "South"]:
                    if abs(rays[1]-rays[3]) < 0.1:
                        self.is_centered = True
                        self.dist_wall = 0
                    else:
                        self.dist_wall = rays[1]-rays[3]
                        self.is_centered = False
                case w if w in ["East", "West"]:
                    if abs(rays[0]-rays[2]) < 0.1:
                        self.is_centered = True
                        self.dist_wall = 0
                    else:
                        self.dist_wall = rays[0]-rays[2]
                        self.is_centered = False
        #Intersection

        #### Gaps ####
        self.previous_gap_dir = [val for val in self.gaps_dir]
        self.gaps_dir = []
        for i in range(len(rays)):
            if rays[i] > 0.85:
                match i:
                    case 0:
                        self.gaps_dir.append("North")
                    case 1:
                        self.gaps_dir.append("East")
                    case 2:
                        self.gaps_dir.append("South")
                    case 3:
                        self.gaps_dir.append("West")
        print(self.gaps_dir)
        self.number_of_gaps = len(self.gaps_dir)
        print(self.number_of_gaps)

if __name__ == "__main__":
    #Init Machine
    drone = DroneMachine()
    print('coucou')

    #Generate diagram
    if GENRERATE_DIAGRAM:
        open(f"Images/order_control_machine_initial_{time.strftime("%d%m%Y_%H%M%S")}.png","w")
        graph = DotGraphMachine(DroneMachine)
        dot = graph()
        dot.to_string()
        dot.write_png(f"Images/order_control_machine_initial_{time.strftime("%d%m%Y_%H%M%S")}.png")

    # #Run
    # for i in range(10):
    #     drone.execute()