#pragma once

#include <vector>

#include "billiard.hpp"
#include "forces.hpp"
#include "grid.hpp"
#include "obstacle.hpp"
#include "particle.hpp"

// Una conversion: el instante en que la particula `index` toca por primera vez
// el obstaculo `obstacle` y pasa de fresca a usada.
struct Conversion {
  double time = 0.0;
  int index = -1;
  int obstacle = -1;
};

// Dinamica molecular regida por el paso temporal con el esquema de Verlet
// original (Teorica 4, diapositiva 13):
//
//   r(t + dt) = 2 r(t) - r(t - dt) + dt^2 F(t) / m
//   v(t)      = [r(t + dt) - r(t - dt)] / (2 dt)
//
// La posicion anterior del primer paso se estima con Euler evaluado en -dt
// (diapositiva 14): r(-dt) = r(0) - v(0) dt + dt^2 F(0) / (2 m). La velocidad
// de un paso queda conocida al cerrar el paso siguiente, asi que el estado que
// se guarda en el paso n lleva r(t_n) y v(t_n).
class Simulation {
 public:
  Simulation(const BilliardParameters& billiard, Particles particles, double step);

  // Avanza un paso de integracion. Devuelve false cuando ya no queda ninguna
  // particula fresca y se pidio terminar ahi.
  void step();

  double time() const { return time_; }
  long steps() const { return steps_; }
  double timeStep() const { return step_; }
  int used() const { return used_; }
  const Particles& particles() const { return particles_; }
  const Obstacles& obstacles() const { return obstacles_; }
  const BilliardParameters& billiard() const { return billiard_; }
  const Grid& grid() const { return grid_; }
  // Conversiones ocurridas en el ultimo paso.
  const std::vector<Conversion>& conversions() const { return conversions_; }

 private:
  void convert();

  BilliardParameters billiard_;
  Obstacles obstacles_;
  Particles particles_;
  Grid grid_;
  double step_;
  double time_ = 0.0;
  long steps_ = 0;
  int used_ = 0;
  std::vector<Conversion> conversions_;
};
