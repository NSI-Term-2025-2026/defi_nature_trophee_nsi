# -*- coding: utf-8 -*-
"""
Stats / simulations (sans pygame).

Objectif (niveau Terminale NSI, code lisible) :
- Comparer des stratégies entre elles sur N parties.
- Afficher :
  1) le winrate
  2) la vitesse (nombre moyen de manches)
  3) une incertitude (IC 95% sur le winrate)
- IMPORTANT : certaines stratégies sont très longues (Monte Carlo, etc.).
  On adapte automatiquement :
  - Petites stratégies : peu de parties, 1 seule expérience (rapide)
  - Grosses stratégies : plus de parties + répétitions (stat "sérieuse")

Aucune dépendance pygame.
"""

import random
import csv
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from sources.cerveau import (
    Joueur, GameState, LISTE_ANIMAUX, distribuer_cartes,
    choix_robot_aleatoire,
    choix_robot_aleatoire_premiere_caracteristique,
    choix_robot_intelligent,
    choix_robot_intelligent_moyenne,
    choix_robot_triche_absolue,
    choix_robot_intelligent_triche,
    choix_robot_monte_carlo_random,
    choix_robot_monte_carlo_median
)

# ============================================================
# ======================= STRATEGIES ==========================
# ============================================================

class Strategie:
    """
    Structure simple (sans dataclass) :

    - nom : nom lisible
    - choisir(etat) : fonction qui renvoie "poids" / "longueur" / "longevite"
    """
    def __init__(self, nom: str, choisir: Callable[[GameState], str]):
        self.nom = nom
        self.choisir = choisir


def _safe_carac(carac: str) -> str:
    """Sécurise la caractéristique (évite crash si stratégie bug)."""
    if isinstance(carac, str):
        c = carac.lower()
        if c in ("poids", "longueur", "longevite"):
            return c
    return "poids"


def _carte_actif(etat: GameState):
    """Raccourci : carte visible du joueur actif."""
    return etat.joueur_actif.carte_visible()


# -----------------------
# Stratégies "naïves"
# -----------------------

def strat_random(etat: GameState) -> str:
    return _safe_carac(choix_robot_aleatoire())


def strat_first(etat: GameState) -> str:
    return _safe_carac(choix_robot_aleatoire_premiere_caracteristique())


# -----------------------
# Stratégies "intermédiaires"
# -----------------------

def strat_median_hist(etat: GameState) -> str:
    carte = _carte_actif(etat)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_intelligent(carte, etat.historique_cartes))


def strat_mean_hist(etat: GameState) -> str:
    carte = _carte_actif(etat)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_intelligent_moyenne(carte, etat.historique_cartes))


# -----------------------
# Monte Carlo (coûteux)
# -----------------------

def strat_monte_carlo_random(etat: GameState) -> str:
    return _safe_carac(choix_robot_monte_carlo_random(etat, essais=30))


def strat_monte_carlo_median(etat: GameState) -> str:
    return _safe_carac(choix_robot_monte_carlo_median(etat, essais=30))


# -----------------------
# Triche (fort)
# -----------------------

def strat_cheat_absolute(etat: GameState) -> str:
    carte_jouee = etat.joueur_actif.carte_visible()
    carte_subie = etat.joueur_passif.carte_visible()
    if carte_jouee is None or carte_subie is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_triche_absolue(carte_jouee, carte_subie))


def strat_cheat_median_allcards(etat: GameState) -> str:
    carte = _carte_actif(etat)
    if carte is None:
        return _safe_carac(choix_robot_aleatoire())
    return _safe_carac(choix_robot_intelligent_triche(carte, LISTE_ANIMAUX))


# Liste officielle
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

STRATEGIE_PAR_NOM: Dict[str, Strategie] = {s.nom: s for s in STRATEGIES}


# ============================================================
# ======================= GROUPES (IMPORTANT) =================
# ============================================================

PETITES_STRATS = {
    "Random",
    "FirstStat(poids)",
    "MeanRatio(hist)",  # tu peux le mettre en "grosse" si tu veux
}

