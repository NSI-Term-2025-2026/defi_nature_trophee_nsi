# -*- coding: utf-8 -*-
"""
Stats / simulations (sans pygame).

But :
- Comparer des stratégies entre elles sur N parties.
- Mesurer "à quel point" une stratégie est meilleure qu'une autre.

Indicateurs demandés :
1) Winrate : sur N parties, % de victoires de A contre B
2) Vitesse : nombre moyen de manches quand A gagne (et quand B gagne)

Important :
- Ce fichier N'IMPORTE PAS pygame, donc il tourne sur le PC des vacances.
- On utilise des seeds pour rendre les résultats reproductibles (mêmes résultats
  si on relance avec les mêmes paramètres).
"""

import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

# On importe uniquement le "cerveau" (logique du jeu / bots / cartes)
from cerveau import (
    Joueur, GameState, LISTE_ANIMAUX, distribuer_cartes,
    choix_robot_aleatoire,
    choix_robot_aleatoire_premiere_caracteristique,
    choix_robot_intelligent,
    choix_robot_intelligent_moyenne,
    choix_robot_triche_absolue,
    choix_robot_intelligent_triche,
    choix_robot_monte_carlo_random,
    choix_robot_monte_carlo_median)

NOMBRE_PARTIES_EFFECTUE = 0

# ============================================================
# ======================= WRAPPERS STRATEGIES =================
# ============================================================

@dataclass(frozen=True)
class Strategie:
    """
    Petite structure de données pour stocker une stratégie.

    - nom : nom lisible pour l'affichage console.
    - choisir : fonction qui reçoit l'état du jeu (GameState) et renvoie
      la caractéristique choisie : "poids", "longueur" ou "longevite".
    """
    nom: str
    choisir: Callable[[GameState], str]


def _safe_carac(carac: str) -> str:
    """
    Sécurise la caractéristique renvoyée par une stratégie.
    Si une stratégie renvoie quelque chose d'invalide, on retombe sur "poids"
    pour éviter un crash.
    """
    if carac.lower() in ("poids", "longueur", "longevite"):
        return carac.lower()
    return "poids"


def _carte_actif(game: GameState):
    """
    Raccourci : récupérer la carte visible du joueur actif.
    """
    return game.joueur_actif.carte_visible()


# -----------------------
# Stratégies "naïves"
# -----------------------

def strat_random(game: GameState) -> str:
    """Choisit une caractéristique au hasard."""
    return _safe_carac(choix_robot_aleatoire())


def strat_first(game: GameState) -> str:
    """Choisit toujours la première caractéristique (ici: poids)."""
    return _safe_carac(choix_robot_aleatoire_premiere_caracteristique())


# -----------------------
# Stratégies "intermédiaires"
# -----------------------

def strat_median_hist(game: GameState) -> str:
    """
    Compare sa carte à une médiane calculée sur l'historique des cartes jouées.
    (Ton bot "intelligent" médiane/ratio)
    """
    carte = _carte_actif(game)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_intelligent(carte, game.historique_cartes))


def strat_mean_hist(game: GameState) -> str:
    """
    Même idée que la médiane, mais avec la moyenne (mean) sur l'historique.
    """
    carte = _carte_actif(game)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_intelligent_moyenne(carte, game.historique_cartes))

def strat_monte_carlo_random(game: GameState) -> str:
    return _safe_carac(choix_robot_monte_carlo_random(game, essais=30))


def strat_monte_carlo_median(game: GameState) -> str:
    return _safe_carac(choix_robot_monte_carlo_median(game, essais=30))


# -----------------------
# Stratégies "fortes / triche"
# -----------------------

def strat_cheat_absolute(game: GameState) -> str:
    """
    "Le plus fort possible" :
    le bot connaît sa carte ET la carte adverse.
    Il choisit une caractéristique gagnante s'il en existe une, sinon aléatoire.
    """
    carte_jouee = game.joueur_actif.carte_visible()
    carte_subie = game.joueur_passif.carte_visible()

    if carte_jouee is None or carte_subie is None:
        return _safe_carac(choix_robot_aleatoire())

    return _safe_carac(choix_robot_triche_absolue(carte_jouee, carte_subie))


def strat_cheat_median_allcards(game: GameState) -> str:
    """
    Triche "médiane globale" :
    le bot connaît la distribution complète des cartes (LISTE_ANIMAUX),
    et calcule la médiane sur TOUTES les cartes existantes.
    (Il ne connaît pas forcément la carte adverse, mais il connaît le "jeu complet".)
    """
    carte = _carte_actif(game)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())

    return _safe_carac(choix_robot_intelligent_triche(carte, LISTE_ANIMAUX))


