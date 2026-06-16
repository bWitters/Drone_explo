import logging

# from agents import Drones

from statemachine import StateChart, State

from abc import abstractmethod

logger = logging.getLogger("Behavior generic class")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()

formatter = logging.Formatter("(%(name)s)[%(levelname)s]: %(message)s")

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def _build_standby(namespace:dict[str,object]):
    standby = None
    for _name, _sub in namespace.items():
        if _name.startswith("Sub_") and isinstance(_sub, State):
            _initial     = next(s for s in _sub.states if s.initial)
            _non_initial = [s for s in _sub.states if not s.initial]
            for _s in _non_initial:
                t = _s.to(_initial)
                standby = t if standby is None else standby | t
    return standby

class Behavior(StateChart):
    Inactive = State(initial=True)

    class Active(State.Parallel):
        class Extra_HeightControl(State.Compound):
            Idle_HeightControl = State(initial=True)
            HeightControl = State()

            do_HeightControl = Idle_HeightControl.to(HeightControl)
            standby_HeightControl = HeightControl.to(Idle_HeightControl)

        class Extra_RotationControl(State.Compound):
            Idle_RotationControl = State(initial=True)
            RotationControl = State()

            do_RotationControl = Idle_RotationControl.to(RotationControl)
            standby_RotationControl = RotationControl.to(Idle_RotationControl)

        class Sub_SendReconfig(State.Compound):
            Idle_SendReconfig = State(initial=True)
            SendReconfig = State()

            do_SendReconfig = Idle_SendReconfig.to(SendReconfig)
            standby_SendReconfig = SendReconfig.to(Idle_SendReconfig)
        
        class Sub_SendCurrentDirection(State.Compound):
            Idle_SendCurrentDirection = State(initial=True)
            SendCurrentDirection = State()

            do_SendCurrentDirection = Idle_SendCurrentDirection.to(SendCurrentDirection)
            standby_SendCurrentDirection = SendCurrentDirection.to(Idle_SendCurrentDirection)
        
        class Sub_ForcedWaiting(State.Compound):
            Idle_ForcedWaiting = State(initial=True)
            ForcedWaiting = State()

            do_ForcedWaiting = Idle_ForcedWaiting.to(ForcedWaiting)
            standby_ForcedWaiting = ForcedWaiting.to(Idle_ForcedWaiting)
        
        class Sub_CenterInIntersection(State.Compound):
            Idle_CenterInIntersection = State(initial=True)
            CenterInIntersection = State()

            do_CenterInIntersection = Idle_CenterInIntersection.to(CenterInIntersection)
            standby_CenterInIntersection = CenterInIntersection.to(Idle_CenterInIntersection)

        class Sub_Takeoff(State.Compound):
            Idle_Takeoff = State(initial=True)
            Takeoff = State()

            do_takeoff = Idle_Takeoff.to(Takeoff)
            standby_takeoff = Takeoff.to(Idle_Takeoff)
        
        class Sub_CenterInCurve(State.Compound):
            Idle_CenterInCurve = State(initial=True)
            CenterInCurve = State()

            do_CenterInCurve = Idle_CenterInCurve.to(CenterInCurve)
            standby_CenterInCurve = CenterInCurve.to(Idle_CenterInCurve)
            
        class Sub_Stop(State.Compound):
            Idle_Stop = State(initial=True)
            Stop = State()

            do_stop = Idle_Stop.to(Stop)
            standby_stop = Stop.to(Idle_Stop)
        
        class Sub_SendComeCloser(State.Compound):
            Idle_SendComeCloser = State(initial=True)
            SendComeCloser = State()

            do_send_come_closer = Idle_SendComeCloser.to(SendComeCloser)
            standby_send_come_closer = SendComeCloser.to(Idle_SendComeCloser)
        
        class Sub_Test(State.Compound):
            Idle_Test = State(initial=True)
            Test = State()

            do_test = Idle_Test.to(Test)
            standby_test = Test.to(Idle_Test)
            
        class Sub_Move(State.Compound):
            Idle_Move = State(initial=True)
            Move = State()

            do_move = Idle_Move.to(Move)
            standby_move = Move.to(Idle_Move)

        class Sub_TurnAround(State.Compound):
            Idle_TurnAround = State(initial=True)
            TurnAround = State()

            do_turn_around = Idle_TurnAround.to(TurnAround)
            standby_turn_around = TurnAround.to(Idle_TurnAround)

        class Sub_Rotation(State.Compound):
            Idle_Rotation = State(initial=True)
            Rotation = State()

            do_rotation = Idle_Rotation.to(Rotation)
            standby_rotation = Rotation.to(Idle_Rotation)
            
        class Sub_ChangeRole(State.Compound):
            Idle_ChangeRole = State(initial=True)
            ChangeRole = State()

            do_change_role = Idle_ChangeRole.to(ChangeRole)
            standby_change_role = ChangeRole.to(Idle_ChangeRole)
        
        class Sub_GapDirectionDetermination(State.Compound):
            Idle_GapDirectionDetermination = State(initial=True)
            GapDirectionDetermination = State()

            do_GapDirectionDetermination = Idle_GapDirectionDetermination.to(GapDirectionDetermination)
            standby_GapDirectionDetermination = GapDirectionDetermination.to(Idle_GapDirectionDetermination)
        
        class Sub_CenterInCorridor(State.Compound):
            Idle_CenterInCorridor = State(initial=True)
            CenterInCorridor = State()

            do_CenterInCorridor = Idle_CenterInCorridor.to(CenterInCorridor)
            standby_CenterInCorridor = CenterInCorridor.to(Idle_CenterInCorridor)
        
        class Sub_ComeCloserDirectionToGo(State.Compound):
            Idle_ComeCloserDirectionToGo = State(initial=True)
            ComeCloserDirectionToGo = State()

            do_ComeCloserDirectionToGo = Idle_ComeCloserDirectionToGo.to(ComeCloserDirectionToGo)
            standby_ComeCloserDirectionToGo = ComeCloserDirectionToGo.to(Idle_ComeCloserDirectionToGo)

        do_explore = (Sub_GapDirectionDetermination.Idle_GapDirectionDetermination.to(Sub_GapDirectionDetermination.GapDirectionDetermination)|
                   Sub_Rotation.Idle_Rotation.to(Sub_Rotation.Rotation)|
                   Sub_Move.Idle_Move.to(Sub_Move.Move))
        
        standby_explore = (Sub_GapDirectionDetermination.GapDirectionDetermination.to(Sub_GapDirectionDetermination.Idle_GapDirectionDetermination)|
                           Sub_Rotation.Rotation.to(Sub_Rotation.Idle_Rotation)|
                           Sub_Move.Move.to(Sub_Move.Idle_Move))
        
        do_follow = (#Ajouter une action qui determine la direction où aller
                     Sub_Rotation.Idle_Rotation.to(Sub_Rotation.Rotation)|
                     Sub_Move.Idle_Move.to(Sub_Move.Move))
        
        standby_follow = (#Ajouter une action qui determine la direction où aller 
                          Sub_Rotation.Rotation.to(Sub_Rotation.Idle_Rotation)|
                          Sub_Move.Move.to(Sub_Move.Idle_Move))
        
        do_come_closer = (Sub_Rotation.Idle_Rotation.to(Sub_Rotation.Rotation)|
                          Sub_Move.Idle_Move.to(Sub_Move.Move))
        
        standby_come_closer = (Sub_Rotation.Rotation.to(Sub_Rotation.Idle_Rotation)|
                               Sub_Move.Move.to(Sub_Move.Idle_Move))
        
        do_turn_around = (Sub_TurnAround.Idle_TurnAround.to(Sub_TurnAround.TurnAround)|
                          Sub_Rotation.Idle_Rotation.to(Sub_Rotation.Rotation))
        
        standby_turn_around = (Sub_TurnAround.TurnAround.to(Sub_TurnAround.Idle_TurnAround)|
                               Sub_Rotation.Rotation.to(Sub_Rotation.Idle_Rotation))
        
        standby_global = _build_standby(vars())

    activate = Inactive.to(Active)
    deactivate = Inactive.from_.any()

    def __init__(self, name: str = None, **kwargs):
        self.name = name

        super().__init__(**kwargs)

    def on_enter_state(self, state):
        if state == self.name:
            self.activate()
            self.send("do_stop")

    def on_exit_state(self, state):
        if state == self.name:
            self.send("standby_global")
            self.deactivate()

    @abstractmethod
    def update_action(self):
        pass