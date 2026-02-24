"""
Base State Machine pour tous les drones.

Librairie: transitions (https://transitions.readthedocs.io/)

## Concepts clés de transitions:

1. **Machine**: Container des états et transitions
2. **States**: Liste d'états (strings ou objets)
3. **Transitions**: Règles de passage entre états
   - source: état actuel
   - dest: état cible
   - trigger: méthode pour déclencher la transition
   - conditions: callback(s) optionnels pour autoriser la transition
   - before/after: callbacks exécutés avant/après la transition

4. **Callbacks**:
   - on_enter_<state>: appelé quand on entre dans un état
   - on_exit_<state>: appelé quand on sort d'un état
   - before_<trigger>: avant une transition
   - after_<trigger>: après une transition

## Avantages vs if/else:
- ✅ États explicites et visibles
- ✅ Transitions impossibles empêchées automatiquement
- ✅ Logs/debug via machine.state et callbacks
- ✅ Testabilité améliorée (mocker les transitions)
"""

from transitions import Machine
import numpy as np


class DroneStateMachine(Machine):
    """
    State Machine parent pour Leader et Follower.
    
    États communs:
    - TAKEOFF: montée à altitude cible
    - IDLE: drone inactif (après takeoff avant exécution)
    """
    
    # ========== ÉTATS ==========
    states = [
        'TAKEOFF',      # Phase de décollage
        'IDLE',         # État d'attente
    ]
    
    def __init__(self, drone_obj, initial='TAKEOFF'):
        """
        Args:
            drone_obj: objet Drone (leader ou follower) auquel cette machine s'attache
            initial: état initial (par défaut TAKEOFF)
        """
        self.drone = drone_obj
        
        # ========== TRANSITIONS DE BASE ==========
        transitions = [
            # Décollage → Idle (après 100 steps)
            {
                'trigger': 'reach_idle',
                'source': 'TAKEOFF',
                'dest': 'IDLE',
                'before': 'on_exit_takeoff'
            },
        ]
        
        # Initialiser la machine
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial=initial,
            ignore_invalid_triggers=False,  # Lever une erreur si trigger invalide
            auto_transitions=False,          # Pas de transitions auto (TAKEOFF→TAKEOFF)
        )
        
        # Ajouter callbacks pour les entrées/sorties d'état
        self.on_enter('TAKEOFF', self.on_enter_takeoff)
        self.on_enter('IDLE', self.on_enter_idle)
    
    # ========== CALLBACKS D'ENTRÉE/SORTIE ==========
    
    def on_enter_takeoff(self):
        """Appelé quand on entre en TAKEOFF"""
        print(f"[{self.drone.__class__.__name__}] → TAKEOFF")
    
    def on_exit_takeoff(self):
        """Appelé juste avant de quitter TAKEOFF"""
        print(f"[{self.drone.__class__.__name__}] ← TAKEOFF")
    
    def on_enter_idle(self):
        """Appelé quand on entre en IDLE"""
        print(f"[{self.drone.__class__.__name__}] → IDLE")
    
    # ========== HELPERS ==========
    
    def get_distance_to(self, other_drone):
        """Distance euclidienne vers un autre drone"""
        return np.linalg.norm(
            np.array(self.drone.position) - np.array(other_drone.position)
        )
    
    def get_action(self):
        """Retourner l'action actuelle du drone"""
        return self.drone.action
    
    def set_action(self, action):
        """Setter pour l'action du drone"""
        self.drone.action = action
