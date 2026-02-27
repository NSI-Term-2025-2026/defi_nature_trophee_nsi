# -*- coding: utf-8 -*-
"""
Cerveau du jeu Défi Nature.

Ce module ne doit JAMAIS importer pygame.
Il contient:
- Modèles: Animaux, Joueur, GameState
- IA: choix_robot_*
- Données: chargement CSV + fallback LISTE_ANIMAUX
- Factory: creer_partie()

But: permettre de simuler des parties (stats) sur un PC sans pygame.
"""

import random
import numpy as np

# AJOUT (cerveau / données) : CSV animaux
import csv
from pathlib import Path


# ============================================================
# ======================= CERVEAU DU JEU ======================
# ============================================================

class Animaux:
    """Carte Animal : nom + 3 caractéristiques. + lien du fichier image"""
    def __init__(self, nom, poids, longueur, longevite):
        self.nom = nom
        self.poids = poids
        self.longueur = longueur
        self.longevite = longevite
        self.path_image = "assets/images/animaux/" + self.nom + ".png"


class Joueur:
    """Joueur : nom + pile de cartes (la carte visible est la dernière)."""
    def __init__(self, nom, cartes):
        self.nom = nom
        self.cartes = cartes

    def carte_visible(self):
        # Sécurité : évite tout crash si le joueur n'a plus de cartes
        if not self.cartes:
            return None
        return self.cartes[-1]

    def enlever_carte(self):
        return self.cartes.pop()

    def ajouter_carte(self, carte):
        # Réinsertion aléatoire
        self.cartes.insert(random.randint(0, len(self.cartes)), carte)

    def est_vaincu(self):
        return len(self.cartes) == 0


def distribuer_cartes(liste):
    """Mélange puis distribue la moitié des cartes à chaque joueur."""
    cartes = liste.copy()
    random.shuffle(cartes)
    milieu = len(cartes) // 2
    return cartes[:milieu], cartes[milieu:]


def choix_robot_aleatoire():
    """Robot A : choix d'une caractéristique au hasard."""
    return random.choice(["poids", "longueur", "longevite"])

def choix_robot_aleatoire_premiere_caracteristique():
    """
    Robot Naif: Choix de la premiere caracteristique
    """
    return "poids"



def choix_robot_intelligent(carte, historique):
    """
    Robot I : compare sa carte à une valeur de référence (médiane) issue
    des cartes déjà jouées, et choisit la caractéristique la plus "forte" relativement.
    """
    if not historique:
        return choix_robot_aleatoire()

    poids_m = np.median([c.poids for c in historique])
    longueur_m = np.median([c.longueur for c in historique])
    longevite_m = np.median([c.longevite for c in historique])

    scores = {
        "poids": carte.poids / poids_m if poids_m > 0 else 0,
        "longueur": carte.longueur / longueur_m if longueur_m > 0 else 0,
        "longevite": carte.longevite / longevite_m if longevite_m > 0 else 0
    }
    return max(scores, key=scores.get)

def choix_robot_intelligent_moyenne(carte, historique):
    """
    Robot I : compare sa carte à une valeur de référence (médiane) issue
    des cartes déjà jouées, et choisit la caractéristique la plus "forte" relativement.
    """
    if not historique:
        return choix_robot_aleatoire()

    poids_m = np.mean([c.poids for c in historique])
    longueur_m = np.mean([c.longueur for c in historique])
    longevite_m = np.mean([c.longevite for c in historique])

    scores = {
        "poids": carte.poids / poids_m if poids_m > 0 else 0,
        "longueur": carte.longueur / longueur_m if longueur_m > 0 else 0,
        "longevite": carte.longevite / longevite_m if longevite_m > 0 else 0
    }
    return max(scores, key=scores.get)

def choix_robot_triche_absolue(carte_jouee,carte_subie):
    if carte_jouee.poids > carte_subie.poids:
        return 'poids'
    elif carte_jouee.longueur > carte_subie.longueur:
        return 'longueur'
    elif carte_jouee.longevite > carte_subie.longevite:
        return 'longevite'
    else:
        return choix_robot_aleatoire()

def choix_robot_intelligent_triche(carte, liste_cartes_totales):
    """
    Robot I : compare sa carte à une valeur de référence (médiane) issue
    des cartes déjà jouées, et choisit la caractéristique la plus "forte" relativement.
    """
    if not liste_cartes_totales:
        return choix_robot_aleatoire()

    poids_m = np.median([c.poids for c in liste_cartes_totales])
    longueur_m = np.median([c.longueur for c in liste_cartes_totales])
    longevite_m = np.median([c.longevite for c in liste_cartes_totales])

    scores = {
        "poids": carte.poids / poids_m if poids_m > 0 else 0,
        "longueur": carte.longueur / longueur_m if longueur_m > 0 else 0,
        "longevite": carte.longevite / longevite_m if longevite_m > 0 else 0
    }
    return max(scores, key=scores.get)

# ================= MONTE CARLO SIMPLE =================

