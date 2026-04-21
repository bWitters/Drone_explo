#Imports
from transitions import Machine
from transitions.extensions.diagrams import HierarchicalGraphMachine
import pyperclip

#Const
COPY_DIAGRAM = True

#Classes
class DroneMachine():
    states = ['takeoff', 'scanGaps', 'followTheGap', 'centerInIntersection', 'failed', "callFollower", "alignWithGap", 'deadEnd']
    transitions = [
        {'trigger' : 'update', "source" : 'takeoff',        "dest" : 'scanGaps',            'conditions':"checkHeight"},
        {'trigger' : "update", "source" : "scanGaps",       "dest" : "followTheGap",        'conditions':"goodDirection"},
        {'trigger' : "update", "source" : "followTheGap",   "dest" : "scanGaps",            'conditions':"moreGaps"},
        {'trigger' : "update", "source" : "scanGaps",       "dest" : "followTheGap",        'conditions':"twoGaps"},   
        {'trigger' : "update", "source" : "scanGaps",       "dest" : "centerInIntersection",'conditions':"moreThanTwoGaps"},
        {'trigger' : "update", "source" : "centerInIntersection", "dest" : "alignWithGap",  'conditions':"goodDirection"},
        {'trigger' : "update", "source" : "followTheGap",   "dest" : "callFollower",        'conditions':"directionChanged"},
        {'trigger' : "update", "source" : "alignWithGap",   "dest" : "callFollower",        'conditions':"directionChanged"},
        {'trigger' : "update", "source" : "followTheGap",   "dest" : "deadEnd",             'conditions':"oneGap"}
    ]
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.height = 50
        self.yaw = 0
        self.gap_direction = None
        self.number_of_gaps = None
        self.previous_gap_direction = None

        self.machine = Machine(model=self, states=DroneMachine.states, transitions=DroneMachine.transitions, initial='takeoff')
        
    def checkHeight(self):
        return self.height >= 100
    
    def goodDirection(self):
        return self.yaw == self.gap_direction
    
    def moreGaps(self):
        return self.number_of_gaps >= 2
    
    def twoGaps(self):
        return self.number_of_gaps == 2
    
    def moreThanTwoGaps(self):
        return self.number_of_gaps > 2
    
    def directionChanged(self):
        return self.gap_direction != self.previous_gap_direction
    
    def oneGap(self):
        return self.number_of_gaps == 1
    
    def _execute(self):
        if self.state == 'takeoff':
            self.height += 10
            print("Increasing height")
        
        if self.state == "scanGaps" :
            while self.yaw < 90:
                self.yaw += 10
                print("Rotating")
            while self.yaw > 0:
                self.yaw -= 10
                print("Rotating back to origin")
            print(str(self.previous_gap_direction) + "était la direction")
            print(str(self.gap_direction) + "est la nouvelle direction choisie")

        if self.state == "followTheGap":
            #Avancer dans le couloir dans la direction du gap
            #Ajuster la position dans le couloir en fonction de la distance avec les murs sur les cotés
            self.action
        
        if self.state == "centerInIntersection":
            #Soit utiliser le cone pour et dire que si la distance minimale est >2 mètres on est centré
            #Soit la technique de mettre le drone de travers pour faire correspondre les distances minimales avec les angles
            self.action

        if self.state == "alignWithGap":
            while self.yaw != self.gap_direction:
                if self.yaw < self.gap_direction:
                    self.yaw += self.gap_direction-self.yaw
                else:
                    self.yaw += self.yaw - self.gap_direction
        
        if self.state == "deadEnd":
            init_yaw = self.yaw
            while self.yaw != init_yaw -180:
                self.yaw += 10
            

if __name__ == "__main__":
    #Init Machine
    drone = DroneMachine("test")

    #Run
    if COPY_DIAGRAM:
        m = HierarchicalGraphMachine(states=drone.states, transitions=drone.transitions, initial="takeoff")

        pyperclip.copy(m.get_graph().draw(None))

    for i in range(10):
        print(drone.state)
        drone._execute()
        drone.update()