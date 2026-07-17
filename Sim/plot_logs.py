import csv
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from datetime import datetime

def read_csv_data(csv_file_path):
    """Lit un fichier CSV et retourne un dictionnaire avec les données."""
    data = {'vx': [], 'vy': [], 'vz': [], 'v_yaw': []}
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        required_columns = ['vx', 'vy', 'vz', 'v_yaw']
        for col in required_columns:
            if reader.fieldnames != None:
                if col not in reader.fieldnames:
                    raise ValueError(f"Colonne '{col}' manquante dans {csv_file_path}.")
        for row in reader:
            data['vx'].append(float(row['vx']))
            data['vy'].append(float(row['vy']))
            data['vz'].append(float(row['vz']))
            data['v_yaw'].append(float(row['v_yaw']) if row['v_yaw'] is not None else 0)
    return data

def read_lidar_data(csv_file_path):
    """Lit un fichier CSV de données lidar et retourne un dictionnaire avec les distances."""
    data = {'lidar_front': [], 'lidar_right': [], 'lidar_back': [], 'lidar_left': []}
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        required_columns = ['lidar_front', 'lidar_right', 'lidar_back', 'lidar_left']
        if reader.fieldnames is not None:
            for col in required_columns:
                if col not in reader.fieldnames:
                    raise ValueError(f"Colonne '{col}' manquante dans {csv_file_path}.")
        for row in reader:
            for col in required_columns:
                data[col].append(float(row[col]))
    return data