def copie_partie_simple(game):
    j1 = Joueur(game.joueurs[0].nom, game.joueurs[0].cartes.copy())
    j2 = Joueur(game.joueurs[1].nom, game.joueurs[1].cartes.copy())

    nouvelle = GameState(j1, j2, mode_robot=None)

    if game.joueur_actif.nom == j1.nom:
        nouvelle.joueur_actif = nouvelle.joueurs[0]
        nouvelle.joueur_passif = nouvelle.joueurs[1]
    else:
        nouvelle.joueur_actif = nouvelle.joueurs[1]
        nouvelle.joueur_passif = nouvelle.joueurs[0]

    return nouvelle


def simuler_partie_aleatoire(game, max_tours=100):
    tours = 0
    while not game.terminee and tours < max_tours:
        carac = choix_robot_aleatoire()
        game.appliquer_manche(carac)
        tours += 1

    if game.gagnant:
        return game.gagnant.nom
    return None


def simuler_partie_median(game, max_tours=100):
    tours = 0
    while not game.terminee and tours < max_tours:
        carte = game.joueur_actif.carte_visible()
        if carte is None:
            return None
        carac = choix_robot_intelligent(carte, game.historique_cartes)
        game.appliquer_manche(carac)
        tours += 1

    if game.gagnant:
        return game.gagnant.nom
    return None


def choix_robot_monte_carlo_random(game, essais=15):
    caracs = ["poids", "longueur", "longevite"]
    nom_actif = game.joueur_actif.nom

    meilleur = "poids"
    meilleur_score = -1

    for carac in caracs:
        victoires = 0

        for i in range(essais):
            test = copie_partie_simple(game)
            test.appliquer_manche(carac)
            gagnant = simuler_partie_aleatoire(test)

            if gagnant == nom_actif:
                victoires += 1

        if victoires > meilleur_score:
            meilleur_score = victoires
            meilleur = carac

    return meilleur


def choix_robot_monte_carlo_median(game, essais=15):
    caracs = ["poids", "longueur", "longevite"]
    nom_actif = game.joueur_actif.nom

    meilleur = "poids"
    meilleur_score = -1

    for carac in caracs:
        victoires = 0

        for i in range(essais):
            test = copie_partie_simple(game)
            test.appliquer_manche(carac)
            gagnant = simuler_partie_median(test)

            if gagnant == nom_actif:
                victoires += 1

        if victoires > meilleur_score:
            meilleur_score = victoires
            meilleur = carac

    return meilleur


class GameState:
    """
    Moteur du jeu (aucun affichage ici).

    Règles :
    - Deux joueurs possèdent chacun un ensemble de cartes (Animal).
    - À chaque manche, le joueur actif choisit une caractéristique.
    - La valeur strictement la plus élevée gagne la manche.
    - En cas d'égalité, le joueur actif perd (règle strict >).
    - Le gagnant récupère la carte adverse et les cartes sont réinsérées aléatoirement.
    - La partie se termine lorsqu'un joueur n'a plus de cartes.

    Invariant :
    - Aucune carte ne doit être perdue ou dupliquée (vérification interne).
    """
    def __init__(self, joueur1, joueur2, mode_robot=None):
        self.joueurs = [joueur1, joueur2]
        self.joueur_actif = joueur1
        self.joueur_passif = joueur2

        # None (PVP), "A" (robot aléatoire), "I" (robot intelligent)
        self.mode_robot = mode_robot

        self.historique_cartes = []
        self.cartes_initiales = joueur1.cartes + joueur2.cartes

        self.terminee = False
        self.gagnant = None

        # infos de manche (pour UI)
        self.derniere_carac = None
        self.derniere_val_actif = None
        self.derniere_val_passif = None
        self.dernier_gagnant = None

        # AJOUT : historique des manches (moteur)
        # Chaque entrée: dict(actif, passif, carac, v_actif, v_passif, gagnant)
        self.historique_manches = []

    def actif_est_robot(self):
        return self.mode_robot is not None and self.joueur_actif.nom == "Robot"

    def appliquer_manche(self, caracteristique):
        if self.terminee:
            return

        carte_active = self.joueur_actif.carte_visible()
        carte_adverse = self.joueur_passif.carte_visible()

        # sécurité
        if carte_active is None or carte_adverse is None:
            return

        v1 = getattr(carte_active, caracteristique)
        v2 = getattr(carte_adverse, caracteristique)

        # règle : strictement supérieur pour gagner, sinon actif perd
        if v1 > v2:
            gagnant, perdant = self.joueur_actif, self.joueur_passif
        else:
            gagnant, perdant = self.joueur_passif, self.joueur_actif

        # transfert + réinsertion aléatoire
        carte_perdue = perdant.enlever_carte()
        gagnant.ajouter_carte(carte_perdue)

        carte_jouee = gagnant.enlever_carte()
        gagnant.ajouter_carte(carte_jouee)

        self.historique_cartes.extend([carte_active, carte_adverse])
        self._verifier_invariants()

        self.derniere_carac = caracteristique
        self.derniere_val_actif = v1
        self.derniere_val_passif = v2
        self.dernier_gagnant = gagnant

        # AJOUT : log de manche (avant le swap de tour)
        try:
            self.historique_manches.append({
                "actif": self.joueur_actif.nom,
                "passif": self.joueur_passif.nom,
                "carac": caracteristique,
                "v_actif": v1,
                "v_passif": v2,
                "gagnant": gagnant.nom
            })
        except Exception:
            pass

        if perdant.est_vaincu():
            self.terminee = True
            self.gagnant = gagnant
            return

        # on change le tour du joueur
        self.joueur_actif, self.joueur_passif = self.joueur_passif, self.joueur_actif

    def _verifier_invariants(self):
        toutes = []
        for j in self.joueurs:
            toutes.extend(j.cartes)

        assert len(toutes) == len(self.cartes_initiales), "ERREUR: nombre total de cartes a changé"
        assert len(set(id(c) for c in toutes)) == len(toutes), "ERREUR: duplication de cartes détectée"
        assert set(id(c) for c in toutes) == set(id(c) for c in self.cartes_initiales), (
            "ERREUR: carte disparue ou carte inconnue apparue"
        )


