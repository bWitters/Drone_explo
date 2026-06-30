from agents import Drones
from Actions.Action import Action
from situation_dict import Situation

class RotationReconfigCurve(Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        super().__init__(self.name)
    
    @property
    def situation(self) -> Situation:
        return self.agent.situation.situation

    @property
    def front(self) -> str:
        return self.agent.front
    
    @property
    def graph_neighbors(self) -> dict:
        return self.agent.sensor_data.gaps_dir
    
    @property
    def occupied_gaps(self):
        return self.agent.sensor_data.occupied_neighborhood
    
    @property
    def new_direction(self):
        #print(f"coucou voici la cell {self.agent.new_cell}")
        return self.agent.new_cell

    def rotate(self, direction:str) -> None:
        if direction == "left":
            if self.front == "E":
                self.agent.front = "N"
            elif self.front == "N":
                self.agent.front = "W"
            elif self.front == "W":
                self.agent.front = "S"
            elif self.front == "S":
                self.agent.front = "E"
        elif direction == "right":
            if self.front == "E":
                self.agent.front = "S"
            elif self.front == "S":
                self.agent.front = "W"
            elif self.front == "W":
                self.agent.front = "N"
            elif self.front == "N":
                self.agent.front = "E"

        elif direction == "turn around":
            if self.front == "E":
                self.agent.front = "W"
            elif self.front == "W":
                self.agent.front = "E"
            elif self.front == "S":
                self.agent.front = "N"
            elif self.front == "N":
                self.agent.front = "S"

    def action(self) -> None:
        #print(self.new_direction)
        gaps = self.graph_neighbors
        if not gaps["R"]:
            self.rotate("right")
        elif not gaps["L"]:
            self.rotate("left")
