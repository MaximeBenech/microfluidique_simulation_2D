"""
simulation.py
=============
Le moteur physique, seul et unique -- plus la verification des
parametres physiques eux-memes (verifier_parametres), qui ne concerne
que des nombres, jamais mesures.py. Ne connait ni l'entropie, ni
alpha/beta, ni aucune figure.

Un "nuage" est un tableau numpy de forme (n_particules, 2) : une ligne
(x, y) par particule.
"""

import numpy as np


def nuage_initial(x0, y0, Nx, Ny, pas):
    """
    Construit un nuage carre de particules, regulierement espacees,
    centre sur (x0, y0).

    Utilisation : nuage = nuage_initial(-24, 12, 50, 50, 0.05)
    """
    xs = x0 + (np.arange(Nx) - Nx / 2) * pas
    ys = y0 + (np.arange(Ny) - Ny / 2) * pas
    X, Y = np.meshgrid(xs, ys)
    return np.column_stack((X.ravel(), Y.ravel()))


def verifier_parametres(Vm, Ty, b_a, b_d):
    """
    A appeler avant toute simulation, sur les parametres physiques
    seuls (jamais besoin du nuage ni de mesures.py). Leve une erreur
    explicite si les parametres ne peuvent pas etre simules correctement.

    Deux conditions :
    - b_a doit etre strictement superieur a b_d, sans quoi les deux
      barrieres n'ont plus d'interpretation coherente (ascendant vs
      descendant).
    - 1,5*Vm*Ty <= b_a - b_d : le pire cas (une particule demarrant
      exactement sur une barriere, poussee maximale du profil de
      Poiseuille) ne doit pas, apres un seul rebond, depasser la
      barriere opposee -- un second rebond dans la meme poussee n'est
      pas modelise (une seule poussee, un seul signe, ne peut
      structurellement s'approcher que d'un seul mur). Cette limite
      reflete aussi une vraie contrainte de conception : une poussee
      plus violente causerait une surpression contre la paroi (usure,
      risque de fuite du dispositif).

    Leve : ValueError, avec un message explicite, si l'une des deux
    conditions n'est pas respectee.
    """
    if b_a <= b_d:
        raise ValueError(f"b_a ({b_a}) doit etre strictement superieur a b_d ({b_d}).")
    poussee = 1.5 * Vm * Ty
    ecart = b_a - b_d
    if poussee > ecart:
        raise ValueError(
            f"1,5*Vm*Ty = {poussee:.3g} depasse b_a - b_d = {ecart:.3g} : "
            "un seul rebond ne suffirait plus (une deuxieme reflexion serait "
            "necessaire dans la meme poussee, non modelisee). Cette limite "
            "reflete aussi une contrainte de conception reelle : une poussee "
            "plus violente causerait une surpression contre la paroi (usure, "
            "risque de fuite). Reduire Vm ou Ty, ou elargir l'ecart entre "
            "b_a et b_d."
        )


