# Stratégies implémentées dans le projet

Ce document décrit les différentes stratégies utilisées par les bots dans les simulations statistiques.  
Chaque stratégie est classée par type d’information utilisée et par niveau de sophistication.

---

## 1. Stratégies naïves

### 1.1 Random

**Type :** Baseline aléatoire  
**Information utilisée :** Aucune  

**Principe :**  
Le bot choisit au hasard l’une des caractéristiques disponibles sur sa carte active.

**Objectif :**  
Servir de référence minimale pour comparer les autres stratégies.

**Avantages :**
- Simple et rapide
- Aucun calcul

**Limites :**
- Ne tient compte ni des données historiques, ni de la distribution des cartes
- Performances faibles en moyenne

---

### 1.2 FirstStat(poids)

**Type :** Heuristique fixe  
**Information utilisée :** Aucune  

**Principe :**  
Le bot choisit toujours la même caractéristique (par exemple `poids`).

**Objectif :**  
Tester si une caractéristique dominante permet d’obtenir un avantage structurel.

**Avantages :**
- Déterministe
- Permet d’évaluer la “force” intrinsèque d’une caractéristique

**Limites :**
- Peut être exploité facilement
- Ne s’adapte jamais à l’adversaire

---

## 2. Stratégies basées sur l’historique local

Ces stratégies utilisent uniquement les cartes déjà observées pendant la partie.

### 2.1 MeanRatio(hist)

**Type :** Heuristique adaptative  
**Information utilisée :** Historique des cartes vues  

**Principe :**  
Pour chaque caractéristique, on compare la valeur de la carte active à la moyenne observée dans l’historique.  
On choisit la caractéristique qui maximise le rapport :
valeur_carte / médiane_historique


**Idée :**  
La médiane est plus robuste aux valeurs extrêmes que la moyenne.

**Avantages :**
- Plus stable statistiquement
- Moins influencée par des cartes atypiques

**Limites :**
- Toujours limitée à l’information observée

---

## 3. Stratégies avec information globale (triche)

Ces stratégies utilisent des informations normalement indisponibles dans une partie réelle.

### 3.1 CheatAbsolute

**Type :** Information parfaite  
**Information utilisée :** Carte adverse actuelle  

**Principe :**  
Le bot observe directement la carte adverse et choisit la caractéristique qui maximise l’écart :
valeur_carte / médiane_globale


**Objectif :**  
Simuler un joueur connaissant parfaitement la distribution complète du jeu.

**Avantages :**
- Exploite la structure statistique globale
- Performances souvent élevées

**Limites :**
- Non réaliste en situation réelle

---

## 4. Stratégies Monte Carlo

Ces stratégies utilisent la simulation pour estimer la probabilité de victoire.

### 4.1 MonteCarlo(aleatoire)

**Type :** Simulation stochastique  
**Information utilisée :** État courant du jeu  

**Principe :**  
Pour chaque caractéristique possible :

1. On simule plusieurs parties complètes à partir de l’état actuel.
2. On joue ensuite aléatoirement jusqu’à la fin.
3. On estime le taux de victoire associé à chaque caractéristique.
4. On choisit celle avec la meilleure performance moyenne.

**Avantages :**
- Approche probabiliste solide
- Peut approcher une stratégie optimale

**Limites :**
- Coûteux en calcul
- Dépend du nombre de simulations

---

### 4.2 MonteCarlo(median)

**Type :** Simulation stochastique guidée  
**Information utilisée :** État courant du jeu  

**Principe :**  
Identique à la version précédente, mais les parties simulées utilisent une stratégie médiane plutôt qu’un choix aléatoire.

**Objectif :**  
Obtenir une estimation plus stable et plus informative que le Monte Carlo purement aléatoire.

**Avantages :**
- Simulations plus intelligentes
- Moins de variance que la version aléatoire

**Limites :**
- Plus complexe
- Toujours dépendant du nombre de simulations

---

# Résumé conceptuel

Les stratégies se répartissent en quatre niveaux :

1. Baselines naïves (aucune information)
2. Heuristiques locales (historique partiel)
3. Information parfaite (borne théorique)
4. Simulation probabiliste (Monte Carlo)

Cette hiérarchie permet d’analyser :

- L’impact de l’information
- La valeur de l’adaptation
- La puissance des méthodes statistiques par simulation
