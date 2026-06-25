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
        print("Sending reconfig")
        self.send_com_follower("Reconfig", self.agent.front)
        self.send("standby_send_reconfig_message")