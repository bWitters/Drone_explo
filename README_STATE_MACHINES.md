# 🤖 Refactorisation State Machine - Guide Rapide

## ⚡ TL;DR (Trop Long; Pas lu)

Votre code a été **refactorisé** pour utiliser la librairie **`transitions`** Python.

**Ce que ça change:**
- ✅ Moins de spaghetti code (if/else imbriqués)
- ✅ États explicites et transitions claires
- ✅ Facile d'ajouter de nouveaux états
- ✅ Facile à déboguer et tester
- ❌ Performance: identique (aucun overhead)

**Comment utiliser:**
1. Lire `STATE_MACHINE_DOCUMENTATION.md` (30 min)
2. Exécuter `python TRANSITIONS_QUICK_GUIDE.py` (10 min)
3. Exécuter `python examples_state_machine.py` (10 min)
4. Lancer `python croix.py` (normalement) (variable)

**Fichiers importants:**
```
states/leader_state_machine.py    ← Logique du leader
states/follower_state_machine.py  ← Logique du follower
croix.py                          ← Boucle principale (simplifiée)
```

---

## 📚 Documentation complète

Ouvrez ces fichiers **dans cet ordre** :

### 1️⃣ [STATE_MACHINE_DOCUMENTATION.md](STATE_MACHINE_DOCUMENTATION.md) (30 min) 📖
**Concepts de base de la librairie `transitions`**
- Qu'est-ce qu'une state machine ?
- Concepts clés: États, Transitions, Callbacks
- Architecture de LeaderStateMachine et FollowerStateMachine
- Diagrammes d'états
- Comment déboguer

### 2️⃣ [TRANSITIONS_QUICK_GUIDE.py](TRANSITIONS_QUICK_GUIDE.py) (Exécutable)
**Exemples pratiques avec code exécutable**
```bash
python TRANSITIONS_QUICK_GUIDE.py
```
Montre:
- Exemple minimal
- Callbacks avant/après
- Conditions (conditional transitions)
- Communication entre états

### 3️⃣ [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) (15 min) 📊
**Pourquoi c'est mieux**
- Ancien code vs Nouveau code (visuellement)
- Comparaison de complexité
- Exemple: Ajouter une feature
- Scénario: Debugger un bug

### 4️⃣ [examples_state_machine.py](examples_state_machine.py) (Exécutable) 🧪
**Tester et déboguer**
```bash
python examples_state_machine.py
```
Montre:
- Inspecter l'état actuel
- Tester les transitions manuellement
- Tester les conditions
- Simulation simplifiée

### 5️⃣ [HOW_TO_USE_STATE_MACHINES.md](HOW_TO_USE_STATE_MACHINES.md) (20 min) 📋
**Guide pratique d'utilisation**
- Description de chaque fichier
- Workflow de développement
- Debugging en pratique
- Bonnes pratiques

---

## 🎯 Architecture

### State Machine du Leader
```
TAKEOFF (100 steps)
   ↓
MOVING_FORWARD ←→ WAITING_FOR_FOLLOWER (basé sur distance)
   ↑    ↓
   └─ ALIGNMENT (basé sur angle au gap)
```

### State Machine du Follower
```
TAKEOFF (100 steps)
   ↓
WAITING_FOR_MESSAGE
   ↓ (reçoit "Come closer")
GETTING_CLOSER (distance diminue)
   ↓ (distance ≤ min)
FOLLOWING ← → GETTING_CLOSER (distance > max)
```

---

## 🚀 Démarrer la simulation

```bash
# Normalement (rien ne change pour l'utilisateur)
python croix.py
```

**Ce qui se passe en coulisse:**
```python
# Boucle principale (dans croix.py)
for step in range(2500):
    obs, reward, terminated, truncated, info = env.step(action)
    
    for j in range(num_drones):
        # Générer les données lidar
        lidar_data = [...]
        
        # Appeler la state machine (tout la logique est là)
        drones[j].run(lidar_data, ray_angles, sim_steps)
        
        # Récupérer l'action
        action[j, :] = drones[j].action
```

---

## 🔧 Ajouter un nouvel état (Exemple)

Supposons qu'on veut ajouter un état **OBSTACLE_AVOIDANCE** au leader.

### Étape 1: Éditer `states/leader_state_machine.py`

```python
# Ajouter l'état
states = [
    'TAKEOFF',
    'MOVING_FORWARD',
    'WAITING_FOR_FOLLOWER',
    'ALIGNMENT',
    'OBSTACLE_AVOIDANCE',  # ← NOUVEAU
]

# Ajouter les transitions
transitions = [
    # ... transitions existantes ...
    
    # MOVING_FORWARD → OBSTACLE_AVOIDANCE si obstacle
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

# Ajouter le callback
def on_enter_obstacle_avoidance(self):
    print("[LEADER] → OBSTACLE_AVOIDANCE")
    # Activer la logique d'évitement

# Ajouter la condition dans update()
if self.state == 'MOVING_FORWARD':
    if min(lidar_data) < 0.3:  # Obstacle à 30cm
        self.obstacle_detected()
        return
```

### Étape 2: Tester isolément

```python
# Dans examples_state_machine.py
def test_obstacle_avoidance():
    leader = Leader()
    leader.state_machine.state = 'MOVING_FORWARD'
    
    # Créer des données lidar avec obstacle
    lidar_data = [0.2] * 181  # Tout proche
    ray_angles = np.linspace(-np.pi, np.pi, 181)
    
    # Simuler l'update
    leader.state_machine.update(lidar_data, ray_angles, 100)
    
    # Vérifier la transition
    assert leader.state_machine.state == 'OBSTACLE_AVOIDANCE'
    print("✅ Test réussi!")
```

