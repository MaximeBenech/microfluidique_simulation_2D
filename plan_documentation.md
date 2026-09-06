# Plan de documentation — refonte du modèle (v2)

*Brouillon de plan, à compléter au fur et à mesure de la rédaction réelle.
Sert de base au prochain post LinkedIn et à la documentation du dépôt.
Ceci est un plan (une structure), pas encore le texte final.*

## 0. Le fil conducteur à adopter pour la rédaction


1. L'objectif de la simulation du TIPE était d'évaluer la qualité
   d'une dilution, et l'inspection visuelle ne permet que des
   impressions ("ça a l'air bien mélangé").
2. L'indice fondé sur l'entropie de Shannon a été construit pour ça.
3. En l'appliquant réellement (plutôt que de se fier à l'œil), il a
   immédiatement révélé quelque chose que la visualisation d'origine ne
   montrait pas du tout : une partie du nuage "bien dilué" avait en fait
   quitté la fenêtre d'observation sans que personne ne s'en aperçoive.
4. C'est cette découverte, faite *grâce* à la mesure quantitative, qui a
   motivé toute la refonte du modèle qui suit.

C'est le lien essentiel à mettre en avant : la mesure quantitative n'a pas
seulement confirmé une intuition, elle a corrigé une intuition fausse que
l'œil ne pouvait pas détecter.

## 1. Pourquoi cette refonte (rappel court)

- Le paradoxe observé : le nuage rouge de la Simulation 2, visuellement
  "bien dilué", perdait en réalité jusqu'à 100 % de son effectif hors de
  la fenêtre d'observation — c'est l'indice d'entropie qui l'a signalé,
  pas l'œil.
- Ce que ça a révélé : le modèle n'avait aucune notion de ce qui existe
  au-delà du carré L0×L0 observé.

## 2. Le nouveau modèle physique

- Rappel de l'architecture réelle (recirculation, canal principal en
  boucle vs canal secondaire local) — contenu déjà rédigé dans
  `notes_modele_v2.md`, section 3.
