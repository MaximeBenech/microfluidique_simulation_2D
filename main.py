"""
main.py
=======
La "recette" : definit le protocole partage (L0, N, I_seuil, n_max),
construit les cycle_fn a partir des parametres choisis par l'utilisateur
(physiques directs ou alpha/beta), et orchestre les appels a
simulation.py, mesures.py et visualisation.py. Aucune physique ni aucune
mesure ne vit ici -- uniquement de l'assemblage.
"""

import numpy as np
import matplotlib.pyplot as plt

import simulation
import mesures
import visualisation


def construire_cycle_fn_physique(Vm, Tx, Ty, L0):
    """
    Construit un cycle_fn (nuage -> nuage) a partir de parametres
    physiques directs. Usage privilegie pour une simulation_unique :
    (Vm, Tx, Ty) suffisent toujours, sans convention necessaire.
    """
    return lambda nuage: simulation.cycle(nuage, Vm, L0, Tx, Ty)


def construire_cycle_fn(alpha, beta, L0):
    """
    Construit un cycle_fn a partir de (alpha, beta) -- passe par
    mesures.params_physiques (et donc par la convention Tx*Ty=1). Usage
    privilegie pour un balayage, ou l'on choisit une grille de (alpha,
    beta) plutot que des valeurs physiques directes.
    """
    Vm, Tx, Ty = mesures.params_physiques(alpha, beta, L0)
    return lambda nuage: simulation.cycle(nuage, Vm, L0, Tx, Ty)


def simulation_unique(cycle_fn, nuages_initiaux, L0, N, n_iterations, instants):
    """
    Lance le meme cycle_fn sur une liste de nuages initiaux (une position
    de depart par nuage) -- permet de comparer plusieurs positions a
    (alpha, beta) fixe, sans dupliquer les parametres physiques.

    Retourne : liste de (historique_I, instantanes), un couple par nuage,
    dans le meme ordre que nuages_initiaux.
    """
    return [
        mesures.simuler(nuage0, cycle_fn, L0, N, n_iterations, instants)
        for nuage0 in nuages_initiaux
    ]


def balayage_complet(axe_balaye, grille_balayee, valeurs_fixees, nuage_test,
                      L0, N, I_seuil, n_max):
    """
    Execute un balayage complet (alpha ou beta) en construisant les
    cycle_fn necessaires via construire_cycle_fn -- pret a etre trace par
    visualisation.tracer_n_star.
    """
    return mesures.balayage(
        axe_balaye, grille_balayee, valeurs_fixees,
        lambda a, b: construire_cycle_fn(a, b, L0),
        nuage_test, L0, N, I_seuil, n_max,
    )


if __name__ == "__main__":

    # ------------------------------------------------------------------
    # Protocole partage, defini une seule fois pour tout cet exemple.
    # ------------------------------------------------------------------
    L0 = 200.0      # Choix pour cet exemple : la largeur de canal de
                    # l'ancienne "Simulation 2", pas les 205 retenus dans
                    # la synthese precedente -- purement pour reutiliser
                    # des valeurs deja discutees, sans autre signification.
    N = 12
    I_seuil = 0.8
    n_max = 500

    # ------------------------------------------------------------------
    # 1) Simulation unique, deux positions de depart, resultats visuels
    #    avec prise de vue -- une seule serie de panneaux, les deux
    #    nuages superposes sur chaque panneau (voir
    #    visualisation.afficher_sequence).
    #    Parametres physiques repris de l'ancienne Simulation 2 -- choix
    #    arbitraire pour illustrer l'usage, aucun calcul n'a ete fait,
    #    ces valeurs ne prejugent en rien du melange obtenu par l'une ou
    #    l'autre position.
    # ------------------------------------------------------------------
    Vm, Tx, Ty = 65.0, 1.8, 0.5
    cycle_fn = construire_cycle_fn_physique(Vm, Tx, Ty, L0)

    nuage_A = simulation.nuage_initial(x0=-24, y0=12, Nx=50, Ny=50, pas=0.05)
    nuage_B = simulation.nuage_initial(x0=-75, y0=-5, Nx=50, Ny=50, pas=0.05)
    labels = ["nuage A (-24, 12)", "nuage B (-75, -5)"]

    instants = [0, 5, 25, 150, 300, 600]
    n_iterations = 1000

    resultats_simulation = simulation_unique(
        cycle_fn, [nuage_A, nuage_B], L0, N, n_iterations, instants
    )

    visualisation.afficher_sequence(resultats_simulation, labels, L0)

    # Points de reference (alpha, beta, n*) issus de cette simulation
    # unique -- calcules une seule fois ici, reutilises sur les DEUX
    # figures de balayage ci-dessous (2 et 3), puisqu'un point de
    # reference a a la fois un alpha et un beta.
    alpha_sim, beta_sim = mesures.alpha_beta(Vm, Tx, Ty, L0)
    points_reference = [
        (alpha_sim, beta_sim, mesures.n_depuis_historique(historique_I, I_seuil))
        for historique_I, _ in resultats_simulation
    ]
    visualisation.afficher_n_star(labels, points_reference)

    # ------------------------------------------------------------------
    # 2) n*(alpha) a beta fixe -- jusqu'a 4 courbes, points de reference
    #    de la simulation unique superposes.
    # ------------------------------------------------------------------
    grille_alpha = np.linspace(0.15, 0.35, 100)
    beta_fixes = [0.5, 1.0, 2.0, 4.0]
    nuage_test = nuage_A  # un seul nuage pour tout le balayage

    resultats_vs_alpha = balayage_complet(
        "alpha", grille_alpha, beta_fixes, nuage_test, L0, N, I_seuil, n_max
    )
    visualisation.tracer_n_star(resultats_vs_alpha, grille_alpha, "alpha", points_reference)

    # ------------------------------------------------------------------
    # 3) n*(beta) a alpha fixe, memes points de reference superposes.
    # ------------------------------------------------------------------
    grille_beta = np.geomspace(0.3, 5.0, 100)
    alpha_fixes = [0.15, 0.20, 0.25, 0.30]

    resultats_vs_beta = balayage_complet(
        "beta", grille_beta, alpha_fixes, nuage_test, L0, N, I_seuil, n_max
    )
    visualisation.tracer_n_star(resultats_vs_beta, grille_beta, "beta", points_reference)

    # ------------------------------------------------------------------
    # 4) I_n(n) pour un couple (alpha, beta) fixe, deux positions
    #    initiales differentes.
    #    Reutilise directement les historiques du point 1) : meme
    #    (Vm, Tx, Ty) donc meme (alpha, beta) pour les nuages A et B --
    #    sans aucune hypothese sur lequel des deux melange le mieux.
    # ------------------------------------------------------------------
    historiques = [h for h, _ in resultats_simulation]
    visualisation.tracer_In_multiple(historiques, labels, I_seuil)

    plt.show()