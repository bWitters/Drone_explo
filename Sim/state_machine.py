from statemachine import StateChart, State
from agents import Drones
from situation_dict import Situation

class DroneStateMachine(StateChart):
    Stock = State("Stock", initial=True)
    Takeoff = State("TakeOff")
    LeaderCorridor = State("LeaderCorridor")
    LeaderCurve = State("LeaderCurve")
    LeaderIntersection = State("LeaderIntersection")
    LeaderDeadEnd = State("LeaderDeadEnd")
    FollowerCorridor = State("FollowerCorridor")
    FollowerCurve = State("FollowerCurve")
    FollowerIntersection = State("FollowerIntersection")
    ForcedWait = State("Forced Wait")
    ReconfigFollower = State("ReconfigFollower")

    
    stock = Stock.to.itself()

    exploration = (Stock.to(Takeoff)|
                   Takeoff.to(LeaderCorridor) |
                   LeaderIntersection.to(LeaderCorridor)|
                   LeaderCorridor.to(LeaderCurve)|
                   LeaderCurve.to(LeaderCorridor))
    
    waiting = (LeaderCorridor.to(ForcedWait)|
               ForcedWait.to(LeaderCorridor))

    reach_intersection = (LeaderCorridor.to(LeaderIntersection)|
                          LeaderIntersection.to.itself())

    follow = (Stock.to(Takeoff)|
              Takeoff.to(FollowerCorridor) |
              FollowerCorridor.to(FollowerIntersection)|
              FollowerIntersection.to(FollowerCorridor)|
              ForcedWait.to(FollowerCorridor))

    take_off_curve = (Takeoff.to(FollowerCurve)|
                      FollowerCurve.to(FollowerCorridor))
    
    follow_curve = (FollowerCorridor.to(FollowerCurve)|
                    FollowerCurve.to(FollowerCorridor))
    
    become_leader = (FollowerCorridor.to(LeaderIntersection)|
                     FollowerIntersection.to(LeaderIntersection))
    
    forced_wait = (FollowerCorridor.to(ForcedWait))

    reach_dead_end = (LeaderCorridor.to(LeaderDeadEnd)|
                      LeaderDeadEnd.to.itself())
    
    reconfig = (LeaderDeadEnd.to(ReconfigFollower)|
                FollowerCorridor.to(ReconfigFollower)|
                FollowerCurve.to(ReconfigFollower)|
                FollowerIntersection.to(ReconfigFollower)|
                ReconfigFollower.to.itself())

    
    @property
    def role(self):
        return self.agent.role.configuration_values
            

    def on_enter_state(self, state):
        # if state in DroneStateMachine.states:
        print(f"Agent {self.agent.unique_id} entering state: {state}")


    def update_behavior(self, situation):
        if "stock" in self.role:
            if self.configuration == {DroneStateMachine.Stock}:
                pass

        elif "leader" in self.role:
            if self.configuration == {DroneStateMachine.Stock}:
                if situation[Situation.STOCK_HEIGHT]:
                    self.exploration()
            if self.configuration == {DroneStateMachine.Takeoff}:
                if situation[Situation.GOOD_HEIGHT]:
                    self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderCorridor}:
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.reach_intersection()
                elif situation[Situation.CURVE]:
                    self.exploration()
                elif situation[Situation.DEAD_END]:
                    self.reach_dead_end()
            elif self.configuration == {DroneStateMachine.LeaderCurve}:
                if situation[Situation.CORRIDOR]:
                    self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderIntersection}:
                if situation[Situation.CORRIDOR]:
                    self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderDeadEnd}:
                if situation[Situation.RECONFIG]:
                    self.reconfig()

        elif "follower" in self.role:
            if self.configuration == {DroneStateMachine.Stock}:
                if situation[Situation.STOCK_HEIGHT]:
                    self.follow()
            if self.configuration == {DroneStateMachine.Takeoff}:
                if situation[Situation.GOOD_HEIGHT]:
                    if situation[Situation.COME_CLOSER][0]:
                        if situation[Situation.CORRIDOR]:
                            self.follow()
                        if situation[Situation.CURVE]:
                            self.take_off_curve()
            elif self.configuration == {DroneStateMachine.FollowerCorridor}:
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.follow()
                elif situation[Situation.CURVE]:
                    self.follow_curve()
                if situation[Situation.RECONFIG]:
                    self.reconfig()
            elif self.configuration == {DroneStateMachine.FollowerCurve}:
                if situation[Situation.CORRIDOR]:
                    self.follow_curve()
                if situation[Situation.RECONFIG]:
                    self.reconfig()
            elif self.configuration == {DroneStateMachine.FollowerIntersection}:
                if situation[Situation.CORRIDOR]:
                    self.follow()
                if situation[Situation.RECONFIG]:
                    self.reconfig()
            elif self.configuration == {DroneStateMachine.ForcedWait}:
                if situation[Situation.CORRIDOR]:
                    if not situation[Situation.FORCED_WAIT]:
                        self.follow()
        

    def __init__(self,agent):
        self.agent:Drones = agent
        super().__init__()
