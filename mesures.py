"""
mesures.py
==========
Tout ce qui sert a MESURER un nuage ou une suite de nuages, sans jamais
savoir comment ils ont ete produits. Ce fichier ne doit jamais importer
simulation.py : il recoit un "cycle_fn" (une fonction nuage -> nuage) deja
toute prete depuis main.py, et se contente de l'appeler. C'est ce
decouplage qui permettra d'ajouter la diffusion dans simulation.py plus
tard sans toucher une ligne ici.
"""

import numpy as np


def indice_melange(nuage, L0, N):
    """
    Indice de melange I : entropie de Shannon sur une grille N x N
    (K = N*N cases) couvrant [-L0/2, L0/2]^2, normalisee par son maximum
    theorique log(K). I proche de 0 : tout concentre dans une case.
    I proche de 1 : particules equireparties entre les cases.

    Utilisation : I = indice_melange(nuage, L0, N)
    """
    bords = np.linspace(-L0 / 2, L0 / 2, N + 1)
    effectifs, _, _ = np.histogram2d(nuage[:, 0], nuage[:, 1], bins=[bords, bords])
    p = effectifs.ravel() / effectifs.sum()
    p = p[p > 0]
    S = -np.sum(p * np.log(p))
    S_max = np.log(N * N)
    return S / S_max


def alpha_beta(Vm, Tx, Ty, L0):
    """
    Convertit des parametres physiques (Vm, Tx, Ty, L0) -- toujours bien
    definis, sans convention necessaire -- vers (alpha, beta). Sert a
    placer un point deja simule (par exemple une simulation_unique) sur
    une figure de balayage : jamais utilisee pour piloter une simulation.

    Utilisation : alpha, beta = alpha_beta(60.0, 1.8, 0.5, 200.0)
    """
    alpha = (Vm / L0) * np.sqrt(Tx * Ty)
    beta = Tx / Ty
    return alpha, beta


def params_physiques(alpha, beta, L0):
    """
    Convertit (alpha, beta, L0) vers des parametres physiques (Vm, Tx, Ty)
    exploitables par simulation.cycle. Necessaire pour les balayages, ou
    l'on choisit (alpha, beta) et ou il faut en deduire des valeurs
    physiques concretes.

    (alpha, beta) ne fournissent que 2 equations pour 3 inconnues : le
    systeme est referme avec la convention Tx*Ty = 1 (un choix d'echelle
    de temps arbitraire, pas une contrainte physique du dispositif -- voir
    plan_documentation.md, section 3). Consequence a garder en tete : Vm
    varie donc avec (alpha, beta) a chaque point d'un balayage, alors
    qu'en pratique Tx et Ty sont plus faciles a regler que Vm.

    Utilisation : Vm, Tx, Ty = params_physiques(0.20, 0.6, 200.0)
    """
    Tx = np.sqrt(beta)
    Ty = 1 / np.sqrt(beta)
    Vm = alpha * L0
    return Vm, Tx, Ty


def simuler(nuage_initial, cycle_fn, L0, N, n_iterations, instants=None):
    """
    Fait avancer un nuage de n_iterations cycles, en calculant I_n a
    chaque cycle. Conserve un instantane du nuage uniquement aux cycles
    listes dans "instants" (liste explicite fournie par l'appelant --
    aucune regle automatique du type puissances ou multiples), pour
    rester leger si on ne veut que les chiffres.

    Parametres
    ----------
    nuage_initial : tableau (n, 2), etat de depart.
    cycle_fn      : fonction nuage -> nuage, deja parametree (voir
                    main.construire_cycle_fn / construire_cycle_fn_physique).
    L0, N         : fenetre d'analyse et resolution de indice_melange.
    n_iterations  : nombre total de cycles a effectuer.
    instants      : liste des cycles a photographier (ex: [0, 5, 100]).
                    None ou liste vide : aucun instantane conserve.

    Retourne
    --------
    (historique_I, instantanes)
    historique_I : liste de longueur n_iterations+1, I_n pour n=0..n_iterations.
    instantanes  : dict {n: nuage a cet instant}, seulement pour les n
                   demandes dans "instants".
    """
    instants = set(instants) if instants else set()
    nuage = nuage_initial.copy()
    historique_I = [indice_melange(nuage, L0, N)]
    instantanes = {}
    if 0 in instants:
        instantanes[0] = nuage.copy()
    for n in range(1, n_iterations + 1):
        nuage = cycle_fn(nuage)
        historique_I.append(indice_melange(nuage, L0, N))
        if n in instants:
            instantanes[n] = nuage.copy()
    return historique_I, instantanes


def n_etoile(nuage_initial, cycle_fn, L0, N, I_seuil, n_max):
    """
    Plus petit n tel que I_n > I_seuil, en repartant de nuage_initial et
    en appliquant cycle_fn a chaque cycle. S'arrete des que le seuil est
    franchi (contrairement a simuler, qui va toujours jusqu'au bout) --
    plus economique dans un balayage, ou l'on ne veut pas payer n_max
    cycles complets a chaque point teste.

    Retourne : n (entier) si le seuil est franchi avant n_max, None sinon
    ("non converge").
    """
    nuage = nuage_initial.copy()
    if indice_melange(nuage, L0, N) > I_seuil:
        return 0
    for n in range(1, n_max + 1):
        nuage = cycle_fn(nuage)
        if indice_melange(nuage, L0, N) > I_seuil:
            return n
    return None


def n_depuis_historique(historique_I, I_seuil):
    """
    Relit un historique_I deja calcule (par exemple via simuler) et
    retourne le premier n tel que I_n > I_seuil, sans rien recalculer.
    Utile pour deduire un n* a partir d'une simulation_unique deja lancee,
    afin de le superposer ensuite a une figure de balayage.

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
    a plusieurs valeurs fixees de l'autre axe (une courbe par valeur
    fixee -- 4 a 6 recommande pour rester lisible sur une figure). Le
    meme nuage_test (une seule position initiale) est utilise pour tous
    les points du balayage.

    Parametres
    ----------
    axe_balaye       : "alpha" ou "beta".
    grille_balayee   : valeurs de l'axe balaye (ex: np.linspace(...)).
    valeurs_fixees   : liste de valeurs de l'autre axe, une courbe chacune.
    cycle_fn_builder : fonction (alpha, beta) -> cycle_fn (voir
                       main.construire_cycle_fn). Encapsule params_physiques.
    nuage_test       : nuage initial unique, utilise pour tout le balayage.
    L0, N, I_seuil, n_max : voir n_etoile.

    Retourne
    --------
    dict {valeur_fixee: liste de n* (un par point de grille_balayee)}.
    """
    resultats = {}
    for val_fixee in valeurs_fixees:
        n_stars = []
        for val_balayee in grille_balayee:
            if axe_balaye == "alpha":
                alpha, beta = val_balayee, val_fixee
            else:
                alpha, beta = val_fixee, val_balayee
            cycle_fn = cycle_fn_builder(alpha, beta)
            n_stars.append(n_etoile(nuage_test, cycle_fn, L0, N, I_seuil, n_max))
        resultats[val_fixee] = n_stars
    return resultats
