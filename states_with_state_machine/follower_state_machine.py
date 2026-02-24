"""
State Machine pour le Follower.

États:
- TAKEOFF: montée initiale
- WAITING_FOR_MESSAGE: attend le message "Come closer" du leader
- GETTING_CLOSER: se rapproche du leader
- FOLLOWING: suit le leader à distance stable

Transitions:
TAKEOFF → WAITING_FOR_MESSAGE (après 100 steps)
WAITING_FOR_MESSAGE → GETTING_CLOSER (quand reçoit "Come closer")
GETTING_CLOSER → FOLLOWING (quand distance OK)
FOLLOWING → GETTING_CLOSER (si distance > max)
FOLLOWING → WAITING_FOR_MESSAGE (si message pour reconfiguration)
"""

from transitions import Machine
import numpy as np


class FollowerStateMachine(Machine):
    
    # ========== ÉTATS FOLLOWER ==========
    states = [
        'TAKEOFF',
        'WAITING_FOR_MESSAGE',
        'GETTING_CLOSER',
        'FOLLOWING',
    ]
    
    def __init__(self, follower_obj, initial='TAKEOFF'):
        """
        Args:
            follower_obj: objet Follower
        """
        self.follower = follower_obj
        
        # ========== TRANSITIONS ==========
        transitions = [
            # TAKEOFF → WAITING après 100 steps
            {
                'trigger': 'start_mission',
                'source': 'TAKEOFF',
                'dest': 'WAITING_FOR_MESSAGE',
                'before': 'on_exit_takeoff',
                'after': 'on_enter_waiting'
            },
            
            # WAITING → GETTING_CLOSER quand reçoit "Come closer"
            {
                'trigger': 'received_come_closer',
                'source': 'WAITING_FOR_MESSAGE',
                'dest': 'GETTING_CLOSER',
                'after': 'on_enter_getting_closer'
            },
            
            # GETTING_CLOSER → FOLLOWING quand distance OK
            {
                'trigger': 'distance_ok',
                'source': 'GETTING_CLOSER',
                'dest': 'FOLLOWING',
                'after': 'on_enter_following'
            },
            
            # FOLLOWING → GETTING_CLOSER si distance > max
            {
                'trigger': 'too_far',
                'source': 'FOLLOWING',
                'dest': 'GETTING_CLOSER',
                'after': 'on_enter_getting_closer'
            },
            
            # FOLLOWING → WAITING si message de reconfiguration
            {
                'trigger': 'received_reconfiguration',
                'source': 'FOLLOWING',
                'dest': 'WAITING_FOR_MESSAGE',
                'after': 'on_enter_waiting'
            },
            
            # GETTING_CLOSER → FOLLOWING avec transitive (en cas de message rapide)
            {
                'trigger': 'received_come_closer',
                'source': 'GETTING_CLOSER',
                'dest': 'GETTING_CLOSER',  # Rester dans le même état
                'after': 'remind_coming_closer'
            },
        ]
        
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=initial,
            ignore_invalid_triggers=True,
            auto_transitions=False,
        )
        
        # Callbacks d'entrée
        self.on_enter('TAKEOFF', self.on_enter_takeoff)
    
    # ========== CALLBACKS D'ÉTAT ==========
    
    def on_enter_takeoff(self):
        """Décollage: action verticale"""
        print("[FOLLOWER] → TAKEOFF")
    
    def on_exit_takeoff(self):
        """Quitter décollage"""
        print("[FOLLOWER] ← TAKEOFF")
    
    def on_enter_waiting(self):
        """Attendre les ordres du leader"""
        print("[FOLLOWER] → WAITING_FOR_MESSAGE")
        # Nettoyer les anciens messages
        self.follower.message_received.clear()
        self.follower.action = [0, 0, 0, 0.1, 0]  # Hover
    
    def on_enter_getting_closer(self):
        """Se rapprocher du leader (drone precedent)"""
        print("[FOLLOWER] → GETTING_CLOSER")
    
    def remind_coming_closer(self):
        """Rappel qu'on est déjà en train de se rapprocher"""
        print(f"[FOLLOWER] En train de se rapprocher... (distance: {self._get_distance_to_preceding():.2f}m)")
    
    def on_enter_following(self):
        """Suivre à distance stable"""
        print("[FOLLOWER] → FOLLOWING (distance stable)")
        # Garder la position actuelle (on suit à distance)
        self.follower.action = [0, 0, 0, 0.1, 0]  # Hover (suivi via le leader)
    
    # ========== MÉTHODES DE DÉCISION ==========
    
    def update(self, sim_steps):
        """
        Appelé chaque iteration. Met à jour l'état selon les conditions.
        
        Args:
            sim_steps: étape actuelle de simulation
        """
        # Transition: TAKEOFF → WAITING après 100 steps
        if self.state == 'TAKEOFF' and sim_steps >= 100:
            self.start_mission()
            return
        
        if self.state == 'TAKEOFF':
            return
        
        # Vérifier les messages reçus (depuis le leader)
        if self.follower.message_received:
            last_msg = self.follower.message_received[-1]
            
            if last_msg == "Come closer":
                # Déclencher transition appropriée
                if self.state == 'WAITING_FOR_MESSAGE':
                    self.received_come_closer()
                    return
                elif self.state == 'GETTING_CLOSER':
                    self.remind_coming_closer()
                    # Ne pas retourner, continuer avec distance check
            
            elif last_msg == "Reconfiguration":
                if self.state == 'FOLLOWING':
                    self.received_reconfiguration()
                    return
        
        # Gestion des distances
        if self.state == 'GETTING_CLOSER':
            dist = self._get_distance_to_preceding()
            if dist is not None:
                if dist <= self.follower.distance_min:
                    self.distance_ok()
                    self.follower.message_received.pop()  # Nettoyer le message
                    return
                else:
                    # Action: se rapprocher
                    self._execute_getting_closer()
        
        elif self.state == 'FOLLOWING':
            dist = self._get_distance_to_preceding()
            if dist is not None and dist > self.follower.distance_max:
                self.too_far()
                return
    
    def _execute_getting_closer(self):
        """Exécuter le rapprochement (vers le leader/preceding)"""
        if self.follower.preceding:
            direction = np.array(self.follower.preceding.position) - np.array(self.follower.position)
            self.follower.action = [direction[0], direction[1], direction[2], 0.1, 0]
            print(f"[FOLLOWER] Se rapproche... (distance: {np.linalg.norm(direction):.2f}m)")
    
    def _get_distance_to_preceding(self):
        """Distance au drone précédent (leader)"""
        if self.follower.preceding:
            return np.linalg.norm(
                np.array(self.follower.position) - np.array(self.follower.preceding.position)
            )
        return None
