# Notes de travail — vers un modèle de mélange plus réaliste (v2)

*Document de travail, à mettre à jour au fil de l'avancée. Ne remplace pas la
synthèse du TIPE — c'est la suite. Objectif : préparer le prochain post
LinkedIn.*

## 1. Le point de départ, très concret

Le modèle initial simule un croisement de canaux (largeur L0) où deux
écoulements de Poiseuille alternent pour replier le fluide. En le testant sur
les deux simulations fournies à l'origine, on est tombé sur quelque chose
d'étrange : le nuage rouge de la Simulation 2, visuellement "bien dilué",
perdait en réalité jusqu'à 100 % de son effectif hors de la fenêtre
d'observation — parfois en 4 ou 5 cycles seulement. L'indice de mélange
donnait l'illusion d'un mélange rapide, alors qu'il ne mesurait presque plus
rien.

## 2. Ce que ce constat a révélé

Le modèle n'a **aucune notion de ce qui existe au-delà du carré L0×L0** qu'on
observe. Une particule qui sort n'est pas perdue physiquement — mais rien
dans le code ne décrit ce qui lui arrive ensuite. C'est le vrai défaut du
modèle, et il se décline en plusieurs oublis précis :

- Pas de condition aux limites au sens physique : l'espace est traité comme
  infini dans les deux directions.
- x et y sont traités de façon parfaitement symétrique, alors qu'on va voir
  qu'ils ne le sont pas.
- Pas de diffusion moléculaire — pas grave sur un seul passage (l'advection
  domine de plusieurs ordres de grandeur), mais indispensable pour
  l'homogénéisation fine cumulée sur de nombreux passages.
- Un grand saut de position par demi-cycle plutôt qu'une intégration fine —
  source de la sensibilité numérique observée, mais probablement secondaire.

## 3. La vraie architecture du dispositif

Un dispositif à recirculation active n'utilise pas un réseau de canaux, mais
**un seul canal** (largeur ~50-200 µm, souvent ~100 µm), qui forme soit une
boucle fermée (pompe péristaltique), soit fait un aller-retour (oscillation
pneumatique). Ce canal repasse plusieurs fois sur la même zone de détection :
c'est le principe même de la recirculation. Les ordres de grandeur trouvés
(boucle de ~2 cm de diamètre pour un canal de ~100 µm) donnent un rapport
d'environ 100 à 200 entre la longueur de la boucle et la largeur du canal.

Le croisement où a lieu le repliement actif (le "boulanger") est un point
local sur cette boucle. C'est cette architecture qui explique le paradoxe du
§1 : une particule qui "sort" par le canal principal ne part pas dans le
vide, elle repart faire le tour de la boucle et revient.

### 3bis. Comment le croisement est isolé : les vannes, et pourquoi le canal principal est long

Au croisement, chaque axe est équipé de vannes (technologie "vannes Quake" :
une fine membrane PDMS, 5-15 µm d'épaisseur, entre le canal de fluide et un
canal de commande pneumatique perpendiculaire ; quelques psi suffisent à la
déformer pour pincer le canal localement). La règle est simple et symétrique :
**pendant une phase x, on ferme les deux vannes de l'axe y ; pendant une phase
y, on ferme les deux vannes de l'axe x.** Ça garantit qu'un seul axe bouge à
la fois. Les vannes elles-mêmes sont de taille comparable à L0 et placées au
plus près du croisement des deux côtés, sans asymétrie entre les axes.

Ce qui est asymétrique, c'est ce qu'il y a *derrière* chaque vanne une fois
ouverte — et ça vient d'une contrainte réelle, pas d'un choix arbitraire :

- Le canal secondaire (axe y) n'a **qu'une seule fonction** : cisailler le
  fluide au croisement. Une fois le pli fait, son travail est terminé — pas
  de raison qu'il aille plus loin qu'un aller-retour local. D'où un vrai mur
  proche.
- Le canal principal (axe x) a **deux fonctions à la fois** : replier le
  fluide au croisement, *et* transporter cet échantillon jusqu'aux zones de
  détection ailleurs sur la puce, pour que sondes et cibles se rencontrent,
  avant de le ramener pour un nouveau passage (le principe même de la
  recirculation, §3). Cette deuxième fonction n'a rien à voir avec le
  mélange local : elle est imposée par la distance réelle entre le
  croisement et les spots d'ADN sur la puce. C'est elle, et elle seule, qui
  oblige le canal principal à être long (boucle de ~1-2 cm) plutôt qu'un
  simple aller-retour.

