from agents import Drones
from Actions.Action import Action
from communication import Com

class SendReconfig(Com, Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        Action.__init__(self,self.name)

    def action(self):
        """ 
        Retourne la nouvelle cellule de l'agent à suivre
        """
        print("Sending reconfig") # TODO ENVOYER à DEVNAT PUISQUE QU4ON TOURNE
        self.send_com_follower("Reconfig", self.agent.front) # TODO : Faire un deuxieme capteur pour emettre en broadcast les come closer et utiliser le systeme de detection des gaps et les positions des drones pour recevoir les messages qui viennent de devant/derriere
        self.send("standby_send_reconfig_message")