# 📚 Guide d'utilisation des fichiers de State Machine

Après la refactorisation, voici comment naviguer et utiliser le code.

## 📁 Structure des fichiers

```
Drone_explo/
├── 🆕 STATE_MACHINE_DOCUMENTATION.md      (📖 LIRE EN PREMIER)
├── 🆕 TRANSITIONS_QUICK_GUIDE.py         (📖 Concepts + exemples)
├── 🆕 BEFORE_AFTER_COMPARISON.md         (📊 Avant/Après)
├── 🆕 HOW_TO_USE_STATE_MACHINES.md       (📋 Ce fichier)
├── 🆕 examples_state_machine.py          (🧪 Exemples d'utilisation)
│
├── states/
│   ├── drone.py                          (🔧 Classe parent)
│   ├── leader.py                         (🎯 Leader avec state machine)
│   ├── follower.py                       (🎯 Follower avec state machine)
│   ├── 🆕 leader_state_machine.py       (⚙️ État machine du Leader)
│   ├── 🆕 follower_state_machine.py     (⚙️ État machine du Follower)
│   └── __pycache__/
│
├── croix.py                              (🎮 Boucle principale simplifiée)
├── croix.yaml                            (⚙️ Configuration)
├── croix.urdf                            (🏗️ Modèle du corridor)
│
└── ... (autres fichiers existants)
```

## 🚀 Par où commencer ?

### 1️⃣ Comprendre les concepts (30 min)
```bash
# Lire dans cet ordre:
1. STATE_MACHINE_DOCUMENTATION.md
   └─ Comprendre: Machine, États, Transitions, Callbacks

2. TRANSITIONS_QUICK_GUIDE.py
   └─ Exécuter: python TRANSITIONS_QUICK_GUIDE.py
   └─ Voir les exemples s'exécuter
```

### 2️⃣ Voir l'architecture (15 min)
```bash
# Lire les diagrammes:
1. BEFORE_AFTER_COMPARISON.md
   └─ Visualiser: Avant (spaghetti) vs Après (machine)

2. Fichiers de state machine:
   - states/leader_state_machine.py (⚠️ Lisez les commentaires)
   - states/follower_state_machine.py
```

### 3️⃣ Exécuter des exemples (20 min)
```bash
# Tester les comportements:
python examples_state_machine.py
```

### 4️⃣ Lancer la simulation (variable)
```bash
# Utiliser normalement:
python croix.py
```

---

## 📖 Description des fichiers

### 🆕 STATE_MACHINE_DOCUMENTATION.md (180 lignes)

**Contenu:**
- ✅ Qu'est-ce que `transitions` ?
- ✅ Concepts clés (Machine, States, Transitions, Callbacks)
- ✅ Architecture des LeaderStateMachine et FollowerStateMachine
- ✅ Diagrammes d'états
- ✅ Exemple: Ajouter un nouvel état
- ✅ Debug et inspection
- ✅ Tests unitaires

**À faire:**
```python
# Lire la section "Exemple : Ajouter un nouvel état"
# pour comprendre comment étendre
```

---

### 🆕 TRANSITIONS_QUICK_GUIDE.py (400+ lignes)

**Contenu (exécutable):**
1. Concepts fondamentaux avec analogies
2. Exemple minimal (SimpleDrone)
3. Utilisation basique
4. Callbacks avancés (before, after)
5. Conditions (conditional transitions)
6. Inspection (debugging)
7. Communication entre états
8. Bonnes pratiques

**Exécuter:**
```bash
python TRANSITIONS_QUICK_GUIDE.py
# Voir les résultats s'afficher
```

---

### 🆕 BEFORE_AFTER_COMPARISON.md (350 lignes)

**Contenu:**
- ✅ Comparaison visuelle code
- ✅ Comparaison lignes de code
- ✅ Comparaison flux de décision (diagrammes)
- ✅ Comparaison testabilité
- ✅ Scénario: Debugging réel
- ✅ Scénario: Ajouter une feature

**Intérêt:**
```
🎯 Comprendre POURQUOI la refactorisation est bonne
```

---

### 🆕 examples_state_machine.py (350 lignes)

**Contenu:**
1. `inspect_drone_state()` → Inspecter l'état actuel
2. `test_transitions_manually()` → Déclencher des transitions
3. `test_distance_conditions()` → Tester les conditions
4. `add_state_change_listener()` → Écouter les changements
5. `test_follower_behavior()` → Comportement du follower
6. `simulate_with_state_machines()` → Simulation simplifiée

**Utilisation:**
```bash
python examples_state_machine.py
# Voir des tests concrets
```

---

### ⚙️ states/leader_state_machine.py (180 lignes)

