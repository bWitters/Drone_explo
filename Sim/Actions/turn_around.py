from agents import Drones
from Actions.Action import Action
from situation_dict import Situation

class TurnAround(Action):
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
        Retourne la nouvelle cellule derrière l'agent
        """
        new_cell = None
        if self.graph_neighbors["B"]:
            new_cell = self.graph_neighbors["B"][0]
        self.agent.new_cell = new_cell