### Étape 3: Tester en simulation

```bash
python croix.py
# Le nouveau comportement devrait fonctionner
```

**C'est tout!** ✨

---

## 🐛 Déboguer

### Afficher l'état des drones

```python
# Dans croix.py, dans la boucle principale
if sim_steps % 50 == 0:  # Tous les 50 steps
    for j, drone in enumerate(drones):
        print(f"Drone {j}: {drone.state_machine.state}")
```

**Output:**
```
Drone 0: TAKEOFF
Drone 0: TAKEOFF
...
Drone 0: MOVING_FORWARD
Drone 0: MOVING_FORWARD
Drone 0: WAITING_FOR_FOLLOWER
```

### Voir les transitions

Les callbacks `on_enter_XXX` et `on_exit_XXX` affichent automatiquement:
```
[LEADER] → MOVING_FORWARD
[FOLLOWER] → WAITING_FOR_MESSAGE
[FOLLOWER] ← WAITING_FOR_MESSAGE
[FOLLOWER] → GETTING_CLOSER
```

### Tester isolément

```python
# exemple_test.py
from states.leader import Leader
from states.follower import Follower
import numpy as np

leader = Leader()
follower = Follower(preceding=leader)
leader.follower = follower

# Forcer un état pour tester
leader.state_machine.state = 'MOVING_FORWARD'
print(f"État: {leader.state_machine.state}")

# Tester une transition
leader.state_machine.follower_too_far()
print(f"Après transition: {leader.state_machine.state}")
# Output:
# État: MOVING_FORWARD
# [LEADER] ← MOVING_FORWARD (follower trop loin)
# [LEADER] → WAITING_FOR_FOLLOWER
# Après transition: WAITING_FOR_FOLLOWER
```

---

## 📊 Fichiers modifiés

| Fichier | Changement |
|---------|-----------|
| `states/drone.py` | + `self.state_machine = None` |
| `states/leader.py` | Crée LeaderStateMachine; Logique dans `run()` |
| `states/follower.py` | Crée FollowerStateMachine; Logique dans `run()` |
| `croix.py` | Boucle simplifiée (pas de if/takeoff) |
| `states/leader_state_machine.py` | **NOUVEAU** (180 lignes) |
| `states/follower_state_machine.py` | **NOUVEAU** (170 lignes) |

---

## ⚠️ Points importants

### ✅ À FAIRE
```python
# Utiliser les triggers (transitions)
drone.state_machine.start_mission()
drone.state_machine.follower_too_far()

# Les callbacks s'exécutent automatiquement
# Les actions se mettent à jour automatiquement
```

### ❌ À ÉVITER
```python
# Ne pas assigner directement l'état
drone.state_machine.state = 'MOVING_FORWARD'  # ❌ Les callbacks ne s'exécutent pas

# Ne pas mettre la logique métier dans croix.py
# Elle doit être dans la state machine
```

---

## 🎓 Ressources

### Librairie `transitions`
- **GitHub:** https://github.com/tyarkoni/transitions
- **Documentation:** https://transitions.readthedocs.io/

### Pattern State Machine
- **Refactoring Guru:** https://refactoring.guru/design-patterns/state

### Livres
- "Design Patterns" (Gang of Four)
- "Microservices Patterns" (Chapitre State Machine)

---

## 🤔 FAQ

**Q: Ça complique le code ?**
A: Non, c'est plus clair. Vous avez des fichiers séparés mais la logique est plus lisible.

**Q: Performance ?**
A: Aucune perte. Les callbacks sont juste des fonction Python normales.

**Q: Je peux toujours utiliser `croix.py` normalement ?**
A: Oui, rien ne change côté utilisateur. Juste lancez `python croix.py`.

**Q: Comment tester sans lancer la simulation entière ?**
A: Exécutez `python examples_state_machine.py` pour des tests isolés.

**Q: Et si j'ajoute plus de drones ?**
A: Chacun aura sa propre state machine. Zéro problème.

**Q: Je peux mixer des drones avec et sans state machine ?**
A: Techniquement oui, mais pas recommandé. Gardez une architecture cohérente.

---

## ✅ Checklist pour bien démarrer

- [ ] Lire `STATE_MACHINE_DOCUMENTATION.md` (30 min)
- [ ] Exécuter `python TRANSITIONS_QUICK_GUIDE.py` (10 min)
- [ ] Exécuter `python examples_state_machine.py` (10 min)
- [ ] Lire `BEFORE_AFTER_COMPARISON.md` (15 min)
- [ ] Lire `HOW_TO_USE_STATE_MACHINES.md` (20 min)
- [ ] Lancer `python croix.py` et vérifier que c'est OK (10 min)
- [ ] Essayer d'ajouter un nouvel état (30 min)

**Total: ~125 minutes (~2 heures) pour être à l'aise**

---

## 🎉 Conclusion

Vous avez maintenant un code:
- ✅ Plus lisible
- ✅ Plus maintenable
- ✅ Plus facile à étendre
- ✅ Plus facile à déboguer
- ✅ Identique en performance

**Bon coding!** 🚀

Pour toute question, relire la documentation correspondante ou lancer les exemples.
