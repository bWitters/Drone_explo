"""
Exemples d'utilisation et de debug des State Machines.

Ce fichier montre comment:
1. Inspecter l'état actuel
2. Déclencher des transitions manuellement
3. Tester les conditions de transition
4. Ajouter du logging personnalisé
"""

from states.leader import Leader
from states.follower import Follower
import numpy as np


# ============================================================================
# 1. INSPECTER L'ÉTAT ACTUEL
# ============================================================================

def inspect_drone_state(drone, name="Drone"):
    """Afficher l'état actuel d'un drone et ses infos."""
    print(f"\n{'='*60}")
    print(f"{name} Status")
    print(f"{'='*60}")
    print(f"Current State: {drone.state_machine.state}")
    print(f"Position: {drone.position}")
    print(f"Action: {drone.action}")
    print(f"Messages received: {drone.message_received}")
    
    if drone.follower:
        print(f"Distance to follower: {np.linalg.norm(np.array(drone.position) - np.array(drone.follower.position)):.3f}m")
    if drone.preceding:
        print(f"Distance to preceding: {np.linalg.norm(np.array(drone.position) - np.array(drone.preceding.position)):.3f}m")


# ============================================================================
# 2. TESTER LES TRANSITIONS MANUELLEMENT
# ============================================================================

def test_transitions_manually():
    """Tester les transitions d'une state machine."""
    print("\n\n" + "="*60)
    print("TEST: Transitions manuelles")
    print("="*60)
    
    # Créer un leader
    leader = Leader()
    print(f"✓ Leader créé. État initial: {leader.state_machine.state}")
    
    # Tester transition TAKEOFF → MOVING_FORWARD
    print("\n→ Tentative: start_mission()")
    try:
        leader.state_machine.start_mission()
        print(f"✓ Transition réussie. Nouvel état: {leader.state_machine.state}")
    except Exception as e:
        print(f"✗ Transition échouée: {e}")
    
    # Tester transition follower_too_far
    print("\n→ Tentative: follower_too_far()")
    try:
        leader.state_machine.follower_too_far()
        print(f"✓ Transition réussie. Nouvel état: {leader.state_machine.state}")
    except Exception as e:
        print(f"✗ Transition échouée (c'est normal en dehors de MOVING_FORWARD): {e}")


# ============================================================================
# 3. TESTER LES CONDITIONS DE TRANSITION
# ============================================================================

def test_distance_conditions():
    """Tester les conditions de distance."""
    print("\n\n" + "="*60)
    print("TEST: Conditions de distance")
    print("="*60)
    
    # Créer un leader et un follower
    leader = Leader()
    follower = Follower(preceding=leader)
    leader.follower = follower
    
    # Mettre le leader en MOVING_FORWARD
    leader.state_machine.state = 'MOVING_FORWARD'
    print(f"✓ Leader état: {leader.state_machine.state}")
    
    # Tester avec follower proche
    leader.position = [0, 0, 1]
    follower.position = [0, 0.1, 1]  # 0.1m de distance
    
    distance = np.linalg.norm(
        np.array(leader.position) - np.array(follower.position)
    )
    print(f"\n→ Follower très proche (distance={distance:.3f}m)")
    print(f"  État leader: {leader.state_machine.state}")
    print(f"  Expected: MOVING_FORWARD (distance < max)")
    
    # Tester avec follower loin
    follower.position = [0, 1.0, 1]  # 1.0m de distance
    
    distance = np.linalg.norm(
        np.array(leader.position) - np.array(follower.position)
    )
    print(f"\n→ Follower loin (distance={distance:.3f}m)")
    print(f"  État leader avant update: {leader.state_machine.state}")
    print(f"  Expected: transition vers WAITING_FOR_FOLLOWER")
    
    # Appeler update pour déclencher la transition
    # (note: il faudrait des données lidar réelles)


# ============================================================================
# 4. ÉCOUTER LES CHANGEMENTS D'ÉTAT
# ============================================================================

def add_state_change_listener(drone, name="Drone"):
    """Ajouter un listener personnalisé pour écouter les changements d'état."""
    original_state = drone.state_machine.state
    
    # Redéfinir les transitions pour ajouter du logging
    for transition_dict in drone.state_machine.transitions:
        if 'dest' in transition_dict and 'source' in transition_dict:
            source = transition_dict['source']
            dest = transition_dict['dest']
            trigger = transition_dict.get('trigger', '?')
            
            # Ajouter un callback personnalisé
            old_callback = transition_dict.get('after')
            
            def custom_callback(src=source, dst=dest, trg=trigger, n=name):
                print(f"[{n}] {src} --({trg})--> {dst}")
            
            # Ici, on pourrait ajouter du logging
            print(f"[{name}] Transition disponible: {source} --({trigger})--> {dest}")


