import pandas as pd
import matplotlib.pyplot as plt

# Lire le fichier CSV (remplace 'ton_fichier.csv' par le chemin de ton fichier)
df = pd.read_csv('logs/Controleur/Controleur_07-07_16h45m54940176/ranger_14.csv')
class MoyenneGlissanteTempsReel:
    """
    Calcule une moyenne glissante en temps réel, échantillon par échantillon.
    Complexité O(1) par échantillon (aucun recalcul complet à chaque appel).
    """
    
    def __init__(self, taille_fenetre):
        if taille_fenetre <= 0:
            raise ValueError("La taille de la fenêtre doit être positive.")
        
        self.taille_fenetre = taille_fenetre
        self.buffer = [0.0] * taille_fenetre  # buffer circulaire pré-alloué
        self.index = 0        # position d'écriture actuelle dans le buffer
        self.somme = 0.0       # somme courante des valeurs dans le buffer
        self.compte = 0        # nombre d'échantillons reçus (utile au démarrage)

    def ajouter_echantillon(self, valeur):
        """
        Ajoute un nouvel échantillon et retourne la moyenne glissante à jour.
        """

        if valeur >1:
            valeur = 1
        # Retirer l'ancienne valeur à cette position du buffer
        ancienne_valeur = self.buffer[self.index]
        self.somme -= ancienne_valeur
        
        # Ajouter la nouvelle valeur
        self.buffer[self.index] = valeur
        self.somme += valeur
        
        # Avancer l'index de manière circulaire
        self.index = (self.index + 1) % self.taille_fenetre
        
        # Gérer le cas où le buffer n'est pas encore plein (démarrage)
        if self.compte < self.taille_fenetre:
            self.compte += 1
            return self.somme / self.compte
        
        return self.somme / self.taille_fenetre

    def valeur_actuelle(self):
        """Retourne la moyenne actuelle sans ajouter de nouvel échantillon."""
        if self.compte == 0:
            return 0.0
        diviseur = min(self.compte, self.taille_fenetre)
        return self.somme / diviseur

    def reinitialiser(self):
        """Réinitialise complètement l'état du filtre."""
        self.buffer = [0.0] * self.taille_fenetre
        self.index = 0
        self.somme = 0.0
        self.compte = 0

class FiltreMedianTempsReel:
    """
    Calcule une médiane glissante en temps réel, échantillon par échantillon.
    Maintient un buffer circulaire (ordre d'arrivée) ET une liste triée
    (pour extraire la médiane rapidement), sans aucune librairie externe.
    
    Complexité par échantillon : O(taille_fenetre) pour l'insertion/suppression
    dans la liste triée (recherche + décalage). Convient bien pour des fenêtres
    de taille raisonnable (quelques dizaines à quelques centaines d'éléments).
    """

    def __init__(self, taille_fenetre):
        if taille_fenetre <= 0:
            raise ValueError("La taille de la fenêtre doit être positive.")

        self.taille_fenetre = taille_fenetre
        self.buffer = [0.0] * taille_fenetre  # ordre chronologique (circulaire)
        self.trie = []                         # valeurs triées, pour la médiane
        self.index = 0
        self.compte = 0

    def _recherche_position(self, valeur):
        """
        Recherche dichotomique de la position d'insertion dans la liste triée.
        (équivalent de bisect.bisect_left, réécrit à la main)
        """
        gauche, droite = 0, len(self.trie)
        while gauche < droite:
            milieu = (gauche + droite) // 2
            if self.trie[milieu] < valeur:
                gauche = milieu + 1
            else:
                droite = milieu
        return gauche

    def ajouter_echantillon(self, valeur):
        """
        Ajoute un nouvel échantillon et retourne la médiane glissante à jour.
        """

        if valeur >1:
            valeur = 1
        # 1. Retirer l'ancienne valeur (celle qui sort de la fenêtre)
        if self.compte >= self.taille_fenetre:
            ancienne_valeur = self.buffer[self.index]
            pos_ancienne = self._recherche_position(ancienne_valeur)
            # pos_ancienne pointe sur la première occurrence égale
            self.trie.pop(pos_ancienne)

        # 2. Ajouter la nouvelle valeur au buffer circulaire
        self.buffer[self.index] = valeur
        self.index = (self.index + 1) % self.taille_fenetre

        # 3. Insérer la nouvelle valeur dans la liste triée, à la bonne position
        pos_nouvelle = self._recherche_position(valeur)
        self.trie.insert(pos_nouvelle, valeur)

        if self.compte < self.taille_fenetre:
            self.compte += 1

        return self._calculer_mediane()

    def _calculer_mediane(self):
        n = len(self.trie)
        milieu = n // 2
        if n % 2 == 1:
            return self.trie[milieu]
        else:
            return (self.trie[milieu - 1] + self.trie[milieu]) / 2

    def valeur_actuelle(self):
        """Retourne la médiane actuelle sans ajouter de nouvel échantillon."""
        if not self.trie:
            return 0.0
        return self._calculer_mediane()

    def reinitialiser(self):
        """Réinitialise complètement l'état du filtre."""
        self.buffer = [0.0] * self.taille_fenetre
        self.trie = []
        self.index = 0
        self.compte = 0


moyenneur_left = MoyenneGlissanteTempsReel(5)
moyenneur_right = MoyenneGlissanteTempsReel(100)
moyenneur_front = MoyenneGlissanteTempsReel(100)
moyenneur_back = MoyenneGlissanteTempsReel(100)
median_left = FiltreMedianTempsReel(10)
# Créer une figure avec 4 sous-graphiques
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('Valeurs des capteurs Ranger (index en abscisse)')

valeur_lidar_left = []
valeur_lidar_apres_moyenne = []
for val in df['Ranger_left']:
    valeur_lidar_left.append(median_left.ajouter_echantillon(val))
    valeur_lidar_apres_moyenne.append(moyenneur_left.ajouter_echantillon(valeur_lidar_left[-1]))

# Graphique 1 : Ranger_left
axes[0, 0].plot(df.index, valeur_lidar_left, label='Left', color='blue')
axes[0, 0].set_title('Ranger Left')
axes[0, 0].set_xlabel('Index')
axes[0, 0].set_ylabel('Valeur')
axes[0, 0].grid(True)

# Graphique 2 : Ranger_front
axes[0, 1].plot(df.index, valeur_lidar_apres_moyenne, label='Front', color='green')
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