GROSSES_STRATS = {
    "MedianRatio(hist)",
    "MonteCarlo_random",
    "MonteCarlo_median",
    "CheatAbsolute(see both)",
}


def est_grosse_strategie(strat: Strategie) -> bool:
    return strat.nom in GROSSES_STRATS


def est_petite_strategie(strat: Strategie) -> bool:
    return strat.nom in PETITES_STRATS


# ============================================================
# ======================= OUTILS STATS ========================
# ============================================================

def ic95_proportion(nb_succes: int, n: int) -> Tuple[float, float]:
    """
    Intervalle de confiance 95% (méthode de Wilson) pour une proportion p = nb_succes/n.
    Retour en proportions (0..1).

    Remarque : Wilson est en général plus fiable que l'approximation normale
    quand p est proche de 0% ou 100%.
    """
    if n <= 0:
        return 0.0, 1.0

    z = 1.96  # 95%
    p = nb_succes / n

    denom = 1.0 + (z * z) / n
    centre = (p + (z * z) / (2.0 * n)) / denom
    demi_largeur = (z / denom) * ((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n)) ** 0.5

    bas = max(0.0, centre - demi_largeur)
    haut = min(1.0, centre + demi_largeur)
    return bas, haut


def moyenne(liste: List[float]) -> float:
    return (sum(liste) / len(liste)) if liste else float("nan")


def ecart_type(liste: List[float]) -> float:
    if not liste:
        return float("nan")
    m = moyenne(liste)
    var = sum((x - m) ** 2 for x in liste) / len(liste)
    return var ** 0.5


# ============================================================
# ======================= EXPORT CSV ==========================
# ============================================================

def chemin_results_csv() -> Path:
    return Path("data") / "results.csv"


def ecrire_ligne_csv(res: Dict[str, object]) -> None:
    path = chemin_results_csv()
    path.parent.mkdir(parents=True, exist_ok=True)

    colonnes = [
        "mode",
        "A", "B",
        "n_games",
        "seed",
        "wins_A", "wins_B",
        "winrate_A_pct", "winrate_B_pct",
        "winrate_A_ci95_low_pct", "winrate_A_ci95_high_pct",
        "avg_rounds_overall",
        "avg_rounds_when_A_wins",
        "avg_rounds_when_B_wins",
        "n_timeouts",
        # mode répétitions :
        "n_repetitions",
        "winrate_A_mean_pct",
        "winrate_A_std_pct",
        "winrate_A_min_pct",
        "winrate_A_max_pct",
        "avg_rounds_overall_mean",
        "avg_rounds_overall_std",
    ]

    fichier_existe = path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
        if not fichier_existe:
            writer.writeheader()

        ligne = {c: res.get(c, "") for c in colonnes}
        writer.writerow(ligne)


# ============================================================
# ======================= GESTION DU HASARD ===================
# ============================================================

def _executer_avec_seed_globale(seed: int, fonction):
    """
    Le module cerveau.py utilise le hasard via le module random (global).
    Pour obtenir des résultats reproductibles et indépendants de l'ordre,
    on force random.seed(seed) uniquement pendant la partie,
    puis on restaure l'état précédent du hasard.
    """
    etat_hasard = random.getstate()
    try:
        random.seed(seed)
        return fonction()
    finally:
        random.setstate(etat_hasard)


# ============================================================
# ======================= SIMULATION CORE ======================
# ============================================================

def creer_partie_bot_vs_bot() -> GameState:
    """
    Crée une partie BotA vs BotB.
    Le joueur qui commence est tiré au hasard.
    """
    c1, c2 = distribuer_cartes(LISTE_ANIMAUX)
    j1 = Joueur("BotA", c1)
    j2 = Joueur("BotB", c2)
    etat = GameState(j1, j2, mode_robot=None)

    if random.random() < 0.5:
        etat.joueur_actif, etat.joueur_passif = etat.joueur_passif, etat.joueur_actif

    return etat


