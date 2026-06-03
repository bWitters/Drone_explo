import csv
import matplotlib.pyplot as plt

def read_csv_data(csv_file_path):
    """Lit un fichier CSV et retourne un dictionnaire avec les données."""
    data = {'vx': [], 'vy': [], 'vz': [], 'v_yaw': []}
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        required_columns = ['vx', 'vy', 'vz', 'v_yaw']
        for col in required_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"Colonne '{col}' manquante dans {csv_file_path}.")
        for row in reader:
            data['vx'].append(float(row['vx']))
            data['vy'].append(float(row['vy']))
            data['vz'].append(float(row['vz']))
            data['v_yaw'].append(float(row['v_yaw']) if row['v_yaw'] is not None else 0)
    return data

def plot_drones_comparison(drones, real_alpha=0.7):
    """
    Affiche une fenêtre séparée pour chaque drone, avec 4 sous-graphiques (vx, vy, vz, v_yaw)
    superposant commande (opaque) et réel (transparent).

    Args:
        drones: Liste de tuples (cmd_path, real_path, drone_label)
        real_alpha: Transparence des tracés réels (0.0 à 1.0, défaut: 0.7)
    """
    cmd_color, real_color = '#1f77b4', '#ff7f0e'
    cmd_linestyle, real_linestyle = '-', '--'

    def set_ylim(ax, data1, data2):
        all_values = data1 + data2
        max_abs = max(abs(min(all_values)), abs(max(all_values))) if all_values else 0
        ax.set_ylim(-max_abs * 1.1, max_abs * 1.1)

    for cmd_path, real_path, drone_label in drones:
        cmd_data = read_csv_data(cmd_path)
        real_data = read_csv_data(real_path)

        fig, axs = plt.subplots(4, 1, figsize=(10, 12))
        fig.suptitle(f"Comparaison Commande vs Réel - {drone_label}")

        # Tracer vx
        axs[0].plot(cmd_data['vx'], label='Commande', color=cmd_color, linestyle=cmd_linestyle, linewidth=1.5)
        axs[0].plot(real_data['vx'], label='Réel', color=real_color, linestyle=real_linestyle, linewidth=1.5, alpha=real_alpha)
        axs[0].set_ylabel('Vitesse (vx)')
        axs[0].grid(True, alpha=0.3)
        axs[0].legend()
        set_ylim(axs[0], cmd_data['vx'], real_data['vx'])

        # Tracer vy
        axs[1].plot(cmd_data['vy'], label='Commande', color=cmd_color, linestyle=cmd_linestyle, linewidth=1.5)
        axs[1].plot(real_data['vy'], label='Réel', color=real_color, linestyle=real_linestyle, linewidth=1.5, alpha=real_alpha)
        axs[1].set_ylabel('Vitesse (vy)')
        axs[1].grid(True, alpha=0.3)
        axs[1].legend()
        set_ylim(axs[1], cmd_data['vy'], real_data['vy'])

        # Tracer vz
        axs[2].plot(cmd_data['vz'], label='Commande', color=cmd_color, linestyle=cmd_linestyle, linewidth=1.5)
        axs[2].plot(real_data['vz'], label='Réel', color=real_color, linestyle=real_linestyle, linewidth=1.5, alpha=real_alpha)
        axs[2].set_ylabel('Vitesse (vz)')
        axs[2].grid(True, alpha=0.3)
        axs[2].legend()
        set_ylim(axs[2], cmd_data['vz'], real_data['vz'])

        # Tracer v_yaw
        axs[3].plot(cmd_data['v_yaw'], label='Commande', color=cmd_color, linestyle=cmd_linestyle, linewidth=1.5)
        axs[3].plot(real_data['v_yaw'], label='Réel', color=real_color, linestyle=real_linestyle, linewidth=1.5, alpha=real_alpha)
        axs[3].set_ylabel('Vitesse de rotation (v_yaw)')
        axs[3].set_xlabel('Échantillons')
        axs[3].grid(True, alpha=0.3)
        axs[3].legend()
        set_ylim(axs[3], cmd_data['v_yaw'], real_data['v_yaw'])

        plt.tight_layout()

    plt.show()

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    drones = [
        (
            "Sim/logs/drone_1_2026-06-03-11-48-16.csv",
            "Sim/logs/drone_velocity_1_2026-06-03-11-48-16.csv",
            "Drone 1"
        ),
        (
            "Sim/logs/drone_2_2026-06-03-11-48-16.csv",
            "Sim/logs/drone_velocity_2_2026-06-03-11-48-16.csv",
            "Drone 2"
        ),
        (
            "Sim/logs/drone_3_2026-06-03-11-48-16.csv",
            "Sim/logs/drone_velocity_3_2026-06-03-11-48-16.csv",
            "Drone 3"
        ),(
            "Sim/logs/drone_4_2026-06-03-11-48-16.csv",
            "Sim/logs/drone_velocity_4_2026-06-03-11-48-16.csv",
            "Drone 4"
        ),
        (
            "Sim/logs/drone_5_2026-06-03-11-48-16.csv",
            "Sim/logs/drone_velocity_5_2026-06-03-11-48-16.csv",
            "Drone 5"
        )
    ]
    plot_drones_comparison(drones, real_alpha=0.7)  # Ajuste real_alpha entre 0.0 et 1.0