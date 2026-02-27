# -*- coding: utf-8 -*-
"""
UI Pygame du jeu Défi Nature.

- Ce fichier dépend de pygame.
- Toute la logique (règles, IA, données) vient de cerveau.py
"""

from cerveau import *
import pygame
import sys
import random
import numpy as np

pygame.init()


def run():
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
    # ========================== OPTIONS UI =======================
    # ============================================================

    # AJOUT : paramètres UI simples (menu Options)
    SETTINGS = {
        "show_opponent_card": False,  # debug : montre l'adversaire (carte visible)
        "volume": 0.8               # volume global [0.0, 1.0]
    }

    def clamp01(x):
        try:
            return max(0.0, min(1.0, float(x)))
        except Exception:
            return 0.8

    # ============================================================
    # =========================== SONS ============================
    # ============================================================

    pygame.mixer.init()

    def charger_son(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None

    S_CLICK = charger_son("assets/sounds/click.wav")
    S_VICTORY = charger_son("assets/sounds/victory.wav")

    def play(sound, volume=0.8):
        """
        volume attendu par pygame: float entre 0.0 et 1.0 :contentReference[oaicite:2]{index=2}
        Ici on applique un volume global SETTINGS["volume"].
        """
        if sound is None:
            return
        try:
            v = clamp01(volume) * clamp01(SETTINGS.get("volume", 0.8))
            sound.set_volume(v)
            sound.play()
        except Exception:
            pass

    victory_sound_played = False

    # ============================================================
    # ===================== MENU HAMBURGER ========================
    # ============================================================

    menu_ouvert = False

    # AJOUT : "Options"
    options = ["Rejouer", "Options", "Règles", "À propos", "Quitter"]
    bouton_menu = pygame.Rect(20, 22, 46, 46)
    option_rects = [pygame.Rect(20, 30 + i * 60, 140, 46) for i in range(len(options))]

    # Overlays
    afficher_regles = False
    afficher_apropos = False
    afficher_options = False

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
        "Fin : lorsqu'un joueur n'a plus de cartes.",
        "",
        "Raccourcis : 1=Poids  2=Longueur  3=Longévité"
    ]

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
        "Retrouvez notre projet sur github : https://github.com/AntoCheMaestro :)"
    ]

    # ============================================================
    # ========================= UTILITAIRES =======================
    # ============================================================

    def wrap_lines(text, font, max_width):
        """Utilitaires pour les textes du menu hamburger"""
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

    # ------------------------------------------------------------
    # Cache images cartes (robuste + performant)
    # ------------------------------------------------------------
    IMAGES_CACHE = {}

    def charger_image_carte(path, target_w, target_h):
        """
        Charge et redimensionne une image de carte pour tenir dans (target_w, target_h)
        en conservant le ratio. Retourne une Surface prête à blitter, ou None si échec.
        Cache interne par (path, target_w, target_h).
        """
        key = (path, target_w, target_h)
        if key in IMAGES_CACHE:
            return IMAGES_CACHE[key]

        try:
            img = pygame.image.load(path).convert_alpha()
            iw, ih = img.get_width(), img.get_height()
            if iw <= 0 or ih <= 0:
                IMAGES_CACHE[key] = None
                return None

            scale = min(target_w / iw, target_h / ih)
            new_w = max(1, int(iw * scale))
            new_h = max(1, int(ih * scale))
            img_scaled = pygame.transform.smoothscale(img, (new_w, new_h))

            IMAGES_CACHE[key] = img_scaled
            return img_scaled
        except Exception:
            IMAGES_CACHE[key] = None
            return None

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

    # -----------------------------
    # AJOUT : overlay Options
    # -----------------------------

    def layout_options_panel():
        panel = pygame.Rect(180, 140, LARGEUR - 360, HAUTEUR - 280)

        toggle_rect = pygame.Rect(panel.x + 30, panel.y + 90, panel.width - 60, 52)

        minus_rect = pygame.Rect(panel.x + 30, panel.y + 175, 52, 52)
        plus_rect  = pygame.Rect(panel.right - 82, panel.y + 175, 52, 52)
        bar_rect   = pygame.Rect(minus_rect.right + 16, panel.y + 187, panel.width - 60 - 52 - 52 - 32, 28)

        return panel, toggle_rect, minus_rect, plus_rect, bar_rect

    def draw_options_overlay():
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        fenetre.blit(overlay, (0, 0))

        panel, toggle_rect, minus_rect, plus_rect, bar_rect = layout_options_panel()

        pygame.draw.rect(fenetre, PANEL, panel, border_radius=16)
        pygame.draw.rect(fenetre, VERT_NATURE, panel, 3, border_radius=16)

        titre = police_menu.render("Options", True, BLANC)
        fenetre.blit(titre, (panel.x + 30, panel.y + 25))

        # Toggle carte adverse (debug)
        pygame.draw.rect(fenetre, FOND, toggle_rect, border_radius=12)
        label = "Afficher la carte adverse (debug)"
        val = "ON" if SETTINGS.get("show_opponent_card", True) else "OFF"
        t1 = police.render(label, True, BLANC)
        t2 = police.render(val, True, BOUTON_ACTIF)
        fenetre.blit(t1, (toggle_rect.x + 14, toggle_rect.y + 14))
        fenetre.blit(t2, (toggle_rect.right - t2.get_width() - 14, toggle_rect.y + 14))

        # Volume
        vol = clamp01(SETTINGS.get("volume", 0.8))
        vol_pct = int(round(vol * 100))

        tvol = police.render("Volume sons", True, BLANC)
        fenetre.blit(tvol, (panel.x + 30, panel.y + 140))

        pygame.draw.rect(fenetre, BOUTON, minus_rect, border_radius=12)
        pygame.draw.rect(fenetre, BOUTON, plus_rect, border_radius=12)
        fenetre.blit(police_menu.render("-", True, NOIR), (minus_rect.x + 18, minus_rect.y + 4))
        fenetre.blit(police_menu.render("+", True, NOIR), (plus_rect.x + 16, plus_rect.y + 2))

        pygame.draw.rect(fenetre, FOND, bar_rect, border_radius=10)
        fill_w = int(bar_rect.width * vol)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
        pygame.draw.rect(fenetre, BOUTON_ACTIF, fill_rect, border_radius=10)

        tv = police.render(f"{vol_pct} %", True, BLANC)
        fenetre.blit(tv, (bar_rect.centerx - tv.get_width() // 2, bar_rect.y - 2))

        hint = police_petite.render("Cliquez hors du panneau pour fermer", True, BOUTON_ACTIF)
        fenetre.blit(hint, (panel.x + 30, panel.bottom - 30))

        return panel, toggle_rect, minus_rect, plus_rect, bar_rect

    # -----------------------------
    # AJOUT : Historique (UI)
    # -----------------------------

    def draw_history_panel(surface, game_obj):
        """
        Affiche les 5 dernières manches dans frame_gauche (UI only).
        Données = game_obj.historique_manches (moteur).
        """
        if game_obj is None:
            return

        # boîte
        box = pygame.Rect(10, 18, GAUCHE_W - 20, (HAUTEUR - HAUT_H) - 36)
        pygame.draw.rect(surface, FOND, box, border_radius=12)
        pygame.draw.rect(surface, VERT_NATURE, box, 2, border_radius=12)

        titre = police_petite.render("Historique (5)", True, BLANC)
        surface.blit(titre, (box.x + 10, box.y + 10))

        # dernières entrées
        lignes = []
        hist = getattr(game_obj, "historique_manches", [])
        if hist:
            derniers = hist[-5:][::-1]  # plus récent en haut
            for h in derniers:
                car = h.get("carac", "")
                car_label = {"poids": "Pds", "longueur": "Lng", "longevite": "Vlv"}.get(car, car)
                a = h.get("actif", "?")
                p = h.get("passif", "?")
                va = h.get("v_actif", "?")
                vp = h.get("v_passif", "?")
                g = h.get("gagnant", "?")
                lignes.append(f"{a} vs {p}")
                lignes.append(f"{car_label}: {va} / {vp} -> {g}")
                lignes.append("")  # espace
        else:
            lignes = ["Aucune manche", "jouée pour", "l'instant."]

        # rendu (wrap)
        y = box.y + 38
        max_w = box.width - 20
        for l in lignes:
            if not l:
                y += 10
                continue
            for ll in wrap_lines(l, police_petite, max_w):
                surface.blit(police_petite.render(ll, True, BLANC), (box.x + 10, y))
                y += 18
            if y > box.bottom - 12:
                break

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
        victory_replay_rect.width, victory_replay_rect.height = 260, 60
        victory_quit_rect.width, victory_quit_rect.height = 260, 60

        victory_replay_rect.x = panel.centerx - victory_replay_rect.width // 2
        victory_replay_rect.y = panel.y + panel.height - 140

        victory_quit_rect.x = panel.centerx - victory_quit_rect.width // 2
        victory_quit_rect.y = panel.y + panel.height - 70
        return panel

    def start_round_animation():
        nonlocal ui_state, anim_start_ms, anim_winner_index
        ui_state = UI_ANIM
        anim_start_ms = pygame.time.get_ticks()
        if game is None or game.dernier_gagnant is None:
            anim_winner_index = None
            return
        anim_winner_index = 0 if game.dernier_gagnant is game.joueurs[0] else 1

    def ui_state_to_end():
        nonlocal ui_state
        ui_state = UI_END

    # Robot auto
    def robot_joue_si_besoin():
        nonlocal message_ui, ui_state, game

        if game is None:
            return

        if game.terminee:
            ui_state_to_end()
            return

        if ui_state == UI_PLAY and game.actif_est_robot():
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

    # Répétition clavier (prénom) :contentReference[oaicite:3]{index=3}
    pygame.key.set_repeat(350, 35)

    clock = pygame.time.Clock()
    running = True

    # ============================================================
    # ======================== DRAW CARD =========================
    # ============================================================

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
            name = police.render(joueur.nom, True, NOIR)
            surface.blit(name, (30, 28))
            surface.blit(police.render("Plus de cartes", True, NOIR), (30, 120))
            txt_count = police_petite.render(f"Cartes : {len(joueur.cartes)}", True, BLANC)
            surface.blit(txt_count, (20, surface.get_height() - 28))
            return

        # ---------------------------------------------------------
        # Affichage image : carte adverse éventuellement cachée
        # ---------------------------------------------------------
        cacher_adverse = False
        try:
            if game is not None and joueur is not game.joueur_actif and not SETTINGS.get("show_opponent_card", True):
                cacher_adverse = True
        except Exception:
            cacher_adverse = False

        if cacher_adverse:
            # dos de carte simple (aucun asset requis)
            pygame.draw.rect(surface, (180, 170, 150), zone_carte, border_radius=12)
            pygame.draw.rect(surface, NOIR, zone_carte, width=3, border_radius=12)
            txt1 = police.render("Carte cachée", True, NOIR)
            surface.blit(txt1, (zone_carte.centerx - txt1.get_width() // 2, zone_carte.centery - 15))
        else:
            img = charger_image_carte(carte.path_image, zone_carte.width, zone_carte.height)

            if img is not None:
                r = img.get_rect()
                r.center = zone_carte.center
                surface.blit(img, r.topleft)
            else:
                pygame.draw.rect(surface, CARTE_COL, zone_carte, border_radius=12)
                pygame.draw.rect(surface, NOIR, zone_carte, width=2, border_radius=12)
                surface.blit(police.render(joueur.nom, True, NOIR), (30, 28))
                surface.blit(police.render(carte.nom, True, NOIR), (30, 62))
                surface.blit(police.render("Image introuvable", True, NOIR), (30, 120))

        # Bandeau semi-transparent (SRCALPHA) :contentReference[oaicite:4]{index=4}
        bandeau = pygame.Surface((zone_carte.width, 30), pygame.SRCALPHA)
        bandeau.fill((0, 0, 0, 90))
        surface.blit(bandeau, (zone_carte.x, zone_carte.y))
        surface.blit(police_petite.render(joueur.nom, True, BLANC), (zone_carte.x + 10, zone_carte.y + 7))

        # Message debug uniquement sur la carte adverse quand elle est visible
        try:
            if (game is not None and joueur is not game.joueur_actif
                and SETTINGS.get("show_opponent_card", True)):
                dbg = police_petite.render("(Mode debug : en vrai on ne voit pas la carte)", True, BOUTON_ACTIF)
                dbg_bg = pygame.Surface((dbg.get_width() + 12, dbg.get_height() + 6), pygame.SRCALPHA)
                dbg_bg.fill((0, 0, 0, 140))
                surface.blit(dbg_bg, (zone_carte.x + 10, zone_carte.y + 36))
                surface.blit(dbg, (zone_carte.x + 16, zone_carte.y + 39))
        except Exception:
            pass

        # Indication du nombre de cartes : en bas (hors carte)
        txt_count = police_petite.render(f"Cartes : {len(joueur.cartes)}", True, BLANC)
        surface.blit(txt_count, (20, surface.get_height() - 28))

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
                    ui_state = UI_RESULT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # clavier : saisie prénom
            if ui_state == UI_START and event.type == pygame.KEYDOWN and prenom_actif and not afficher_regles and not afficher_apropos and not afficher_options:
                if event.key == pygame.K_BACKSPACE:
                    prenom = prenom[:-1]
                elif event.key == pygame.K_RETURN:
                    prenom_actif = False
                else:
                    if len(prenom) < 16 and event.unicode.isprintable():
                        if event.unicode.isalnum() or event.unicode in [" ", "-", "_"]:
                            prenom += event.unicode

            # AJOUT : raccourcis 1/2/3 en jeu (KEYDOWN) :contentReference[oaicite:5]{index=5}
            if event.type == pygame.KEYDOWN:
                if (ui_state == UI_PLAY and game is not None and not game.actif_est_robot()
                    and not game.terminee and not afficher_regles and not afficher_apropos and not afficher_options):

                    mapping = {
                        pygame.K_1: ("Poids", "poids"),
                        pygame.K_KP1: ("Poids", "poids"),
                        pygame.K_2: ("Longueur", "longueur"),
                        pygame.K_KP2: ("Longueur", "longueur"),
                        pygame.K_3: ("Longévité", "longevite"),
                        pygame.K_KP3: ("Longévité", "longevite"),
                    }
                    if event.key in mapping:
                        label, key = mapping[event.key]
                        play(S_CLICK, 0.7)

                        game.appliquer_manche(key)
                        message_ui = f"{label} : {game.derniere_val_actif} vs {game.derniere_val_passif} — {game.dernier_gagnant.nom} gagne"
                        start_round_animation()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Overlay règles / à propos
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

                # AJOUT : overlay options (interaction)
                if afficher_options:
                    panel, toggle_rect, minus_rect, plus_rect, bar_rect = layout_options_panel()

                    # clic hors panneau -> fermer
                    if not panel.collidepoint(x, y):
                        afficher_options = False
                        play(S_CLICK, 0.6)
                        continue

                    # clic dans panneau -> gérer boutons
                    if toggle_rect.collidepoint(x, y):
                        SETTINGS["show_opponent_card"] = not SETTINGS.get("show_opponent_card", True)
                        play(S_CLICK, 0.6)
                    elif minus_rect.collidepoint(x, y):
                        SETTINGS["volume"] = clamp01(SETTINGS.get("volume", 0.8) - 0.1)
                        play(S_CLICK, 0.6)
                    elif plus_rect.collidepoint(x, y):
                        SETTINGS["volume"] = clamp01(SETTINGS.get("volume", 0.8) + 0.1)
                        play(S_CLICK, 0.6)
                    else:
                        # clic ailleurs dans le panneau : rien
                        pass
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
                                elif opt == "Options":
                                    afficher_options = True
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
        else:
            # AJOUT : Historique (quand menu fermé) pour ne pas chevaucher
            if ui_state != UI_START and game is not None:
                draw_history_panel(frame_gauche, game)

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

            hint = police_petite.render("Menu ≡ : Rejouer / Options / Règles / À propos / Quitter", True, BLANC)
            fenetre.blit(hint, (box.x + 70, box.bottom - 30))

        else:
            # Jeu : cartes + boutons
            if game is not None:
                est_actif_j1 = (game.joueur_actif is game.joueurs[0])
                est_actif_j2 = (game.joueur_actif is game.joueurs[1])

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

        # ===================== OVERLAYS =====================
        if afficher_regles:
            draw_overlay_box("Règles du jeu", regles_texte)

        if afficher_apropos:
            draw_overlay_box("À propos / Robots", apropos_texte)

        if afficher_options:
            draw_options_overlay()

        # ===================== ECRAN VICTOIRE DEDIE =====================
        if ui_state == UI_END:
            nonlocal_victory_sound_played = False  # placeholder to keep structure
            # (On garde exactement la logique existante ci-dessous)
            if game is not None and game.terminee and (not victory_sound_played):
                play(S_VICTORY, 0.9)
                victory_sound_played = True

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

                j1, j2 = game.joueurs[0], game.joueurs[1]
                s1 = police.render(f"{j1.nom} : {len(j1.cartes)} cartes", True, BLANC)
                s2 = police.render(f"{j2.nom} : {len(j2.cartes)} cartes", True, BLANC)
                fenetre.blit(s1, (panel.x + 30, panel.y + 125))
                fenetre.blit(s2, (panel.x + 30, panel.y + 155))
            else:
                tmsg = police.render("Partie terminée", True, BOUTON_ACTIF)
                fenetre.blit(tmsg, (panel.x + 30, panel.y + 80))

            dessiner_bouton(fenetre, victory_replay_rect, "Rejouer", actif=True)
            dessiner_bouton(fenetre, victory_quit_rect, "Quitter", actif=False)

            hint = police_petite.render("Astuce : Menu ≡ fonctionne aussi", True, BLANC)
            fenetre.blit(hint, (panel.x + 30, panel.bottom - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
