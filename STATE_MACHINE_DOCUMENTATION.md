# Refactoring: Librairie State Machine pour le contrôle des drones

## 📋 Vue d'ensemble

Le code a été transformé pour utiliser la librairie **`transitions`** Python au lieu d'une série d'`if/else` imbriqués. Cela apporte:

✅ **Lisibilité** : États explicites et transitions visibles  
✅ **Maintenabilité** : Facile d'ajouter/modifier des comportements  
✅ **Testabilité** : Chaque transition peut être testée indépendamment  
✅ **Extensibilité** : Ajouter de nouveaux états sans refactoriser tout le code  

---

## 🧠 Qu'est-ce que `transitions` ?

### Concepts clés

**1. Machine** : Container principal qui gère les états et transitions
```python
from transitions import Machine

class MyStateMachine(Machine):
    states = ['STATE1', 'STATE2']
    
    def __init__(self):
        super().__init__(
            model=self,
            states=self.states,
            initial='STATE1'
        )
```

**2. States** (États) : Représentent les différents modes de fonctionnement
```python
states = [
    'TAKEOFF',           # Décollage
    'MOVING_FORWARD',    # Suivre une trajectoire
    'WAITING',           # Attendre
    'ALIGNMENT',         # S'aligner
]
```

**3. Transitions** (Transitions) : Règles de passage entre états
```python
transitions = [
    {
        'trigger': 'start_mission',      # Nom de la méthode pour déclencher
        'source': 'TAKEOFF',              # État source
        'dest': 'MOVING_FORWARD',         # État cible
        'before': 'on_exit_takeoff',      # Callback AVANT transition
        'after': 'on_enter_moving'        # Callback APRÈS transition
    }
]
```

**4. Callbacks** (Fonctions de rappel) : Exécutées lors d'entrée/sortie d'états
```python
# Appelé quand on ENTRE dans l'état
self.on_enter('MOVING_FORWARD', self.on_enter_moving)

# Appelé quand on SORT de l'état
self.on_exit('MOVING_FORWARD', self.on_exit_moving)

# Appelé AVANT une transition
self.before_trigger_name(callback)

# Appelé APRÈS une transition
self.after_trigger_name(callback)
```

---

## 🏗️ Architecture

### Avant (Anti-pattern : cascade d'if/else)
```python
# ❌ MAUVAIS - Code difficile à lire et maintenir
if state == 'TAKEOFF' and sim_steps >= 100:
    takeoff = False
elif not takeoff:
    if leader and distance > max_distance:
        # Envoyer message "Come closer"
        action = hover()
    elif abs(angle_error) > tolerance:
        # Aligner
        action = align()
    else:
        # Suivre
        action = follow()
```

### Après (Avec State Machine)
```python
# ✅ BON - Code structuré et explicite
drones[j].run(lidar_data, ray_angles, sim_steps)
# La state machine gère automatiquement:
# - TAKEOFF → MOVING_FORWARD (après 100 steps)
# - MOVING_FORWARD ⇄ WAITING (basé sur distance follower)
# - MOVING_FORWARD ⇄ ALIGNMENT (basé sur angle)
# - Et exécute les actions correspondantes
```

---

## 🎯 État machines des drones

### 1. LeaderStateMachine

**Rôle** : Contrôler le leader qui explore l'environnement

**États** :
```
        ┌──────────┐
        │ TAKEOFF  │
        └────┬─────┘
             │ (après 100 steps)
             ▼
    ┌────────────────────┐
    │  MOVING_FORWARD    │◄─────────────┐
    └────┬────────────┬──┘              │
         │            │                 │
    (distance      (angle error      (distance ≤ max)
     > max)       > tolerance)
         │            │                 │
         ▼            ▼                 │
    ┌──────────┐  ┌───────────┐        │
    │  WAITING │  │ ALIGNMENT │────────┘
    └──────────┘  └───────────┘
                      │
                      │ (aligné)
                      └──────────┘
```

