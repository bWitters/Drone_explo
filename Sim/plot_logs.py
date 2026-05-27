import csv
import matplotlib.pyplot as plt

def plot_velocities(csv_file_paths):
    for csv_file_path in csv_file_paths:
        # Lire le fichier CSV
        vx, vy, vz, v_yaw = [], [], [], []

        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)

            # Vérifier les colonnes nécessaires
            required_columns = ['vx', 'vy', 'vz', 'v_yaw']
            for col in required_columns:
                if col not in reader.fieldnames:
                    raise ValueError(f"La colonne '{col}' est manquante dans le fichier {csv_file_path}.")

            # Extraire les données
            for row in reader:
                vx.append(float(row['vx']))
                vy.append(float(row['vy']))
                vz.append(float(row['vz']))
                v_yaw.append(float(row['v_yaw']) if row['v_yaw'] is not None else 0)

        # Créer une nouvelle figure pour ce fichier
        fig, axs = plt.subplots(4, 1, figsize=(10, 12))
        fig.suptitle(f"Analyse des vitesses et rotation - {csv_file_path.split('/')[-1]}")

        # Fonction pour centrer le 0 et ajouter une marge de 0.1
        def set_symmetrical_ylim_with_margin(ax, data):
            max_abs = max(abs(min(data)), abs(max(data))) if data else 0
            margin = 0.1
            ax.set_ylim(-max_abs - margin, max_abs + margin)

        # Tracer vx
        axs[0].plot(vx, label='Vitesse sur X', color='blue')
        axs[0].set_ylabel('Vitesse (vx)')
        axs[0].grid(True)
        axs[0].legend()
        set_symmetrical_ylim_with_margin(axs[0], vx)

        # Tracer vy
        axs[1].plot(vy, label='Vitesse sur Y', color='green')
        axs[1].set_ylabel('Vitesse (vy)')
        axs[1].grid(True)
        axs[1].legend()
        set_symmetrical_ylim_with_margin(axs[1], vy)

        # Tracer vz
        axs[2].plot(vz, label='Vitesse sur Z', color='red')
        axs[2].set_ylabel('Vitesse (vz)')
        axs[2].grid(True)
        axs[2].legend()
        set_symmetrical_ylim_with_margin(axs[2], vz)

        # Tracer v_yaw
        axs[3].plot(v_yaw, label='Vitesse de rotation (v_yaw)', color='purple')
        axs[3].set_ylabel('Vitesse de rotation (v_yaw)')
        axs[3].set_xlabel('Échantillons')
        axs[3].grid(True)
        axs[3].legend()
        set_symmetrical_ylim_with_margin(axs[3], v_yaw)

        plt.tight_layout()

    plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    csv_paths = [
        "Sim/logs/drone_1_2026-05-14-28-48.csv",
        "Sim/logs/drone_2_2026-05-14-28-48.csv",
        "Sim/logs/drone_3_2026-05-14-28-48.csv"
    ]
    plot_velocities(csv_paths)