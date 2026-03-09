# Présentation du projet

## Présentation globale

### Contexte de réalisation
Ce projet a été réalisé en spécialité NSI, avec l’objectif de transformer un jeu de cartes connu en application numérique jouable. Nous voulions développer une solution complète, pas seulement un prototype : logique de jeu, interface graphique, adversaire robot et module d’analyse statistique.

### Naissance de l’idée
L’idée est née pendant les échanges de groupe : nous cherchions un projet à la fois ludique et utile pour montrer des compétences variées en NSI. Le jeu « Défis Nature » nous a paru idéal, car il combine des règles accessibles, des comparaisons de données et des choix stratégiques.

### Problématique initiale
Comment recréer fidèlement un jeu de comparaison de cartes en Python, tout en proposant :
- une interface claire pour des joueurs débutants ;
- plusieurs modes de jeu (humain contre humain et humain contre robot) ;
- une IA qui prenne des décisions cohérentes ;
- une architecture de code suffisamment propre pour évoluer.

### Objectifs de la solution proposée
- **Objectif 1 : Jouabilité** — proposer une version stable et agréable à utiliser.
- **Objectif 2 : Intérêt algorithmique** — implémenter différentes stratégies de robot et les comparer.
- **Objectif 3 : Qualité logicielle** — séparer moteur, interface et statistiques.
- **Objectif 4 : Utilité pédagogique** — montrer la modélisation d’un problème concret en NSI.

## Présentation de l'équipe

### Présentation de l’équipe
Notre équipe est composée de trois élèves : Antonin, Alexi et Léo. Nous avons travaillé de manière complémentaire, avec des points de synchronisation réguliers pour éviter les blocages.

### Rôle de chacun et répartition des tâches
- **Antonin (développeur lead)**
  - développement du moteur de jeu (`Animaux`, `Joueur`, `GameState`) ;
  - implémentation des stratégies de robot (aléatoire, heuristique, Monte Carlo) ;
  - intégration des modules et suivi technique global.
- **Alexi (UI/UX)**
  - création de l’interface Pygame ;
  - mise en place des boutons, menus, zones visuelles et réglages ergonomiques ;
  - intégration des effets sonores.
- **Léo (intégration, données, tests, documentation)**
  - analyse des règles du jeu et préparation des cartes, gestion des ressources graphiques ;
  - mise en place de la modularité entre `main.py`, `cerveau.py`, `game_pygame.py`, `stats.py`  ;
  - bêta-tests, retours qualité et contribution à la documentation.

### Temps passé sur le projet
Le projet représente environ 15 séances de travail en classe, auxquelles s’ajoutent des sessions hors cours (débogage, corrections, rédaction et finalisation du dépôt).

## Étapes du projet

### Étape 1 : Fondations en mode texte
Nous avons commencé par une version console pour vérifier la logique des manches, la comparaison des caractéristiques et les conditions de fin de partie.

### Étape 2 : Robot et décisions automatiques
Une première IA aléatoire a été implémentée, puis une IA plus intelligente basée sur des calculs statistiques (médiane, moyenne, simulation).

### Étape 3 : Interface graphique
Nous avons construit une interface Pygame complète : affichage des cartes, boutons de choix, menu latéral, écran de victoire, règles et page à propos.

### Étape 4 : Liaison et modularité
Nous avons séparé le projet en modules (`sources/main.py`, `sources/cerveau.py`, `sources/game_pygame.py`, `sources/stats.py`) afin de faire évoluer chaque partie sans tout casser.

### Étape 5 : Tests et stabilisation
La fin du projet a été consacrée aux tests, à la correction de bugs, à l’ajustement de l’équilibrage des stratégies et à la préparation du dossier de participation.

## Validation de l’opérationnalité et du fonctionnement

### État d’avancement au moment du dépôt
Le projet est opérationnel :
- mode joueur contre joueur fonctionnel ;
- mode joueur contre robot fonctionnel ;
- interface Pygame stable ;
- module de simulations statistiques utilisable.

### Approches mises en œuvre pour vérifier l’absence de bugs
- tests réguliers en conditions réelles pendant le développement ;
- tests croisés entre membres de l’équipe ;
- vérification de scénarios limites (égalité, fin de partie, piles de cartes) ;
- contrôle de cohérence des résultats dans le module statistique ;
- vérification de la compilation Python des modules.

### Difficultés rencontrées et solutions apportées
- **Difficulté :** liaison entre interface et moteur de jeu.  
  **Solution :** clarifier les responsabilités de chaque module et centraliser l’état de partie dans `GameState`.