def jouer_une_partie(
    strat_a: Strategie,
    strat_b: Strategie,
    seed: int,
    max_manches: int = 5000
) -> Tuple[str, int]:
    """
    Joue UNE partie.
    Retourne (gagnant, nb_manches).
    gagnant ∈ {"BotA","BotB","TIMEOUT"}.
    """
    def _faire_partie():
        etat = creer_partie_bot_vs_bot()
        manches = 0

        while (not etat.terminee) and manches < max_manches:
            if etat.joueur_actif.nom == "BotA":
                carac = strat_a.choisir(etat)
            else:
                carac = strat_b.choisir(etat)

            carac = _safe_carac(carac)
            etat.appliquer_manche(carac)
            manches += 1

        if (not etat.terminee) or (etat.gagnant is None):
            return "TIMEOUT", manches

        return etat.gagnant.nom, manches

    return _executer_avec_seed_globale(seed, _faire_partie)


def _jouer_deux_parties_symetrisees(
    strat_a: Strategie,
    strat_b: Strategie,
    seed: int,
    max_manches: int = 5000
) -> Tuple[int, int, int]:
    """
    Comparaison équitable (technique "common random numbers") :
    - Partie 1 : A en BotA contre B en BotB avec seed = seed
    - Partie 2 : B en BotA contre A en BotB avec seed = seed
    On agrège les 2 résultats.

    Retour :
    - nb_victoires_A_sur_2
    - nb_manches_total_sur_2
    - nb_timeouts_sur_2
    """
    victoires_a = 0
    manches_total = 0
    timeouts = 0

    # Partie 1
    g1, m1 = jouer_une_partie(strat_a, strat_b, seed=seed, max_manches=max_manches)
    manches_total += m1
    if g1 == "TIMEOUT":
        timeouts += 1
    elif g1 == "BotA":
        victoires_a += 1  # ici BotA = stratégie A

    # Partie 2 (swap)
    g2, m2 = jouer_une_partie(strat_b, strat_a, seed=seed, max_manches=max_manches)
    manches_total += m2
    if g2 == "TIMEOUT":
        timeouts += 1
    else:
        # ici BotB = stratégie A
        if g2 == "BotB":
            victoires_a += 1

    return victoires_a, manches_total, timeouts


def comparer_deux_strategies(
    strat_a: Strategie,
    strat_b: Strategie,
    n_games: int,
    seed: int,
    print_every: int = 0,
    export_csv: bool = True,
    symetriser: bool = True,
    max_manches: int = 5000,
) -> Dict[str, object]:
    """
    UNE expérience :
    - symetriser=True (recommandé) : on joue 2 parties par seed (A/B puis B/A)
      => beaucoup plus robuste, et surtout indépendant de l'ordre.
    - symetriser=False : une seule partie par seed (ancien comportement).

    Les TIMEOUTS sont comptés et exclus du winrate.
    """
    victoires_a = 0
    victoires_b = 0
    manches_total = 0
    manches_quand_a_gagne: List[int] = []
    manches_quand_b_gagne: List[int] = []
    nb_timeouts = 0

    generateur = random.Random(seed)

    for k in range(1, n_games + 1):
        s = generateur.randrange(0, 2**31 - 1)

        if symetriser:
            va2, mt2, to2 = _jouer_deux_parties_symetrisees(
                strat_a, strat_b, seed=s, max_manches=max_manches
            )
            manches_total += mt2
            nb_timeouts += to2

            nb_valides = 2 - to2
            victoires_a += va2
            victoires_b += (nb_valides - va2)

            # Pour rester simple (Terminale), on ne calcule pas ici les manches
            # conditionnelles dans le mode symétrisé.
        else:
            gagnant, m = jouer_une_partie(strat_a, strat_b, seed=s, max_manches=max_manches)
            manches_total += m
            if gagnant == "TIMEOUT":
                nb_timeouts += 1
            elif gagnant == "BotA":
                victoires_a += 1
                manches_quand_a_gagne.append(m)
            else:
                victoires_b += 1
                manches_quand_b_gagne.append(m)

        if print_every > 0 and (k % print_every == 0):
            print("  Parties terminées:", k, "/", n_games)

    nb_total = (2 * n_games) if symetriser else n_games
    nb_valides = nb_total - nb_timeouts

    if nb_valides <= 0:
        winrate_a = float("nan")
        winrate_b = float("nan")
        bas, haut = 0.0, 1.0
    else:
        winrate_a = 100.0 * victoires_a / nb_valides
        winrate_b = 100.0 * victoires_b / nb_valides
        bas, haut = ic95_proportion(victoires_a, nb_valides)

    res = {
        "mode": "simple",
        "A": strat_a.nom,
        "B": strat_b.nom,
        "n_games": n_games,
        "seed": seed,

        "wins_A": victoires_a,
        "wins_B": victoires_b,
        "winrate_A_pct": winrate_a,
        "winrate_B_pct": winrate_b,
        "winrate_A_ci95_low_pct": 100.0 * bas,
        "winrate_A_ci95_high_pct": 100.0 * haut,

        "avg_rounds_overall": (manches_total / nb_total) if nb_total > 0 else float("nan"),
        "avg_rounds_when_A_wins": (sum(manches_quand_a_gagne) / len(manches_quand_a_gagne)) if manches_quand_a_gagne else "",
        "avg_rounds_when_B_wins": (sum(manches_quand_b_gagne) / len(manches_quand_b_gagne)) if manches_quand_b_gagne else "",
        "n_timeouts": nb_timeouts,
    }

    if export_csv:
        ecrire_ligne_csv(res)

    return res