def etape_x(nuage, Vm, L0, Tx, signe):
    """
    Un demi-cycle de poussee le long de x (le canal principal).

    Represente : l'ecoulement de Poiseuille dans le canal principal, de
    duree Tx, dans le sens donne par signe (+1 ou -1). Le profil de
    vitesse depend de y (transverse), qui reste fige pendant cette phase.

    Le canal principal se ferme transversalement a y = +L0/2 et
    y = -L0/2 -- sa propre largeur physique, independante de b_a et
    b_d qui ne concernent que le canal secondaire. Une particule
    actuellement hors de cette largeur (deja loin dans le canal
    secondaire, au-dela du croisement) n'est pas poussee ce demi-cycle :
    elle n'est physiquement plus dans le canal principal. Elle y
    reviendra par les phases y elles-memes (leur formule ne depend que
    de x, jamais menacee), pas par une regle speciale ici.

    Condition de bord (position elle-meme, pas la poussee) : le canal
    principal boucle sur lui-meme (boucle de recirculation, longueur
    grande devant L0). Une particule qui depasse L0/2 en x reapparait
    de l'autre cote, a la meme distance de depassement (condition
    periodique), generalisee par modulo pour absorber n'importe quel
    nombre de tours en une seule operation.

    Parametres
    ----------
    nuage : tableau (n, 2), les positions actuelles.
    Vm    : vitesse moyenne de l'ecoulement.
    L0    : largeur du canal (et cote du carre de rencontre L0^2).
    Tx    : duree de la phase.
    signe : +1 ou -1, sens de la poussee.

    Retourne
    --------
    Un nouveau tableau (n, 2) (ne modifie pas "nuage" en place).
    """
    x = nuage[:, 0].copy()
    y = nuage[:, 1]
    masque = np.abs(y) < L0 / 2
    v = signe * 1.5 * Vm * (1 - 4 * y[masque] ** 2 / L0 ** 2)
    x[masque] = x[masque] + v * Tx
    x = np.mod(x + L0 / 2, L0) - L0 / 2
    return np.column_stack((x, y))


def etape_y(nuage, Vm, L0, Ty, signe, b_a, b_d):
    """
    Un demi-cycle de poussee le long de y (le canal secondaire, le
    cisaillement transverse qui replie le fluide).

    Represente : l'injection perpendiculaire au croisement, de duree Ty,
    dans le sens donne par signe. Le profil de vitesse depend de x
    (fige pendant cette phase).

    Un seul rebond possible, contre la seule paroi concernee par le
    sens de la poussee : b_a en y+ (ascendant), b_d en y- (descendant)
    -- jamais les deux dans la meme fonction, puisqu'une seule poussee
    (un seul signe) ne peut structurellement s'approcher que d'un seul
    mur. La reflexion n'est pas la modelisation d'un choc reel : c'est
    une approximation grossiere d'un phenomene physique different
    (accumulation de fluide contre un cul-de-sac, refoulement par
    surpression), non modelise explicitement.

    Parametres
    ----------
    nuage       : tableau (n, 2), les positions actuelles.
    Vm, L0, Ty  : voir etape_x.
    signe       : +1 (ascendant, contre b_a) ou -1 (descendant, contre b_d).
    b_a         : position algebrique de la barriere ascendante.
    b_d         : position algebrique de la barriere descendante
                  (b_d < b_a, voir verifier_parametres).

    Retourne
    --------
    Un nouveau tableau (n, 2).
    """
    x = nuage[:, 0]
    y = nuage[:, 1].copy()
    v = signe * 1.5 * Vm * (1 - 4 * x ** 2 / L0 ** 2)
    y_brut = y + v * Ty
    if signe > 0:
        depasse = y_brut > b_a
        y_brut[depasse] = 2 * b_a - y_brut[depasse]
    else:
        depasse = y_brut < b_d
        y_brut[depasse] = 2 * b_d - y_brut[depasse]
    return np.column_stack((x, y_brut))


def cycle(nuage, Vm, L0, Tx, Ty, b_a, b_d):
    """
    Un cycle complet : x+, y+, x-, y- -- un pli elementaire du
    "boulanger" local. C'est la repetition de cette fonction, n fois,
    qui produit le melange chaotique.

    Utilisation typique : appelee a l'interieur d'une boucle, jamais
    directement par l'utilisateur final (voir mesures.simuler et
    mesures.n_etoile, appelees via un "cycle_fn" prepare dans
    orchestration.py).
    """
    nuage = etape_x(nuage, Vm, L0, Tx, +1)
    nuage = etape_y(nuage, Vm, L0, Ty, +1, b_a, b_d)
    nuage = etape_x(nuage, Vm, L0, Tx, -1)
    nuage = etape_y(nuage, Vm, L0, Ty, -1, b_a, b_d)
    return nuage
