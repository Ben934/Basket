import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Paramètres de la simulation
P_max = 100  # Performance maximale
n_steps = 48  # Nombre de minutes de jeu

# Streamlit UI
st.title("Simulation de la rotation des joueurs en basket 🏀")

# Sliders pour ajuster les paramètres de fatigue et récupération
col1, col2, col3, col4 = st.columns(4)

with col1:
    fatigue_rate = st.slider("Taux de fatigue par minute", 0.05, 0.2, 0.1)
with col2:
    recovery_rate = st.slider("Taux de récupération par minute", 0.05, 0.2, 0.1)
with col3:
    fatigue_threshold = st.slider("Seuil de fatigue pour sortir (%)", 50, 80, 60)
with col4:
    recovery_threshold = st.slider("Seuil de récupération pour rentrer (%)", 70, 90, 80)

# Initialisation des performances et états des joueurs
P_titulaire = np.zeros(n_steps)
P_remplaçant = np.zeros(n_steps)
P_en_jeu = np.full(n_steps, P_max)
rotation = []  # Stocke qui est en jeu à chaque minute

P_titulaire[0] = P_max
P_remplaçant[0] = P_max

titulaire_sur_terrain = True
remplaçant_sur_terrain = False
perf_titulaire = P_max
perf_remplaçant = P_max
minute_remplaçant_entre = -1

for n in range(1, n_steps):
    if titulaire_sur_terrain:
        perf_titulaire -= fatigue_rate * perf_titulaire
        P_titulaire[n] = perf_titulaire
        P_remplaçant[n] = perf_remplaçant
        perf_remplaçant += recovery_rate * (P_max - perf_remplaçant)
        P_en_jeu[n] = perf_titulaire
        rotation.append("Titulaire")
        if perf_titulaire <= fatigue_threshold:
            titulaire_sur_terrain = False
            remplaçant_sur_terrain = True
            minute_remplaçant_entre = n
    else:
        perf_titulaire += recovery_rate * (P_max - perf_titulaire)
        P_titulaire[n] = perf_titulaire
    
    if remplaçant_sur_terrain:
        if n > minute_remplaçant_entre:
            perf_remplaçant -= fatigue_rate * perf_remplaçant
        P_remplaçant[n] = perf_remplaçant
        P_en_jeu[n] = perf_remplaçant
        rotation.append("Remplaçant")
        if perf_remplaçant <= fatigue_threshold and perf_titulaire >= recovery_threshold:
            remplaçant_sur_terrain = False
            titulaire_sur_terrain = True
    else:
        perf_remplaçant += recovery_rate * (P_max - perf_remplaçant)
        P_remplaçant[n] = perf_remplaçant

# Calcul de la performance moyenne du joueur en jeu
total_perf_moyenne = np.mean(P_en_jeu)

# Ajout du slider pour voir les rotations avec prise en charge des flèches directionnelles
minute = st.slider("Minute du match", 0, n_steps-1, 0, key="minute_slider")
status = rotation[minute]

# Affichage des joueurs sur le terrain ou sur le banc
st.markdown("### Position des joueurs")
if status == "Titulaire":
    st.write("Joueur titulaire : **en jeu** 🏀")
    st.write("Joueur remplaçant : **sur le banc** 🪑")
elif status == "Remplaçant":
    st.write("Joueur titulaire : **sur le banc** 🪑")
    st.write("Joueur remplaçant : **en jeu** 🏀")

# Affichage du graphique
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(P_titulaire, label="Joueur titulaire", color="b")
ax.plot(P_remplaçant, label="Joueur remplaçant", color="g")
ax.plot(P_en_jeu, label="Joueur en jeu", color="r", linestyle="--")
ax.axhline(y=fatigue_threshold, color="r", linestyle="--", label="Seuil de fatigue")
ax.axhline(y=recovery_threshold, color="y", linestyle="--", label="Seuil de récupération")

# Ajout du point correspondant à la minute choisie
ax.scatter(minute, P_en_jeu[minute], color='black', zorder=3, label="Minute sélectionnée")
ax.set_title("Évolution de la performance des joueurs")
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
