"""
visualisation.py
=================
La presentation des resultats deja calcules par mesures.py -- graphique
ou texte. Ce fichier ne relance jamais de calcul lui-meme : il recoit des
historiques, des instantanes ou des resultats de balayage tout faits, et
les met en forme pour l'utilisateur. Trois familles de sorties,
independantes les unes des autres :
- le visuel direct (particules dans le carre du croisement, a un instant) ;
- les resultats agreges en figure (n* ou I_n en fonction de alpha, beta ou n) ;
- les resultats agreges en texte (n* affiche en console).
"""

import matplotlib.pyplot as plt


def afficher_sequence(resultats, labels, L0):
    """
    Une grille d'images, une par instant demande, chaque panneau
    superposant tous les nuages fournis (une couleur par nuage) --
    permet de comparer directement plusieurs positions de depart au
    meme cycle n, sans avoir a sauter d'une figure a l'autre.

    Parametres
    ----------
    resultats : liste de (historique_I, instantanes), un couple par
                nuage, telle que retournee par main.simulation_unique.
                Tous les nuages doivent partager les memes instants --
                garanti par simulation_unique, qui applique un seul
                "instants" a tous les nuages a la fois.
    labels    : liste de legendes, une par nuage, dans le meme ordre que
                "resultats".
    L0        : pour fixer les memes limites d'affichage sur chaque image.

    Retourne : la figure matplotlib (a afficher ensuite avec plt.show()).
    """
    instants = sorted(resultats[0][1].keys())
    fig, axes = plt.subplots(1, len(instants), figsize=(4 * len(instants), 4))
    if len(instants) == 1:
        axes = [axes]
    couleurs = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    for ax, n in zip(axes, instants):
        titre = [f"n={n}"]
        for i, (historique_I, instantanes) in enumerate(resultats):
            pts = instantanes[n]
            ax.scatter(
                pts[:, 0], pts[:, 1], s=1,
                color=couleurs[i % len(couleurs)], label=labels[i],
            )
            titre.append(f"{labels[i]} : I={historique_I[n]:.3f}")
        ax.set_xlim(-L0 / 2, L0 / 2)
        ax.set_ylim(-L0 / 2, L0 / 2)
        ax.set_aspect("equal")
        ax.set_title("\n".join(titre), fontsize=8)

    axes[0].legend(loc="upper left", fontsize=7, markerscale=5)
    fig.tight_layout()
    return fig


def tracer_n_star(resultats_balayage, grille_balayee, axe_balaye, points_reference=None):
    """
    n* en fonction de alpha ou de beta, une courbe par valeur fixee de
    l'autre axe (Figures 1/2 modernisees).

    Parametres
    ----------
    resultats_balayage : dict tel que retourne par mesures.balayage.
    grille_balayee      : les valeurs d'abscisse (memes que passees a balayage).
    axe_balaye          : "alpha" ou "beta" -- pour les labels des axes/legende.
    points_reference    : liste optionnelle de tuples (alpha, beta, n_star),
                           par exemple issus d'une simulation_unique deja
                           lancee, superposes en etoiles sur la figure.
                           A pour vocation d'etre passee aux DEUX figures
                           (vs alpha et vs beta) : chaque point de
                           reference a un alpha et un beta, donc sa place
                           est legitime sur les deux.

    Retourne : la figure matplotlib.
    """
    autre_axe = "beta" if axe_balaye == "alpha" else "alpha"
    fig, ax = plt.subplots()
    for val_fixee, n_stars in resultats_balayage.items():
        ax.plot(grille_balayee, n_stars, marker="o", label=f"{autre_axe} = {val_fixee}")
    if points_reference:
        for alpha, beta, n_star in points_reference:
            if n_star is not None:
                x = alpha if axe_balaye == "alpha" else beta
                ax.scatter([x], [n_star], marker="*", s=150, color="red", zorder=5)
    ax.set_yscale("log")
    ax.set_xlabel(axe_balaye)
    ax.set_ylabel("n*")
    ax.legend()
    return fig


def afficher_n_star(labels, points_reference):
    """
    Affiche en console le n* de chaque nuage d'une simulation_unique deja
    lancee, avec un rappel de ce que represente ce nombre -- ne recalcule
    rien, se contente de relire points_reference (voir main.py, juste
    apres resultats_simulation).

    Parametres
    ----------
    labels           : liste de legendes, une par nuage.
    points_reference : liste de tuples (alpha, beta, n_star), dans le
                        meme ordre que labels.
    """
    print("n* : nombre de cycles necessaires pour que I_n depasse I_seuil")
    for label, (alpha, beta, n_star) in zip(labels, points_reference):
        if n_star is None:
            print(f"  {label} (alpha={alpha:.3f}, beta={beta:.3f}) : "
                  f"seuil jamais atteint sur les cycles simules")
        else:
            print(f"  {label} (alpha={alpha:.3f}, beta={beta:.3f}) : "
                  f"n* = {n_star} cycles")


def tracer_In_multiple(historiques, labels, I_seuil):
    """
    I_n en fonction de n, une courbe par historique fourni -- sert aussi
    bien a comparer des couples (alpha, beta) differents qu'a comparer
    plusieurs positions initiales pour un meme (alpha, beta) (Figure 3
    modernisee).

    Parametres
    ----------
    historiques : liste d'historique_I (chacun tel que retourne par
                  mesures.simuler).
    labels      : liste de legendes, une par historique.
    I_seuil     : trace en pointilles pour reperer le seuil.

    Retourne : la figure matplotlib.
    """
    fig, ax = plt.subplots()
    for historique_I, label in zip(historiques, labels):
        ax.plot(range(len(historique_I)), historique_I, label=label)
    ax.axhline(I_seuil, linestyle="--", color="black", label="I_seuil")
    ax.set_xscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("I_n")
    ax.legend()
    return fig