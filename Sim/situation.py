from agents import Drones
from situation_dict import Situation
from math import sqrt

class SituationState():
    """Class representing the situation of an agent in the environment."""

    def __init__(self, agent):
        self.agent: Drones = agent
        self.intersection_entrance = None
        self.entrance = True

        self.situation = {
            Situation.STOCK: False,
            Situation.CORRIDOR: False,
            Situation.INTERSECTION: False,
            Situation.CURVE: False,
            Situation.AGENT_IN_INTERSECTION_DETECTION: False,
            Situation.ALL_BRANCH_EXPLORED: False,
            Situation.COME_CLOSER: False,
            Situation.FORCED_WAIT: False,
            Situation.CLOSE_TO_LEADER: False,
            Situation.FORCED_WAIT_AGENT_DETECTION: False,
            Situation.AGENT_IN_FRONT_DETECTION: False,
            Situation.AGENT_BEHIND_DETECTION: False,
            Situation.AGENT_DETECTION: (False, []),
            Situation.TOO_CLOSE: (False, []),
            Situation.BACKWARD_TOO_CLOSE : False,
            Situation.FRONT_TOO_CLOSE : False,
            Situation.CLOSE_TO_EXPLORED_BRANCH : False,
            Situation.GOOD_HEIGHT : False,
            Situation.CENTERED_IN_CORRIDOR : False,
            Situation.COME_CLOSER_SENT : False,
            Situation.BACKWARD_TOO_FAR : False
            }

    @property
    def position(self):
        return self.agent.position

    @property
    def role(self):
        return self.agent.role.current_state.id
    
    def is_good_height(self):
        return self.position[2] > 0.95
    
    def is_stock_height(self):
            return self.position[2] < 0.1

    def is_in_stock(self):
        ok = 0
        for i in range(3):
            if self.position[i] > self.agent.stocking_area[i][0] and self.position[i] < self.agent.stocking_area[i][1]:
                ok += 1
        if ok == 3:
            return True
        else:
            return False
        
    def is_in_intersection(self, graph_branch_counter: int) -> bool:
        if graph_branch_counter > 2:
            if self.entrance:
                self.intersection_entrance = [self.agent.position[0], self.agent.position[1]]
                self.entrance = False
            return True
        else:
            return False
    
    def is_in_corridor(self, graph_branch_counter: int, graph_neighborhood : dict, occupied_gaps : dict) -> bool:
        if graph_branch_counter == 2:
            if graph_neighborhood["B"] and graph_neighborhood["F"]:
                self.entrance = True
                return True
            else:
                return False
        elif graph_branch_counter == 1:
            if occupied_gaps["B"] != False and graph_neighborhood["F"]:
                self.entrance = True
                return True
            else:
                return False
        else:
            return False
        
    def is_in_curve(self, graph_branch_counter :int, graph_neighborhood : dict) -> bool:
        #print(f"Number of branch : {graph_branch_counter}" )
        #print(f"Voisinage : {graph_neighborhood}" )
        if graph_branch_counter == 2:
            if graph_neighborhood["L"] or graph_neighborhood["R"]:
                return True
            else:
                return False
        else:
            return False
    
    def is_in_dead_end(self, graph_branch_counter: int) -> bool:
        if not self.is_in_stock():
            if graph_branch_counter == 1:
                return True
            else:
                return False
    
    def dist(self,a:list):
        return sqrt(a[0]**2 + a[1]**2)
    
    def is_to_close(self, neighborhood_distances:dict[str, list[float]]) -> tuple[bool, list]:
        DIR = []
        for dir, distances in neighborhood_distances.items():
            if distances != None:
                if self.dist(distances) < 0.6:
                    DIR.append(dir)
        if DIR:
            return (True, DIR)
        else:
            return (False, [])
    
    def backward_is_to_close(self) -> bool:
        if "F" in self.situation[Situation.TOO_CLOSE][1]:
            return True
        else:
            return False
        
    def front_is_to_close(self) -> bool:
        if "P" in self.situation[Situation.TOO_CLOSE][1]:
            return True
        else:
            return False

    def agent_detection(self, occupied_neighborhood: dict[str, list[int]]) -> tuple[bool, list]:
        DIR = []
        for dir, cells in occupied_neighborhood.items():
            if cells:
                DIR.append(dir)
        if dir:
            return (True, DIR)
        else:
            return (False, [])
    
    # def is_close_to_explored_branch(self, occupied_neighborhood: dict[str, list[int]]) -> bool: # TODO : Modifier ça ça semble bizarre
    #     if self.situation[Situation.INTERSECTION]:
    #         for dir, ids in occupied_neighborhood.items():
    #             if ids:
    #                 if not dir in self.situation[Situation.TOO_CLOSE][1]:
    #                     return False
    #         return True
    #     else:
    #         return False

    def com_analyzer(self, com_received):
        if not com_received.empty():
            while not com_received.empty():
                last_com = com_received.get()
                if last_com[0] == "Come Closer":
                    if self.role == "leader":
                        self.situation[Situation.COME_CLOSER] = (False,last_com[1])
                    else:
                        self.situation[Situation.COME_CLOSER] = (True,last_com[1])
                else:
                    self.situation[Situation.COME_CLOSER] = (False,last_com[1])
                if last_com[0] == "Stop forced wait":
                    self.situation[Situation.FORCED_WAIT] = (False,last_com[1])
        else:
            self.situation[Situation.COME_CLOSER] = (False,None)
    
    def is_centered_in_corridor(self):
        if abs(self.agent.sensor_data.dist_R_wall - self.agent.sensor_data.dist_L_wall) < 0.1:
            return True
        return False
    
    def is_backward_too_far(self,neighbors_distance):
        if neighbors_distance["F"] != None:
            print(f"Distance with follower : {self.dist(neighbors_distance["F"])}")
            if self.dist(neighbors_distance["F"]) > 1.7:
                print("Too long distance")
                return (True, 2)
            elif self.dist(neighbors_distance["F"]) > 1:
                print("Long distance ok to continue")
                return (True, 1)
            else:
                return (False, 0)
        else:
            return (False, 0)
    
    def update_situation(self, gaps_dir,
                         occupied_neighborhood,
                         graph_branch_counter_var,
                         neighbors_distance,
                         com_received
                         ):
        
        self.com_analyzer(com_received)
        self.situation[Situation.STOCK_HEIGHT] = self.is_stock_height()
        self.situation[Situation.GOOD_HEIGHT] = self.is_good_height()
        self.situation[Situation.STOCK] = self.is_in_stock()
        self.situation[Situation.CORRIDOR] = self.is_in_corridor(graph_branch_counter_var, gaps_dir, occupied_neighborhood)
        self.situation[Situation.INTERSECTION] = self.is_in_intersection(graph_branch_counter_var)
        self.situation[Situation.CURVE] = self.is_in_curve(graph_branch_counter_var, gaps_dir)
        self.situation[Situation.TOO_CLOSE] = self.is_to_close(neighbors_distance)
        self.situation[Situation.BACKWARD_TOO_CLOSE] = self.backward_is_to_close()
        self.situation[Situation.FRONT_TOO_CLOSE] = self.front_is_to_close()
        #self.situation[Situation.CLOSE_TO_EXPLORED_BRANCH] = self.is_close_to_explored_branch(occupied_neighborhood)
        self.situation[Situation.AGENT_DETECTION] = self.agent_detection(occupied_neighborhood)
        self.situation[Situation.CENTERED_IN_CORRIDOR] = self.is_centered_in_corridor()
        self.situation[Situation.BACKWARD_TOO_FAR] = self.is_backward_too_far(neighbors_distance)