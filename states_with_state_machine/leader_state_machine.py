"""
State Machine pour le Leader.

États:
- TAKEOFF: montée initiale
- WAITING_FOR_FOLLOWER: on attend que le follower se rapproche (distance > 0.51 m)
- MOVING_FORWARD: on suit la branche détectée par lidar
- ALIGNMENT: on s'aligne avec le gap (angle > 10°)

Transitions:
TAKEOFF → MOVING_FORWARD (après 100 steps)
MOVING_FORWARD ⇄ WAITING_FOR_FOLLOWER (basé sur distance follower)
MOVING_FORWARD ⇄ ALIGNMENT (basé sur angle au gap)
"""

from transitions import Machine
import numpy as np
import math


class LeaderStateMachine(Machine):
    
    # ========== ÉTATS LEADER ==========
    states = [
        'TAKEOFF',
        'MOVING_FORWARD',
        'WAITING_FOR_FOLLOWER',
        'ALIGNMENT',
    ]
    
    def __init__(self, leader_obj, initial='TAKEOFF'):
        """
        Args:
            leader_obj: objet Leader
        """
        self.leader = leader_obj
        self.step_count = 0  # Compteur d'étapes pour la condition de transition
        
        # ========== TRANSITIONS ==========
        transitions = [
            # TAKEOFF → MOVING_FORWARD après 100 steps
            {
                'trigger': 'start_mission',
                'source': 'TAKEOFF',
                'dest': 'MOVING_FORWARD',
                'before': 'on_exit_takeoff',
                'after': 'on_enter_moving'
            },
            
            # MOVING_FORWARD → WAITING si follower trop loin
            {
                'trigger': 'follower_too_far',
                'source': 'MOVING_FORWARD',
                'dest': 'WAITING_FOR_FOLLOWER',
                'before': 'on_exit_moving',
                'after': 'on_enter_waiting'
            },
            
            # WAITING → MOVING_FORWARD si follower assez proche
            {
                'trigger': 'follower_close_enough',
                'source': 'WAITING_FOR_FOLLOWER',
                'dest': 'MOVING_FORWARD',
                'before': 'on_exit_waiting',
                'after': 'on_enter_moving'
            },
            
            # MOVING_FORWARD → ALIGNMENT si angle erreur > 10°
            {
                'trigger': 'need_alignment',
                'source': 'MOVING_FORWARD',
                'dest': 'ALIGNMENT',
                'after': 'on_enter_alignment'
            },
            
            # ALIGNMENT → MOVING_FORWARD si aligné (angle < 10°)
            {
                'trigger': 'aligned',
                'source': 'ALIGNMENT',
                'dest': 'MOVING_FORWARD',
                'after': 'on_enter_moving'
            },
        ]
        
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=initial,
            ignore_invalid_triggers=True,  # Ignorer les triggers invalides (ex: aligned() en WAITING)
            auto_transitions=False,
        )
        
        # Callbacks d'entrée
        self.on_enter('TAKEOFF', self.on_enter_takeoff)
        self.on_enter('ALIGNMENT', self.on_enter_alignment)
    
    # ========== CALLBACKS D'ÉTAT ==========
    
    def on_enter_takeoff(self):
        """Décollage: action verticale"""
        print("[LEADER] → TAKEOFF")
        self.step_count = 0
    
    def on_exit_takeoff(self):
        """Quitter décollage"""
        print("[LEADER] ← TAKEOFF")
    
    def on_enter_moving(self):
        """Commencer à suivre la branche"""
        print("[LEADER] → MOVING_FORWARD")
    
    def on_exit_moving(self):
        """Arrêter le mouvement"""
        print("[LEADER] ← MOVING_FORWARD (follower trop loin)")
    
    def on_enter_waiting(self):
        """Attendre que le follower se rapproche"""
        print("[LEADER] → WAITING_FOR_FOLLOWER")
        self.leader.action = [0, 0, 0, 0.1, 0]  # Hover
    
    def on_exit_waiting(self):
        """Quitter l'attente"""
        print("[LEADER] ← WAITING_FOR_FOLLOWER (follower assez proche)")
        # Notifier le follower
        if self.leader.follower:
            self.leader.msg_to_follower("Come closer")
    
    def on_enter_alignment(self):
        """S'aligner avec le gap (rotation lente)"""
        print("[LEADER] → ALIGNMENT")
    
    # ========== MÉTHODES DE DÉCISION (appelées dans croix.py) ==========
    
    def update(self, lidar_data, lidar_ray_angles, sim_steps):
        """
        Appelé chaque iteration. Met à jour l'état selon les conditions.
        
        Args:
            lidar_data: distances lidar
            lidar_ray_angles: angles des rayons
            sim_steps: étape actuelle de simulation
        """
        self.step_count += 1
        
        # Transition: TAKEOFF → MOVING_FORWARD après 100 steps
        if self.state == 'TAKEOFF' and sim_steps >= 100:
            self.start_mission()
            return
        
        if self.state == 'TAKEOFF':
            # Durant TAKEOFF: action verticale
            return
        
        # Analyser lidar
        self.leader.sensorsAnalyzer.analyze(lidar_data, lidar_ray_angles)
        gap_direction = self.leader.sensorsAnalyzer.analyzed_data["positive gap direction"][0]
        
        # Gestion des distances avec follower
        if self.leader.follower:
            dist_to_follower = np.linalg.norm(
                np.array(self.leader.position) - np.array(self.leader.follower.position)
            )
            
            # Transitions liées au follower
            if self.state == 'MOVING_FORWARD':
                if dist_to_follower > self.leader.distance_max:
                    self.follower_too_far()
                    return
            
            elif self.state == 'WAITING_FOR_FOLLOWER':
                if dist_to_follower <= self.leader.distance_max:
                    self.follower_close_enough()
                    return
        
        # Transitions d'alignement
        if self.state in ['MOVING_FORWARD', 'ALIGNMENT']:
            angle_error = gap_direction[0]  # angle_error de la direction du gap
            angle_tolerance = 0.174  # 10 degrés
            
            if self.state == 'MOVING_FORWARD' and abs(angle_error) > angle_tolerance:
                self.need_alignment()
            elif self.state == 'ALIGNMENT' and abs(angle_error) <= angle_tolerance:
                self.aligned()
        
        # Exécuter l'action correspondant à l'état
        self._execute_action(gap_direction)
    
    def _execute_action(self, gap_direction):
        """Exécuter l'action correspondant à l'état actuel"""
        if self.state == 'TAKEOFF':
            # Décollage géré dans croix.py (on ne fait rien ici)
            pass
        
        elif self.state == 'WAITING_FOR_FOLLOWER':
            # Déjà set dans on_enter_waiting (hover)
            pass
        
        elif self.state in ['MOVING_FORWARD', 'ALIGNMENT']:
            # Utiliser le contrôleur de follow_the_branch
            gap_index = 0  # Suivre le premier (plus grand) gap
            nb_gaps = len(self.leader.sensorsAnalyzer.analyzed_data["positive gap direction"])
            self.leader.follow_the_branch(
                gap_direction,
                gap_index,
                nb_gaps
            )
