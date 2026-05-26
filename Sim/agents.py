from Behaviors.Behavior import Behavior
from Actions.Action import Action
from datetime import datetime
import csv

class Drones():
    """The base class for the drones"""

    def __init__(self,unique_id,drones,env_id_drones,stocking_area):
        self.front = "N"
        self.neighboring_agent_list = {"F":None,"P":None}
        self.stocking_area = stocking_area
        self.unique_id = unique_id
        self.move_drone = [0,0,0,0,0]
        self.position = [0,0,0]
        self.rpy = [0,0,0]

        nom_fichier = f"Sim/logs/drone_{unique_id}_{datetime.now().strftime('%Y-%m-%H-%M-%S')}.csv"
        nom_fichier_rt = f"Sim/real_time_logs/drone_{unique_id}.csv"
        self.file_rt = open(nom_fichier_rt,"w")
        self.commands_logs_rt = csv.writer(self.file_rt)
        self.commands_logs_rt.writerow(["vx","vy","vz","speed_frac","v_yaw"])
        self.file_rt.flush()
        self.file = open(nom_fichier,"w")
        self.commands_logs = csv.writer(self.file)
        self.commands_logs.writerow(["vx","vy","vz","speed_frac","v_yaw"])
        self.file.flush()

       
        from state_machine import DroneStateMachine
        from analysis import Analyzer
        from situation import SituationState
        from role import Role

        self.sensor_data = Analyzer(self,drones,env_id_drones)
        self.situation = SituationState(self)
        self.role = Role(self)
        self.state = DroneStateMachine(self)

        from Behaviors.stock import Stock
        from Behaviors.takeoff import Takeoff
        from Behaviors.leader_corridor import LeaderCorridor
        from Behaviors.follower_corridor import FollowerCorridor
        from Behaviors.leader_intersection import LeaderIntersection
        from Behaviors.follower_intersection import FollowerIntersection
        from Behaviors.leader_curve import LeaderCurve
        from Behaviors.follower_curve import FollowerCurve
        from Behaviors.forced_wait import ForcedWait

        self.stock_behavior = Stock(agent = self)
        self.takeoff_behavior = Takeoff(agent = self)
        self.leader_corridor_behavior = LeaderCorridor(agent = self)    
        self.leader_intersection_behavior = LeaderIntersection(agent = self)
        self.leader_curve_behavior = LeaderCurve(agent = self)
        self.follower_corridor_behavior = FollowerCorridor(agent = self)
        self.follower_intersection_behavior = FollowerIntersection(agent = self)
        self.follower_curve_behavior = FollowerCurve(agent = self)


        self.sm_behavior_dict = {"Stock" : self.stock_behavior,
                                 "Takeoff" : self.takeoff_behavior,
                                 "Leader Corridor" : self.leader_corridor_behavior,
                                 "Leader Intersection" : self.leader_intersection_behavior,
                                 "Leader Curve" : self.leader_curve_behavior,
                                 "Follower Corridor" : self.follower_corridor_behavior,
                                 "Follower Intersection" : self.follower_intersection_behavior,
                                 "Follower Curve" : self.follower_curve_behavior,
                                 }

        self.state.add_listener(self.stock_behavior,
                                self.takeoff_behavior,
                                self.leader_corridor_behavior,
                                self.leader_intersection_behavior,
                                self.leader_curve_behavior,
                                self.follower_corridor_behavior,
                                self.follower_intersection_behavior,
                                self.follower_curve_behavior,
                                )
        
        from Actions.stop import Stop
        from Actions.change_role import ChangeRole
        from Actions.move import Move
        from Actions.send_cell import SendCell
        from Actions.gap_direction_determination import GapDirectionDetermination
        from Actions.rotation import Rotation
        from Actions.new_cell_to_follow import NewCellToFollow
        from Actions.come_closer_cell_to_follow import ComeCloserDirectionToGo
        from Actions.send_come_closer import SendComeCloser
        from Actions.turn_around import TurnAround
        from Actions.takeoff import Takeoff
        from Actions.test import Test
        from Actions.center_in_corridor import CenterInCorridor
        from Actions.center_in_curve import CenterInCurve
        from Actions.height_control import HeightControl
        from Actions.center_in_intersection import CenterInIntersection
        from Actions.rotation_control import RotationControl

        self.stop_action = Stop(self)
        self.change_role_action = ChangeRole(self)
        self.move_action = Move(self)
        self.send_cell_action = SendCell(self)
        self.gap_direction_determination_action = GapDirectionDetermination(self)
        self.rotation_action = Rotation(self)
        self.new_cell_to_follow_action = NewCellToFollow(self)
        self.come_closer_cell_to_follow_action = ComeCloserDirectionToGo(self)
        self.turn_around_action = TurnAround(self)
        self.takeoff_action = Takeoff(self)
        self.send_come_closer_action = SendComeCloser(self)
        self.test_action = Test(self)
        self.center_in_corridor_action = CenterInCorridor(self)
        self.center_in_curve_action = CenterInCurve(self)
        self.height_control_action = HeightControl(self)
        self.center_in_intersection_action = CenterInIntersection(self)
        self.rotation_conrol_action = RotationControl(self)

        self.actions_dict = {"Stop" : self.stop_action,
                             "Change Role" : self.change_role_action,
                             "Gap Direction Determination" : self.gap_direction_determination_action,
                             "Follow" : self.new_cell_to_follow_action,
                             "Come Closer Direction" : self.come_closer_cell_to_follow_action,
                             "Turn Around" : self.turn_around_action,
                             "Rotation" : self.rotation_action,
                             "Takeoff" : self.takeoff_action,
                             "Send Come Closer" : self.send_come_closer_action,
                             "Move" : self.move_action,
                             "Test" : self.test_action,
                             "Center in corridor" : self.center_in_corridor_action,
                             "Center in curve" : self.center_in_curve_action,
                             "Height control" : self.height_control_action,
                             "Center in intersection" : self.center_in_intersection_action,
                             "Rotation control" : self.rotation_conrol_action
                             }


        self.stock_behavior.add_listener(self.stop_action,
                                         self.change_role_action
                                         )
        
        self.takeoff_behavior.add_listener(self.takeoff_action,
                                           self.stop_action,
                                           self.height_control_action,
                                           self.rotation_conrol_action
                                           )

        self.leader_corridor_behavior.add_listener(self.stop_action,
                                                   self.gap_direction_determination_action,
                                                   self.rotation_action,
                                                   self.move_action,
                                                   self.send_come_closer_action,
                                                   self.center_in_corridor_action,
                                                   self.height_control_action,
                                                   self.rotation_conrol_action
                                                   )
        
        self.leader_intersection_behavior.add_listener(self.stop_action,
                                                       self.send_cell_action,
                                                       self.gap_direction_determination_action,
                                                       self.rotation_action,
                                                       self.move_action,
                                                       self.change_role_action,
                                                       self.send_come_closer_action,
                                                       self.center_in_intersection_action
                                                       )
        
        self.leader_curve_behavior.add_listener(self.stop_action,
                                                self.send_come_closer_action,
                                                self.send_cell_action,
                                                self.gap_direction_determination_action,
                                                self.rotation_action,
                                                self.move_action,
                                                self.test_action,
                                                self.center_in_curve_action
                                                )

        
        self.follower_corridor_behavior.add_listener(self.stop_action,
                                                     self.new_cell_to_follow_action,
                                                     self.come_closer_cell_to_follow_action,
                                                     self.rotation_action,
                                                     self.move_action,
                                                     self.change_role_action,
                                                     self.send_come_closer_action,
                                                     self.center_in_corridor_action,
                                                     self.height_control_action,
                                                     self.rotation_conrol_action
                                                     )
        
        self.follower_intersection_behavior.add_listener(self.stop_action,
                                                         self.send_cell_action,
                                                         self.new_cell_to_follow_action,
                                                         self.come_closer_cell_to_follow_action,
                                                         self.rotation_action,
                                                         self.move_action,
                                                         self.change_role_action,
                                                         self.send_come_closer_action,
                                                         self.center_in_corridor_action,
                                                         self.center_in_intersection_action
                                                         )
        
        self.follower_curve_behavior.add_listener(self.stop_action,
                                                  self.send_cell_action,
                                                  self.new_cell_to_follow_action,
                                                  self.come_closer_cell_to_follow_action,
                                                  self.rotation_action,
                                                  self.move_action,
                                                  self.send_come_closer_action,
                                                  self.change_role_action,
                                                  self.center_in_corridor_action,
                                                  self.center_in_curve_action
                                                  )

        self.initialize_agent()

        # graph = DotGraphMachine(self.state)
        # graph().write_png("state_machine.png")

    def active_sm_behavior_set(self, behavior_dict: dict[str, Behavior]) -> Behavior:
        return next((behavior for behavior in behavior_dict.values() if behavior.Active in behavior.configuration), None)
    
    def active_actions_set(self, actions_dict: dict[str, Action]) -> list[Action]:
        res = []
        for action in actions_dict.values():
            if action.Active in action.configuration:
                res.append(action)
        return res


    def step(self, rays):
        self.move_drone = [0,0,0,0,0]
        self.rays = rays
        self.sensor_data.neighborhood_analysis()
        self.situation.update_situation(self.sensor_data.gaps_dir,
                                        self.sensor_data.occupied_neighborhood,
                                        self.sensor_data.graph_branch_counter_var,
                                        self.sensor_data.neighbors_distance,
                                        self.sensor_data.com_stack)
        self.state.update_behavior(self.situation.situation)

        self.active_sm_behavior = self.active_sm_behavior_set(self.sm_behavior_dict)
        print(f"{self.unique_id}; active behavior : {self.active_sm_behavior.name}")
        self.active_sm_behavior.update_action()

        self.active_actions = self.active_actions_set(self.actions_dict)
        print(f"{self.unique_id}; active actions : {[action.name for action in self.active_actions]}")
        print(f"Current front : {self.front}")
        for action in self.active_actions:
            action.action()
        
        self.move_drone[3] = 1
        print(f"Current drone move : {self.move_drone}")
        self.commands_logs.writerow(self.move_drone)
        self.file.flush()
        self.commands_logs_rt.writerow(self.move_drone)
        self.file_rt.flush()


    def initialize_agent(self):
        self.stock_behavior.send("activate")
        self.stock_behavior.send("do_stop")
    
    def close(self):
        if hasattr(self, 'file') and not self.file.closed:
            self.file.close()
        if hasattr(self, 'file_rt') and not self.file_rt.closed:
            self.file_rt.close()

    def __del__(self):  # Appelé à la suppression de l'objet (mais pas fiable à 100%)
        self.close()

if __name__ == "__main__":
    print("Lancement Statemachine seule")