"""
main.py
=======
Execution pure : aucune fonction n'est definie ici. Construit les
nuages, appelle orchestration.py pour faire tourner les simulations et
balayages, envoie les resultats a visualisation.py. Tous les reglages
partages viennent de protocole.py.

Ce fichier n'a pas ete execute : le contenu ci-dessous illustre
l'utilisation prevue, sans qu'aucun resultat n'ait ete verifie.
"""

import numpy as np
import matplotlib.pyplot as plt

import protocole
import simulation
import mesures
import orchestration
import visualisation


if __name__ == "__main__":

    # ------------------------------------------------------------------
    # 1) Simulation unique, deux positions de depart, resultats visuels
    #    avec prise de vue.
    #    Tx, Ty repris de l'ancienne Simulation 2 -- choix arbitraire
    #    pour illustrer l'usage ; Vm vient de protocole.VM0 (fixe pour
    #    tout le protocole), pas de cette ancienne valeur.
    # ------------------------------------------------------------------
    Tx, Ty = 1.8, 0.5

    cycle_fn = orchestration.construire_cycle_fn_physique(
        protocole.VM0, Tx, Ty, protocole.L0, protocole.B_A, protocole.B_D
    )

    nuage_A = simulation.nuage_initial(x0=-24, y0=12, Nx=50, Ny=50, pas=0.05)
    nuage_B = simulation.nuage_initial(x0=-75, y0=-5, Nx=50, Ny=50, pas=0.05)
    labels = ["nuage A (-24, 12)", "nuage B (-75, -5)"]

    instants = [0, 5, 20, 100, 300]
    n_iterations = 300

    resultats_simulation = orchestration.simulation_unique(
        cycle_fn, [nuage_A, nuage_B], protocole.L0, protocole.N,
        n_iterations, instants,
    )

    visualisation.afficher_sequence(resultats_simulation, labels, protocole.L0)
    visualisation.tracer_f_I_carre(resultats_simulation, labels)

    # Points de reference (alpha, beta, n*) issus de cette simulation
    # unique -- calcules une seule fois, reutilises sur les DEUX figures
    # de balayage ci-dessous (2 et 3).
    alpha_sim, beta_sim = mesures.alpha_beta(protocole.VM0, Tx, Ty, protocole.L0)
    points_reference = [
        (alpha_sim, beta_sim, mesures.n_depuis_historique(historique_I, protocole.I_SEUIL))
        for historique_I, _, _, _ in resultats_simulation
    ]
    visualisation.afficher_n_star(labels, points_reference)

    # ------------------------------------------------------------------
    # 2) n*(alpha) a beta fixe -- jusqu'a 4 courbes, points de reference
    #    superposes.
    # ------------------------------------------------------------------
    grille_alpha = np.linspace(0.15, 0.35, 5)
    beta_fixes = [0.5, 1.0, 2.0, 4.0]
    nuage_test = nuage_A  # un seul nuage pour tout le balayage

    resultats_vs_alpha = orchestration.balayage_complet(
        "alpha", grille_alpha, beta_fixes, nuage_test,
        protocole.L0, protocole.N, protocole.I_SEUIL, protocole.N_MAX,
        protocole.VM0, protocole.B_A, protocole.B_D,
    )
    visualisation.tracer_n_star(resultats_vs_alpha, grille_alpha, "alpha", points_reference)

    # ------------------------------------------------------------------
    # 3) n*(beta) a alpha fixe, memes points de reference superposes.
    # ------------------------------------------------------------------
    grille_beta = np.geomspace(0.3, 5.0, 5)
    alpha_fixes = [0.15, 0.20, 0.25, 0.30]

    resultats_vs_beta = orchestration.balayage_complet(
        "beta", grille_beta, alpha_fixes, nuage_test,
        protocole.L0, protocole.N, protocole.I_SEUIL, protocole.N_MAX,
        protocole.VM0, protocole.B_A, protocole.B_D,
    )
    visualisation.tracer_n_star(resultats_vs_beta, grille_beta, "beta", points_reference)

    # ------------------------------------------------------------------
    # 4) I_n(n) pour un couple (alpha, beta) fixe, deux positions
    #    initiales differentes. Reutilise les historiques du point 1).
    # ------------------------------------------------------------------
    historiques = [h for h, _, _, _ in resultats_simulation]
    visualisation.tracer_In_multiple(historiques, labels, protocole.I_SEUIL)

    plt.show()
