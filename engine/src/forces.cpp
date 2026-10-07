#include "forces.hpp"

#include <cmath>

namespace {

// Resorte lineal normal entre dos discos: devuelve la fuerza sobre el primero.
// xi = ri + rj - |rj - ri|; si no hay solapamiento la fuerza es nula.
inline Vec2 springForce(const Vec2& from, const Vec2& to, double contact, double stiffness) {
  const Vec2 difference = to - from;
  const double distance = norm(difference);
  const double overlap = contact - distance;
  if (overlap <= 0.0 || distance == 0.0) {
    return {};
  }
  return difference * (-stiffness * overlap / distance);
}

// Centro de la particula imagen de la pared: sobre la normal saliente
// n = r / |r|, a distancia R + r del origen, de modo que su borde toca la
// pared en C = R n. Se recalcula todos los dt porque la particula se desplaza
// tangencialmente durante el choque.
inline Vec2 wallImage(const Vec2& position, double domainRadius, double radius) {
  const double distance = norm(position);
  if (distance == 0.0) {
    return {domainRadius + radius, 0.0};
  }
  return position * ((domainRadius + radius) / distance);
}

}

void computeForces(Particles& particles, const BilliardParameters& billiard,
                   const Obstacles& obstacles, const Grid& grid) {
  const double contact = 2.0 * billiard.radius;
  const double stiffness = billiard.stiffness;

  for (Particle& particle : particles) {
    particle.force = {};
  }
  grid.forEachNeighbourPair([&](int i, int j) {
    const Vec2 force = springForce(particles[i].position, particles[j].position, contact,
                                   stiffness);
    particles[i].force += force;
    particles[j].force -= force;
  });
  for (Particle& particle : particles) {
    for (const Obstacle& obstacle : obstacles) {
      particle.force += springForce(particle.position, obstacle.center,
                                    billiard.radius + obstacle.radius, stiffness);
    }
    particle.force += springForce(particle.position,
                                  wallImage(particle.position, billiard.domainRadius,
                                            billiard.radius),
                                  contact, stiffness);
  }
}
