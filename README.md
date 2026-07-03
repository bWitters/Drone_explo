# Synchronization of simulation and CrazyFlie drones for tunnels exploration
Simulation of drone exploration based on a Mathis Fleuriel State Machine in [Exploring Underground Environments by Deploying and Reconfiguring a Chain of Visually Connected UAVs](https://ieeexplore.ieee.org/document/11162959)

## Simulator used
For the simulation we are using [gym-pybullet-drones](https://github.com/learnsyslab/gym-pybullet-drones)

![Illustration](https://github.com/learnsyslab/gym-pybullet-drones/blob/main/gym_pybullet_drones/assets/helix.gif?raw=true)

## Controller
We are using [CFlib2](https://github.com/bitcraze/crazyflie-lib-python-v2/tree/main) to control CrazyFlie drones

# Installation

```git clone https://gitlab.inria.fr/bwitters/Drone_explo.git
cd 
pip install -r requirements.txt
```

# Run

## Run the simulator alone

`python Sim/app.py`

## Run with CrazyFlie connection

`python Sim/orchestrateur.py`
