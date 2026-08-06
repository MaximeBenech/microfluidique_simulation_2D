\# Chaotic Mixing by Baker's Transformation



Python simulation of chaotic advection inspired by the baker's transformation, developed during a French CPGE MP TIPE.



The program models the dilution of two initially localized particle clouds inside a square microfluidic domain subjected to alternating Poiseuille flows along the horizontal and vertical directions.



The resulting stretching and folding mechanisms accelerate mixing and reproduce the chaotic behavior exploited in microfluidic DNA chips.





\## Model



Each cycle is composed of four forced flow phases:



→  Horizontal Poiseuille flow



↑  Vertical Poiseuille flow



←  Reverse horizontal flow



↓  Reverse vertical flow



After many cycles, the particle clouds are stretched and folded, producing chaotic mixing.





\## Parameters



| Parameter    | Meaning                                        |

| ------------ | ---------------------------------------------- |

| `Vm`         | Mean flow velocity                             |

| `L0`         | Side length of the square computational domain |

| `Tx`         | Duration of horizontal half-cycle              |

| `Ty`         | Duration of vertical half-cycle                |

| `p`          | Number of complete mixing cycles               |

| `Nx1`, `Ny1` | Dimensions (in particles) of the first cloud   |

| `Nx2`, `Ny2` | Dimensions (in particles) of the second cloud  |

| `x1`, `y1`   | Initial lower-left corner of the first cloud   |

| `x2`, `y2`   | Initial lower-left corner of the second cloud  |

| `pas`        | Spatial discretization step between particles  |