*Précision honnête : ce lien entre "canal principal long" et "double fonction
mélange + livraison" est une reconstruction logique à partir de ce qu'on a lu
sur la recirculation active, pas une donnée confirmée pour un dispositif
particulier — mais c'est la seule explication qui tienne compte tenu de tout
le reste (sans une deuxième fonction, rien n'imposerait au canal principal
d'être plus long que le secondaire).*

## 4. Le nouveau modèle — un seul cycle

Rien ne change dans la poussée elle-même : profil de Poiseuille, durées Tx et
Ty, largeur de canal L0, alternance x+ / y+ / x- / y-. Ce qui change, c'est la
règle appliquée à la position juste après chaque poussée, et elle dépend de
l'axe :

- **y (position à travers le tube)** : une vraie paroi physique, non
  négociable. Si le demi-cycle pousse la particule au-delà de ±L0/2, on
  **réfléchit** le dépassement vers l'intérieur (rebond sur la paroi).
- **x (position le long du tube)** : pas de mur, mais un retour garanti par la
  boucle. Le long trajet de retour ne comporte aucun cisaillement transverse
  (rien ne s'y passe pour le mélange, y reste figé pendant tout ce temps,
  exactement comme le modèle le suppose déjà pendant une phase x) — on peut
  donc le compresser en un aller-retour instantané : une **condition
  périodique** à ±L0/2. Cette compression n'est légitime que parce que la
  boucle est beaucoup plus longue que L0 (rapport ~100-200, §3) — c'est le
  seul rôle que joue la taille du dispositif D dans ce modèle : elle ne
  rentre dans aucune équation, elle justifie seulement que l'approximation
  est raisonnable.

Conséquence : plus aucune particule ne peut sortir de [-L0/2, L0/2]². Les
masques conditionnels de l'ancien modèle (qui décidaient si une particule
"voyait" ou non l'écoulement) deviennent inutiles et peuvent disparaître —
toutes les particules participent à chaque sous-étape.

## 5. Le nouveau modèle — plusieurs cycles

Rien de nouveau ici : la correction s'applique à chaque demi-cycle,
indépendamment des autres, et `cycle()` continue d'être appliqué n fois pour
faire évoluer la population. C'est la répétition de cette petite règle locale
qui, cumulée sur n cycles, doit changer le comportement global — en
particulier faire disparaître les faux diagnostics de "fuite" observés
jusqu'ici, sans changer la définition de n*, de I_n ou de α, β.

## 6. Conséquences pour le code

- `etape()` se scinde en deux blocs, **un par axe** (pas un par signe) : x+ et
  x- partagent la même logique (poussée + condition périodique), y+ et y-
  partagent la même logique (poussée + réflexion). Le signe reste un simple
  paramètre.
- Les masques disparaissent.
- `indice_melange`, `n_etoile`, les balayages (α, β) restent structurellement
  les mêmes ; seuls les résultats numériques doivent être refaits.

## 7. Ce qu'on laisse volontairement de côté pour l'instant

- La diffusion moléculaire (marche aléatoire superposée à l'advection) —
  prochaine itération, une fois ce modèle validé.
- Le grand saut instantané par demi-cycle (vs une intégration plus fine) —
  pas jugé prioritaire pour l'instant.
- La longueur exacte de boucle ℓ, la taille exacte de puce D, le nombre de
  croisements réels — non nécessaires : leur seul rôle est de justifier
  l'approximation du §4, pas d'apparaître comme paramètres.
- Le mélangeur passif — écarté (nécessiterait la 3D).

## 8. Prochaines étapes

1. Implémenter la correction (§4, §6).
2. Refaire tourner l'indice d'entropie sur ce modèle corrigé — sans attendre
   la diffusion, l'outil de mesure ne dépend pas de la dynamique mesurée.
3. Comparer qualitativement à l'ancien modèle (disparition des points
   "fuite" attendue).
4. Diffusion, dans une itération ultérieure, mesurée avec le même indice.
