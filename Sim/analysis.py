from agents import Drones
from queue import Queue

class Analyzer:
    def __init__(self, agent, drones_list, env_id):
        self.agent:Drones = agent
        self.com_stack = Queue()
        self.drones = drones_list
        self.env_id_drones = env_id

        self.dist_L_wall,self.dist_R_wall,self.dist_F_wall,self.dist_B_wall = None,None,None,None

        self.maybe_corner = False

        self.wall_distance = {"F": False, "R":False, "B":False, "L":False}

        self.gaps_dir_world = {"N": False, "S":False, "E":False, "W":False}
        self.gaps_dir = {"F": False, "R":False, "B":False, "L":False}
        self.previous_gap_dir = {"F": False, "R":False, "B":False, "L":False}

        self.occupied_neighborhood = {"F":[], "R":[], "B":[], "L":[]}
        self.unoccupied_neighborhood = {"F": False, "R":False, "B":False, "L":False}

        self.neighbors_distance = {"F": False, "R":False, "B":False, "L":False}

        self.graph_branch_counter_var = None
        self.occupied_branch_counter_var = None
        
        self.centered_in_corner = False
        self.centered_in_intersection = False


    @property
    def rays(self): #TODO : Problème avec la variable rays qui n'est pas bien utilisé quand on est avec le multiranger
        if self.agent.uri == None:
            rx = self.agent.rays
            #print(f"Should be pybullet lidar : \n{rx}")
        else:
            rx = []
            for i in range(4):
                rays = self.drone_to_world_list(self.agent.rays_reel)
                #print(rays)
                rx.append((rays[i],self.agent.rays[i][1]))
            #print(f"Should be multiranger lidar : \n{rx}")
        return rx
    
    @property
    def neighborhood(self):
        if self.agent.uri == None:
            rx = self.agent.rays
        else:
            rx = []
            for i in range(4):
                rx.append((self.agent.rays_reel[i],self.agent.rays[i][1]))
            #print(f"Should be multiranger lidar : \n{rx}")
        return self.world_to_drone_list(rx)
    
    #Follow the gap
    def get_alignement_in_gap(self):
        match self.agent.current_active_direction:
            case w if w in ["North", "South"]:
                if abs(self.rays[1][0]-self.rays[3][0]) < 0.1:
                    is_centered = True
                    dist_wall = 0
                else:
                    dist_wall = self.rays[1][0]-self.rays[3][0]
                    is_centered = False
            case w if w in ["East", "West"]:
                if abs(self.rays[0][0]-self.rays[2][0]) < 0.1:
                    is_centered = True
                    dist_wall = 0
                else:
                    dist_wall = self.rays[0][0]-self.rays[2][0]
                    is_centered = False
        print("get_alignement_in_gap works !")
        return (is_centered,dist_wall)
    
    #Distance close enough to leader
    def get_close_to_leader(self):
        close_to_leader = False
        match self.agent.front:
            case "N":
                if self.rays[0][0] < 0.6:
                    close_to_leader = True
            case "E":
                if self.rays[1][0] < 0.6:
                    close_to_leader = True
            case "S":
                if self.rays[2][0] < 0.6:
                    close_to_leader = True
            case "W":
                if self.rays[3][0] < 0.6:
                    close_to_leader = True
        print("get_close_to_leader works !")
        return close_to_leader

    #Center in corner
    def get_centered_in_corner(self):
        centered_in_corner = False
        match self.agent.front:
            case "N":
                if self.rays[0][0] < 0.26:
                    centered_in_corner = True
            case "E":
                if self.rays[1][0] < 0.26:
                    centered_in_corner = True
            case "S":
                if self.rays[2][0] < 0.26:
                    centered_in_corner = True
            case "W":
                if self.rays[3][0] < 0.26:
                    centered_in_corner = True
        print("get_centerd_in_corner works !")
        return centered_in_corner
                
    #Intersection
    def get_centered_in_intersection(self):
        if self.agent.situation.intersection_entrance != None:
            match self.agent.front:
                case "N":
                    objectif = self.agent.situation.intersection_entrance[1] + 0.2
                    i=1
                case "S":
                    objectif = self.agent.situation.intersection_entrance[1] - 0.2
                    i=1
                case "E":
                    objectif = self.agent.situation.intersection_entrance[0] + 0.2
                    i=0
                case "W":
                    objectif = self.agent.situation.intersection_entrance[0] - 0.2
                    i=0

            if abs(objectif - self.agent.position[i]) < 0.03:
                return True
            return False
        else:
            return False

    #### Gaps ####
    def get_gap_direction(self):
        self.previous_gap_dir = [val for val in self.gaps_dir]
        gaps_dir = {"N": False, "E":False, "S":False, "W":False}
        print(self.rays)
        print(self.env_id_drones.keys())
        
        for i in range(len(self.rays)):
            if self.rays[i][0] > 0.4: #or self.rays[i][1] in self.env_id_drones.keys()
                match i:
                    case 0:
                        gaps_dir["N"] = True
                    case 1:
                        gaps_dir["E"] = True
                    case 2:
                        gaps_dir["S"] = True
                    case 3:
                        gaps_dir["W"] = True
        print("get_gap_direction works !")
        return gaps_dir
    
    def gaps_type(self): #FIXME for the curve corridor transition
        unoccupied_gaps = {"F": False, "R":False, "B":False, "L":False}
        occupied_gaps = {"F": False, "R":False, "B":False, "L":False}
        maybe_corner = False
        print(f"Neighborhood of {self.agent.unique_id} : {self.neighborhood}")
        for key in self.neighborhood.keys():
            if self.neighborhood[key][0] > 1:
                match key:
                    case "F":
                        unoccupied_gaps["F"] = True
                    case "R":
                        unoccupied_gaps["R"] = True
                    case "B":
                        unoccupied_gaps["B"] = True
                    case "L":
                        unoccupied_gaps["L"] = True
            elif self.neighborhood[key][1] in self.env_id_drones.keys():
                match key:
                    case "F":
                        occupied_gaps["F"] = self.neighborhood[key][1]
                    case "R":
                        occupied_gaps["R"] = self.neighborhood[key][1]
                    case "B":
                        occupied_gaps["B"] = self.neighborhood[key][1]
                    case "L":
                        occupied_gaps["L"] = self.neighborhood[key][1]
            if self.neighborhood[key][0] > 0.25 and self.neighborhood[key][0] < 0.7 and key != "B" and not self.neighborhood[key][1] in self.env_id_drones.keys():
                maybe_corner = True
        print(f"Occupied gaps of {self.agent.unique_id} : {occupied_gaps}")
        print(f"Is it maybe a corner : {maybe_corner}")
        return occupied_gaps,unoccupied_gaps,maybe_corner

    def get_neighbors_distance(self):
        neighbors_distance = {"F": None, "P": None}
        #print(self.agent.neighboring_agent_list)
        if self.agent.neighboring_agent_list["F"] != None:
            distance_follower = [self.agent.position[0] - self.agent.neighboring_agent_list["F"].position[0], self.agent.position[1] - self.agent.neighboring_agent_list["F"].position[1]]
            neighbors_distance["F"] = distance_follower
        if self.agent.neighboring_agent_list["P"] != None:
            distance_preceding = [self.agent.position[0] - self.agent.neighboring_agent_list["P"].position[0], self.agent.position[1] - self.agent.neighboring_agent_list["P"].position[1]]
            neighbors_distance["P"] = distance_preceding
        return neighbors_distance

    def get_neighboring_agents(self):
        neighboring_agents = {"F":None, "B":None, "R":None, "L":None}
        neighboring_agents["F"] = self.get_agent_by_id(self.neighborhood["F"][1])
        neighboring_agents["R"] = self.get_agent_by_id(self.neighborhood["R"][1])
        neighboring_agents["B"] = self.get_agent_by_id(self.neighborhood["B"][1])
        neighboring_agents["L"] = self.get_agent_by_id(self.neighborhood["L"][1])
        
        return neighboring_agents
            
    def get_agent_by_id(self, id_drone):
        if id_drone != None and id_drone in self.env_id_drones.keys():
            return self.drones[self.env_id_drones[id_drone]["drone_id"]]
        return None

    def gaps_counter(self,gaps_dir:dict) -> int:
        counter = 0
        for val in gaps_dir.values():
            if val == True:
                counter +=1
        return counter

    def occupied_gaps_counter(self,occupied_neighorhood:dict) -> int:
        counter = 0
        for val in occupied_neighorhood.values():
            if val == True:
                counter +=1
        return counter
    
    def world_to_drone_list(self, gaps_dir):
        gaps_drone_dir = {"F":None, "B":None, "R":None, "L":None}
        if self.agent.front == "N":
            i = 0
        elif self.agent.front == "E":
            i = 1
        elif self.agent.front == "S":
            i = 2
        elif self.agent.front == "W":
            i = 3
        gaps_drone_dir["F"] = gaps_dir[i%4]
        gaps_drone_dir["R"] = gaps_dir[(i+1)%4]
        gaps_drone_dir["B"] = gaps_dir[(i+2)%4]
        gaps_drone_dir["L"] = gaps_dir[(i+3)%4]
        return gaps_drone_dir
    
    def drone_to_world_list(self, gaps_dir):
        gaps_drone_dir = []
        if self.agent.front == "N":
            i = 0
        elif self.agent.front == "E":
            i = 3
        elif self.agent.front == "S":
            i = 2
        elif self.agent.front == "W":
            i = 1
        gaps_drone_dir.append(gaps_dir[i%4])
        gaps_drone_dir.append(gaps_dir[(i+1)%4])
        gaps_drone_dir.append(gaps_dir[(i+2)%4])
        gaps_drone_dir.append(gaps_dir[(i+3)%4])
        return gaps_drone_dir

    def wolrd_to_drone_dict(self, gaps_dir): #FIXME for the curve corridor transition
        gaps_drone_dir = {"B":None, "R":None, "F":None, "L":None}
        dir = ["N","W","S","E"]
        if self.agent.front == "N":
            i = 2
        elif self.agent.front == "E":
            i = 1
        elif self.agent.front == "S":
            i = 0
        elif self.agent.front == "W":
            i = 3
        gaps_drone_dir["B"] = gaps_dir[dir[i%4]]
        gaps_drone_dir["R"] = gaps_dir[dir[(i+1)%4]]
        gaps_drone_dir["F"] = gaps_dir[dir[(i+2)%4]]
        gaps_drone_dir["L"] = gaps_dir[dir[(i+3)%4]]
        return gaps_drone_dir
    
    def get_wall_distance(self):
        wall_distance = {"N":None, "E":None, "S":None,"W":None}
        direction = ["N","E","S","W"]
        for i in range(len(self.rays)):
            wall_distance[direction[i]] = self.rays[i][0]
        print("get_wall_dsitance works !")
        return wall_distance
    
    def get_wall_distance_drone(self,wall_distance):
        drone_distance = self.wolrd_to_drone_dict(wall_distance)
        self.dist_B_wall = drone_distance["B"]
        self.dist_F_wall = drone_distance["F"]
        self.dist_R_wall = drone_distance["R"]
        self.dist_L_wall = drone_distance["L"]

    def drone_to_world_dict(self, gaps_dir):
        gaps_drone_dir = {"N":None, "W":None, "S":None, "E":None}
        dir = ["S", "E", "N", "W"]
        if self.agent.front == "N":
            i = 2
        elif self.agent.front == "E":
            i = 1
        elif self.agent.front == "S":
            i = 0
        elif self.agent.front == "W":
            i = 3
        gaps_drone_dir[dir[i%4]] = gaps_dir["F"]
        gaps_drone_dir[dir[(i+1)%4]] = gaps_dir["L"]
        gaps_drone_dir[dir[(i+2)%4]] = gaps_dir["B"]
        gaps_drone_dir[dir[(i+3)%4]] = gaps_dir["R"]
        return gaps_drone_dir
    
    def neighborhood_analysis(self):
        self.gaps_dir_world = self.get_gap_direction()
        self.gaps_dir = self.wolrd_to_drone_dict(self.gaps_dir_world)
        print(f"Gaps directions : {self.gaps_dir}")
        
        self.occupied_neighborhood, self.unoccupied_neighborhood,self.maybe_corner = self.gaps_type()
        
        self.wall_distance = self.get_wall_distance()
        self.get_wall_distance_drone(self.wall_distance)

        self.neighbors_distance = self.get_neighbors_distance()
        self.graph_branch_counter_var = self.gaps_counter(self.gaps_dir)
        self.occupied_branch_counter_var = self.occupied_gaps_counter(self.occupied_neighborhood)

        self.centered_in_corner = self.get_centered_in_corner()
        self.centered_in_intersection = self.get_centered_in_intersection()