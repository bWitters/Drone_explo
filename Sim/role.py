from statemachine import StateChart, State

class Role(StateChart):
    """State machine for the role of an agent"""

    stock = State("Stock", initial=True)
    leader = State("Leader")
    follower = State("Follower")
    reconfig_leader = State("ReconfigLeader")
    reconfig_follower = State("ReconfigFollower")

    become_leader = stock.to(leader) | follower.to(leader) | reconfig_follower.to(leader) | reconfig_leader.to(leader)
    become_follower = stock.to(follower) | leader.to(follower) | reconfig_follower.to(follower) | reconfig_leader.to(follower)
    become_reconfig_follower = leader.to(reconfig_follower) | follower.to(reconfig_follower) | reconfig_follower.to.itself(internal=True) | reconfig_leader.to(reconfig_follower)
    become_reconfig_leader = leader.to(reconfig_leader) | follower.to(reconfig_leader) | reconfig_leader.to.itself(internal=True) | reconfig_follower.to(reconfig_leader)

    def __init__(self, agent):

        self.agent = agent

        super().__init__()
        self.activate_initial_state()

    def on_enter_state(self, state):
        print(f"Agent {self.agent.unique_id} becoming role: {state}")