def comparer_deux_strategies_repetitions(
    strat_a: Strategie,
    strat_b: Strategie,
    n_games: int,
    seed: int,
    n_repetitions: int,
    print_every: int = 0,
    export_csv: bool = True,
    symetriser: bool = True,
    max_manches: int = 5000,
) -> Dict[str, object]:
    """
    Analyse robuste (répétitions) :
    - On répète l'expérience plusieurs fois.
    - Chaque répétition utilise une seed différente.
    - On résume : moyenne / écart-type / min / max du winrate.
    """
    winrates: List[float] = []
    moyennes_manches: List[float] = []
    timeouts: List[int] = []

    for rep in range(n_repetitions):
        seed_locale = seed + 10000 * rep

        if print_every > 0:
            print("Répétition", rep + 1, "/", n_repetitions)

        res_rep = comparer_deux_strategies(
            strat_a, strat_b,
            n_games=n_games,
            seed=seed_locale,
            print_every=print_every,
            export_csv=False,
            symetriser=symetriser,
            max_manches=max_manches
        )

        try:
            winrates.append(float(res_rep["winrate_A_pct"]))
        except Exception:
            pass

        try:
            moyennes_manches.append(float(res_rep["avg_rounds_overall"]))
        except Exception:
            pass

        try:
            timeouts.append(int(res_rep.get("n_timeouts", 0)))
        except Exception:
            pass

    res = {
        "mode": "repetitions",
        "A": strat_a.nom,
        "B": strat_b.nom,
        "n_games": n_games,
        "seed": seed,

        "n_repetitions": n_repetitions,
        "winrate_A_mean_pct": moyenne(winrates),
        "winrate_A_std_pct": ecart_type(winrates),
        "winrate_A_min_pct": min(winrates) if winrates else float("nan"),
        "winrate_A_max_pct": max(winrates) if winrates else float("nan"),

        "avg_rounds_overall_mean": moyenne(moyennes_manches),
        "avg_rounds_overall_std": ecart_type(moyennes_manches),

        "n_timeouts": sum(timeouts) if timeouts else 0,
    }

    if export_csv:
        ecrire_ligne_csv(res)

    return res


# ============================================================
# ======================= AFFICHAGE ===========================
# ============================================================

