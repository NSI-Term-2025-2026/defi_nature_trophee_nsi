# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 10:54:10 2026

@author: Antonin

Point d'entrée du projet.

- Mode jeu (Pygame) : python sources/main.py play
- Mode stats (sans Pygame) : python sources/main.py stats
"""

import sys


def main():
    mode = "play"
    if len(sys.argv) >= 2:
        mode = sys.argv[1].strip().lower()

    if mode in ("play", "jeu", "pygame"):
        # Import conditionnel pour que le PC sans pygame puisse lancer "stats"
        from game_pygame import run
        run()
        return

    if mode in ("stats", "sim", "simulation"):
        from stats import run_stats
        run_stats()
        return

    print("Mode inconnu.")
    print("Utilisation :")
    print("  python sources/main.py play   # jeu Pygame")
    print("  python sources/main.py stats  # simulations sans Pygame")


if __name__ == "__main__":
    main()
