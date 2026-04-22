#Imports
from statemachine import StateChart, State

#Const
GENRERATE_DIAGRAM = False

#Classes
class DroneMachine(StateChart):
    position = [0,0,0]
    is_centered = None
    current_active_direction = None
    previous_active_direction = None
    gaps_dir = []
    previous_gap_dir = []
    dist_wall = 0
    rays = None

    class takeoff(State.Compound):
        stoped = State(initial=True)
        goingUp = State()
        top = State(final=True)

        takingoff = stoped.to(goingUp, cond="ready")
        
        flying = goingUp.to.itself(internal=True, on="do_goingUp")
        
        goingUp.to(top, cond='topHeight')

        def ready(self):
            return input('Are you ready ? y/n') == 'y'
        
        def do_goingUp(self):
            self.action = [0,0,1/20,0,0]
        
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
            stopped = State()
            #waiting_follower = State()

            moving.to(stopped, cond='dir_changed')

            continue_moving = stopped.to(moving)
    
            def dir_changed(self):
                if self.previous_active_direction != None:
                    return self.previous_active_direction == self.current_active_direction
                else:
                    return False
            

    # class centerInIntersection(State.Compound):
    #     class aligningEastWest(State.Compound):
    #         goingEast = State()
    #         goingWest = State()
    #         centeredEastWest = State(final=True)

    #         goingEast.to(centeredEastWest, cond='centered')
    #         goingWest.to(centeredEastWest, cond='centered')

    #         def centered(self):
    #             return self.is_centered

            

    #     class aligningNorthSouth(State.Compound):
    #         goingNorth = State()
    #         goingSouth = State()
    
    # class alignWithGap(State.Compound):
    #     #Je rotationne pas pour le moment
    #     print("Aligned due to no rotation")

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
    # followTheGap.to(centerInIntersection, cond="moreThanTwoGaps")
    # centerInIntersection.to(alignWithGap, cond="centered")
    # alignWithGap.to(callFollower, cond="directionChanged")
    # followTheGap.to(callFollower, cond="directionChanged")
    # callFollower.to(followTheGap, cond="followerClose")
    # followTheGap.to(deadEnd, cond="oneGap")

    # def __init__(self,name):
    #     super().__init__()
    #     self.name = name
    #     self.height = 50
    #     self.yaw = 0
    #     self.gap_direction = None
    #     self.number_of_gaps = None
    #     self.previous_gap_direction = None
    #     self.centeredInGap = None
    #     self.followerIsClose = None
    #     self.is_centered = None
    #     self.action = [0,0,0, 0, 0] #vx,vy,vz,speed_frac,wz

    def checkTop(self):
        return DroneMachine.takeoff.top in self.configuration
    
    # def goodDirection(self):
    #     return self.yaw == self.gap_direction
    
    # def moreThanTwoGaps(self):
    #     return self.number_of_gaps > 2
    
    # def directionChanged(self):
    #     return self.gap_direction != self.previous_gap_direction
    
    # def oneGap(self):
    #     return self.number_of_gaps == 1
    
    # def centered(self):
    #     return self.centeredInGap

    # def followerClose(self):
    #     return self.followerIsClose
    
    def execute(self):
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
        
        if DroneMachine.followTheGap.movingForward.moving in self.configuration:
            print("Moving")
            self.previous_active_direction = self.current_active_direction
            if "West" in self.gaps_dir:
                self.action = [-0.5/10,0,0,0,0]
                self.current_active_direction = "West"
            elif "North" in self.gaps_dir:
                self.action = [0,0.5/10,0,0,0]
                self.current_active_direction = "North"
            elif "East" in self.gaps_dir:
                self.action = [0.5/10,0,0,0,0]
                self.current_active_direction = "East"
            elif "South" in self.gaps_dir:
                self.action = [0,-0.5/10,0,0,0]
                self.current_active_direction = "South"
            
        print(self.configuration)
        if DroneMachine.followTheGap in self.configuration:
            print(self.gaps_dir)
            print(self.is_centered)
            print(self.rays)
            print(self.current_active_direction)

        if DroneMachine.followTheGap.aligning.correctingEastWest in self.configuration:
            self.action = [0,self.dist_wall/10,0,0,0]
            print("Correcting East/West center")
        
        if DroneMachine.followTheGap.aligning.correctingNorthSouth in self.configuration:
            self.action = [self.dist_wall/10,0,0,0,0]
            print("Correcting North/South center")
        
        
            
        if DroneMachine.followTheGap.movingForward.stopped in self.configuration:
            print("Stopped")
            self.action = [0,0,0,0,0]
            self.send("continue_moving",delay=2000)
        
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
        self.rays = rays
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
                case w if w in ["East", "West"]:
                    if abs(rays[0]-rays[2]) < 0.1:
                        self.is_centered = True
                        self.dist_wall = 0
                    else:
                        self.dist_wall = rays[0]-rays[2]
        #Intersection

        #### Gaps ####
        self.previous_gap_dir = [val for val in self.gaps_dir]
        self.gaps_dir = []
        for i in range(len(rays)):
            if rays[i] > 2:
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
            

if __name__ == "__main__":
    #Init Machine
    drone = DroneMachine()
    print('coucou')

    #Generate diagram
    if GENRERATE_DIAGRAM:
        try:
            img_path = "docs/images/readme_trafficlightmachine.png"
            drone._graph().write_png(img_path)
        except:
            print("Need dot to generate diagram")

    #Run
    for i in range(10):
        drone.execute()