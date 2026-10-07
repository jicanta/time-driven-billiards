#include "simulation.hpp"

#include <utility>

namespace {

// r(-dt) con Euler evaluado en -dt (Teorica 4, diapositiva 14).
Vec2 previousPosition(const Particle& particle, double mass, double step) {
  return particle.position - particle.velocity * step +
         particle.force * (0.5 * step * step / mass);
}

}

// Invariante al salir del constructor y de cada step():
//   position = r(t), velocity = v(t), previous = r(t - dt), next = r(t + dt),
//   force = F(t). La velocidad del enunciado (diferencia centrada) necesita
//   r(t + dt), asi que se adelanta un paso de posiciones para que el estado
//   que se guarda lleve la posicion y la velocidad del mismo instante.
Simulation::Simulation(const BilliardParameters& billiard, Particles particles, double step)
    : billiard_(billiard),
      obstacles_(obstaclesOf(billiard)),
      particles_(std::move(particles)),
      grid_(billiard.domainRadius, 2.0 * billiard.radius),
      step_(step) {
  grid_.rebuild(particles_);
  computeForces(particles_, billiard_, obstacles_, grid_);
  for (Particle& particle : particles_) {
    particle.previous = previousPosition(particle, billiard_.mass, step_);
    particle.next = particle.position * 2.0 - particle.previous +
                    particle.force * (step_ * step_ / billiard_.mass);
    particle.velocity = (particle.next - particle.previous) * (0.5 / step_);
  }
  convert();
}

void Simulation::step() {
  conversions_.clear();
  for (Particle& particle : particles_) {
    particle.previous = particle.position;
    particle.position = particle.next;
  }
  time_ = ++steps_ * step_;

  grid_.rebuild(particles_);
  computeForces(particles_, billiard_, obstacles_, grid_);
  for (Particle& particle : particles_) {
    particle.next = particle.position * 2.0 - particle.previous +
                    particle.force * (step_ * step_ / billiard_.mass);
    particle.velocity = (particle.next - particle.previous) * (0.5 / step_);
  }
  convert();
}

// Una particula fresca pasa a usada en cuanto se solapa con cualquiera de los
// dos obstaculos (xi > 0). Solo cuenta el primer contacto: despues sigue
// moviendose e interactuando igual, asi que N y la densidad no cambian.
void Simulation::convert() {
  for (int index = 0; index < static_cast<int>(particles_.size()); ++index) {
    Particle& particle = particles_[index];
    if (!particle.fresh) {
      continue;
    }
    for (int k = 0; k < static_cast<int>(obstacles_.size()); ++k) {
      const double contact = billiard_.radius + obstacles_[k].radius;
      if (squaredNorm(particle.position - obstacles_[k].center) < contact * contact) {
        particle.fresh = false;
        ++used_;
        conversions_.push_back({time_, index, k});
        break;
      }
    }
  }
}