def print_result(res: Dict[str, object]) -> None:
    mode = res.get("mode", "simple")

    if mode == "simple":
        A = res["A"]
        B = res["B"]
        n = res["n_games"]

        print("=" * 72)
        print(f"Match-up (simple):  A = {A}   vs   B = {B}   |   N = {n}")
        print("-" * 72)

        if isinstance(res.get("winrate_A_pct"), float):
            print(
                f"Winrate A: {res['winrate_A_pct']:.2f}%"
                f"   |   IC95 (Wilson): [{res['winrate_A_ci95_low_pct']:.2f}% ; {res['winrate_A_ci95_high_pct']:.2f}%]"
            )
            print(f"Winrate B: {res['winrate_B_pct']:.2f}%")
        else:
            print("Winrate: non disponible (trop de timeouts)")

        print("-" * 72)
        print(f"Avg rounds overall:         {res['avg_rounds_overall']:.2f}")
        if res.get("avg_rounds_when_A_wins") != "":
            print(f"Avg rounds when A wins:     {res['avg_rounds_when_A_wins']:.2f}")
        if res.get("avg_rounds_when_B_wins") != "":
            print(f"Avg rounds when B wins:     {res['avg_rounds_when_B_wins']:.2f}")

        print(f"Timeouts: {res.get('n_timeouts', 0)}")
        print("=" * 72)
        print()

    else:
        A = res["A"]
        B = res["B"]
        n = res["n_games"]
        k = res["n_repetitions"]

        print("=" * 72)
        print(f"Match-up (répétitions):  A = {A}   vs   B = {B}   |   N = {n}   |   K = {k}")
        print("-" * 72)
        print(f"Winrate A (moyenne): {res['winrate_A_mean_pct']:.2f}%")
        print(f"Winrate A (écart-type): {res['winrate_A_std_pct']:.2f}%")
        print(f"Winrate A (min..max): [{res['winrate_A_min_pct']:.2f}% ; {res['winrate_A_max_pct']:.2f}%]")
        print("-" * 72)
        print(f"Avg rounds overall (moyenne): {res['avg_rounds_overall_mean']:.2f}")
        print(f"Avg rounds overall (écart-type): {res['avg_rounds_overall_std']:.2f}")
        print(f"Timeouts (total): {res.get('n_timeouts', 0)}")
        print("=" * 72)
        print()


# ============================================================
# ======================= COMPARAISON ADAPTATIVE ==============
# ============================================================

def comparer_toutes_strategies_adaptatif(
    seed: int = 12345,
    n_games_petit: int = 80,
    n_games_gros: int = 250,
    n_repetitions_gros: int = 5,
    print_every_gros: int = 50,
    export_csv: bool = True,
) -> None:
    """
    Compare toutes les stratégies entre elles, effort adaptatif.

    Note : on utilise la comparaison symétrisée par défaut
    pour éviter les biais liés à l'ordre A/B.
    """
    for i in range(len(STRATEGIES)):
        for j in range(i + 1, len(STRATEGIES)):
            strat1 = STRATEGIES[i]
            strat2 = STRATEGIES[j]

            seed_locale = seed + 1000 * i + j

            strat1_grosse = est_grosse_strategie(strat1)
            strat2_grosse = est_grosse_strategie(strat2)

            if strat1_grosse and strat2_grosse:
                print(">>> GROS vs GROS :", strat1.nom, "vs", strat2.nom)
                res = comparer_deux_strategies_repetitions(
                    strat1, strat2,
                    n_games=n_games_gros,
                    seed=seed_locale,
                    n_repetitions=n_repetitions_gros,
                    print_every=print_every_gros,
                    export_csv=export_csv,
                    symetriser=True
                )
                print_result(res)
            else:
                res = comparer_deux_strategies(
                    strat1, strat2,
                    n_games=n_games_petit,
                    seed=seed_locale,
                    print_every=0,
                    export_csv=export_csv,
                    symetriser=True
                )
                print_result(res)


def run_stats() -> None:
    """
    Point d'entrée : python main.py stats
    """
    print("=== MODE STATS (sans pygame) ===")
    print("Stratégies disponibles:")
    for s in STRATEGIES:
        tag = ""
        if est_grosse_strategie(s):
            tag = " (GROSSE)"
        elif est_petite_strategie(s):
            tag = " (petite)"
        print(" -", s.nom + tag)
    print()

    SEED = 12345

    comparer_toutes_strategies_adaptatif(
        seed=SEED,
        n_games_petit=500,
        n_games_gros=400,
        n_repetitions_gros=6,
        print_every_gros=50,
        export_csv=True
    )


if __name__ == "__main__":
    run_stats()