- **Pourquoi le canal principal est long** (double fonction : replier le
  fluide au croisement *et* le transporter jusqu'aux spots ADN) — déjà
  rédigé dans `notes_modele_v2.md`, section 3bis, à reprendre tel quel.
- Le mécanisme des vannes (vannes Quake), fermeture symétrique par axe
  (fermer l'axe perpendiculaire à l'écoulement actif) — la vanne bloque
  toute la section du canal à l'endroit où elle se ferme, quelle que soit
  la longueur du canal au-delà : sa position ne dépend donc jamais de la
  longueur du canal principal, seulement de sa proximité au croisement
  (dead volume minimal). Point à illustrer simplement (image d'un tuyau
  d'arrosage pincé) pour éviter la confusion qu'on a eue en discussion.
- x périodique : ce que ça représente (retour par la boucle), pourquoi
  c'est un raccourci légitime (rien de notable ne se passe pendant le
  transit, y reste figé).
- y réfléchi : ce que ça représente (paroi réelle du tube), pourquoi
  c'est une **correction numérique** et non la modélisation d'un choc réel
  (la vitesse de Poiseuille s'annule en douceur près du mur ; le rebond
  compense la grossièreté du grand saut par demi-cycle). Pas de facteur
  de freinage/restitution à ajouter : en écoulement de Stokes (laminaire,
  microscopique), il n'y a pas d'inertie à dissiper, et le ralentissement
  près du mur est déjà contenu dans le profil de Poiseuille lui-même.
- Bien insister sur la différence de nature entre les deux corrections :
  l'une répare une approximation (y), l'autre fait l'économie d'un calcul
  réel mais sans intérêt (x).
- La généralisation en repli par modulo (x) et en accordéon (y), qui
  absorbe plusieurs rebonds/tours d'affilée en une seule opération —
  utile pour ne pas se limiter à des balayages trop étroits en (α, β).
- Ce que représente "n cycles" : un compteur de plis, pas du temps réel
  écoulé — un retour par la boucle prend beaucoup plus de temps réel
  qu'une réflexion locale, mais ça n'intervient pas dans I_n(n). À noter
  comme limite explicite, pas comme un problème résolu.

## 3. La convention Tx·Ty = 1 — section à ne pas oublier

- D'où vient la sous-détermination : (alpha, beta) donnent 2 équations
  pour 3 inconnues (Vm, Tx, Ty).
- Ce que la convention choisit : Tx = √β, Ty = 1/√β, Vm = α·L0.
- Conséquence concrète dans un balayage : Vm varie automatiquement avec
  (α, β) à chaque point testé.
- Sa limite, à assumer clairement : Tx, Ty sont plus faciles à régler
  expérimentalement que Vm — cette convention est une commodité
  mathématique pour boucler le système, pas un reflet de ce qu'on ferait
  au laboratoire.
- Où elle intervient exactement : uniquement dans `params_physiques` /
  `balayage` (donc dans `construire_cycle_fn`). Une `simulation_unique` en
  paramètres physiques directs (Vm, Tx, Ty) n'en a jamais besoin — le
  système y est toujours bien déterminé sans convention.

## 4. Architecture du code

- Tableau des 4 fichiers et leur rôle unique chacun (simulation / mesures
  / visualisation / main).
- Le principe du `cycle_fn` / `cycle_fn_builder` : pourquoi `mesures.py`
  ne connaît jamais `simulation.py`, et pourquoi ce choix permettra
  d'ajouter la diffusion sans toucher `mesures.py` ni `visualisation.py`.
- Pourquoi deux familles de tracés séparées dans `visualisation.py` (le
  visuel direct d'un nuage vs les résultats agrégés d'un balayage), plus
  la présentation texte de n* (`afficher_n_star`).

## 5. Comment utiliser le code (mode d'emploi)

- Simulation unique : entrer Vm, Tx, Ty (ou alpha, beta) + une liste de
  nuages initiaux + une liste explicite d'instants à photographier.
- Balayage : un axe balayé, jusqu'à 4-6 valeurs fixées de l'autre axe.
- Combiner les deux : superposer les points d'une simulation réellement
  lancée sur une figure de balayage (voir `main.py`, exemple complet).

## 6. Ouverture — vers la lutte contre les faux positifs

Section de discussion, pas de résultat calculé : relier la qualité du
mélange à sa conséquence pratique sur la puce à ADN.

- Une mauvaise dilution (ou une partie du marqueur qui quitte la zone de
  réaction sans qu'on le sache) peut biaiser un résultat de diagnostic
  dans les deux sens : un faux négatif (les sondes n'ont pas rencontré
  assez de cibles pour donner un signal), ou un faux positif si la perte
  de marqueur perturbe la lecture du signal de référence.
- Le parallèle direct avec le résultat de cette étude : c'est exactement
  le même mécanisme qui a produit une fausse impression de "bonne
  dilution" sur la Simulation 2 — un défaut invisible à l'œil, révélé
  uniquement par une mesure quantitative.
- Ouverture (sans y répondre ici) : un indice de mélange quantitatif,
  mesuré en continu, pourrait servir de garde-fou de conception ou de
  contrôle qualité pour limiter ce risque en amont — piste à formuler
  prudemment, pas à développer dans cette version.

## 7. Diffusion — démarche prévue (à détailler une fois implémentée)

- Ajouter, à chaque mise à jour de position dans `simulation.py`, un
  petit déplacement aléatoire tiré d'une loi normale (moyenne nulle,
  variance proportionnelle à 2·D_diff·Δt), en plus du déplacement
  déterministe.
- Implique de subdiviser chaque demi-cycle en plusieurs petits pas de
  temps plutôt que de garder le grand saut analytique unique : la
  diffusion agit en continu, alors que l'hypothèse actuelle ("y figé
  pendant toute la phase x") ne tiendrait plus si on ajoutait du bruit
  d'un seul coup sur le grand saut.
- Mesure inchangée : `indice_melange`, `n_etoile`, les balayages
  continuent de fonctionner sans modification — seule la dynamique dans
  `simulation.cycle` change (voir le découplage voulu dès le §4).
- Point physique à rappeler dans la doc : l'advection domine très
  largement la diffusion sur un seul passage (rapport de plusieurs
  ordres de grandeur) ; le rôle réel de la diffusion est de finir
  l'homogénéisation une fois les filaments suffisamment amincis par les
  passages répétés (synergie étirement/diffusion), pas de mélanger à
  elle seule.

## 8. Changer la largeur du canal (L0) — question ouverte à trancher plus tard

- L'indice `indice_melange(nuage, L0, N)` reçoit déjà L0 en paramètre :
  rien ne casse mécaniquement si L0 change, et l'entropie normalisée
  reste comparable en valeur (0 à 1) quelle que soit la taille absolue
  du canal.
- Le vrai point d'attention, à ne pas oublier : la résolution de grille N
  fixe la taille absolue de chaque case une fois L0 choisi. Si L0 change
  sans réajuster N, la finesse réelle de la mesure change avec lui (des
  cases plus grandes rendent le mélange artificiellement plus facile à
  atteindre, sans que ça reflète une vraie différence physique). Il
  faudra donc redéfinir N (ou une taille de case cible, en lien avec une
  échelle physique pertinente — taille des spots ADN, longueur de
  diffusion) plutôt que de garder N fixe par habitude.
- Volontairement pas traité maintenant : la diffusion passe avant, cette
  question sera reprise une fois la diffusion en place.

### 8bis. Piste à garder : plusieurs indices plutôt qu'un seul choix de N

Au lieu de trancher entre les trois ancrages proposés pour N (échelle
physique des spots, longueur de diffusion, taille statistique par case),
envisager de calculer les trois en parallèle, comme trois indices
distincts plutôt qu'un seul I. Chacun raconte une histoire différente
(pertinence biologique, pertinence dynamique, fiabilité statistique de la
mesure elle-même) et rien n'oblige à n'en garder qu'un — surtout si les
trois s'accordent, ça renforcerait la conclusion ; s'ils divergent, ça
serait en soi un résultat intéressant à creuser. Décision à prendre une
fois la diffusion en place (la longueur de diffusion n'existe pas avant).

## 9. Ce qui reste volontairement de côté après ces trois étapes

- Correspondance cycles ↔ temps réel.
- Forme du nuage initial (carré/cercle/ellipse) — ne touchera que
  `simulation.nuage_initial`.
- Étude systématique de la dépendance de n* à la position initiale
  (bassins de piégeage) — rendue possible par l'architecture actuelle,
  pas encore menée comme étude à part entière.
- Amélioration de la convention Tx·Ty=1 pour un balayage plus réaliste
  expérimentalement (à Vm fixé plutôt qu'à Tx·Ty fixé).
- Zones mortes placées volontairement pour retenir le marqueur dans une
  zone de bon brassage (piste de conception à plus long terme, discutée
  mais non chiffrée).

## 10. Ordre de publication retenu

*Mis à jour : la documentation étant plus longue à rédiger que prévu, la
diffusion et le lien N↔L0 passent avant la publication, pas après.*

1. **Diffusion** (§7).
2. **Lien N↔L0** (§8, avec la piste des indices multiples, §8bis).
3. **Documentation / post**, en reprenant depuis la volonté d'évaluer
   quantitativement la dilution (§0), la découverte de la fuite grâce à
   l'entropie, le modèle corrigé (§2-5), l'ouverture faux positifs (§6),
   *et* les deux étapes ci-dessus une fois faites — plus de séparation
   entre "publier maintenant" et "ouverture sur la diffusion" puisque
   tout sera déjà en place.

## 11. Prochaines étapes

- Premier test réel du code (non exécuté à ce stade).
- Recalibrage de I_seuil sur le nouveau modèle (l'ancien 0,5 avait été
  calibré sur un modèle où l'entropie apparente était gonflée par la
  fuite).
- Rédaction du post LinkedIn à partir de ce plan et de
  `notes_modele_v2.md`.
