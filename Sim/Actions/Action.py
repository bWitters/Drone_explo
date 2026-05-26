
from statemachine import StateChart, State

from abc import abstractmethod

class Action(StateChart):
    Active = State()
    Inactive = State(initial=True)

    activate = Inactive.to(Active)
    deactivate = Active.to(Inactive)

    def __init__(self, name: str = None, **kwargs):
        self.name = name

        super().__init__(**kwargs)

    def on_enter_state(self, state):
        if state == self.name:
            self.activate()

    def on_exit_state(self, state):
        if state == self.name:
            self.deactivate()

    @abstractmethod
    def action(self, **kwargs):
        pass