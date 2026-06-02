from agents import Drones
from Actions.Action import Action
from situation_dict import Situation

class GapDirectionDetermination(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)

    @property
    def role(self):
        return self.agent.role.configuration_values
    @property
    def situation(self) -> Situation:
        return self.agent.situation.situation
    @property
    def graph_neighbors(self) -> dict:
        return self.agent.sensor_data.gaps_dir
    @property
    def occupied_neighbors(self) -> dict:
        return self.agent.sensor_data.occupied_neighborhood
    @property
    def unoccupied_neighbors(self):
        return self.agent.sensor_data.unoccupied_neighborhood
    @property
    def graph_branch_counter(self):
        return self.agent.sensor_data.graph_branch_counter_var

    def action(self):
        """ 
        Retourne la nouvelle cellule à explorer selon la logique "left most"
        """
        new_cell = None
        #print(self.graph_neighbors)
        #print(self.occupied_neighbors)
        # print("Determining gap to go")
        # print(f"Current front direction : {self.agent.front}")
        # print(f"Occupied gaps : {self.occupied_neighbors}")
        for dir, possible_direction in self.graph_neighbors.items():
            # print(f"Direction : {dir}")
            if not self.occupied_neighbors[dir] and possible_direction:
                new_cell = dir
        # print(f"Direction selected : {new_cell}")
        self.agent.new_cell = new_cell