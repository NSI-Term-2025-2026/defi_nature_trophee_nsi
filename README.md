# Jeu de Cartes Animaux – Projet Python / NSI

## Description
Ce projet est une simulation d’un jeu de cartes en Python, développée dans le cadre du programme de Terminale NSI.  
Le jeu oppose deux joueurs, humains ou IA, qui s’affrontent en comparant les caractéristiques d’animaux (poids, longueur et longévité). À chaque tour, un joueur choisit une caractéristique et la compare avec celle de l’adversaire. Le joueur possédant la valeur la plus élevée remporte la carte adverse.

Le programme inclut un système de distribution équilibrée des cartes et permet de jouer contre un autre joueur ou contre un robot, configurable en mode aléatoire ou intelligent.

---

## Fonctionnalités

- Simulation de parties entre deux joueurs humains ou contre un robot
- Choix de la caractéristique à comparer à chaque tour : poids, longueur ou longévité
- Distribution équilibrée des cartes sans modifier la liste initiale
- Robot configurable : mode aléatoire ou mode intelligent basé sur un quotient des caractéristiques par rapport à la médiane
- Affichage détaillé des cartes et des résultats de chaque manche
- Suivi du nombre de cartes restantes pour chaque joueur

---

## Installation et exécution

1. Cloner le dépôt :

```bash
git clone https://github.com/AntoCheMaestro/jeu_cartes_animaux.git
cd jeu_cartes_animaux
python main.py