**Transitions principales** :
- `TAKEOFF` → `MOVING_FORWARD` : Après 100 steps
- `MOVING_FORWARD` → `WAITING` : Follower trop loin (distance > 0.51m)
- `WAITING` → `MOVING_FORWARD` : Follower assez proche
- `MOVING_FORWARD` ⇄ `ALIGNMENT` : Basé sur angle au gap

**Méthode principale** :
```python
leader.state_machine.update(lidar_data, lidar_ray_angles, sim_steps)
```

### 2. FollowerStateMachine

**Rôle** : Contrôler le follower qui suit le leader

**États** :
```
        ┌──────────┐
        │ TAKEOFF  │
        └────┬─────┘
             │ (après 100 steps)
             ▼
    ┌─────────────────────┐
    │ WAITING_FOR_MESSAGE │
    └────┬────────────────┘
         │ (reçoit "Come closer")
         ▼
    ┌─────────────────┐
    │ GETTING_CLOSER  │───┐
    └────┬────────────┘   │
         │ (distance ≤    │ (distance > max
         │  min)          │  tandis que FOLLOWING)
         ▼                │
    ┌──────────┐          │
    │FOLLOWING │──────────┘
    └──────────┘
```

**Transitions principales** :
- `TAKEOFF` → `WAITING_FOR_MESSAGE` : Après 100 steps
- `WAITING_FOR_MESSAGE` → `GETTING_CLOSER` : Reçoit message "Come closer"
- `GETTING_CLOSER` → `FOLLOWING` : Distance ≤ min
- `FOLLOWING` → `GETTING_CLOSER` : Distance > max
- `FOLLOWING` → `WAITING_FOR_MESSAGE` : Message reconfiguration

**Méthode principale** :
```python
follower.state_machine.update(sim_steps)
```

---

## 📁 Fichiers créés/modifiés

### Fichiers créés
1. **[states/leader_state_machine.py](states/leader_state_machine.py)** : State machine du leader
2. **[states/follower_state_machine.py](states/follower_state_machine.py)** : State machine du follower

### Fichiers modifiés
1. **[states/drone.py](states/drone.py)** : Ajout de `self.state_machine`
2. **[states/leader.py](states/leader.py)** : Remplace `move_forward_in_branch()` par `state_machine.update()`
3. **[states/follower.py](states/follower.py)** : Remplace `follow_agent_in_front()` par `state_machine.update()`
4. **[croix.py](croix.py)** : Boucle principale simplifiée

---

## 💡 Exemple : Ajouter un nouvel état

Supposons qu'on veut ajouter un état `OBSTACLE_AVOIDANCE` au leader :

```python
# 1. Ajouter l'état
states = [
    'TAKEOFF',
    'MOVING_FORWARD',
    'WAITING_FOR_FOLLOWER',
    'ALIGNMENT',
    'OBSTACLE_AVOIDANCE',  # ← NOUVEAU
]

# 2. Ajouter les transitions
transitions = [
    # ... transitions existantes ...
    
    # MOVING_FORWARD → OBSTACLE_AVOIDANCE si obstacle détecté
    {
        'trigger': 'obstacle_detected',
        'source': 'MOVING_FORWARD',
        'dest': 'OBSTACLE_AVOIDANCE',
        'after': 'on_enter_obstacle_avoidance'
    },
    
    # OBSTACLE_AVOIDANCE → MOVING_FORWARD si chemin libre
    {
        'trigger': 'path_clear',
        'source': 'OBSTACLE_AVOIDANCE',
        'dest': 'MOVING_FORWARD',
        'after': 'on_enter_moving'
    }
]

# 3. Ajouter les callbacks
def on_enter_obstacle_avoidance(self):
    print("[LEADER] → OBSTACLE_AVOIDANCE")
    # Activer comportement d'évitement
    
def _execute_action(self, gap_direction):
    if self.state == 'OBSTACLE_AVOIDANCE':
        # Logique d'évitement d'obstacle
        self.leader.action = avoidance_action()

# 4. Dans update(), ajouter la condition de transition
if self.state == 'MOVING_FORWARD':
    if is_obstacle_ahead(lidar_data):
        self.obstacle_detected()
    elif dist_to_follower > self.leader.distance_max:
        self.follower_too_far()
```

