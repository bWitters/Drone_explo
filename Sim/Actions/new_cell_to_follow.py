from agents import Drones
from Actions.Action import Action
from situation_dict import Situation

class NewCellToFollow(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)
    
    @property
    def situation(self) -> Situation:
        return self.agent.situation.situation
    @property
    def graph_neighbors(self) -> dict:
        return self.agent.sensor_data.graph_neighborhood
    @property
    def occupied_neighbors(self) -> dict:
        return self.agent.sensor_data.occupied_neighborhood

    def action(self):
        """ 
        Retourne la nouvelle cellule de l'agent à suivre
        """
        new_cell = None
        for dir, cell in self.occupied_neighbors.items():
            if self.occupied_neighbors[dir]:
                new_cell = cell[0]
        self.agent.new_cell = new_cell