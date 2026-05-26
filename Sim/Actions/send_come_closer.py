from agents import Drones
from Actions.Action import Action
from communication import Com

class SendComeCloser(Com, Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        Action.__init__(self,self.name)

    def action(self):
        """ 
        Retourne la nouvelle cellule de l'agent à suivre
        """
        #print("coucou")
        #print(self.agent.front)
        self.send_com_follower("Come Closer", self.agent.front) # TODO : Faire un deuxieme capteur pour emettre en broadcast les come closer et utiliser le systeme de detection des gaps et les positions des drones pour recevoir les messages qui viennent de devant/derriere
        self.send("standby_send_come_closer")