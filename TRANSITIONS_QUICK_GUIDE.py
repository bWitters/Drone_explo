"""
GUIDE RAPIDE: Transitions Library

Un résumé des concepts principaux pour bien comprendre et utiliser
la librairie 'transitions' dans votre projet de drones.
"""

# ============================================================================
# 1. CONCEPTS FONDAMENTAUX
# ============================================================================

"""
🎯 STATE MACHINE (Machine à États Finie)

Une state machine est un modèle de calcul qui:
- A un ensemble FINI d'états possibles
- Peut passer d'un état à un autre via des TRANSITIONS
- Exécute des actions en entrant/sortant des états

Analogie réelle:
┌─────────────────────────────────────────────┐
│         Feu tricolore                       │
├─────────────────────────────────────────────┤
│ États: RED, YELLOW, GREEN                   │
│ Transitions:                                │
│  - RED → GREEN (après timer)                │
│  - GREEN → YELLOW (après timer)             │
│  - YELLOW → RED (après timer)               │
│ Actions:                                    │
│  - on_enter_RED: arrêter les voitures      │
│  - on_enter_GREEN: laisser passer          │
└─────────────────────────────────────────────┘
"""

# ============================================================================
# 2. COMPOSANTS CLÉS
# ============================================================================

from transitions import Machine

class SimpleDrone(object):
    """Exemple minimal d'une state machine pour un drone."""
    
    # ╔════════════════════════════════════════════════════════════╗
    # ║ 1. DÉFINIR LES ÉTATS                                        ║
    # ╚════════════════════════════════════════════════════════════╝
    states = [
        'IDLE',        # Drone au repos
        'TAKING_OFF',  # En train de monter
        'FLYING',      # Vole normalement
        'LANDING',     # En train de descendre
    ]
    
    def __init__(self):
        # ╔════════════════════════════════════════════════════════════╗
        # ║ 2. DÉFINIR LES TRANSITIONS                                 ║
        # ╚════════════════════════════════════════════════════════════╝
        transitions = [
            # Format simple
            {'trigger': 'take_off',
             'source': 'IDLE',
             'dest': 'TAKING_OFF'},
            
            # Format avancé (avec callbacks)
            {'trigger': 'reach_altitude',
             'source': 'TAKING_OFF',
             'dest': 'FLYING',
             'before': 'on_exit_taking_off',
             'after': 'on_enter_flying'},
            
            # Transition avec condition
            {'trigger': 'land',
             'source': 'FLYING',
             'dest': 'LANDING',
             'conditions': 'fuel_available'},  # Voir section 5
            
            {'trigger': 'landed',
             'source': 'LANDING',
             'dest': 'IDLE'},
        ]
        
        # ╔════════════════════════════════════════════════════════════╗
        # ║ 3. CRÉER LA MACHINE                                        ║
        # ╚════════════════════════════════════════════════════════════╝
        self.machine = Machine(
            model=self,              # 'self' devient le modèle
            states=self.states,      # États possibles
            transitions=transitions, # Règles de transition
            initial='IDLE',          # État de départ
            auto_transitions=False   # Pas de transitions auto (A→A)
        )
        
        # ╔════════════════════════════════════════════════════════════╗
        # ║ 4. DÉFINIR LES CALLBACKS D'ENTRÉE/SORTIE D'ÉTAT           ║
        # ╚════════════════════════════════════════════════════════════╝
        self.machine.on_enter('IDLE', self.on_enter_idle)
        self.machine.on_exit('TAKING_OFF', self.on_exit_taking_off)
    
    # Callbacks d'état
    def on_enter_idle(self):
        print("🛬 Drone en repos")
    
    def on_exit_taking_off(self):
        print("✅ Altitude atteinte !")
    
    def on_enter_flying(self):
        print("🛸 Drone en vol normal")
    
    # Condition (optionnel)
    def fuel_available(self):
        return True  # Simulé


# ============================================================================
# 3. UTILISATION DE LA MACHINE
# ============================================================================

print("="*70)
print("UTILISATION SIMPLE")
print("="*70)

drone = SimpleDrone()
print(f"État initial: {drone.state}")  # Output: IDLE

# Déclencher une transition
drone.take_off()
print(f"État après take_off: {drone.state}")  # Output: TAKING_OFF

# Autre transition
drone.reach_altitude()
print(f"État après reach_altitude: {drone.state}")  # Output: FLYING

# Tentative de transition invalide
try:
    drone.take_off()  # Can't take off from FLYING
except:
    print("❌ Transition invalide depuis FLYING")


# ============================================================================
# 4. CALLBACKS AVANCÉS
# ============================================================================

"""
La librairie transitions supporte plusieurs types de callbacks:

1. on_enter_<state>: Appelé quand on ENTRE dans un état
   - Utile pour: initialiser, démarrer un processus
   
2. on_exit_<state>: Appelé quand on SORT d'un état
   - Utile pour: nettoyer, arrêter un processus
   
3. before_<trigger>: Appelé AVANT une transition
   - Utile pour: vérifier les préconditions
   
4. after_<trigger>: Appelé APRÈS une transition
   - Utile pour: enregistrer les changements

Ordre d'exécution:
    État A  ─────→  État B
     ↑               ↓
   on_exit_A    on_enter_B
     ↑               ↓
   before_trigger  after_trigger
"""

