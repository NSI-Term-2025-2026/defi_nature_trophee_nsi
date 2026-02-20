# 🐾 Défi Nature — Projet NSI (Terminale) | Jeu de cartes en Python (Pygame)

## 📌 Présentation du projet
Ce dépôt contient une **recréation du jeu de société Défi Nature** sous forme de jeu vidéo en **Python** (interface **Pygame**).
Deux joueurs (humains ou robots) s’affrontent avec des cartes “Animaux” contenant 3 caractéristiques :

- **Poids**
- **Longueur**
- **Longévité**

À chaque manche, le joueur actif choisit une caractéristique, puis on compare les valeurs :
✅ **La valeur strictement la plus grande gagne**  
⚠️ **En cas d’égalité, le joueur actif perd la manche** (règle volontaire pour éviter les matchs nuls).

---

## 🚀 Fonctionnalités principales

### 🎮 Gameplay
- Modes de jeu :
  - **Joueur vs Joueur**
  - **Joueur vs Robot (aléatoire)**
  - **Joueur vs Robot (intelligent)**
- Réinsertion des cartes de façon **aléatoire** pour éviter les boucles trop prévisibles
- Affichage complet : cartes, tours, résultats de manche, nombre de cartes restantes
- Menu “hamburger” (Rejouer / Options / Règles / À propos / Quitter)

### 🧠 IA (Robots)
Plusieurs stratégies sont disponibles (et documentées) :
- **Aléatoire** : choisit une caractéristique au hasard
- **Première caractéristique** : joue toujours “poids”
- **Triche (max)** : connaît sa carte + la carte adverse (choisit une caractéristique gagnante si possible)
- **Intermédiaire (stats)** : compare sa carte à une **moyenne** ou une **médiane** de l’historique
- **Variante globale** : connaît toutes les cartes du jeu (médiane “globale”)

➡️ Détails dans : `strategies/strategies.txt`

---

## 🧩 Architecture (séparation cerveau / interface)
Le projet est organisé pour séparer :
- ✅ **Le moteur du jeu (règles, joueurs, robots, données)** → `cerveau.py`
- ✅ **L’interface graphique Pygame** → `game_pygame.py`
- ✅ **Le point d’entrée (lancement du jeu)** → `main.py`

🎯 Objectif important : pouvoir faire tourner des **simulations / statistiques** sans dépendre de Pygame (utile sur un PC où Pygame n’est pas installé).

---

## 📂 Structure du projet

```text
defi_nature_trophee_nsi/
│
├── main.py                  # Point d'entrée (lance le jeu)
├── cerveau.py               # Moteur du jeu : règles + robots + données
├── game_pygame.py           # Interface Pygame (UI uniquement)
├── stats.py                 # Menu de statistiques entre choix robots
├── requirements.txt          
│
├── assets/                  # Ressources du jeu
│   ├── images/animaux/      # Images des cartes (nommage = nom_animal.png)
│   └── sounds/              # Sons (click, victory, etc.)
│
└── strategies/
    └── strategies.txt       # Liste des stratégies de robots
```

## 🛠️ Installation des dépendances

Avant de lancer le projet, installez les bibliothèques nécessaires à l'aide du fichier `requirements.txt` :

```bash
pip install -r requirements.txt 
