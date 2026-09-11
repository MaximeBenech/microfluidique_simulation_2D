"""
mesures.py
==========
Tout ce qui sert a MESURER un nuage ou une suite de nuages, sans jamais
savoir comment ils ont ete produits. Ce fichier ne doit jamais importer
simulation.py : il recoit un "cycle_fn" (une fonction nuage -> nuage)
deja toute prete depuis orchestration.py, et se contente de l'appeler.
"""

import numpy as np


def indice_melange(nuage, L0, N):
    """
    Indice de melange I_n = f * I_carre, et ses deux composantes
    renvoyees separement pour pouvoir les tracer chacune de leur cote
    (utile pour diagnostiquer une redescente de I_n : vient-elle d'une
    vraie perte d'entropie interne, I_carre qui baisse, ou d'une sortie
    de particules hors du carre, f qui baisse, ou les deux ?).

    f       : fraction de la population actuellement dans le carre de
              rencontre L0^2 (a maximiser). Se reduit a une seule
              condition, |y| < L0/2, puisque x reste toujours dans
              [-L0/2, L0/2] par construction (repli periodique).
    I_carre : entropie de Shannon normalisee (grille N x N, K=N^2 cases)
              sur le carre L0^2, calculee UNIQUEMENT parmi les
              particules qui y sont presentes (renormalisee sur cet
              effectif, pas sur l'effectif total du nuage).

    Le produit I_n = f * I_carre (pas une somme) garantit que l'indice
    reste nul si l'un des deux facteurs l'est. Si f=0, retourne
    (0.0, 0.0, 0.0) par convention (aucune entropie calculable sur un
    ensemble vide, mais on garde des historiques de type flottant
    homogenes plutot que None).

    Utilisation : I_n, f, I_carre = indice_melange(nuage, L0, N)

    Retourne : (I_n, f, I_carre)
    """
    x, y = nuage[:, 0], nuage[:, 1]
    dans_carre = np.abs(y) < L0 / 2
    n_dans_carre = np.count_nonzero(dans_carre)
    if n_dans_carre == 0:
        return 0.0, 0.0, 0.0
    f = n_dans_carre / len(nuage)

    bords = np.linspace(-L0 / 2, L0 / 2, N + 1)
    effectifs, _, _ = np.histogram2d(x[dans_carre], y[dans_carre], bins=[bords, bords])
    p = effectifs.ravel() / effectifs.sum()
    p = p[p > 0]
    S = -np.sum(p * np.log(p))
    S_max = np.log(N * N)
    I_carre = S / S_max

    return f * I_carre, f, I_carre


def alpha_beta(Vm, Tx, Ty, L0):
    """
    Convertit des parametres physiques (Vm, Tx, Ty, L0) -- toujours bien
    definis, sans convention necessaire -- vers (alpha, beta). Sert a
    placer un point deja simule sur une figure de balayage : jamais
    utilisee pour piloter une simulation.

    Utilisation : alpha, beta = alpha_beta(60.0, 1.8, 0.5, 200.0)
    """
    alpha = (Vm / L0) * np.sqrt(Tx * Ty)
    beta = Tx / Ty
    return alpha, beta


def params_physiques(alpha, beta, L0, Vm0):
    """
    Convertit (alpha, beta, L0) vers des parametres physiques (Vm, Tx, Ty)
    exploitables par simulation.cycle, en fermant le systeme par
    Vm = Vm0 (une constante physique fixee, voir protocole.py) plutot
    que par une convention arbitraire (Tx*Ty=1, abandonnee) :

        Tx = (alpha * L0 / Vm0) * sqrt(beta)
        Ty = (alpha * L0 / Vm0) / sqrt(beta)

    Vm0 est un vrai choix physique (Tx, Ty sont plus faciles a regler
    experimentalement que Vm) et non un artefact mathematique : les
    quantites Vm*Tx = alpha*L0*sqrt(beta) et Vm*Ty = alpha*L0/sqrt(beta)
    ne dependent que de (alpha, beta, L0), jamais du choix de fermeture
    retenu -- la carte de validite (voir simulation.verifier_parametres)
    est donc identique, quelle que soit la convention utilisee.

    Utilisation : Vm, Tx, Ty = params_physiques(0.20, 0.6, 200.0, 60.0)
    """
    Tx = (alpha * L0 / Vm0) * np.sqrt(beta)
    Ty = (alpha * L0 / Vm0) / np.sqrt(beta)
    return Vm0, Tx, Ty


