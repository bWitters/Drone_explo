import pandas as pd
import matplotlib.pyplot as plt

# Lire le fichier CSV (remplace 'data.csv' par ton nom de fichier)
df = pd.read_csv('logs/Controleur/Controleur_07-07_16h40m21960860/14.csv')

# Tracer chaque colonne en fonction de l'index
plt.figure(figsize=(12, 6))

# Variables de position
plt.subplot(2, 1, 1)
plt.plot(df.index, df['x'], label='x')
plt.plot(df.index, df['y'], label='y')
plt.plot(df.index, df['z'], label='z')
plt.title('Position en fonction de l\'index')
plt.xlabel('Index')
plt.ylabel('Valeur')
plt.legend()
plt.grid(True)

# Variables de vitesse et commandes
plt.subplot(2, 1, 2)
plt.plot(df.index, df['vx'], label='vx')
plt.plot(df.index, df['vy'], label='vy')
plt.plot(df.index, df['vz'], label='vz')
plt.plot(df.index, df['Vx_cmd'], label='Vx_cmd', linestyle='--')
plt.plot(df.index, df['Vy_cmd'], label='Vy_cmd', linestyle='--')
plt.plot(df.index, df['Vz_cmd'], label='Vz_cmd', linestyle='--')
plt.title('Vitesse et commandes en fonction de l\'index')
plt.xlabel('Index')
plt.ylabel('Valeur')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()