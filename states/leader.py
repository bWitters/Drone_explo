from states.drone import Drone
from states.leader_state_machine import LeaderStateMachine
import numpy as np

class Leader(Drone):
    """
    Leader: drone qui explore l'environnement.
    
    Comportement via LeaderStateMachine:
    - TAKEOFF: montée initiale
    - MOVING_FORWARD: suit le gap (espace libre) détecté
    - WAITING_FOR_FOLLOWER: attend que le follower se rapproche
    - ALIGNMENT: s'aligne avec le gap si angle erreur > 10°
    """
    
    def __init__(self, follower=None, position=None, preceding=None, follower_id=None, preceding_id=None):
        super().__init__(follower=follower, position=position, preceding=preceding, follower_id=follower_id, preceding_id=preceding_id)
        
        # Créer la state machine pour ce Leader
        self.state_machine = LeaderStateMachine(self, initial='TAKEOFF')
    
    def run(self, lidar_data, lidar_ray_angles, sim_steps):
        """
        Appelé chaque étape de simulation.
        Délègue au state machine pour décider de l'action.
        
        Args:
            lidar_data: distances lidar
            lidar_ray_angles: angles des rayons lidar
            sim_steps: étape actuelle de simulation
        """
        # Mettre à jour la state machine
        # Elle gère les transitions et exécute l'action appropriée
        self.state_machine.update(lidar_data, lidar_ray_angles, sim_steps)

        # if self.lidar.loop :
        #     print("Loop management begin")
        #     self.loop_management()
        # elif self.lidar.dead_end :
        #     print("Dead end management begin")
        #     self.dead_end_management()
        # elif self.lidar.intersaction:
        #     print("Intersection management begin")
        #     self.intersection_management()
        

    # def loop_management(self):
    #     self.msg_to_follower("Reconfiguration")
    #     self.turn_around()
    #     self.

    # def dead_end_management(self):
    #     self.msg_to_follower("Reconfiguration")
    #     self.turn_around()
    
    # def intersection_management(self):
    #     self.msg_to_follower("Come closer")
    #     self.centering()
    #     self.rotation()
    #     while np.linalg.norm(np.array(self.position)-np.array(self.follower.position)) > self.distance_max:
    #         self.wait()
    #     else:
    #         self.move_forward_in_branch()