**Contenu:**
- États: TAKEOFF, MOVING_FORWARD, WAITING_FOR_FOLLOWER, ALIGNMENT
- Transitions avec conditions (distance, angle)
- Callbacks d'entrée/sortie d'états
- Méthode `update()` → appelée à chaque étape

**Points clés:**
```python
class LeaderStateMachine(Machine):
    states = ['TAKEOFF', 'MOVING_FORWARD', 'WAITING_FOR_FOLLOWER', 'ALIGNMENT']
    
    # Transitions définies dans __init__()
    # Callbacks: on_enter_XXX(), on_exit_XXX()
    
    def update(self, lidar_data, lidar_ray_angles, sim_steps):
        # Appelé chaque itération pour mettre à jour l'état
```

---

### ⚙️ states/follower_state_machine.py (170 lignes)

**Contenu:**
- États: TAKEOFF, WAITING_FOR_MESSAGE, GETTING_CLOSER, FOLLOWING
- Transitions basées sur messages et distance
- Callbacks d'entrée/sortie d'états
- Méthode `update()` → appelée à chaque étape

**Points clés:**
```python
class FollowerStateMachine(Machine):
    states = ['TAKEOFF', 'WAITING_FOR_MESSAGE', 'GETTING_CLOSER', 'FOLLOWING']
    
    # Transition déclenchée par message "Come closer"
    # Condition: distance <= distance_min pour FOLLOWING
```

---

### 🔧 states/drone.py (modifié)

**Changements:**
```python
def __init__(self, ...):
    # ...
    self.state_machine = None  # ← À implémenter dans sous-classes
```

**Nouvelles méthodes:**
- `follow_the_branch()` → Contrôleur PD (inchangé)
- `msg_to_follower()` → Envoyer des messages (amélioré)

---

### 🎯 states/leader.py (modifié)

**Avant:**
```python
def run(self, lidar_data, lidar_ray_angles):
    self.sensorsAnalyzer.analyze(lidar_data, lidar_ray_angles)
    self.move_forward_in_branch()
```

**Après:**
```python
def __init__(self, ...):
    super().__init__(...)
    self.state_machine = LeaderStateMachine(self, initial='TAKEOFF')

def run(self, lidar_data, lidar_ray_angles, sim_steps):
    self.state_machine.update(lidar_data, lidar_ray_angles, sim_steps)
```

---

### 🎯 states/follower.py (modifié)

**Avant:**
```python
def run(self, lidar_data, lidar_ray_angles):
    self.follow_agent_in_front()
```

**Après:**
```python
def __init__(self, ...):
    super().__init__(...)
    self.state_machine = FollowerStateMachine(self, initial='TAKEOFF')

def run(self, lidar_data, lidar_ray_angles, sim_steps):
    self.state_machine.update(sim_steps)
```

---

### 🎮 croix.py (simplifié)

**Avant:**
```python
if takeoff:
    # 50+ lignes de code
else:
    # 50+ lignes de code (avec if/elif imbriqués)
```

**Après:**
```python
for j in range(num_drones):
    # ... générer lidar_data ...
    
    if drones[j].is_leader:
        drones[j].run(lidar_data, ray_angles, sim_steps)
    elif drones[j].is_follower:
        drones[j].run(lidar_data, ray_angles, sim_steps)
    
    action[j, :] = drones[j].action
```

---

## 🧪 Workflow typique de développement

### Étape 1 : Ajouter une feature (ex: Obstacle avoidance)

```python
# 1. Éditer leader_state_machine.py
states = [..., 'OBSTACLE_AVOIDANCE']

transitions = [
    ...,
    {'trigger': 'obstacle_detected',
     'source': 'MOVING_FORWARD',
     'dest': 'OBSTACLE_AVOIDANCE'},
]

def on_enter_obstacle_avoidance(self):
    print("[LEADER] → OBSTACLE_AVOIDANCE")

# 2. Dans update():
if self.state == 'MOVING_FORWARD':
    if min(lidar_data) < OBSTACLE_DISTANCE:
        self.obstacle_detected()
```

### Étape 2 : Tester isolément

```python
# Dans examples_state_machine.py
def test_obstacle_avoidance():
    leader = Leader()
    leader.state_machine.state = 'MOVING_FORWARD'
    
    # Lidar data avec obstacle proche
    lidar_data = [0.2] * 181
    
    leader.state_machine.update(lidar_data, ray_angles, 100)
    
    assert leader.state_machine.state == 'OBSTACLE_AVOIDANCE'
```

### Étape 3 : Tester en simulation

```bash
python croix.py
# Voir le nouveau comportement en action
```

---

## 🐛 Debugging

### Afficher l'état actuel