# -------------------------------------------------------------------
# AJOUT (cerveau / données) : chargement CSV robuste + fallback
# -------------------------------------------------------------------

def _trouver_racine_projet():
    """
    Retourne un Path de base pour retrouver /data même si on exécute depuis ailleurs.
    - si __file__ existe : dossier du script
    - sinon : dossier courant
    """
    try:
        return Path(__file__).resolve().parent
    except Exception:
        return Path.cwd()


def charger_animaux_csv(path_csv):
    """
    Charge des animaux depuis un CSV.
    - Supporte délimiteur ';' ou ',' (auto: essaie ';' puis ',').
    - Supporte en-tête: nom, poids, longueur, longevite.
    - Ignore les lignes invalides (robustesse).
    Retourne une liste (peut être vide si échec).
    """
    p = Path(path_csv)
    if not p.exists():
        return []

    try:
        contenu = p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    if not contenu:
        return []

    def _parse_with_delim(delim):
        animaux = []
        try:
            reader = csv.DictReader(contenu, delimiter=delim)
        except Exception:
            return []

        champs = set([c.strip().lower() for c in (reader.fieldnames or [])])
        attendus = {"nom", "poids", "longueur", "longevite"}
        if not attendus.issubset(champs):
            return []

        for row in reader:
            try:
                nom = (row.get("nom") or "").strip()
                if not nom:
                    continue
                poids = float(str(row.get("poids")).replace(",", "."))
                longueur = float(str(row.get("longueur")).replace(",", "."))
                longevite = float(str(row.get("longevite")).replace(",", "."))
                animaux.append(Animaux(nom, poids, longueur, longevite))
            except Exception:
                continue

        return animaux

    animaux = _parse_with_delim(";")
    if animaux:
        return animaux

    animaux = _parse_with_delim(",")
    return animaux


LISTE_ANIMAUX = [
    Animaux("aigle_royal", 4.8, 84, 25),
    Animaux("cobra_royal", 10, 400, 22),
    Animaux("corail_rouge", 2, 40, 60),
    Animaux("dragon_de_komodo", 165, 310, 53),
    Animaux("elephant_d_afrique", 5000, 600, 65),
    Animaux("lion_d_afrique", 189, 210, 18),
    Animaux("loup_rouge", 25, 110, 13),
    Animaux("merou_golfe", 90, 198, 48),
    Animaux("panda_geant", 97, 170, 22),
    Animaux("panda_roux", 5, 57, 10),
    Animaux("protee_anguillard", 0.02, 25, 69),
    Animaux("raie_manta", 1500, 550, 19),
    Animaux("requin_marteau_halicorne", 152, 330, 35),
    Animaux("tapir", 200, 212, 30),
    Animaux("tigre_de_siberie", 300, 230, 17),
    Animaux("tortue_verte", 175, 100, 70),
]

_RACINE = _trouver_racine_projet()
_CSV_PATH = _RACINE / "data" / "animaux.csv"
_animaux_csv = charger_animaux_csv(_CSV_PATH)
if _animaux_csv:
    print('csv trouve')
    LISTE_ANIMAUX = _animaux_csv


def creer_partie(mode, prenom="Humain"):
    c1, c2 = distribuer_cartes(LISTE_ANIMAUX)

    if mode == "PVP":
        j1 = Joueur("Joueur 1", c1)
        j2 = Joueur("Joueur 2", c2)
        return GameState(j1, j2, mode_robot=None)

    nom_humain = prenom.strip() if prenom.strip() else "Humain"

    if mode == "RA":
        humain = Joueur(nom_humain, c1)
        robot = Joueur("Robot", c2)
        return GameState(humain, robot, mode_robot="A")

    if mode == "RI":
        humain = Joueur(nom_humain, c1)
        robot = Joueur("Robot", c2)
        return GameState(humain, robot, mode_robot="I")

    raise ValueError("Mode inconnu")
