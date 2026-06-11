import glob
import pandas as pd
import matplotlib.pyplot as plt

def plot_csv_files(directory='.'):
    # Trouver tous les fichiers CSV dans le répertoire
    csv_files = glob.glob(f'{directory}/*.csv')

    if not csv_files:
        print("Aucun fichier CSV trouvé dans le répertoire.")
        return

    # Calculer l'échelle commune à tous les fichiers pour x, y, yaw
    global_max = 0
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        required_columns = ['x', 'y', 'z', 'yaw']
        if not all(col in df.columns for col in required_columns):
            print(f"Le fichier {csv_file} ne contient pas toutes les colonnes requises : {required_columns}")
            continue
        current_max = max(
            df['x'].abs().max(),
            df['y'].abs().max(),
            df['yaw'].abs().max()
        )
        if current_max > global_max:
            global_max = current_max

    # Ajouter une marge de 10%
    global_max *= 1.1

    # Désactiver l'affichage immédiat pour ouvrir toutes les fenêtres à la fin
    plt.ioff()

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        required_columns = ['x', 'y', 'z', 'yaw']
        if not all(col in df.columns for col in required_columns):
            continue

        # Créer une seule fenêtre par fichier
        plt.figure(figsize=(14, 12))

        # --- y en fonction de x (centré sur 0,0, échelle globale) ---
        plt.subplot(3, 2, (1, 2))
        plt.plot(df['x'], df['y'], label='y en fonction de x', color='blue')
        plt.title(f'y en fonction de x - {csv_file}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.xlim(-global_max, global_max)
        plt.ylim(-global_max, global_max)

        # --- x en fonction du temps (échelle globale) ---
        plt.subplot(3, 2, 3)
        plt.plot(df.index, df['x'], label='x vs temps', color='red')
        plt.title('x en fonction du temps')
        plt.xlabel('Temps')
        plt.ylabel('x')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.ylim(-global_max, global_max)

        # --- y en fonction du temps (échelle globale) ---
        plt.subplot(3, 2, 4)
        plt.plot(df.index, df['y'], label='y vs temps', color='green')
        plt.title('y en fonction du temps')
        plt.xlabel('Temps')
        plt.ylabel('y')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.ylim(-global_max, global_max)

        # --- z en fonction du temps (échelle libre) ---
        plt.subplot(3, 2, 5)
        plt.plot(df.index, df['z'], label='z vs temps', color='purple')
        plt.title('z en fonction du temps')
        plt.xlabel('Temps')
        plt.ylabel('z')
        plt.grid(True)

        # --- yaw en fonction du temps (échelle globale) ---
        plt.subplot(3, 2, 6)
        plt.plot(df.index, df['yaw'], label='yaw vs temps', color='orange')
        plt.title('yaw en fonction du temps')
        plt.xlabel('Temps')
        plt.ylabel('yaw')
        plt.grid(True)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.ylim(-global_max, global_max)

        plt.suptitle(f'Graphiques pour {csv_file}')
        plt.tight_layout()

    # Afficher toutes les fenêtres à la fin
    plt.show()

plot_csv_files('Sim/positions/')