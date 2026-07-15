import pandas as pd
import matplotlib.pyplot as plt

# Lire le fichier CSV (remplace 'ton_fichier.csv' par le chemin de ton fichier)
df = pd.read_csv('logs/Controleur/Controleur_07-08_17h50m50876412/ranger_with_filter14.csv')

# Créer une figure avec 4 sous-graphiques
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Valeurs des capteurs Ranger (index en abscisse)')

# Graphique 1 : Ranger_left
axes[0, 0].plot(df.index, df['Ranger_left'], label='Left', color='blue')
axes[0, 0].set_title('Ranger Left')
axes[0, 0].set_xlabel('Index')
axes[0, 0].set_ylabel('Valeur')
axes[0, 0].grid(True)

# Graphique 2 : Ranger_front
axes[0, 1].plot(df.index, df['Ranger_front'], label='Front', color='green')
axes[0, 1].set_title('Ranger Front')
axes[0, 1].set_xlabel('Index')
axes[0, 1].set_ylabel('Valeur')
axes[0, 1].grid(True)

# Graphique 3 : Ranger_right
axes[1, 0].plot(df.index, df['Ranger_right'], label='Right', color='red')
axes[1, 0].set_title('Ranger Right')
axes[1, 0].set_xlabel('Index')
axes[1, 0].set_ylabel('Valeur')
axes[1, 0].grid(True)

# Graphique 4 : Ranger_back
axes[1, 1].plot(df.index, df['Ranger_back'], label='Back', color='purple')
axes[1, 1].set_title('Ranger Back')
axes[1, 1].set_xlabel('Index')
axes[1, 1].set_ylabel('Valeur')
axes[1, 1].grid(True)

# Ajuster la disposition
plt.tight_layout()
plt.show()