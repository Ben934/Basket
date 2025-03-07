import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Paramètres de la simulation
P_max = 100  # Performance maximale
n_steps = 48  # Nombre de minutes de jeu

# Streamlit UI
st.title("Simulation de la rotation des joueurs en basket 🏀")

# Présentation et hypothèses de l'étude
st.markdown("""
### Hypothèses de la simulation :
- Un joueur titulaire commence avec une performance de 100%.
- Il perd de la performance en jouant en raison de la fatigue.
- Lorsqu'il atteint un seuil de fatigue défini, il est remplacé.
- Le remplaçant, qui commence aussi à 100%, prend sa place et **ne commence à se fatiguer qu'à partir de la minute suivante**.
- Pendant que le joueur est sur le banc, il récupère progressivement jusqu'à atteindre un seuil défini pour rentrer en jeu.
- Ces seuils de fatigue et de récupération sont ajustables via les curseurs.
""")

# Utilisation de st.columns pour mettre les sliders côte à côte
col1, col2, col3, col4 = st.columns(4)

with col1:
    fatigue_rate = st.slider("Taux de fatigue par minute", 0.05, 0.2, 0.1)
    
with col2:
    recovery_rate = st.slider("Taux de récupération par minute", 0.05, 0.2, 0.1)

with col3:
    fatigue_threshold = st.slider("Seuil de fatigue pour sortir (%)", 50, 80, 60)

with col4:
    recovery_threshold = st.slider("Seuil de récupération pour rentrer (%)", 70, 90, 80)

# Initialisation des performances
P_titulaire = np.zeros(n_steps)
P_remplaçant = np.zeros(n_steps)
P_en_jeu = np.full(n_steps, P_max)

P_titulaire[0] = P_max
P_remplaçant[0] = P_max  # Le remplaçant commence bien à 100 %

# États initiaux
titulaire_sur_terrain = True
remplaçant_sur_terrain = False
perf_titulaire = P_max
perf_remplaçant = P_max
minute_remplaçant_entre = -1  # Variable pour savoir à quelle minute le remplaçant entre en jeu

for n in range(1, n_steps):
    if titulaire_sur_terrain:
        # Le titulaire perd de la performance en jouant
        perf_titulaire -= fatigue_rate * perf_titulaire
        P_titulaire[n] = perf_titulaire
        P_remplaçant[n] = perf_remplaçant  # Le remplaçant reste sur le banc et récupère
        perf_remplaçant += recovery_rate * (P_max - perf_remplaçant)
        P_en_jeu[n] = perf_titulaire

        if perf_titulaire <= fatigue_threshold:  # Sortie si atteint le seuil de fatigue
            titulaire_sur_terrain = False
            remplaçant_sur_terrain = True
            minute_remplaçant_entre = n  # Enregistrer la minute où le remplaçant entre
    else:
        # Le titulaire récupère sur le banc
        perf_titulaire += recovery_rate * (P_max - perf_titulaire)
        P_titulaire[n] = perf_titulaire
    
    if remplaçant_sur_terrain:
        # Le remplaçant ne se fatigue qu'après la minute suivante où il est entré
        if n > minute_remplaçant_entre:
            perf_remplaçant -= fatigue_rate * perf_remplaçant  # Fatigue après sa première minute sur le terrain
        P_remplaçant[n] = perf_remplaçant
        P_en_jeu[n] = perf_remplaçant
        P_titulaire[n] = perf_titulaire  # Le titulaire continue de récupérer sur le banc

        if perf_remplaçant <= fatigue_threshold:
            if perf_titulaire >= recovery_threshold:
                remplaçant_sur_terrain = False
                titulaire_sur_terrain = True
            else:
                # Le remplaçant continue à jouer
                P_remplaçant[n] = perf_remplaçant
    else:
        # Le remplaçant récupère sur le banc
        perf_remplaçant += recovery_rate * (P_max - perf_remplaçant)
        P_remplaçant[n] = perf_remplaçant

# Calcul de la performance moyenne
total_perf_moyenne = np.mean(P_en_jeu)

# Affichage du graphique
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(P_titulaire, label="Joueur titulaire", color="b")
ax.plot(P_remplaçant, label="Joueur remplaçant", color="g")
ax.plot(P_en_jeu, label="Joueur en jeu", color="r", linestyle="--")
ax.axhline(y=fatigue_threshold, color="r", linestyle="--", label="Seuil de fatigue")
ax.axhline(y=recovery_threshold, color="y", linestyle="--", label="Seuil de récupération")

ax.set_title("Évolution de la performance des joueurs avec fatigue et récupération")
ax.set_xlabel("Temps (minutes)")
ax.set_ylabel("Performance (%)")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# Affichage de la performance moyenne
st.write(f"Performance moyenne du joueur en jeu sur la durée du match : {total_perf_moyenne:.2f} %")

# Création d'un DataFrame avec les valeurs des performances à chaque étape
df = pd.DataFrame({
    'Temps (minutes)': np.arange(n_steps),
    'Joueur Titulaire (%)': P_titulaire,
    'Joueur Remplaçant (%)': P_remplaçant,
    'Joueur en Jeu (%)': P_en_jeu
})

# Affichage du tableau des performances
st.write("Tableau des performances des joueurs pendant le match :", df)
