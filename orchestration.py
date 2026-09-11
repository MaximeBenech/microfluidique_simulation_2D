"""
orchestration.py
=================
Le seul fichier qui a le droit d'importer a la fois simulation.py et
mesures.py, pour les relier. Construit les cycle_fn a partir des
parametres choisis (physiques directs ou alpha/beta), en verifiant leur
validite via simulation.verifier_parametres avant de renvoyer quoi que
ce soit -- toute construction invalide echoue au plus tot, avec un
message explicite.

Ce fichier consomme b_a, b_d (et L0, Vm0) tels que definis dans
protocole.py, mais ne les lit jamais lui-meme : ils lui sont passes en
parametres par main.py. Le jour ou b_a, b_d doivent etre balayes
plutot que fixes, c'est ici que la boucle supplementaire s'ajoute --
ni simulation.py ni mesures.py n'ont besoin de changer.
"""

import simulation
import mesures


def construire_cycle_fn_physique(Vm, Tx, Ty, L0, b_a, b_d):
    """
    Construit un cycle_fn (nuage -> nuage) a partir de parametres
    physiques directs -- usage privilegie pour une simulation_unique :
    (Vm, Tx, Ty) suffisent toujours, sans convention necessaire.

    Leve ValueError (via simulation.verifier_parametres) si ces
    parametres ne peuvent pas etre simules correctement.
    """
    simulation.verifier_parametres(Vm, Ty, b_a, b_d)
    return lambda nuage: simulation.cycle(nuage, Vm, L0, Tx, Ty, b_a, b_d)


def construire_cycle_fn(alpha, beta, L0, Vm0, b_a, b_d):
    """
    Construit un cycle_fn a partir de (alpha, beta) -- passe par
    mesures.params_physiques (fermeture par Vm=Vm0). Usage privilegie
    pour un balayage, ou l'on choisit une grille de (alpha, beta) plutot
    que des valeurs physiques directes.

    Leve ValueError si le point (alpha, beta) resultant est invalide.
    """
    Vm, Tx, Ty = mesures.params_physiques(alpha, beta, L0, Vm0)
    simulation.verifier_parametres(Vm, Ty, b_a, b_d)
    return lambda nuage: simulation.cycle(nuage, Vm, L0, Tx, Ty, b_a, b_d)


def simulation_unique(cycle_fn, nuages_initiaux, L0, N, n_iterations, instants):
    """
    Lance le meme cycle_fn sur une liste de nuages initiaux (une
    position de depart par nuage) -- permet de comparer plusieurs
    positions a (alpha, beta) fixe, sans dupliquer les parametres
    physiques.

    Retourne : liste de (historique_I, instantanes), un couple par
    nuage, dans le meme ordre que nuages_initiaux.
    """
    return [
        mesures.simuler(nuage0, cycle_fn, L0, N, n_iterations, instants)
        for nuage0 in nuages_initiaux
    ]


def balayage_complet(axe_balaye, grille_balayee, valeurs_fixees, nuage_test,
                      L0, N, I_seuil, n_max, Vm0, b_a, b_d):
    """
    Execute un balayage complet (alpha ou beta) en construisant les
    cycle_fn necessaires via construire_cycle_fn -- pret a etre trace
    par visualisation.tracer_n_star.
    """
    return mesures.balayage(
        axe_balaye, grille_balayee, valeurs_fixees,
        lambda a, b: construire_cycle_fn(a, b, L0, Vm0, b_a, b_d),
        nuage_test, L0, N, I_seuil, n_max,
    )