- **Difficulté :** comportement du robot trop fort ou trop imprévisible selon les versions.  
  **Solution :** ajuster les stratégies (médiane sur historique plutôt que connaissance totale).

- **Difficulté :** organisation des fichiers et chemins vers les ressources.  
  **Solution :** structuration propre du projet avec dossier `sources/`, et adaptation des chemins de données/assets.

## Ouverture

### Idées d’amélioration du projet
- ajouter de nouvelles cartes et de nouvelles caractéristiques ;
- intégrer une mécanique de rareté complète ;
- proposer un mode tournoi ou classement ;
- enrichir le module statistique avec visualisations.

### Analyse critique
Le projet est solide sur la modularité et la jouabilité, mais il reste perfectible sur la couverture de tests automatiques et sur le raffinement de certaines stratégies IA.

### Compétences personnelles développées
- modélisation orientée objet ;
- gestion d’un projet en équipe ;
- développement d’interface événementielle avec Pygame ;
- analyse de résultats et prise de décision technique ;
- utilisation de GitHub en mode collaboratif.

### Démarche d’inclusion
Nous avons fait attention à produire une interface simple et lisible : boutons explicites, menu clair, règles accessibles dans le jeu, et fonctionnement compréhensible pour un joueur non expert. L’objectif est que le jeu soit utilisable par des élèves de niveaux variés, sans prérequis technique.

## Informations complémentaires intégrées

### Organisation de l’équipe (version détaillée)

#### Composition
Équipe de 3 élèves : Antonin, Alexi, Léo.

#### Répartition des responsabilités
- **Antonin** : pilotage technique du moteur du jeu, conception des classes principales, développement des stratégies de robot, intégration du module de statistiques.
- **Alexi** : conception et développement de l’interface Pygame, ergonomie/design, interactions utilisateur, intégration des éléments sonores.
- **Léo** : recherche/validation des règles, gestion des ressources visuelles, tests utilisateurs et retours qualité, contribution à la documentation finale.

#### Méthode de travail
- Réunions courtes en début de séance pour fixer les objectifs.
- Travail en parallèle par domaines (moteur, UI, données/tests).
- Intégrations régulières sur GitHub.
- Séances de test collectif en fin d’itération.

### Journal de bord (synthèse)
- **Séances 1 à 3** : fondations, version console, structuration des classes.
- **Séances 4 à 6** : démarrage interface Pygame, robot aléatoire puis robot intelligent.
- **Séances 7 à 9** : liaison moteur/UI, amélioration design et modularité du projet.
- **Séances 10 à 12** : ajout d’options de jeu (prénom, sons, page à propos), corrections de bugs.
- **Séances 13 à 15** : finalisation Git, tests, retouches UI, documentation finale.

### Déclaration d’originalité et usage de l’IA

#### Le projet est-il original ?
Oui. Le projet est une création originale de notre équipe. Nous nous sommes inspirés des règles générales de « Défis Nature », mais l’implémentation logicielle, la structure du code et l’intégration sont réalisées par nous.

#### Usage de l’IA
Nous avons utilisé l’IA comme outil d’assistance pour :
- améliorer certaines images (upscaling) ;
- comprendre des fonctionnalités Pygame ;
- vérifier des bonnes pratiques de programmation ;
- vérifier la cohérence de certains résultats statistiques ;
- progresser sur GitHub (organisation du dépôt, pull requests, publication).

L’IA n’a pas remplacé le travail de l’équipe : les choix techniques, l’architecture, les corrections de bugs et la validation finale ont été réalisés par nous.

### Lancement du projet
Depuis la racine du dépôt :

```bash
python sources/main.py play
```

Pour le mode statistiques :

```bash
python sources/main.py stats
```


## Conformité participation Trophées NSI

### Vérification des éléments du dépôt
- `README.md` : présent et à jour (description globale + lancement).
- `dossier/presentation.md` : présent (ce document).
- `sources/` : code source principal (moteur, UI, stats, entrée).
- `data/` et `assets/` : ressources nécessaires au fonctionnement.

### Architecture du projet
L'architecture est alignée avec une structure de base recommandée pour un projet NSI :
- séparation du code (`sources/`)
- séparation des données (`data/`)
- séparation des ressources (`assets/`)
- séparation de la documentation (`docs/`, `dossier/`)

### Vidéo de présentation
La vidéo de présentation n'est pas encore fournie à ce stade du projet.
Le reste des éléments de participation est prêt et cohérent.