def simuler(nuage_initial, cycle_fn, L0, N, n_iterations, instants=None):
    """
    Fait avancer un nuage de n_iterations cycles, en calculant I_n, f et
    I_carre a chaque cycle. Conserve un instantane du nuage uniquement
    aux cycles listes dans "instants" (liste explicite fournie par
    l'appelant).

    Parametres
    ----------
    nuage_initial : tableau (n, 2), etat de depart.
    cycle_fn      : fonction nuage -> nuage, deja parametree (voir
                    orchestration.construire_cycle_fn / _physique).
    L0, N         : fenetre d'analyse et resolution de indice_melange.
    n_iterations  : nombre total de cycles a effectuer.
    instants      : liste des cycles a photographier (ex: [0, 5, 100]).
                    None ou liste vide : aucun instantane conserve.

    Retourne
    --------
    (historique_I, historique_f, historique_I_carre, instantanes)
    historique_I, historique_f, historique_I_carre : listes de longueur
        n_iterations+1, valeurs pour n=0..n_iterations.
    instantanes : dict {n: nuage a cet instant}, seulement pour les n
                  demandes dans "instants".
    """
    instants = set(instants) if instants else set()
    nuage = nuage_initial.copy()
    I_n, f, I_carre = indice_melange(nuage, L0, N)
    historique_I, historique_f, historique_I_carre = [I_n], [f], [I_carre]
    instantanes = {}
    if 0 in instants:
        instantanes[0] = nuage.copy()
    for n in range(1, n_iterations + 1):
        nuage = cycle_fn(nuage)
        I_n, f, I_carre = indice_melange(nuage, L0, N)
        historique_I.append(I_n)
        historique_f.append(f)
        historique_I_carre.append(I_carre)
        if n in instants:
            instantanes[n] = nuage.copy()
    return historique_I, historique_f, historique_I_carre, instantanes


def n_etoile(nuage_initial, cycle_fn, L0, N, I_seuil, n_max):
    """
    Plus petit n tel que I_n > I_seuil, en repartant de nuage_initial et
    en appliquant cycle_fn a chaque cycle. S'arrete des que le seuil est
    franchi (contrairement a simuler, qui va toujours jusqu'au bout).

    Retourne : n (entier) si le seuil est franchi avant n_max, None sinon
    ("non converge").
    """
    nuage = nuage_initial.copy()
    I_n, _, _ = indice_melange(nuage, L0, N)
    if I_n > I_seuil:
        return 0
    for n in range(1, n_max + 1):
        nuage = cycle_fn(nuage)
        I_n, _, _ = indice_melange(nuage, L0, N)
        if I_n > I_seuil:
            return n
    return None


def n_depuis_historique(historique_I, I_seuil):
    """
    Relit un historique_I deja calcule (par exemple via simuler) et
    retourne le premier n tel que I_n > I_seuil, sans rien recalculer.

    Retourne : n (entier) ou None si jamais depasse dans l'historique fourni.
    """
    for n, I in enumerate(historique_I):
        if I > I_seuil:
            return n
    return None


def balayage(axe_balaye, grille_balayee, valeurs_fixees, cycle_fn_builder,
             nuage_test, L0, N, I_seuil, n_max):
    """
    Balaye n_etoile sur une grille de valeurs pour un axe (alpha ou beta),
    a plusieurs valeurs fixees de l'autre axe. Le meme nuage_test (une
    seule position initiale) est utilise pour tous les points.

    Un point (alpha, beta) qui violerait simulation.verifier_parametres
    (via cycle_fn_builder, voir orchestration.construire_cycle_fn) est
    enregistre comme None dans le resultat plutot que d'interrompre tout
    le balayage -- un coin de l'espace des parametres invalide ne doit
    pas faire perdre les autres points deja calcules.

    Parametres
    ----------
    axe_balaye       : "alpha" ou "beta".
    grille_balayee   : valeurs de l'axe balaye (ex: np.linspace(...)).
    valeurs_fixees   : liste de valeurs de l'autre axe, une courbe chacune.
    cycle_fn_builder : fonction (alpha, beta) -> cycle_fn. Peut lever
                       ValueError pour un point invalide (rattrapee ici).
    nuage_test       : nuage initial unique, utilise pour tout le balayage.
    L0, N, I_seuil, n_max : voir n_etoile.

    Retourne
    --------
    dict {valeur_fixee: liste de n* ou None (un par point de grille_balayee)}.
    """
    resultats = {}
    for val_fixee in valeurs_fixees:
        n_stars = []
        for val_balayee in grille_balayee:
            if axe_balaye == "alpha":
                alpha, beta = val_balayee, val_fixee
            else:
                alpha, beta = val_fixee, val_balayee
            try:
                cycle_fn = cycle_fn_builder(alpha, beta)
            except ValueError:
                n_stars.append(None)
                continue
            n_stars.append(n_etoile(nuage_test, cycle_fn, L0, N, I_seuil, n_max))
        resultats[val_fixee] = n_stars
    return resultats