# Liste officielle des stratégies testées
STRATEGIES: List[Strategie] = [
    Strategie("Random", strat_random),
    Strategie("FirstStat(poids)", strat_first),
    Strategie("MedianRatio(hist)", strat_median_hist),
    Strategie("MeanRatio(hist)", strat_mean_hist),
    Strategie("MonteCarlo_random", strat_monte_carlo_random),
    Strategie("MonteCarlo_median", strat_monte_carlo_median),
    Strategie("CheatAbsolute(see both)", strat_cheat_absolute),
    Strategie("CheatMedianAllCards(median global)", strat_cheat_median_allcards),
]

# Dictionnaire pratique si un jour tu veux sélectionner par nom
STRATEGY_BY_NAME: Dict[str, Strategie] = {s.nom: s for s in STRATEGIES}


# ============================================================
# ======================= SIMULATION CORE ======================
# ============================================================

def creer_partie_bot_vs_bot(seed: Optional[int] = None) -> GameState:
    """
    Crée une partie BotA vs BotB.

    Pourquoi une seed ?
    - Pour rendre la distribution et le mélange de cartes reproductibles.
    - Si on relance la même expérience, on peut obtenir exactement les mêmes résultats.

    Important : on reste en mode_robot=None car ici on pilote les bots nous-mêmes
    (on appelle strat_a / strat_b en fonction du joueur actif).
    """
    if seed is not None:
        random.seed(seed)

    c1, c2 = distribuer_cartes(LISTE_ANIMAUX)
    j1 = Joueur("BotA", c1)
    j2 = Joueur("BotB", c2)
    return GameState(j1, j2, mode_robot=None)


def jouer_une_partie(
    strat_a: Strategie,
    strat_b: Strategie,
    seed: Optional[int] = None,
    max_rounds_guard: int = 5000
) -> Tuple[str, int]:
    """
    Joue UNE partie complète entre strat_a (BotA) et strat_b (BotB).

    Retour :
    - winner_name : "BotA" ou "BotB"
    - nb_manches : nombre de manches jouées

    max_rounds_guard :
    - garde-fou anti-boucle infinie (normalement inutile, mais utile en dev).
    """
    global NOMBRE_PARTIES_EFFECTUE
    game = creer_partie_bot_vs_bot(seed=seed)
    rounds = 0

    # Tant que la partie n'est pas terminée :
    while (not game.terminee) and rounds < max_rounds_guard:

        # Qui doit jouer ? joueur_actif = celui qui choisit la caractéristique
        if game.joueur_actif.nom == "BotA":
            carac = strat_a.choisir(game)
        else:
            carac = strat_b.choisir(game)

        # Sécurité : s'assure que la stratégie a renvoyé une carac valide
        carac = _safe_carac(carac)

        # On applique la manche dans le moteur
        game.appliquer_manche(carac)
        rounds += 1

    # Si jamais la partie n'a pas fini (devrait être très rare),
    # on évite de crasher : on attribue un gagnant au hasard.
    if not game.terminee or game.gagnant is None:
        winner = random.choice(["BotA", "BotB"])
        return winner, rounds
    # TEST DEBUG 
    NOMBRE_PARTIES_EFFECTUE += 1
    print('Partie terminee: ', NOMBRE_PARTIES_EFFECTUE)

    return game.gagnant.nom, rounds


