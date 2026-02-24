from states.drone import Drone
from states.follower_state_machine import FollowerStateMachine

class Follower(Drone):
    """
    Follower: drone qui suit le leader.
    
    Comportement via FollowerStateMachine:
    - TAKEOFF: montée initiale
    - WAITING_FOR_MESSAGE: attend les ordres du leader
    - GETTING_CLOSER: se rapproche du leader (preceding)
    - FOLLOWING: maintient distance stable avec le leader
    """
    
    def __init__(self, follower=None, position=None, preceding=None, follower_id=None, preceding_id=None): 
        super().__init__(follower=follower, position=position, preceding=preceding, follower_id=follower_id, preceding_id=preceding_id)
        
        # Créer la state machine pour ce Follower
        self.state_machine = FollowerStateMachine(self, initial='TAKEOFF')
    
    def run(self, lidar_data, lidar_ray_angles, sim_steps):
        """
        Appelé chaque étape de simulation.
        Délègue au state machine pour décider de l'action.
        
        Args:
            lidar_data: distances lidar (pas utilisées pour le follower)
            lidar_ray_angles: angles des rayons lidar (pas utilisées)
            sim_steps: étape actuelle de simulation
        """
        # Mettre à jour la state machine
        # Elle gère les transitions et exécute l'action appropriée
        self.state_machine.update(sim_steps)


        