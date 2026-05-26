from statemachine import StateChart, State

class Role(StateChart):
    """State machine for the role of an agent"""

    stock = State("Stock", initial=True)
    leader = State("Leader")
    follower = State("Follower")
    reconfiguration = State("Reconfiguration")

    become_leader = stock.to(leader) | follower.to(leader) | reconfiguration.to(leader)
    become_follower = stock.to(follower) | leader.to(follower) | reconfiguration.to(follower)
    become_reconfiguration = leader.to(reconfiguration) | follower.to(reconfiguration) | reconfiguration.to.itself(internal=True)

    def __init__(self, agent):

        self.agent = agent

        super().__init__()
        self.activate_initial_state()

    def on_enter_state(self, state):
        print(f"Agent {self.agent.unique_id} becoming role: {state}")