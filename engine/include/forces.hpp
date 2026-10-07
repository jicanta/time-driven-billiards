#pragma once

#include "billiard.hpp"
#include "grid.hpp"
#include "obstacle.hpp"
#include "particle.hpp"

// Fuerza de contacto del enunciado: resorte lineal en la direccion normal,
// sin friccion ni disipacion.
//
//   F_i = sum_j -k xi_ij e_ij,   xi_ij = r_i + r_j - |r_j - r_i| > 0,
//   e_ij = (r_j - r_i) / |r_j - r_i|
//
// Los j son las demas particulas, los dos obstaculos fijos y la particula
// imagen de la pared, cuyo centro se recalcula todos los dt sobre la normal
// saliente: r_img = (R + r) n, con n = r_i / |r_i|, y xi_iw = |r_i| + r - R.
void computeForces(Particles& particles, const BilliardParameters& billiard,
                   const Obstacles& obstacles, const Grid& grid);
