from agents import Drones
from Actions.Action import Action
from communication import Com

class SendStopReconfig(Com, Action):
    def __init__(self, agent):
        self.agent:Drones = agent
        Action.__init__(self,self.name)

    def action(self):
        """ 
        Retourne la nouvelle cellule de l'agent à suivre
        """
        print("Sending stop reconfig")
        self.send_com_preceding("Stop_Reconfig", self.agent.front)
        self.send("standby_send_stop_reconfig_message")