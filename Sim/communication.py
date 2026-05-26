from agents import Drones
from situation import Situation

class Com:
    def __init__(self, agent, **kwargs):
        self.agent: Drones = agent
        super().__init__(**kwargs)

    @property
    def neighboring_agents(self):
        return self.agent.neighboring_agent_list

    def send_com_follower(self, title:str, content):
        if self.neighboring_agents["F"] != None:
            #print("sending com")
            #print(content)
            self.neighboring_agents["F"].sensor_data.com_stack.put((title, content))
            self.agent.situation.situation[Situation.COME_CLOSER_SENT] = True
    
    def send_com_preceding(self, title:str, content):
        if self.neighboring_agents["P"] != None:
            self.neighboring_agents["P"].sensor_data.com_stack.put((title, content))
