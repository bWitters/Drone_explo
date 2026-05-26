class mission(State.Parallel):
        class movements(State.Compound):
            class followTheGap(State.Parallel):
                class aligning(State.Compound):
                    correctingNothing = State(initial=True)
                    correctingNorthSouth = State()
                    correctingEastWest = State()

                    waiting_follower = State(final=True)



                    correctingNorthSouth.to(correctingNothing, cond='centered')
                    correctingEastWest.to(correctingNothing, cond='centered')

                    correctingNothing.to(correctingNorthSouth, cond=['not_centered', 'dirEastWest'])
                    correctingNothing.to(correctingEastWest, cond=['not_centered', 'dirNorthSouth'])

                    correctingNorthSouth.to(waiting_follower, cond="dir_changed")
                    correctingEastWest.to(waiting_follower, cond="dir_changed")
                    correctingNothing.to(waiting_follower, cond="dir_changed")

                    def centered(self):
                        return self.is_centered

                    def not_centered(self):
                        return not self.is_centered

                    def dirNorthSouth(self):
                        return self.current_active_direction in ["North", "South"]

                    def dirEastWest(self):
                        return self.current_active_direction in ["East", "West"]

                    def dir_changed(self):
                        print(self.previous_active_direction)
                        print(self.current_active_direction)
                        if self.previous_active_direction != None:
                            return self.previous_active_direction != self.current_active_direction
                        return False

                class movingForward(State.Compound):
                    moving = State(initial = True)
                    centering_in_corner = State()
                    waiting_follower_to_move = State(final=True)

                    moving.to(centering_in_corner, cond='dir_changed')
                    centering_in_corner.to(waiting_follower_to_move, cond='centered_in_corner')

                    def centered_in_corner(self):
                        return self.middle_of_corner[0]

                    def dir_changed(self):
                        if self.previous_active_direction != None:
                            return self.previous_active_direction != self.current_active_direction
                        return False
            
            waitingFollower = State()

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

            done_state_followTheGap = followTheGap.to(waitingFollower)
            coucou_trop_bien = waitingFollower.to(followTheGap)
            followTheGap.to(centerInIntersection, cond="moreThanTwoGaps")
            align = centerInIntersection.to(alignWithGap)
            gap_chose = alignWithGap.to(enteringGap)
            follow = enteringGap.to(followTheGap)

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

            # alignWithGap.to(callFollower, cond="directionChanged")
            # followTheGap.to(callFollower, cond="directionChanged")
            # callFollower.to(followTheGap, cond="followerClose")
            # followTheGap.to(deadEnd, cond="oneGap")
        class height(State.Compound):
            goodHeight = State(initial=True)
            correctingHeight = State()

            goodHeight.to(correctingHeight, unless='checkHeight')
            correctingHeight.to(goodHeight, cond='checkHeight')

            tick_height = (
                goodHeight.to.itself(internal=True)
                | correctingHeight.to.itself(internal=True)
            )