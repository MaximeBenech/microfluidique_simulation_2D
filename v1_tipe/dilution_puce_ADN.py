# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

# ── Flèches de direction : →  ←  ↑  ↓
SIGNS  = {'x+': 1, 'x-': -1, 'y+': 1, 'y-': -1}  # signe du déplacement
ARROWS = {'x+': '→', 'x-': '←', 'y+': '↑', 'y-': '↓'}  # symbole visuel

# ── Grille initiale de particules
def etape0(x0, y0, Nx0, Ny0, pas):
    Kx, Ky = np.meshgrid(np.arange(Nx0), np.arange(Ny0))
    pts = np.vstack(((Kx * pas + x0).ravel(),
                     (Ky * pas + y0).ravel())).T
    return pts  # tableau (N, 2)

# ── Déplacement parabolique de Poiseuille sur un demi-cycle
def etape(Vm, L0, t, L, direction):
    Lx, Ly = L.T
    sign = SIGNS[direction]
    if direction in ('x+', 'x-'):           # → ou ← : profil selon y
        mask = np.abs(Ly) < L0 / 2
        Lx = np.where(mask,
                      Lx + sign * 1.5 * Vm * t * (1 - 4*Ly**2 / L0**2),
                      Lx)
    else:                                    # ↑ ou ↓ : profil selon x
        mask = np.abs(Lx) < L0 / 2
        Ly = np.where(mask,
                      Ly + sign * 1.5 * Vm * t * (1 - 4*Lx**2 / L0**2),
                      Ly)
    return np.vstack((Lx, Ly)).T

# ── Séquence d'un cycle complet : → ↑ ← ↓  (mixage chaotique)
def cycle(Vm, L0, Tx, Ty, L):
    for d, t in (('x+', Tx), ('y+', Ty), ('x-', Tx), ('y-', Ty)):
        L = etape(Vm, L0, t, L, d)
    return L

# ── Évolution sur p cycles, en retenant ~10 instantanés réguliers
def dilution_with_steps(Vm, L0, Tx, Ty, R, p):
    step_size = max(p // 9, 1)          # fréquence d'enregistrement
    L, steps = R.copy(), [R.copy()]
    for i in range(p):
        L = cycle(Vm, L0, Tx, Ty, L)
        if (i + 1) % step_size == 0 or i == p - 1:
            steps.append(L.copy())
    return steps[:10]                   # 10 instantanés max

# ── Tracé d'un nuage de points dans un sous-graphique
def plot_subplot(ax, pts, L0, color, title):
    ax.plot(pts[:, 0], pts[:, 1], color=color,
            marker='.', markersize=1, ls='None')
    ax.set_xlim(-L0/2, L0/2)
    ax.set_ylim(-L0/2, L0/2)
    ax.set_title(title)
    ax.set_aspect('equal')

# ── Figure 2×5 comparant rouge et bleu au fil des itérations
def solution2(Nx1, Ny1, Nx2, Ny2, pas, x1, y1, x2, y2, Vm, L0, Tx, Ty, p):
    N_red  = etape0(x1, y1, Nx1, Ny1, pas)   # nuage rouge (position initiale 1)
    N_blue = etape0(x2, y2, Nx2, Ny2, pas)   # nuage bleu  (position initiale 2)

    red_steps  = dilution_with_steps(Vm, L0, Tx, Ty, N_red,  p)
    blue_steps = dilution_with_steps(Vm, L0, Tx, Ty, N_blue, p)

    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    plt.subplots_adjust(wspace=0.3, hspace=0.3)

    step_size = max(p // 9, 1)
    for idx, ax in enumerate(axes.flatten()):
        if idx >= len(red_steps):
            break
        it = idx * step_size
        plot_subplot(ax, red_steps[idx],  L0, 'red',  f'Itération {it}')
        plot_subplot(ax, blue_steps[idx], L0, 'blue', f'Itération {it}')

    plt.show()

# ══════════════════════════════════════════════════════════════════
# Simulation 1 — mauvaise dilution (zones mortes pour les deux)
# ══════════════════════════════════════════════════════════════════
Nx1, Ny1, Nx2, Ny2             = 150, 150, 150, 150
pas, x1, y1, x2, y2        = 0.05, -24, 12, 12, 24
Vm, L0, Tx, Ty, p          = 30, 205, 1.1, 1.5, 1000
solution2(Nx1, Ny1, Nx2, Ny2, pas, x1, y1, x2, y2, Vm, L0, Tx, Ty, p)

# ══════════════════════════════════════════════════════════════════
# Simulation 2 — bleu en zone morte, rouge bien dilué
# ══════════════════════════════════════════════════════════════════
Nx1, Ny1, Nx2, Ny2             = 150, 150, 150, 150
pas, x1, y2, x2, y2        = 0.05, -24, 12, -75, -5
Vm, L0, Tx, Ty, p          = 60, 200, 1.8, 0.5, 500
solution2(Nx1, Ny1, Nx2, Ny2, pas, x1, y1, x2, y2, Vm, L0, Tx, Ty, p)