```python
# Dans croix.py
if sim_steps % 10 == 0:  # Tous les 10 steps
    for j in range(num_drones):
        print(f"Drone {j}: {drones[j].state_machine.state}")
```

**Output:**
```
Drone 0: TAKEOFF
Drone 0: TAKEOFF
...
Drone 0: MOVING_FORWARD
Drone 0: MOVING_FORWARD
Drone 0: WAITING_FOR_FOLLOWER
Drone 0: MOVING_FORWARD
```

### Afficher les transitions

```python
# Ajouter des logs dans les callbacks
def on_enter_moving(self):
    print(f"[{self.__class__.__name__}] → MOVING_FORWARD")

def on_exit_moving(self):
    print(f"[{self.__class__.__name__}] ← MOVING_FORWARD")
```

### Inspecter les conditions

```python
# Dans update()
if self.state == 'MOVING_FORWARD':
    dist = ...
    print(f"Distance follower: {dist:.3f}m > {self.leader.distance_max}m?")
    
    if dist > self.leader.distance_max:
        self.follower_too_far()
        print("  → Transition: follower_too_far()")
```

---

## 🧠 Bonne pratiques à retenir

### ✅ À FAIRE

1. **Changer l'état via triggers**
   ```python
   drone.state_machine.start_mission()  # ✅ BON
   ```

2. **Éviter d'assigner directement**
   ```python
   # ❌ MAUVAIS (les callbacks ne s'exécutent pas)
   drone.state_machine.state = 'MOVING_FORWARD'
   
   # Acceptable seulement pour les tests
   ```

3. **Mettre la logique dans les callbacks**
   ```python
   def on_enter_moving(self):
       # Initialiser les variables
       self.start_time = time.time()
   ```

4. **Utiliser les conditions pour les transitions**
   ```python
   'conditions': 'is_ready_to_land'
   ```

### ❌ À ÉVITER

1. **Ne pas hacker l'état machine**
   ```python
   # ❌ MAUVAIS
   drone.state_machine.state = 'FLYING'
   ```

2. **Ne pas mettre la logique dans croix.py**
   ```python
   # ❌ MAUVAIS
   if drones[j].state_machine.state == 'MOVING':
       # Logique ici
   
   # ✅ BON: La logique dans la state machine
   ```

3. **Ne pas créer trop d'états**
   ```python
   # ❌ MAUVAIS (> 10 états)
   states = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
   
   # ✅ BON: Garder < 10 états
   ```

---

## 📊 Résumé rapide

| Fichier | Rôle | Modifiez si... |
|---------|------|---|
| `STATE_MACHINE_DOCUMENTATION.md` | 📖 Conceptes | Besoin d'apprendre |
| `TRANSITIONS_QUICK_GUIDE.py` | 🧪 Exemples | Avez des doutes |
| `BEFORE_AFTER_COMPARISON.md` | 📊 Justification | Convainciez quelqu'un |
| `leader_state_machine.py` | ⚙️ Leader logic | Besoin de changer le leader |
| `follower_state_machine.py` | ⚙️ Follower logic | Besoin de changer le follower |
| `states/leader.py` | 🎯 Interface Leader | Jamais (use state machine) |
| `states/follower.py` | 🎯 Interface Follower | Jamais (use state machine) |
| `croix.py` | 🎮 Main loop | Besoin de changer les params |

---

## 🎓 Prochaines étapes

### Court terme (1-2 semaines)
- [ ] Lire `STATE_MACHINE_DOCUMENTATION.md`
- [ ] Exécuter `examples_state_machine.py`
- [ ] Comprendre les diagrammes d'états

### Moyen terme (1 mois)
- [ ] Ajouter un nouvel état (ex: LANDING)
- [ ] Implémenter les tests correspondants
- [ ] Faire tourner la simulation avec la nouvelle feature

### Long terme (3+ mois)
- [ ] Ajouter 3ème drone (ou plus)
- [ ] Ajouter des états de reconfiguration
- [ ] Implémenter la détection d'obstacles
- [ ] Optimiser la communication entre drones

---

## 🆘 FAQ

**Q: Est-ce que ça va plus lent ?**
A: Non, performance identique. Les callbacks sont juste des fonctions.

**Q: Puis-je mixer ancien code et state machine ?**
A: Non, c'est tout ou rien (mais vous n'en avez pas besoin).

**Q: Comment tester les transitions sans simuler 100 steps ?**
A: Regardez `examples_state_machine.py`, section "Test isolé".

**Q: Puis-je avoir plusieurs state machines par drone ?**
A: Oui, créez un autre atribute `self.state_machine_2 = ...`.

**Q: Ça complique le code ?**
A: Non, ça le simplifie. Vous avez juste plus de fichiers.

---

Bon coding! 🚀
