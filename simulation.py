"""
simulation.py
=============
Le moteur physique, seul et unique. Fait evoluer un nuage de particules
d'un demi-cycle ou d'un cycle complet a l'autre. Ne connait ni l'entropie,
ni alpha/beta, ni aucune figure -- uniquement des positions (x, y) et
comment elles se deplacent.

Un "nuage" est un tableau numpy de forme (n_particules, 2) : une ligne
(x, y) par particule.
"""

import numpy as np


def nuage_initial(x0, y0, Nx, Ny, pas):
    """
    Construit un nuage carre de particules, regulierement espacees,
    centre sur (x0, y0).

    Utilisation : nuage = nuage_initial(-24, 12, 50, 50, 0.05)

    Parametres
    ----------
    x0, y0 : position du centre du nuage.
    Nx, Ny : nombre de particules le long de chaque cote du carre.
    pas    : espacement entre deux particules voisines.

    Retourne
    --------
    Un tableau numpy (Nx*Ny, 2).

    Remarque : seule la forme "carre" est geree pour l'instant. Passer a
    d'autres formes (cercle, ellipse) plus tard ne demandera de modifier
    que cette fonction -- ni le reste de ce fichier, ni mesures.py, ni
    visualisation.py n'ont besoin de savoir quelle forme a ete choisie.
    """
    xs = x0 + (np.arange(Nx) - Nx / 2) * pas
    ys = y0 + (np.arange(Ny) - Ny / 2) * pas
    X, Y = np.meshgrid(xs, ys)
    return np.column_stack((X.ravel(), Y.ravel()))


def etape_x(nuage, Vm, L0, Tx, signe):
    """
    Un demi-cycle de poussee le long de x (le canal principal).

    Represente : l'ecoulement de Poiseuille dans le canal principal, de
    duree Tx, dans le sens donne par signe (+1 ou -1). Le profil de
    vitesse depend de y (transverse), qui reste fige pendant cette phase
    -- seul x bouge.

    Condition de bord : le canal principal boucle sur lui-meme (boucle de
    recirculation, longueur grande devant L0 -- rapport ~100-200 dans les
    dispositifs reels). Une particule qui depasse L0/2 en x reapparait de
    l'autre cote, a la meme distance de depassement (condition
    periodique). Ce raccourci est legitime parce que rien de notable pour
    le melange ne se produit durant le long trajet de retour (y reste
    fige) -- voir notes_modele_v2.md, section 4.

    Repli par modulo : ramene x dans [-L0/2, L0/2) en une seule operation,
    quel que soit le nombre de tours de boucle representes par le
    depassement (pas seulement un seul tour, comme dans la version
    precedente).

    Parametres
    ----------
    nuage : tableau (n, 2), les positions actuelles.
    Vm    : vitesse moyenne de l'ecoulement.
    L0    : largeur du canal (et taille du cote de la fenetre d'analyse).
    Tx    : duree de la phase.
    signe : +1 ou -1, sens de la poussee.

    Retourne
    --------
    Un nouveau tableau (n, 2) (ne modifie pas "nuage" en place).
    """
    x = nuage[:, 0].copy()
    y = nuage[:, 1]
    v = signe * 1.5 * Vm * (1 - 4 * y**2 / L0**2)
    x = x + v * Tx
    x = np.mod(x + L0 / 2, L0) - L0 / 2
    return np.column_stack((x, y))


def etape_y(nuage, Vm, L0, Ty, signe):
    """
    Un demi-cycle de poussee le long de y (le canal secondaire, le
    cisaillement transverse qui replie le fluide).

    Represente : l'injection perpendiculaire au croisement, de duree Ty,
    dans le sens donne par signe. Le profil de vitesse depend de x
    (fige pendant cette phase) -- seul y bouge.

    Condition de bord : y est borne par une vraie paroi physique (la
    largeur du tube, non negociable). Une particule qui depasse L0/2 en y
    est reflechie (repliee vers l'interieur, comme un rebond). Cette
    reflexion approxime ce qu'une trajectoire continue plus fine aurait
    fait -- la vitesse de Poiseuille s'annule en douceur pres du mur, donc
    une particule reelle ne l'atteint jamais vraiment ; le rebond corrige
    la grossierete de notre saut unique par demi-cycle, voir
    notes_modele_v2.md.

    Repli en accordeon : au lieu de supposer qu'un seul rebond suffit, on
    imagine la trajectoire theorique (sans mur) se deroulant sur une
    bande deux fois plus large que le canal (periode 2*L0), ou le motif
    se repete en dents de scie -- une "montee" jusqu'au mur du haut, puis
    une "descente" symetrique jusqu'au mur du bas. Reperer dans quelle
    moitie de cette bande on tombe donne directement la position reelle,
    quel que soit le nombre de rebonds que ca representait. Absorbe donc
    n'importe quel nombre de rebonds d'affilee en une seule operation, et
    redonne exactement l'ancienne formule quand un seul rebond suffisait
    deja.

    Parametres et retour : identiques a etape_x, appliques a y.
    """
    x = nuage[:, 0]
    y = nuage[:, 1].copy()
    v = signe * 1.5 * Vm * (1 - 4 * x**2 / L0**2)
    y = y + v * Ty
    r = np.mod(y + L0 / 2, 2 * L0)
    y = np.where(r <= L0, -L0 / 2 + r, 3 * L0 / 2 - r)
    return np.column_stack((x, y))


def cycle(nuage, Vm, L0, Tx, Ty):
    """
    Un cycle complet : x+, y+, x-, y- -- un pli elementaire du
    "boulanger" local. C'est la repetition de cette fonction, n fois,
    qui produit le melange chaotique -- pas un grand trajet unique le
    long de la boucle physique.

    Utilisation typique : appelee a l'interieur d'une boucle, jamais
    directement par l'utilisateur final (voir mesures.simuler et
    mesures.n_etoile, qui l'appellent via un "cycle_fn" prepare dans
    main.py).
    """
    nuage = etape_x(nuage, Vm, L0, Tx, +1)
    nuage = etape_y(nuage, Vm, L0, Ty, +1)
    nuage = etape_x(nuage, Vm, L0, Tx, -1)
    nuage = etape_y(nuage, Vm, L0, Ty, -1)
    return nuage