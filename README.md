# Mélange chaotique en puce à ADN — simulation 2D

Simulation Python d'un mélangeur microfluidique par advection chaotique
("transformation du boulanger", écoulements de Poiseuille alternés),
avec un indice quantitatif de qualité de mélange fondé sur l'entropie de
Shannon. Projet initialement développé en CPGE (TIPE), repris et
largement refondu depuis.

**Statut** : modèle en développement actif (V2). Le code n'a pas encore
été testé de bout en bout par une campagne complète — voir l'issue
« Bilan complet V1 → V2 » du dépôt pour l'historique détaillé, les choix
de modélisation, et la liste des points encore ouverts.

## Le principe, en bref

Deux canaux perpendiculaires poussent alternativement le fluide (phases
x et y), repliant progressivement un nuage de particules par un
mécanisme d'advection chaotique. La qualité du mélange, après n cycles,
est mesurée par :

```
I_n = f × I_carré
```

- **f** : fraction des particules présentes dans le carré de rencontre
  sondes/cibles.
- **I_carré** : entropie de Shannon normalisée, sur une grille N×N,
  parmi les particules présentes dans ce carré.

**n\*** est le plus petit nombre de cycles pour lequel I_n dépasse un
seuil fixé — la grandeur centrale des résultats produits par ce dépôt.

## Architecture du code

Six fichiers, un rôle chacun :

| Fichier | Rôle |
|---|---|
| `protocole.py` | Constantes partagées uniquement (L0, Vm0, b_a, b_d, N, I_seuil, N_MAX) |
| `simulation.py` | Physique pure : un cycle (x+, y+, x-, y-), et la vérification de validité des paramètres |
| `mesures.py` | Calcul de l'indice, de n\*, et des balayages — ne connaît jamais `simulation.py` |
| `orchestration.py` | Seul fichier reliant `simulation.py` et `mesures.py` |
| `visualisation.py` | Figures et sorties texte, à partir de résultats déjà calculés |
| `main.py` | Exécution : construit les nuages, lance les simulations/balayages, affiche les résultats |

`v1_tipe/` contient la version d'origine du TIPE, conservée pour
l'historique — non maintenue.

## Utilisation rapide

```bash
python3 main.py
```

Modifier `protocole.py` pour changer les constantes du protocole
(largeur de canal, position des barrières...), ou directement
`main.py` pour changer les paramètres d'une simulation ou d'un
balayage donné.

Sur Google Colab :

```python
!git clone https://github.com/<utilisateur>/<depot>.git
%cd <depot>
%run main.py
```

## Ce que le modèle représente physiquement

- **x (canal principal)** : périodique — une particule qui sort d'un
  côté revient de l'autre, à l'image d'une boucle de recirculation.
- **y (canal secondaire)** : un seul rebond possible, contre une
  barrière asymétrique (b_a en montée, b_d en descente) — une
  approximation grossière d'un refoulement par surpression contre un
  cul-de-sac, pas un choc élastique.
- Un garde-fou (`simulation.verifier_parametres`) empêche de lancer une
  simulation dont l'amplitude de poussée dépasserait, en un seul
  rebond, l'écart entre les deux barrières.

Le détail complet du raisonnement (pourquoi ce modèle, ce qui a changé
depuis la V1, ce qui reste ouvert) est dans l'issue du dépôt plutôt que
dupliqué ici.

## À venir

Diffusion moléculaire, lien entre la résolution de mesure et la
largeur du canal, exploration de barrières asymétriques — voir les
issues du dépôt pour le détail et l'avancement.
