from statemachine import StateChart, State
from agents import Drones
from situation_dict import Situation

class DroneStateMachine(StateChart):
    Stock = State("Stock", initial=True)
    Takeoff = State("TakeOff")
    LeaderCorridor = State("LeaderCorridor")
    LeaderCurve = State("LeaderCurve")
    LeaderIntersection = State("LeaderIntersection")
    FollowerCorridor = State("FollowerCorridor")
    FollowerCurve = State("FollowerCurve")
    FollowerIntersection = State("FollowerIntersection")
    ForcedWait = State("Forced Wait")
    
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
    
    follow_curve = (FollowerCorridor.to(FollowerCurve)|
                    FollowerCurve.to(FollowerCorridor))
    
    become_leader = (FollowerCorridor.to(LeaderIntersection)|
                     FollowerIntersection.to(LeaderIntersection))
    
    forced_wait = (FollowerCorridor.to(ForcedWait))

    
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
                    if situation[Situation.CORRIDOR]:
                        self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderCorridor}:
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.reach_intersection()
                elif situation[Situation.CURVE]:
                    self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderCurve}:
                if situation[Situation.CORRIDOR]:
                    self.exploration()
            elif self.configuration == {DroneStateMachine.LeaderIntersection}:
                if situation[Situation.CORRIDOR]:
                    self.exploration()

        elif "follower" in self.role:
            if self.configuration == {DroneStateMachine.Stock}:
                if situation[Situation.STOCK_HEIGHT]:
                    self.follow()
            if self.configuration == {DroneStateMachine.Takeoff}:
                if situation[Situation.GOOD_HEIGHT]:
                    if situation[Situation.COME_CLOSER][0]:
                        self.follow()
            elif self.configuration == {DroneStateMachine.FollowerCorridor}:# FIXME : Going into corridor state while being in curve, but there is a drone at the entrance and the exit
                print("StateMachine : In Corridor mode")
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.follow()
                elif situation[Situation.CURVE]:
                    self.follow_curve()
            elif self.configuration == {DroneStateMachine.FollowerCurve}:
                #print("StateMachine : In Curve mode")
                if situation[Situation.CORRIDOR]:
                    #print("StateMachine : In Corridor while Curve mode going to Corridor mode")
                    self.follow_curve()
            elif self.configuration == {DroneStateMachine.FollowerIntersection}:
                if situation[Situation.CORRIDOR]:
                    self.follow()
            elif self.configuration == {DroneStateMachine.ForcedWait}:
                if situation[Situation.CORRIDOR]:
                    if not situation[Situation.FORCED_WAIT]:
                        self.follow()
        

    def __init__(self,agent):
        self.agent:Drones = agent
        super().__init__()
