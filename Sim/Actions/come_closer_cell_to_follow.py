from agents import Drones
from Actions.Action import Action
from situation_dict import Situation

class ComeCloserDirectionToGo(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)
    
    @property
    def situation(self) -> Situation:
        return self.agent.situation.situation
    
    @property
    def gaps(self) -> dict:
        return self.agent.sensor_data.gaps_dir_world
    @property
    def occupied_neighbors(self) -> dict:
        return self.agent.sensor_data.occupied_neighborhood

    def action(self):
        """ 
        Retourne la nouvelle cellule de l'agent qui demande une approche
        """
        new_cell = None
        #print("coucou, getting direction")
        #print(self.gaps)
        if self.situation[Situation.COME_CLOSER][1] != None:
            print(self.situation[Situation.COME_CLOSER][1])
            if self.gaps[self.situation[Situation.COME_CLOSER][1]]:
                new_cell =  self.situation[Situation.COME_CLOSER][1]
            self.agent.new_cell = new_cell