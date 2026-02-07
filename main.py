# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 10:54:10 2026

@author: Antonin

Architecture :
- Le "cerveau" (règles) est séparé de l'interface Pygame.
- L'UI affiche l'état du jeu et traduit les clics en actions.
- Cela rend le projet plus robuste et facile à faire évoluer (sons, animations, etc.).
"""

import pygame
import sys
import random
import numpy as np

pygame.init()

# ============================================================
# ======================= CERVEAU DU JEU ======================
# ============================================================

class Animaux:
    """Carte Animal : nom + 3 caractéristiques."""
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


# ============================================================
# ======================= PYGAME / UI =========================
# ============================================================

# Fenêtre 
LARGEUR, HAUTEUR = 900, 600
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Défi Nature")

# Couleurs 
FOND = (30, 34, 40)
PANEL = (42, 47, 54)
VERT_NATURE = (58, 125, 90)
CARTE_COL = (230, 216, 181)
BOUTON = (220, 220, 220)
BOUTON_ACTIF = (242, 201, 76)
BLANC = (245, 245, 245)
NOIR = (26, 26, 26)

# Polices
police_titre = pygame.font.SysFont("arial", 44, bold=True)
police = pygame.font.SysFont("arial", 22)
police_menu = pygame.font.SysFont("arial", 30, bold=True)
police_petite = pygame.font.SysFont("arial", 16)

# Dimensions layout
HAUT_H = 90
GAUCHE_W = 180

# Surfaces 
frame_haut = pygame.Surface((LARGEUR, HAUT_H))
frame_gauche = pygame.Surface((GAUCHE_W, HAUTEUR - HAUT_H))
frame_jeu = pygame.Surface((LARGEUR - GAUCHE_W, HAUTEUR - HAUT_H))

# Deux zones joueurs dans frame_jeu
frame_j1 = pygame.Surface(((frame_jeu.get_width() - 20) // 2, frame_jeu.get_height() - 150))
frame_j2 = pygame.Surface(((frame_jeu.get_width() - 20) // 2, frame_jeu.get_height() - 150))

# ============================================================
# =========================== SONS ============================
# ============================================================

# Sons attendus dans le même dossier que main.py :
# - click.wav
# - win_round.wav
# - lose_round.wav
# - victory.wav

# initialisation du module de pygame permettant de gerer les sons
pygame.mixer.init() 

def charger_son(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

S_CLICK = charger_son("assets/sounds/click.wav")
S_VICTORY = charger_son("assets/sounds/victory.wav")

def play(sound, volume=0.8):
    if sound is None:
        return
    try:
        sound.set_volume(volume)
        sound.play()
    except Exception:
        pass

victory_sound_played = False

# ============================================================
# ===================== MENU HAMBURGER ========================
# ============================================================

menu_ouvert = False
options = ["Rejouer", "Règles", "À propos", "Quitter"]
bouton_menu = pygame.Rect(20, 22, 46, 46)
option_rects = [pygame.Rect(20, 30 + i * 60, 140, 46) for i in range(len(options))]

# Zone carte (dans frame_j1/j2)
zone_carte = pygame.Rect(20, 20, frame_j1.get_width() - 40, frame_j1.get_height() - 40)

# Boutons caractéristiques (dans frame_jeu)
caracteristiques = [("Poids", "poids"), ("Longueur", "longueur"), ("Longévité", "longevite")]
boutons_carac = []
BTN_W, BTN_H = 170, 46

# Bandeau tour (dans frame_jeu)
tour_bar_rect = pygame.Rect(20, frame_jeu.get_height() - 120, frame_jeu.get_width() - 40, 34)

# Boutons en bas
y_btn = frame_jeu.get_height() - 75
x0 = 80
gap = 30
for i, (label, key) in enumerate(caracteristiques):
    x = x0 + i * (BTN_W + gap)
    boutons_carac.append((label, key, pygame.Rect(x, y_btn, BTN_W, BTN_H)))

# Règles (overlay)
regles_texte = [
    "Modes : Joueur vs Joueur / Joueur vs Robot.",
    "",
    "Chaque carte représente un animal avec :",
    "- Poids",
    "- Longueur",
    "- Longévité",
    "",
    "Distribution : cartes mélangées puis partagées.",
    "Carte jouée = dernière carte du tas.",
    "",
    "Le joueur actif choisit une caractéristique.",
    "La valeur la plus élevée gagne la manche.",
    "",
    "Important : en cas d'égalité, le joueur actif perd.",
    "",
    "Le gagnant récupère la carte adverse.",
    "Les cartes sont réinsérées aléatoirement.",
    "",
    "Fin : lorsqu'un joueur n'a plus de cartes."
]
afficher_regles = False

# À propos (overlay)
apropos_texte = [
    "À propos du projet",
    "",
    "Défi Nature – Projet NSI",
    "Langage : Python",
    "Interface : Pygame",
    "",
    "Organisation :",
    "- Un moteur de jeu (règles, joueurs, robots) indépendant",
    "- Une interface (affichage, clics, animations)",
    "",
    "Robots :",
    "Robot aléatoire : choisit une caractéristique au hasard.",
    "Robot intelligent : observe les cartes jouées, calcule une médiane",
    "et choisit la caractéristique la plus avantageuse.",
    "",
    "Évolutions possibles : sons, musiques, nouvelles cartes, etc."
]
afficher_apropos = False

# ============================================================
# ========================= UTILITAIRES =======================
# ============================================================

def wrap_lines(text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_card(surface, joueur, est_actif, highlight=False):
    # base
    pygame.draw.rect(surface, CARTE_COL, zone_carte, border_radius=12)

    # bordure actif / highlight animation
    if highlight:
        pygame.draw.rect(surface, BOUTON_ACTIF, zone_carte, width=8, border_radius=12)
    elif est_actif:
        pygame.draw.rect(surface, BOUTON_ACTIF, zone_carte, width=4, border_radius=12)

    carte = joueur.carte_visible()
    if carte is None:
        surface.blit(police.render(joueur.nom, True, NOIR), (30, 28))
        surface.blit(police.render("Plus de cartes", True, NOIR), (30, 120))
        surface.blit(police.render(f"Cartes : {len(joueur.cartes)}", True, NOIR), (30, 235))
        return

    surface.blit(police.render(joueur.nom, True, NOIR), (30, 28))
    surface.blit(police.render(carte.nom, True, NOIR), (30, 62))

    surface.blit(police.render(f"Poids : {carte.poids}", True, NOIR), (30, 120))
    surface.blit(police.render(f"Longueur : {carte.longueur}", True, NOIR), (30, 152))
    surface.blit(police.render(f"Longévité : {carte.longevite}", True, NOIR), (30, 184))

    surface.blit(police.render(f"Cartes : {len(joueur.cartes)}", True, NOIR), (30, 235))


def dessiner_bouton(surface, rect, texte, actif=True):
    couleur = BOUTON_ACTIF if actif else BOUTON
    pygame.draw.rect(surface, couleur, rect, border_radius=12)
    t = police.render(texte, True, NOIR)
    surface.blit(t, (rect.x + 18, rect.y + 16))


def draw_overlay_box(title, lines):
    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    fenetre.blit(overlay, (0, 0))

    box = pygame.Rect(120, 90, LARGEUR - 240, HAUTEUR - 180)
    pygame.draw.rect(fenetre, PANEL, box, border_radius=14)
    pygame.draw.rect(fenetre, VERT_NATURE, box, 3, border_radius=14)

    titre = police_menu.render(title, True, BLANC)
    fenetre.blit(titre, (box.x + 30, box.y + 20))

    max_w = box.width - 60
    y_text = box.y + 75
    line_h = 20
    font_rules = police

    lignes = []
    for l in lines:
        if not l.strip():
            lignes.append("")
        elif l.startswith("- "):
            for ll in wrap_lines(l, font_rules, max_w):
                lignes.append("  " + ll)
        else:
            lignes.extend(wrap_lines(l, font_rules, max_w))

    max_lines = (box.height - 120) // line_h
    if len(lignes) > max_lines:
        font_rules = pygame.font.SysFont("arial", 18)
        line_h = 18
        lignes = []
        for l in lines:
            if not l.strip():
                lignes.append("")
            elif l.startswith("- "):
                for ll in wrap_lines(l, font_rules, max_w):
                    lignes.append("  " + ll)
            else:
                lignes.extend(wrap_lines(l, font_rules, max_w))

    max_lines = (box.height - 120) // line_h
    for l in lignes[:max_lines]:
        fenetre.blit(font_rules.render(l, True, BLANC), (box.x + 30, y_text))
        y_text += line_h

    fermer = police_petite.render("Cliquez dans la fenêtre pour fermer", True, BOUTON_ACTIF)
    fenetre.blit(fermer, (box.x + 30, box.bottom - 35))

    return box

# ============================================================
# ========================= ETATS UI ==========================
# ============================================================

UI_START = "START"
UI_PLAY = "PLAY"
UI_ANIM = "ANIM"      # animation fin de manche
UI_RESULT = "RESULT"  # résultat + clic pour continuer
UI_END = "END"        # écran victoire dédié

ui_state = UI_START
game = None
message_ui = ""

# Animation fin de manche
anim_start_ms = 0
ANIM_DUREE_MS = 700
anim_winner_index = None  # 0 ou 1 (joueur gagnant de la manche)

# Écran start : prénom + modes
prenom = ""
prenom_actif = True
input_rect = pygame.Rect(0, 0, 320, 50)
clear_rect = pygame.Rect(0, 0, 46, 50)
start_buttons = []

# Boutons écran de victoire (Rejouer direct + Quitter)
victory_replay_rect = pygame.Rect(0, 0, 260, 60)
victory_quit_rect = pygame.Rect(0, 0, 260, 60)

def layout_start():
    box = pygame.Rect(GAUCHE_W + 40, HAUT_H + 30, LARGEUR - GAUCHE_W - 80, HAUTEUR - HAUT_H - 60)

    input_rect.width, input_rect.height = 320, 50
    input_rect.x = box.x + 70
    input_rect.y = box.y + 85

    clear_rect.x = input_rect.right + 12
    clear_rect.y = input_rect.y
    clear_rect.width, clear_rect.height = 46, 50

    start_buttons.clear()
    bw, bh = 360, 58
    bx = box.x + 70
    by = input_rect.y + 85
    start_buttons.extend([
        ("Joueur vs Joueur", "PVP", pygame.Rect(bx, by, bw, bh)),
        ("Vs Robot aléatoire", "RA", pygame.Rect(bx, by + 75, bw, bh)),
        ("Vs Robot intelligent", "RI", pygame.Rect(bx, by + 150, bw, bh)),
    ])
    return box

def layout_victory_panel():
    panel = pygame.Rect(GAUCHE_W + 110, HAUT_H + 90, LARGEUR - GAUCHE_W - 220, HAUTEUR - HAUT_H - 180)
    # boutons centrés dans panel
    victory_replay_rect.width, victory_replay_rect.height = 260, 60
    victory_quit_rect.width, victory_quit_rect.height = 260, 60

    victory_replay_rect.x = panel.centerx - victory_replay_rect.width // 2
    victory_replay_rect.y = panel.y + panel.height - 140

    victory_quit_rect.x = panel.centerx - victory_quit_rect.width // 2
    victory_quit_rect.y = panel.y + panel.height - 70
    return panel

def start_round_animation():
    global ui_state, anim_start_ms, anim_winner_index
    ui_state = UI_ANIM
    anim_start_ms = pygame.time.get_ticks()
    if game is None or game.dernier_gagnant is None:
        anim_winner_index = None
        return
    anim_winner_index = 0 if game.dernier_gagnant is game.joueurs[0] else 1

def ui_state_to_end():
    global ui_state
    ui_state = UI_END

# Robot auto
def robot_joue_si_besoin():
    global message_ui

    if game is None:
        return

    # si déjà finie, on va au END (écran victoire dédié)
    if game.terminee:
        ui_state_to_end()
        return

    if ui_state == UI_PLAY and game.actif_est_robot():
        # clic "virtuel" -> petit feedback
        play(S_CLICK, 0.6)

        carte = game.joueur_actif.carte_visible()
        if carte is None:
            ui_state_to_end()
            return

        if game.mode_robot == "A":
            car = choix_robot_aleatoire()
        else:
            car = choix_robot_intelligent(carte, game.historique_cartes)

        game.appliquer_manche(car)

        label = {"poids": "Poids", "longueur": "Longueur", "longevite": "Longévité"}[car]
        message_ui = f"{label} : {game.derniere_val_actif} vs {game.derniere_val_passif} — {game.dernier_gagnant.nom} gagne"


        start_round_animation()

# Répétition clavier (prénom)
pygame.key.set_repeat(350, 35)

clock = pygame.time.Clock()
running = True

# ============================================================
# ============================ BOUCLE =========================
# ============================================================

while running:
    # robot joue automatiquement si besoin
    robot_joue_si_besoin()

    # fin animation -> basculer vers RESULT ou END
    if ui_state == UI_ANIM:
        if pygame.time.get_ticks() - anim_start_ms >= ANIM_DUREE_MS:
            if game is not None and game.terminee:
                ui_state_to_end()
            else:
                ui_state = UI_RESULT  # on garde le clic pour continuer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # clavier : saisie prénom
        if ui_state == UI_START and event.type == pygame.KEYDOWN and prenom_actif and not afficher_regles and not afficher_apropos:
            if event.key == pygame.K_BACKSPACE:
                prenom = prenom[:-1]
            elif event.key == pygame.K_RETURN:
                prenom_actif = False
            else:
                if len(prenom) < 16 and event.unicode.isprintable():
                    if event.unicode.isalnum() or event.unicode in [" ", "-", "_"]:
                        prenom += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos

            # Overlay règles / à propos : clic pour fermer
            if afficher_regles:
                if 120 <= x <= LARGEUR - 120 and 90 <= y <= HAUTEUR - 90:
                    afficher_regles = False
                    play(S_CLICK, 0.6)
                continue
            if afficher_apropos:
                if 120 <= x <= LARGEUR - 120 and 90 <= y <= HAUTEUR - 90:
                    afficher_apropos = False
                    play(S_CLICK, 0.6)
                continue

            # hamburger
            if bouton_menu.collidepoint(x, y):
                menu_ouvert = not menu_ouvert
                play(S_CLICK, 0.6)

            # menu options (gauche)
            if menu_ouvert:
                lx, ly = x, y - HAUT_H
                if 0 <= lx <= GAUCHE_W and 0 <= ly <= (HAUTEUR - HAUT_H):
                    for i, rect in enumerate(option_rects):
                        if rect.collidepoint(lx, ly):
                            opt = options[i]
                            play(S_CLICK, 0.6)

                            if opt == "Quitter":
                                running = False
                            elif opt == "Règles":
                                afficher_regles = True
                            elif opt == "À propos":
                                afficher_apropos = True
                            elif opt == "Rejouer":
                                ui_state = UI_START
                                game = None
                                message_ui = ""
                                menu_ouvert = False
                                prenom_actif = True
                                victory_sound_played = False
                            menu_ouvert = False

            # START : clic champ / clear / mode
            if ui_state == UI_START:
                box = layout_start()

                if input_rect.collidepoint(x, y):
                    prenom_actif = True
                    play(S_CLICK, 0.6)
                elif clear_rect.collidepoint(x, y):
                    prenom = ""
                    prenom_actif = True
                    play(S_CLICK, 0.6)

                for label, mode, rect in start_buttons:
                    if rect.collidepoint(x, y):
                        play(S_CLICK, 0.7)
                        game = creer_partie(mode, prenom=prenom)
                        ui_state = UI_PLAY
                        message_ui = ""
                        menu_ouvert = False
                        victory_sound_played = False
                        break

            # RESULT : clic pour continuer
            elif ui_state == UI_RESULT:
                ui_state = UI_PLAY
                message_ui = ""
                play(S_CLICK, 0.6)

            # ANIM : on ignore les clics (anti-spam)
            elif ui_state == UI_ANIM:
                pass

            # END : écran victoire dédié avec boutons directs
            elif ui_state == UI_END:
                panel = layout_victory_panel()
                if victory_replay_rect.collidepoint(x, y):
                    play(S_CLICK, 0.7)
                    ui_state = UI_START
                    game = None
                    message_ui = ""
                    menu_ouvert = False
                    prenom_actif = True
                    victory_sound_played = False
                elif victory_quit_rect.collidepoint(x, y):
                    play(S_CLICK, 0.6)
                    running = False

            # PLAY : clic carac si humain actif
            elif ui_state == UI_PLAY and game is not None and not game.actif_est_robot() and not game.terminee:
                local_x = x - GAUCHE_W
                local_y = y - HAUT_H
                for label, key, rect in boutons_carac:
                    if rect.collidepoint(local_x, local_y):
                        play(S_CLICK, 0.7)

                        actif_avant = game.joueur_actif
                        game.appliquer_manche(key)

                        message_ui = f"{label} : {game.derniere_val_actif} vs {game.derniere_val_passif} — {game.dernier_gagnant.nom} gagne"



                        start_round_animation()
                        break

    # ============================================================
    # ========================= AFFICHAGE =========================
    # ============================================================

    fenetre.fill(FOND)

    frame_haut.fill(VERT_NATURE)
    frame_gauche.fill(PANEL)
    frame_jeu.fill(PANEL)
    frame_j1.fill(PANEL)
    frame_j2.fill(PANEL)

    # Titre
    texte_titre = police_titre.render("Défi Nature", True, BLANC)
    frame_haut.blit(texte_titre, (LARGEUR // 2 - texte_titre.get_width() // 2, 20))

    # Hamburger
    pygame.draw.rect(frame_haut, PANEL, bouton_menu, border_radius=8)
    icone = police_menu.render("≡" if not menu_ouvert else "×", True, BLANC)
    frame_haut.blit(icone, (bouton_menu.x + 13, bouton_menu.y + 4))

    # Menu gauche
    if menu_ouvert:
        for i, rect in enumerate(option_rects):
            pygame.draw.rect(frame_gauche, FOND, rect, border_radius=10)
            txt = police.render(options[i], True, BLANC)
            frame_gauche.blit(txt, (rect.x + 18, rect.y + 12))

    # START
    if ui_state == UI_START:
        box = layout_start()

        fenetre.blit(frame_haut, (0, 0))
        fenetre.blit(frame_gauche, (0, HAUT_H))
        fenetre.blit(frame_jeu, (GAUCHE_W, HAUT_H))

        pygame.draw.rect(fenetre, PANEL, box, border_radius=16)
        pygame.draw.rect(fenetre, VERT_NATURE, box, width=3, border_radius=16)

        titre = police_menu.render("Choisis un mode", True, BLANC)
        fenetre.blit(titre, (box.x + 70, box.y + 25))

        lab = police.render("Ton prénom :", True, BLANC)
        fenetre.blit(lab, (input_rect.x, input_rect.y - 30))

        pygame.draw.rect(fenetre, CARTE_COL, input_rect, border_radius=12)
        pygame.draw.rect(
            fenetre,
            BOUTON_ACTIF if prenom_actif else VERT_NATURE,
            input_rect,
            width=2,
            border_radius=12
        )
        fenetre.blit(police.render(prenom, True, NOIR), (input_rect.x + 12, input_rect.y + 12))

        pygame.draw.rect(fenetre, BOUTON, clear_rect, border_radius=12)
        fenetre.blit(police_menu.render("×", True, NOIR), (clear_rect.x + 14, clear_rect.y + 4))

        for label, mode, rect in start_buttons:
            dessiner_bouton(fenetre, rect, label, actif=True)

        hint = police_petite.render("Menu ≡ : Rejouer / Règles / À propos / Quitter", True, BLANC)
        fenetre.blit(hint, (box.x + 70, box.bottom - 30))

    else:
        # Jeu : cartes + boutons
        if game is not None:
            est_actif_j1 = (game.joueur_actif is game.joueurs[0])
            est_actif_j2 = (game.joueur_actif is game.joueurs[1])

            # highlight animation: bordure forte sur le gagnant de la manche
            highlight_j1 = (ui_state == UI_ANIM and anim_winner_index == 0)
            highlight_j2 = (ui_state == UI_ANIM and anim_winner_index == 1)

            draw_card(frame_j1, game.joueurs[0], est_actif_j1, highlight=highlight_j1)
            draw_card(frame_j2, game.joueurs[1], est_actif_j2, highlight=highlight_j2)

            frame_jeu.blit(frame_j1, (0, 0))
            frame_jeu.blit(frame_j2, (frame_j1.get_width() + 20, 0))

            # Bandeau tour
            pygame.draw.rect(frame_jeu, FOND, tour_bar_rect, border_radius=12)
            info = f"Tour de : {game.joueur_actif.nom}"
            if game.actif_est_robot():
                info += " (Robot)"
            txt_info = police.render(info, True, BLANC)
            frame_jeu.blit(txt_info, (tour_bar_rect.x + 14, tour_bar_rect.y + 6))

            # Boutons carac : désactivés pendant ANIM/RESULT/END ou robot
            boutons_actifs = (ui_state == UI_PLAY and not game.actif_est_robot() and not game.terminee)
            for label, key, rect in boutons_carac:
                couleur = BOUTON_ACTIF if boutons_actifs else BOUTON
                pygame.draw.rect(frame_jeu, couleur, rect, border_radius=10)
                t = police.render(label, True, NOIR)
                frame_jeu.blit(t, (rect.x + 20, rect.y + 12))

            # Message
            if message_ui:
                txt_msg = police_petite.render(message_ui, True, BLANC)
                frame_jeu.blit(txt_msg, (20, frame_jeu.get_height() - 20))

            if ui_state == UI_RESULT:
                txt = police_petite.render("Clique pour continuer…", True, BOUTON_ACTIF)
                frame_jeu.blit(txt, (frame_jeu.get_width() - 210, frame_jeu.get_height() - 20))

        # blit principal
        fenetre.blit(frame_haut, (0, 0))
        fenetre.blit(frame_gauche, (0, HAUT_H))
        fenetre.blit(frame_jeu, (GAUCHE_W, HAUT_H))

    # ===================== OVERLAY RÈGLES =====================
    if afficher_regles:
        draw_overlay_box("Règles du jeu", regles_texte)

    # ===================== OVERLAY À PROPOS ===================
    if afficher_apropos:
        draw_overlay_box("À propos / Robots", apropos_texte)

    # ===================== ECRAN VICTOIRE DEDIE =====================
    if ui_state == UI_END:
        # jouer le son de victoire une seule fois
        if game is not None and game.terminee and (not victory_sound_played):
            play(S_VICTORY, 0.9)
            victory_sound_played = True

        # overlay sombre
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        fenetre.blit(overlay, (0, 0))

        panel = layout_victory_panel()
        pygame.draw.rect(fenetre, PANEL, panel, border_radius=18)
        pygame.draw.rect(fenetre, VERT_NATURE, panel, 3, border_radius=18)

        titre = police_menu.render("Victoire !", True, BLANC)
        fenetre.blit(titre, (panel.x + 30, panel.y + 25))

        if game is not None and game.gagnant is not None:
            msg = f"🏆 {game.gagnant.nom} a gagné la partie"
            tmsg = police.render(msg, True, BOUTON_ACTIF)
            fenetre.blit(tmsg, (panel.x + 30, panel.y + 80))

            # stats simples
            j1, j2 = game.joueurs[0], game.joueurs[1]
            s1 = police.render(f"{j1.nom} : {len(j1.cartes)} cartes", True, BLANC)
            s2 = police.render(f"{j2.nom} : {len(j2.cartes)} cartes", True, BLANC)
            fenetre.blit(s1, (panel.x + 30, panel.y + 125))
            fenetre.blit(s2, (panel.x + 30, panel.y + 155))
        else:
            tmsg = police.render("Partie terminée", True, BOUTON_ACTIF)
            fenetre.blit(tmsg, (panel.x + 30, panel.y + 80))

        # Boutons directs
        dessiner_bouton(fenetre, victory_replay_rect, "Rejouer", actif=True)
        dessiner_bouton(fenetre, victory_quit_rect, "Quitter", actif=False)

        hint = police_petite.render("Astuce : Menu ≡ fonctionne aussi", True, BLANC)
        fenetre.blit(hint, (panel.x + 30, panel.bottom - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
