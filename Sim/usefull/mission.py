class mission(State.Parallel):
    class movements(State.Compound):
        class waitingLeader(State.Compound):
            waiting = State(initial=True)
            can_move = State(final=True)

            waiting.to(can_move, cond="my_message_received")
            
            def my_message_received(self):
                return len(self.leader_message) > 0 and self.leader_message[-1] == "come_closer"

        class comeCloser(State.Parallel):
            class aligning(State.Compound):
                correctingNothing = State(initial=True)
                correctingNorthSouth = State()
                correctingEastWest = State()
                stopAligning = State(final=True)

                correctingNorthSouth.to(correctingNothing, cond='centered')
                correctingEastWest.to(correctingNothing, cond='centered')

                correctingNothing.to(correctingNorthSouth, cond=['not_centered', 'dirEastWest'])
                correctingNothing.to(correctingEastWest, cond=['not_centered', 'dirNorthSouth'])

                correctingNothing.to(stopAligning, cond="closeToLeader")
                correctingNorthSouth.to(stopAligning, cond="closeToLeader")
                correctingEastWest.to(stopAligning, cond="closeToLeader")

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
                cornerEntry = State(final=True)
                
                moving.to(cornerEntry, cond="closeToLeader")
                

                def on_exit_cornerEntry(self):
                    print("Follower :leaving Corner entry")
                
                def on_enter_cornerEntry(self):
                    if len(self.preceding.message_received) == 0 or self.preceding.message_received[-1] != "continue moving":
                        print("Follower :Sending message")
                        self.preceding.message_received.append("continue moving")
                        print(self.preceding.message_received)
                        print(self.configuration)
                    print("Follower :entering Corner entry")
                
                def on_enter_waitingLeaderToGo(self):
                    print("Follower :entering waiting leader to go")

                def on_exit_waitingLeaderToGo(self):
                    print("Follower :Leaving waiting leader to go")

            def closeToLeader(self):
                return self.close_to_leader and FollowerMachine.mission.movements.comeCloser.movingForward.moving in self.configuration

            def left_intersection_received(self):
                if len(self.leader_message) > 0 and "left_intersection" in self.leader_message:
                    print("Follower :Leader as left intersection")
                return len(self.leader_message) > 0 and "left_intersection" in self.leader_message
                
            def middleOfTheCorner(self):
                return self.centered_in_corner
        
        waitingLeaderToGo = State()
        # inCorner = State()
        # centeredInCorner = State(final=True)

        waitingFollower = State()
        # waitingLeaderToGo.to(inCorner, cond='left_intersection_received')
        # inCorner.to(centeredInCorner, cond='middleOfTheCorner')

        # class centerInIntersection(State.Compound):
        #     enteringIntersection = State(initial=True)
        #     centered = State(final=True)

        #     class aligningEastWest(State.Compound):
        #         goingEastWest = State()
        #         centeredEastWest = State(final=True)

        #         goingEastWest.to(centeredEastWest, cond='centered_EastWest')

        #         def centered_EastWest(self):
        #             return self.is_centered_east_west

        #     class aligningNorthSouth(State.Compound):
        #         goingNorthSouth = State()
        #         centeredNorthSouth = State(final=True)

        #         goingNorthSouth.to(centeredNorthSouth, cond='centered_NorthSouth')

        #         def centered_NorthSouth(self):
        #             return self.is_centered_north_south

        #     center_east_west_from_start = enteringIntersection.to(aligningEastWest.goingEastWest)
        #     center_north_south_from_start = enteringIntersection.to(aligningNorthSouth.goingNorthSouth)

        #     center_east_west_after = aligningNorthSouth.centeredNorthSouth.to(aligningEastWest.goingEastWest)
        #     center_north_south_after = aligningEastWest.centeredEastWest.to(aligningNorthSouth.goingNorthSouth)

        #     centered.from_(aligningEastWest.centeredEastWest,aligningNorthSouth.centeredNorthSouth)


        # alignWithGap = State()
        # enteringGap = State()

        done_state_waitingLeader = waitingLeader.to(comeCloser)
        done_state_comeCloser = comeCloser.to(waitingLeaderToGo)
        coms_received = waitingLeaderToGo.to(waitingFollower)
        # comeCloser.to(centerInIntersection, cond="moreThanTwoGaps")
        # align = centerInIntersection.to(alignWithGap)
        # gap_chose = alignWithGap.to(enteringGap)
        # follow = enteringGap.to(comeCloser)

        # class callFollower(State.Compound):
        #     sendingMessage = State()
        #     waiting = State()
        #     followerNearby = State()

        # class deadEnd(State.Compound):
        #     #Je rotationne pas pour le moment
        #     print("Follower :Aligned due to no rotation")

        # class failure(State.Compound):
        #     sendingData = State()
        #     goingDown = State()

        # alignWithGap.to(callFollower, cond="directionChanged")
        # comeCloser.to(callFollower, cond="directionChanged")
        # callFollower.to(comeCloser, cond="followerClose")
        # comeCloser.to(deadEnd, cond="oneGap")
    class height(State.Compound):
        goodHeight = State(initial=True)
        correctingHeight = State()

        goodHeight.to(correctingHeight, unless='checkHeight')
        correctingHeight.to(goodHeight, cond='checkHeight')

        tick_height = (
            goodHeight.to.itself(internal=True)
            | correctingHeight.to.itself(internal=True)
        )