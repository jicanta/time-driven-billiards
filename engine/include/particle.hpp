#pragma once

#include <vector>

#include "geometry.hpp"

// Verlet original necesita tres posiciones consecutivas: r(t - dt) para
// avanzar y r(t + dt) para que la velocidad del paso, que es la diferencia
// centrada (r(t + dt) - r(t - dt)) / (2 dt), quede junto a r(t) y no un paso
// atras. `fresh` es el color: azul mientras la particula no toco un obstaculo,
// rojo despues.
struct Particle {
  Vec2 position;
  Vec2 previous;
  Vec2 next;
  Vec2 velocity;
  Vec2 force;
  bool fresh = true;
};

using Particles = std::vector<Particle>;