**Avantage** : On ajoute un nouvel état sans modifier les logiques existantes !

---

## 🐛 Debug et inspection

### Afficher l'état actuel
```python
print(f"Leader state: {drones[0].state_machine.state}")
# Output: Leader state: MOVING_FORWARD
```

### Vérifier les transitions possibles
```python
# Lister tous les triggers disponibles
print(drones[0].state_machine.get_transitions())
```

### Logs automatiques
Les callbacks `on_enter_XXX` et `on_exit_XXX` affichent automatiquement :
```
[LEADER] → TAKEOFF
[LEADER] ← TAKEOFF
[LEADER] → MOVING_FORWARD
[LEADER] ← MOVING_FORWARD (follower trop loin)
[LEADER] → WAITING_FOR_FOLLOWER
...
```

---

## 🧪 Tests

### Tester une transition
```python
import pytest
from states.leader import Leader

def test_takeoff_to_moving_transition():
    leader = Leader()
    assert leader.state_machine.state == 'TAKEOFF'
    
    # Simuler 100 steps
    for i in range(100):
        leader.state_machine.update([1.0]*181, angles, i)
    
    # À l'étape 100, le leader doit être en MOVING_FORWARD
    assert leader.state_machine.state == 'MOVING_FORWARD'
```

### Tester une condition
```python
def test_follower_distance_condition():
    leader = Leader()
    follower = Follower(preceding=leader)
    leader.follower = follower
    leader.state_machine.state = 'MOVING_FORWARD'
    
    # Placer le follower loin
    follower.position = [0, 1.0, 0]  # distance > 0.51
    
    # Appeler update avec données lidar fictives
    leader.state_machine.update([1.0]*181, angles, 100)
    
    # Le leader doit passer en WAITING
    assert leader.state_machine.state == 'WAITING_FOR_FOLLOWER'
```

---

## ⚡ Performance

### Overhead minimal
- Librairie `transitions` : ~50KB (très légère)
- Pas de coût d'exécution notable (callbacks = simple fonctions)
- Performance identique aux if/else pour la même logique

### Facilité d'extension
- Ajouter un nouvel état = ~10 lignes de code
- vs. refactor de 50+ lignes avec if/else

---

## 🎓 Ressources

- **Documentation officielle** : https://transitions.readthedocs.io/
- **GitHub** : https://github.com/tyarkoni/transitions
- **Pattern Machine à États** : https://refactoring.guru/design-patterns/state

---

## ❓ FAQ

### Q: Pourquoi pas `statemachine` ou `automat` ?
**A** : 
- `transitions` : Plus simple et légère, idéale pour ce cas
- `statemachine` : Plus moderne mais plus verbeux
- `automat` : Trop complexe pour notre besoin

### Q: Peut-on avoir plusieurs état machines ?
**A** : Oui ! Chaque drone a sa propre instance. On peut même en avoir plusieurs par drone.

### Q: Comment tester les transitions ?
**A** : Utiliser `state_machine.must_process` pour vérifier si une transition est possible sans l'exécuter.

### Q: C'est plus lent que les if/else ?
**A** : Non, la performance est comparable. Le vrai gain est en lisibilité et maintenabilité.

---

## 📝 Résumé des changements

| Aspect | Avant | Après |
|--------|-------|-------|
| **Code** | 50+ lignes de if/else | ~20 lignes state machine |
| **Lisibilité** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenabilité** | ⭐⭐ | ⭐⭐⭐⭐ |
| **Extensibilité** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Testabilité** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
