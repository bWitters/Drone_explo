def execute(self):
    self.send("tick")
    self.send("tick_height")
    print("Follower")
    print(self.configuration)
    self.action = [0,0,0,0,0]


    ### Takeoff ###
    if FollowerMachine.takeoff.goingUp in self.configuration:
        distance = 1 - self.position[2]
        self.action[2] = distance
        print("Follower :Increasing height")
    if FollowerMachine.takeoff.top in self.configuration:
        self.action = [0,0,0,0,0]
        print("Follower :Reached the top !")

    ### Height conrol ###
    if FollowerMachine.mission.height.correctingHeight in self.configuration:
        distance = 1 - self.position[2]
        self.action[2] += distance

    ### Follow the gap ###
    if FollowerMachine.mission.movements.comeCloser.movingForward.moving in self.configuration:
        if self.current_active_direction != None:
            self.front = self.current_active_direction
        dir = ["West","North","East","South"]
        if self.front == "North":
            i = 0
        elif self.front == "East":
            i = 1
        elif self.front == "South":
            i = 2
        elif self.front == "West":
            i = 3
        action_dir = {"West":[-0.5,0,0,0,0],"North":[0,0.5,0,0,0],"East":[0.5,0,0,0,0],"South":[0,-0.5,0,0,0]}
        #print("Follower :Moving")
        self.previous_active_direction = self.current_active_direction
        if dir[i%4] in self.gaps_dir:
            for j in range(len(self.action)):
                self.action[j] += action_dir[dir[i%4]][j]
            self.current_active_direction = dir[i%4]
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
        if self.previous_active_direction != None:
            print("Follower :Previous : " + self.previous_active_direction)
        print("Follower :Active : " + self.current_active_direction)

    if FollowerMachine.mission.movements.comeCloser.aligning.correctingEastWest in self.configuration:
        self.action[0] += self.dist_wall/10
        print("Follower :Correcting East/West center")

    if FollowerMachine.mission.movements.comeCloser.aligning.correctingNorthSouth in self.configuration:
        self.action[1] += self.dist_wall/10
        print("Follower :Correcting North/South center")

    ### Waiting follower ###
    if FollowerMachine.mission.movements.waitingFollower in self.configuration:
        self.action = [0,0,0,0,0]
        if self.follower != None:
            self.follower.send("come_closer")

    # ### Center in intersection ###
    # if FollowerMachine.mission.movements.centerInIntersection.enteringIntersection in self.configuration:
    #     print("Follower :Coucou, plus de deux gaps apparemment : " + str(self.number_of_gaps))
    #     self.is_centered_east_west = False
    #     self.is_centered_north_south = False
    #     self.intersection_start = []
    #     for val in self.position:
    #         self.intersection_start.append(val)
    #     match self.current_active_direction:
    #         case w if w in ["North", "South"]:
    #             self.send("center_north_south_from_start")
    #         case w if w in ["East", "West"]:
    #             self.send("center_east_west_from_start")


    # if FollowerMachine.mission.movements.centerInIntersection.aligningEastWest.goingEastWest in self.configuration:
    #     if self.current_active_direction == "East":
    #         center = -0.6
    #     elif self.current_active_direction == "West":
    #         center = 0.6
    #     distance = self.position[0] - self.intersection_start[0] + center
    #     if distance > 0.1 or distance < -0.1:
    #         self.action = [-distance,0,0,0,0]
    #         self.is_centered_east_west = False
    #     else:
    #         self.is_centered_east_west = True
    #         self.action = [0,0,0,0,0]
    #         if not self.is_centered_north_south:
    #             self.send("center_north_south_after")

    # if FollowerMachine.mission.movements.centerInIntersection.aligningNorthSouth.goingNorthSouth in self.configuration:
    #     if self.current_active_direction == "North":
    #         center = -0.6
    #     elif self.current_active_direction == "South":
    #         center = 0.6
    #     print("Follower :Center : " + str(center))
    #     distance = self.position[1] - self.intersection_start[1] + center
    #     print("Follower :Distance : " + str(distance))
    #     if distance > 0.1 or distance < -0.1:
    #         self.action = [0,-distance,0,0,0]
    #         self.is_centered_north_south = False
    #     else:
    #         self.is_centered_north_south = True
    #         self.action = [0,0,0,0,0]
    #         if not self.is_centered_east_west:
    #             self.send("center_east_west_after")

    # if FollowerMachine.mission.movements.centerInIntersection.centered in self.configuration:
    #     self.action = [0,0,0,0,0]
    #     already_visited = False
    #     for i in range(len(self.intersection_visited)):
    #         intersection = self.intersection_visited[i]
    #         if self.position[0]<intersection["Area"]["x"][1] and self.position[0]>intersection["Area"]["x"][0] and self.position[1]<intersection["Area"]["y"][1] and self.position[1]>intersection["Area"]["y"][0]:
    #             already_visited = True
    #             id_intersection = i
    #     if already_visited:
    #         match self.current_active_direction:
    #             case "North":
    #                 self.intersection_visited[id_intersection]["Visited"][0] = 1
    #             case "East":
    #                 self.intersection_visited[id_intersection]["Visited"][1] = 1
    #             case "South":
    #                 self.intersection_visited[id_intersection]["Visited"][2] = 1
    #             case "West":
    #                 self.intersection_visited[id_intersection]["Visited"][3] = 1
    #         self.current_intersection = self.intersection_visited[id_intersection]
    #     elif not already_visited:
    #         self.intersection_visited.append({"Area" : {"x":[self.position[0]-0.8,self.position[0]+0.8],"y":[self.position[1]-0.8,self.position[1]+0.8]}, "Visited" : {"North":False,"South":False,"East":False,"West":False}})
    #         match self.current_active_direction:
    #             case "North":
    #                 self.intersection_visited[-1]["Visited"][0] = 1
    #             case "East":
    #                 self.intersection_visited[-1]["Visited"][1] = 1
    #             case "South":
    #                 self.intersection_visited[-1]["Visited"][2] = 1
    #             case "West":
    #                 self.intersection_visited[-1]["Visited"][3] = 1
    #         self.current_intersection = self.intersection_visited[-1]
    #     self.send("align")

    
    # ### Align with gap ###
    # if FollowerMachine.mission.movements.alignWithGap in self.configuration:
    #     print("Follower :AligningGap")
    #     if self.current_active_direction != None:
    #         self.front = self.current_active_direction
    #     dir = ["West","North","East","South"]
    #     if self.front == "North":
    #         i = 0
    #     elif self.front == "East":
    #         i = 1
    #     elif self.front == "South":
    #         i = 2
    #     elif self.front == "West":
    #         i = 3
    #     if dir[i%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[i%4]]:
    #         self.current_active_direction = dir[i%4]
    #     elif dir[(i+1)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+1)%4]]:
    #         self.current_active_direction = dir[(i+1)%4]
    #     elif dir[(i+2)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+2)%4]]:
    #         self.current_active_direction = dir[(i+2)%4]
    #     elif dir[(i+3)%4] in self.gaps_dir and not self.current_intersection["Visited"][dir[(i+3)%4]]:
    #         self.current_active_direction = dir[(i+3)%4]
    #     self.send("gap_chose")


    # ### Entering Gap ###
    # if FollowerMachine.mission.movements.enteringGap in self.configuration:
    #     # if self.begin_entering_gap:
    #     #     self.begin_entering_gap = False
    #     #     self.inital_position = []
    #     #     for val in self.position:
    #     #         self.inital_position.append(val)
    #     action_dir = {"West":[-0.5,0,0,0,0],"North":[0,0.5,0,0,0],"East":[0.5,0,0,0,0],"South":[0,-0.5,0,0,0]}
    #     self.action = action_dir[self.current_active_direction]
    #     # if self.current_active_direction in ["North", "East"]:
    #     #     direction = -1.2
    #     # elif self.current_active_direction in ["South", "West"]:
    #     #     direction = 1.2
    #     # if self.current_active_direction in ["North", "South"]:
    #     #     distance = self.position[1] - self.inital_position[1] + direction
    #     # if self.current_active_direction in ["East", "West"]:
    #     #     distance = self.position[0] - self.inital_position[0] + direction
    #     # if abs(distance) < 0.1:
    #     #     self.begin_entering_gap = True
    #     if self.number_of_gaps <= 2:
    #         self.send("follow")
        
    if FollowerMachine.mission.movements.waitingLeaderToGo in self.configuration:
        self.action = [0,0,0,0,0]
        print("Follower :waiting leader to go")

    print(self.action)
    print(self.configuration)

    # print(self.configuration)
    # if FollowerMachine.mission.movements.comeCloser in self.configuration:
    #     print(self.gaps_dir)
    #     print(self.is_centered)
    #     print(self.rays)
    #     print(self.current_active_direction)

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