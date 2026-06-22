import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.animation as animation

def go(queue_commande):
    # Configuration de la figure
    fig, axs = plt.subplots(4, 1, figsize=(10, 12))
    vx_data, vy_data, vz_data, v_yaw_data, sim_step_data = [], [], [], [], []
    lines = []
    for ax in axs:
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)
        line, = ax.plot([], [], 'b-')
        lines.append(line)

    # Fonction de mise à jour pour FuncAnimation
    def update(frame):
        # Récupérer toutes les commandes disponibles dans la queue
        while not queue_commande.empty():
            vx,vy,vz,v_yaw,_,sim_step = queue_commande.get()
            vx_data.append(vx)
            vy_data.append(vy)
            vz_data.append(vz)
            v_yaw_data.append(v_yaw)
            sim_step_data.append(sim_step)
        # Mettre à jour la courbe
        lines[0].set_data(sim_step_data, vx_data)
        lines[1].set_data(sim_step_data, vy_data)
        lines[2].set_data(sim_step_data, vz_data)
        lines[3].set_data(sim_step_data, v_yaw_data)
        # Ajuster les axes si nécessaire
        if vx_data:
            axs[0].set_xlim(min(sim_step_data), max(sim_step_data) + 1)
            axs[0].set_ylim(min(vx_data) - 0.1, max(vx_data) + 0.1)
        if vy_data:
            axs[1].set_xlim(min(sim_step_data), max(sim_step_data) + 1)
            axs[1].set_ylim(min(vy_data) - 0.1, max(vy_data) + 0.1)
        if vz_data:
            axs[2].set_xlim(min(sim_step_data), max(sim_step_data) + 1)
            axs[2].set_ylim(min(vz_data) - 0.1, max(vz_data) + 0.1)
        if v_yaw_data:
            axs[3].set_xlim(min(sim_step_data), max(sim_step_data) + 1)
            axs[3].set_ylim(min(v_yaw_data) - 0.1, max(v_yaw_data) + 0.1)
        return lines[0],lines[1],lines[2],lines[3]
    
    # Lancer l'animation
    ani = animation.FuncAnimation(
        fig,
        update,
        interval=50,  # Mise à jour toutes les 50 ms
        blit=True,
        cache_frame_data=False  # Désactive la mise en cache pour éviter les problèmes
    )

    plt.show()

if __name__ == "__main__":
    go([11,2,3,4])