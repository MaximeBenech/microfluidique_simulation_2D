"""
protocole.py
============
Uniquement des constantes : le protocole partage par toute l'etude
(largeur de canal, vitesse fixee, position des barrieres, reglages de
mesure). Rien d'autre ne doit vivre ici -- ni fonction, ni logique.

Le jour ou b_a et b_d (ou Vm0, L0) doivent etre balayes plutot que
fixes, c'est ici -- et dans orchestration.py, qui les consomme -- que
ca se decide. Ni simulation.py ni mesures.py n'ont besoin d'en savoir
quoi que ce soit : ils recoivent ces valeurs en parametres, ils ne les
lisent jamais directement ici.
"""

# Largeur du canal principal (aussi le cote du carre de rencontre L0^2).
L0 = 200.0

# Vitesse moyenne, fixee une fois pour toutes (fermeture du systeme
# (alpha, beta) -> (Vm, Tx, Ty) par Vm = Vm0, voir mesures.params_physiques).
VM0 = 60.0

# Position des barrieres de rebond en y (voir simulation.etape_y).
# Valeurs par defaut : coincident avec les bords du carre, comportement
# identique a une reflexion simple a L0/2.
B_A = 3 * L0 / 2
B_D = -L0 / 2

# Reglages de mesure.
N = 12
I_SEUIL = 0.9
N_MAX = 150