class AdvancedDrone(Machine):
    """Exemple avec callbacks avancés."""
    
    states = ['IDLE', 'FLYING']
    
    def __init__(self):
        transitions = [
            {'trigger': 'start_mission',
             'source': 'IDLE',
             'dest': 'FLYING',
             'before': 'pre_flight_check',   # ← AVANT transition
             'after': 'post_flight_setup'}    # ← APRÈS transition
        ]
        
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial='IDLE'
        )
        
        self.on_enter('FLYING', self.on_enter_flying)
        self.on_exit('IDLE', self.on_exit_idle)
    
    def pre_flight_check(self):
        print("🔧 Vérification pré-vol...")
        # Vérifier batterie, capteurs, etc.
    
    def on_exit_idle(self):
        print("🚀 Quitter le repos")
    
    def on_enter_flying(self):
        print("✈️  Drone en vol !")
    
    def post_flight_setup(self):
        print("📡 Configuration post-décollage...")
        # Démarrer la navigation, etc.


# ============================================================================
# 5. CONDITIONS (Conditional Transitions)
# ============================================================================

"""
Une transition peut avoir une CONDITION qui doit être vraie
pour que la transition s'exécute.

Syntaxe:
    {'trigger': 'try_land',
     'source': 'FLYING',
     'dest': 'LANDING',
     'conditions': 'is_safe_to_land'}  # Fonction qui retourne bool

Plusieurs conditions:
    'conditions': ['condition1', 'condition2']
    # Toutes doivent être True
"""

class ConditionalDrone(Machine):
    states = ['FLYING', 'LANDING']
    
    def __init__(self, altitude=100, battery=100):
        self.altitude = altitude
        self.battery = battery
        
        transitions = [
            {'trigger': 'land',
             'source': 'FLYING',
             'dest': 'LANDING',
             'conditions': ['is_low_altitude', 'has_battery']}
        ]
        
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial='FLYING'
        )
    
    def is_low_altitude(self):
        """Condition 1: Altitude suffisamment basse"""
        result = self.altitude < 10
        print(f"  ✓ Altitude check: {self.altitude}m < 10m? {result}")
        return result
    
    def has_battery(self):
        """Condition 2: Batterie disponible"""
        result = self.battery > 10
        print(f"  ✓ Battery check: {self.battery}% > 10%? {result}")
        return result


print("\n" + "="*70)
print("TEST DE CONDITIONS")
print("="*70)

drone = ConditionalDrone(altitude=5, battery=50)
print(f"État: {drone.state}")
print(f"Tentative de landing (altitude=5, battery=50)...")
try:
    drone.land()
    print(f"✅ Landing autorisé ! État: {drone.state}")
except:
    print("❌ Landing refusé (conditions non remplies)")

drone2 = ConditionalDrone(altitude=50, battery=50)
print(f"\nTentative de landing (altitude=50, battery=50)...")
try:
    drone2.land()
    print(f"État: {drone2.state}")
except:
    print("❌ Landing refusé (altitude trop haute)")


# ============================================================================
# 6. INSPECTION D'UNE STATE MACHINE
# ============================================================================

print("\n" + "="*70)
print("INSPECTION")
print("="*70)

drone = SimpleDrone()

# État actuel
print(f"État courant: {drone.state}")

# Tous les états
print(f"États possibles: {drone.machine.states}")

# Triggers disponibles
print(f"Triggers (transitions) disponibles:")
for trigger in ['take_off', 'reach_altitude', 'land', 'landed']:
    try:
        drone.machine.get_transitions(source=drone.state, trigger=trigger)
        print(f"  ✓ {trigger}")
    except:
        print(f"  ✗ {trigger}")


# ============================================================================
# 7. MESSAGES ENTRE ÉTATS (Communication)
# ============================================================================

"""
Exemple: Passer des données entre états

Le Follower doit attendre un message du Leader pour transitioner.
On enregistre les messages dans une liste et on les lit dans update().
"""

class CommunicatingDrone(Machine):
    def __init__(self):
        self.messages = []  # Queue de messages
        
        states = ['WAITING', 'MOVING']
        transitions = [
            {'trigger': 'received_command',
             'source': 'WAITING',
             'dest': 'MOVING'}
        ]
        
        super().__init__(
            model=self,
            states=self.states,
            transitions=transitions,
            initial='WAITING'
        )
    
    def receive_message(self, msg):
        """Recevoir un message"""
        self.messages.append(msg)
        print(f"📨 Message reçu: {msg}")
    
    def update(self):
        """Appelé chaque itération"""
        if self.messages:
            msg = self.messages.pop()
            if msg == "MOVE" and self.state == 'WAITING':
                self.received_command()
                print(f"✅ Transition vers {self.state}")


# ============================================================================
# 8. BONNES PRATIQUES
# ============================================================================

"""
✅ À FAIRE:

1. Définir les états explicitement
   states = ['STATE1', 'STATE2', ...]

2. Utiliser des noms de states descriptifs
   ✓ WAITING_FOR_FOLLOWER
   ✗ W

3. Documenter les transitions
   # Commentaires explicites sur le pourquoi

4. Utiliser les callbacks pour les actions
   on_enter_XXX() pour les entrées
   on_exit_XXX() pour les sorties

5. Tester les transitions
   # Unitaire: tester chaque transition
   # Intégration: tester les chaînes d'états

❌ À ÉVITER:

1. Trop d'états (> 10)
   → Rendre la logique complexe
   → Utiliser plutôt plusieurs machines

2. États avec la même logique
   → Fusionner ou utiliser l'héritage

3. Transitions sans condition ni callback
   → Dur à déboguer

4. Oublier les états d'erreur
   → Toujours avoir un état IDLE ou ERROR

5. Machine globale unique
   → Créer une machine par drone/entité
"""

print("\n" + "="*70)
print("✅ Guide State Machine terminé !")
print("="*70)