# ============================================================================
# 5. TESTER LE COMPORTEMENT DU FOLLOWER
# ============================================================================

def test_follower_behavior():
    """Tester le comportement du follower avec les messages."""
    print("\n\n" + "="*60)
    print("TEST: Comportement du Follower")
    print("="*60)
    
    # Créer un leader et un follower
    leader = Leader()
    follower = Follower(preceding=leader)
    leader.follower = follower
    
    # Étape 1: État initial
    print(f"\n1️⃣ État initial")
    print(f"   Follower état: {follower.state_machine.state}")
    print(f"   Messages reçus: {follower.message_received}")
    
    # Étape 2: Simuler le décollage (100 steps)
    print(f"\n2️⃣ Après décollage (sim_steps >= 100)")
    follower.state_machine.state = 'WAITING_FOR_MESSAGE'
    print(f"   Follower état: {follower.state_machine.state}")
    
    # Étape 3: Leader envoie "Come closer"
    print(f"\n3️⃣ Leader envoie 'Come closer'")
    leader.msg_to_follower("Come closer")
    print(f"   Messages reçus: {follower.message_received}")
    
    # Étape 4: Follower reçoit le message et transition
    print(f"\n4️⃣ Follower réagit au message")
    if follower.message_received and follower.message_received[-1] == "Come closer":
        if follower.state_machine.state == 'WAITING_FOR_MESSAGE':
            follower.state_machine.received_come_closer()
    print(f"   Follower état: {follower.state_machine.state}")
    
    # Étape 5: Follower se rapproche
    print(f"\n5️⃣ Follower se rapproche (distance diminue)")
    leader.position = [0, 0, 1]
    follower.position = [0, 0.45, 1]  # Suffisamment proche
    distance = np.linalg.norm(np.array(leader.position) - np.array(follower.position))
    print(f"   Distance: {distance:.3f}m (min={follower.distance_min:.3f}m)")
    
    # Simuler la transition
    if distance <= follower.distance_min:
        follower.state_machine.distance_ok()
    
    print(f"   Follower état: {follower.state_machine.state}")


# ============================================================================
# 6. EXEMPLE DE BOUCLE DE SIMULATION SIMPLIFIÉ
# ============================================================================

def simulate_with_state_machines(num_steps=10):
    """Simulation simplifiée montrant comment utiliser les state machines."""
    print("\n\n" + "="*60)
    print("SIMULATION SIMPLIFIÉE avec State Machines")
    print("="*60)
    
    # Créer les drones
    leader = Leader()
    follower = Follower(preceding=leader)
    leader.follower = follower
    
    # Positions initiales
    leader.position = np.array([0.0, 0.0, 1.0])
    follower.position = np.array([0.0, -0.5, 1.0])
    
    # Boucle de simulation
    for step in range(num_steps):
        print(f"\n{'─'*60}")
        print(f"Step {step}")
        print(f"{'─'*60}")
        
        # Afficher les états
        print(f"Leader:   {leader.state_machine.state:20} | Pos: {leader.position}")
        print(f"Follower: {follower.state_machine.state:20} | Pos: {follower.position}")
        
        # Créer des données lidar fictives
        lidar_data = [1.5] * 181  # Pas d'obstacle
        ray_angles = np.linspace(-np.pi, np.pi, 181)
        
        # Mettre à jour les state machines
        try:
            leader.state_machine.update(lidar_data, ray_angles, step)
            follower.state_machine.update(step)
            
            # Afficher les actions
            print(f"Leader action:   {leader.action}")
            print(f"Follower action: {follower.action}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Simuler le mouvement (pseudo)
        if step >= 100:  # Après décollage
            leader.position = leader.position + np.array(leader.action[:3]) * 0.1
            follower.position = follower.position + np.array(follower.action[:3]) * 0.1


# ============================================================================
# MAIN: Exécuter les tests
# ============================================================================

if __name__ == "__main__":
    # Test 1: Inspección
    leader = Leader()
    inspect_drone_state(leader, "Test Leader")
    
    # Test 2: Transitions
    test_transitions_manually()
    
    # Test 3: Distance conditions
    test_distance_conditions()
    
    # Test 4: Follower behavior
    test_follower_behavior()
    
    # Test 5: Simulation simplifiée
    simulate_with_state_machines(num_steps=5)
    
    print("\n\n" + "="*60)
    print("✅ Tous les tests sont terminés !")
    print("="*60)
