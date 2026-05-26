class takeoff(State.Compound):
    goingUp = State()
    top = State(final=True)

    goingUp.to(top, cond='topHeight')

    def topHeight(self):
        return self.position[2] > 0.99