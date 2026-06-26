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
    ReconfigFollower = State("ReconfigFollower")
    ReconfigCorridor = State("ReconfigCorridor")
    ReconfigCurve = State("ReconfigCurve")
    ReconfigIntersection = State("ReconfigIntersection")
    
    stock = Stock.to.itself()

    exploration = (Stock.to(Takeoff)|
                   Takeoff.to(LeaderCorridor) |
                   LeaderIntersection.to(LeaderCorridor)|
                   LeaderCorridor.to(LeaderCurve)|
                   LeaderCurve.to(LeaderCorridor))

    reach_intersection = (LeaderCorridor.to(LeaderIntersection)|
                          LeaderIntersection.to.itself())

    follow = (Stock.to(Takeoff)|
              Takeoff.to(FollowerCorridor) |
              FollowerCorridor.to(FollowerIntersection)|
              FollowerIntersection.to(FollowerCorridor)|
              ReconfigFollower.to(FollowerCorridor))

    take_off_curve = (Takeoff.to(FollowerCurve)|
                      FollowerCurve.to(FollowerCorridor))
    
    follow_curve = (FollowerCorridor.to(FollowerCurve)|
                    FollowerCurve.to(FollowerCorridor)|
                    ReconfigFollower.to(FollowerCurve))
    
    become_leader = (FollowerCorridor.to(LeaderIntersection)|
                     FollowerIntersection.to(LeaderIntersection))

    reach_dead_end = (LeaderCorridor.to(LeaderDeadEnd)|
                      LeaderDeadEnd.to.itself())
    
    reconfig = (LeaderDeadEnd.to(ReconfigFollower)|
                FollowerCorridor.to(ReconfigFollower)|
                FollowerCurve.to(ReconfigFollower)|
                FollowerIntersection.to(ReconfigFollower)|
                ReconfigFollower.to.itself())

    reconfig_intersection = (ReconfigFollower.to(ReconfigIntersection)|
                             ReconfigCurve.to(ReconfigIntersection)|
                             ReconfigCorridor.to(ReconfigIntersection))

    reconfig_curve = (ReconfigFollower.to(ReconfigCurve)|
                      ReconfigIntersection.to(ReconfigCurve)|
                      ReconfigCorridor.to(ReconfigCurve))
    
    reconfig_corridor = (ReconfigFollower.to(ReconfigCorridor)|
                         ReconfigCurve.to(ReconfigCorridor)|
                         ReconfigIntersection.to(ReconfigCorridor))
    
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
                        elif situation[Situation.CURVE]:
                            self.take_off_curve()
            elif self.configuration == {DroneStateMachine.FollowerCorridor}:
                if situation[Situation.RECONFIG]:
                    self.reconfig()
                elif situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.follow()
                elif situation[Situation.CURVE]:
                    self.follow_curve()          
            elif self.configuration == {DroneStateMachine.FollowerCurve}:
                if situation[Situation.RECONFIG]:
                    self.reconfig()
                elif situation[Situation.CORRIDOR]:
                    self.follow_curve()
            elif self.configuration == {DroneStateMachine.FollowerIntersection}:
                if situation[Situation.RECONFIG]:
                    self.reconfig()
                elif situation[Situation.CORRIDOR]:
                    self.follow()
        
        elif "reconfig_leader" in self.role:
            if self.configuration == {DroneStateMachine.ReconfigFollower}:
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.reconfig_intersection()
                elif situation[Situation.CURVE]:
                    self.reconfig_curve()
                if situation[Situation.CORRIDOR]:
                    self.reconfig_corridor()
            elif self.configuration == {DroneStateMachine.ReconfigCorridor}:
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.reconfig_intersection()
                elif situation[Situation.CURVE]:
                    self.reconfig_curve()
                # elif situation[Situation.DEAD_END]:
                #     self.reach_dead_end()
            elif self.configuration == {DroneStateMachine.ReconfigCurve}:
                if situation[Situation.CORRIDOR]:
                    self.reconfig_corridor()
            elif self.configuration == {DroneStateMachine.ReconfigIntersection}:
                if situation[Situation.CORRIDOR]:
                    self.reconfig_corridor()
            # elif self.configuration == {DroneStateMachine.ReconfigDeadEnd}:
            #     if situation[Situation.RECONFIG]:
            #         self.reconfig()

        elif "reconfig_follower" in self.role:
            if self.configuration == {DroneStateMachine.ReconfigFollower}:
                if situation[Situation.CURVE]:
                    self.follow_curve()
                elif situation[Situation.CORRIDOR]:
                    self.follow()
            if self.configuration == {DroneStateMachine.FollowerCorridor}:
                # if situation[Situation.RECONFIG]:
                #     self.reconfig()
                if situation[Situation.INTERSECTION] and not self.agent.sensor_data.maybe_corner:
                    self.follow()
                elif situation[Situation.CURVE]:
                    self.follow_curve()          
            elif self.configuration == {DroneStateMachine.FollowerCurve}:
                # if situation[Situation.RECONFIG]:
                #     self.reconfig()
                if situation[Situation.CORRIDOR]:
                    self.follow_curve()
            elif self.configuration == {DroneStateMachine.FollowerIntersection}:
                if self.agent.neighboring_agent_list["F"] ==  None:
                    print("End of reconfig")
                # if situation[Situation.RECONFIG]:
                #     self.reconfig()
                elif situation[Situation.CORRIDOR]:
                    self.follow()
        

    def __init__(self,agent):
        self.agent:Drones = agent
        super().__init__()