def read_behaviors(behavior_file_path):
    """Lit un fichier CSV avec une colonne 'Behavior' et retourne une liste de tuples (start, end, behavior)."""
    behaviors = []
    with open(behavior_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != None:
            if 'Behavior' not in reader.fieldnames:
                raise ValueError(f"Colonne 'Behavior' manquante dans {behavior_file_path}.")
        lines = [row['Behavior'] for row in reader]

    if not lines:
        return behaviors

    current_behavior = lines[0]
    start = 0
    for i, behavior in enumerate(lines[1:], start=1):
        if behavior != current_behavior:
            behaviors.append((start, i, current_behavior))
            start = i
            current_behavior = behavior
    behaviors.append((start, len(lines), current_behavior))
    return behaviors

def get_drone_files(folder_path):
    """Retourne une liste de tuples (cmd_path, real_path, behavior_path, lidar_path, drone_label) pour chaque drone."""
    drone_files = []
    files = os.listdir(folder_path)

    # Filtrer les fichiers pertinents
    drone_csvs = [f for f in files if f.startswith('drone_') and f.endswith('.csv') and 'position' not in f]
    drone_ids = set()

    for f in drone_csvs:
        parts = f.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            drone_id = parts[1]
            drone_ids.add(drone_id)

    # Construire les chemins pour chaque drone
    for drone_id in sorted(drone_ids):
        cmd_pattern = f"drone_{drone_id}_*.csv"
        real_pattern = f"drone_velocity_{drone_id}_*.csv"
        behavior_pattern = f"drone_behavior_{drone_id}_*.csv"
        lidar_pattern = f"drone_lidar_{drone_id}_*.csv"

        cmd_files = [f for f in files if f.startswith(f"drone_{drone_id}_") and 'velocity' not in f and 'behavior' not in f and 'lidar' not in f]
        real_files = [f for f in files if f.startswith(f"drone_velocity_{drone_id}_")]
        behavior_files = [f for f in files if f.startswith(f"drone_behavior_{drone_id}_")]
        lidar_files = [f for f in files if f.startswith(f"drone_lidar_{drone_id}_")]

        if cmd_files and real_files and behavior_files and lidar_files:
            cmd_path = os.path.join(folder_path, cmd_files[0])
            real_path = os.path.join(folder_path, real_files[0])
            behavior_path = os.path.join(folder_path, behavior_files[0])
            lidar_path = os.path.join(folder_path, lidar_files[0])
            drone_label = f"Drone {drone_id}"
            drone_files.append((cmd_path, real_path, behavior_path, lidar_path, drone_label))

    return drone_files

def plot_drones_comparison(drones, real_alpha=0.7):
    """Affiche les graphiques pour chaque drone avec les behaviors en fond coloré."""
    cmd_color, real_color = '#1f77b4', '#ff7f0e'
    cmd_linestyle, real_linestyle = '-', '--'

    behavior_colors = {
        'Stock': '#e6f7ff',
        'Takeoff': '#90ee90',
        'TakeOff': '#90ee90',
        'LeaderCorridor': '#ff00f7',
        'LeaderCurve': '#ffb347',
        'LeaderIntersection': "#ff6e54",
        'FollowerCorridor': '#b6ade6',
        'FollowerCurve': '#90e0ef',
        'FollowerIntersection': '#dda0dd',
        'LeaderDeadEnd': '#f08080',
        'ReconfigFollower': "#ff0000",
    }

    def set_ylim(ax, data1, data2):
        all_values = data1 + data2
        max_abs = max(abs(min(all_values)), abs(max(all_values))) if all_values else 0
        ax.set_ylim(-max_abs * 1.1, max_abs * 1.1)

    for cmd_path, real_path, behavior_path, _, drone_label in drones:
        cmd_data = read_csv_data(cmd_path)
        real_data = read_csv_data(real_path)
        behaviors = read_behaviors(behavior_path)

        fig, axs = plt.subplots(4, 1, figsize=(10, 12))
        fig.suptitle(f"Comparaison Commande vs Réel - {drone_label}")

        # Légende pour les behaviors
        legend_elements = [
            Patch(facecolor=behavior_colors[behavior], label=behavior)
            for behavior in behavior_colors
            if any(behavior == bh[2] for bh in behaviors)
        ]
        if legend_elements:
            fig.legend(handles=legend_elements, loc='upper right', title='Behaviors')

        for ax in axs:
            for start, end, behavior in behaviors:
                if behavior in behavior_colors:
                    ax.axvspan(start, end, facecolor=behavior_colors[behavior], alpha=0.3)

        # Tracer vx, vy, vz, v_yaw
        for i, (var, label) in enumerate(zip(['vx', 'vy', 'vz', 'v_yaw'], ['vx', 'vy', 'vz', 'v_yaw'])):
            axs[i].plot(cmd_data[var], label='Commande', color=cmd_color, linestyle=cmd_linestyle, linewidth=1.5)
            axs[i].plot(real_data[var], label='Réel', color=real_color, linestyle=real_linestyle, linewidth=1.5, alpha=real_alpha)
            axs[i].set_ylabel(f'Vitesse ({label})')
            axs[i].grid(True, alpha=0.3)
            axs[i].legend()
            set_ylim(axs[i], cmd_data[var], real_data[var])

        axs[3].set_xlabel('Échantillons')
        plt.tight_layout()

    plt.show()

def plot_lidar_comparison(drones, real_alpha=0.7):
    """Affiche les graphiques des données lidar pour chaque drone avec les behaviors en fond coloré."""
    behavior_colors = {
        'Stock': '#e6f7ff',
        'Takeoff': '#90ee90',
        'TakeOff': '#90ee90',
        'LeaderCorridor': '#ff00f7',
        'LeaderCurve': '#ffb347',
        'LeaderIntersection': "#ff6e54",
        'FollowerCorridor': '#b6ade6',
        'FollowerCurve': '#90e0ef',
        'FollowerIntersection': '#dda0dd',
        'LeaderDeadEnd': '#f08080',
        'ReconfigFollower': "#ff0000",
    }

    lidar_colors = {
        'lidar_front': '#1f77b4',
        'lidar_right': '#ff7f0e',
        'lidar_back': '#2ca02c',
        'lidar_left': '#d62728'
    }

    lidar_labels = {
        'lidar_front': 'Front',
        'lidar_right': 'Droit',
        'lidar_back': 'Arrière',
        'lidar_left': 'Gauche'
    }

    for _, _, behavior_path, lidar_path, drone_label in drones:
        lidar_data = read_lidar_data(lidar_path)
        behaviors = read_behaviors(behavior_path)

        fig, axs = plt.subplots(4, 1, figsize=(10, 12))
        fig.suptitle(f"Données Lidar - {drone_label}")

        # Légende pour les behaviors
        legend_elements = [
            Patch(facecolor=behavior_colors[behavior], label=behavior)
            for behavior in behavior_colors
            if any(behavior == bh[2] for bh in behaviors)
        ]
        if legend_elements:
            fig.legend(handles=legend_elements, loc='upper right', title='Behaviors')

        # Fond coloré pour les behaviors
        for ax in axs:
            for start, end, behavior in behaviors:
                if behavior in behavior_colors:
                    ax.axvspan(start, end, facecolor=behavior_colors[behavior], alpha=0.3)

        # Tracer les données lidar
        for i, (var, label) in enumerate(zip(
            ['lidar_front', 'lidar_right', 'lidar_back', 'lidar_left'],
            ['Front', 'Droit', 'Arrière', 'Gauche']
        )):
            axs[i].plot(
                lidar_data[var],
                label=label,
                color=lidar_colors[var],
                linewidth=1.5
            )
            axs[i].set_ylabel(f'Distance {label} (m)')
            axs[i].grid(True, alpha=0.3)
            axs[i].legend()

            # Ajustement des limites Y
            if lidar_data[var]:
                min_val = min(lidar_data[var])
                max_val = max(lidar_data[var])
                margin = (max_val - min_val) * 0.1
                axs[i].set_ylim(min_val - margin, max_val + margin)

        axs[3].set_xlabel('Échantillons')
        plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    folder_path = "logs/Simu/Sim_2026-07-17-16-03-42"
    drones = get_drone_files(folder_path)
    plot_drones_comparison(drones, real_alpha=0.7)
    plot_lidar_comparison(drones, real_alpha=0.7)