def comparer_deux_strategies(
    strat_a: Strategie,
    strat_b: Strategie,
    n_games: int = 1000,
    seed: int = 12345
) -> Dict[str, object]:
    """
    Compare A vs B sur n_games parties.

    On calcule :
    - winrate_A_pct / winrate_B_pct
    - avg_rounds_overall : manches moyennes toutes parties confondues
    - avg_rounds_when_A_wins : manches moyennes seulement parmi les victoires de A
    - avg_rounds_when_B_wins : manches moyennes seulement parmi les victoires de B
    """
    global NOMBRE_PARTIES_EFFECTUE
    wins_a = 0
    wins_b = 0

    rounds_total = 0
    rounds_when_a_wins: List[int] = []
    rounds_when_b_wins: List[int] = []

    # On crée un générateur pseudo-aléatoire local (reproductible)
    # Plutôt que d'utiliser random global partout.
    rng = random.Random(seed)

    for _ in range(n_games):
        # Pour éviter que toutes les parties aient le même mélange,
        # on tire une seed différente pour chaque partie.
        s = rng.randrange(0, 2**31 - 1)

        winner, r = jouer_une_partie(strat_a, strat_b, seed=s)
        rounds_total += r

        if winner == "BotA":
            wins_a += 1
            rounds_when_a_wins.append(r)
        else:
            wins_b += 1
            rounds_when_b_wins.append(r)

    def _avg(lst: List[int]) -> float:
        """Moyenne simple; renvoie NaN si liste vide."""
        return (sum(lst) / len(lst)) if lst else float("nan")

    NOMBRE_PARTIES_EFFECTUE = 0
    return {
        "A": strat_a.nom,
        "B": strat_b.nom,
        "n_games": n_games,
        "wins_A": wins_a,
        "wins_B": wins_b,
        "winrate_A_pct": 100.0 * wins_a / n_games,
        "winrate_B_pct": 100.0 * wins_b / n_games,
        "avg_rounds_overall": rounds_total / n_games,
        "avg_rounds_when_A_wins": _avg(rounds_when_a_wins),
        "avg_rounds_when_B_wins": _avg(rounds_when_b_wins),
    }


# ============================================================
# ======================= CONSOLE OUTPUT =======================
# ============================================================

def print_result(res: Dict[str, object]) -> None:
    """
    Affichage lisible d'un match-up.
    """
    A = res["A"]
    B = res["B"]
    n = res["n_games"]

    print("=" * 72)
    print(f"Match-up:  A = {A}   vs   B = {B}   |   N = {n}")
    print("-" * 72)

    # 1) % victoires
    print(f"Winrate A: {res['winrate_A_pct']:.1f}%   ({res['wins_A']}/{n})")
    print(f"Winrate B: {res['winrate_B_pct']:.1f}%   ({res['wins_B']}/{n})")

    print("-" * 72)

    # 2) vitesse (manches)
    print(f"Avg rounds overall:         {res['avg_rounds_overall']:.2f}")
    print(f"Avg rounds when A wins:     {res['avg_rounds_when_A_wins']:.2f}")
    print(f"Avg rounds when B wins:     {res['avg_rounds_when_B_wins']:.2f}")

    print("=" * 72)
    print()

def logs_result(res) -> None:
    
    filename = "data/results.txt"
    file = open(filename,'a+')

    A = res["A"]
    B = res["B"]
    n = res["n_games"]

    file.write("=" * 72+' \n ')
    file.write(f"Match-up:  A = {A}   vs   B = {B}   |   N = {n} \n ")
    file.write("-" * 72 + ' \n ')

    # 1) % victoires
    file.write(f"Winrate A: {res['winrate_A_pct']:.1f}%   ({res['wins_A']}/{n}) \n ")
    file.write(f"Winrate B: {res['winrate_B_pct']:.1f}%   ({res['wins_B']}/{n}) \n ")

    file.write("-" * 72 + ' \n ')

    # 2) vitesse (manches)
    file.write(f"Avg rounds overall:         {res['avg_rounds_overall']:.2f} \n ")
    file.write(f"Avg rounds when A wins:     {res['avg_rounds_when_A_wins']:.2f}  \n ")
    file.write(f"Avg rounds when B wins:     {res['avg_rounds_when_B_wins']:.2f}  \n ")

    file.write("=" * 72)
    file.write(' \n ')
    file.close()

def comparer_toutes_strategies(n_games: int = 1000, seed: int = 12345) -> None:
    """
    Compare toutes les stratégies entre elles :
    - pour chaque paire (i < j), on fait A vs B et on affiche le résultat.
    """
    for i in range(len(STRATEGIES)):
        for j in range(i + 1, len(STRATEGIES)):
            a = STRATEGIES[i]
            b = STRATEGIES[j]

            # On modifie légèrement le seed selon la paire pour éviter
            # d'avoir des suites trop similaires entre les comparaisons.
            local_seed = seed + 1000 * i + j

            res = comparer_deux_strategies(a, b, n_games=n_games, seed=local_seed)
            print_result(res)
            logs_result(res)


def run_stats() -> None:
    """
    Point d'entrée appelé par : python main.py stats
    """
    print("=== MODE STATS (sans pygame) ===")
    print("Stratégies disponibles:")
    for s in STRATEGIES:
        print(" -", s.nom)
    print()

    # Paramètres principaux :
    N = 100     # nombre de parties par match-up
    SEED = 12345 # seed de base pour la reproductibilité

    comparer_toutes_strategies(n_games=N, seed=SEED)


if __name__ == "__main__":
    run_stats()



