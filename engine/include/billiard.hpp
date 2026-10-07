#pragma once

#include <random>
#include <string>

#include "obstacle.hpp"
#include "particle.hpp"

// Como se generan las posiciones iniciales. `Random` es la del enunciado
// (adicion secuencial al azar con rechazo de solapamientos); `Hexagonal` pone
// los centros sobre una red triangular y es la unica que entra por encima de
// N = 450, donde la fraccion de area supera el limite del empaquetamiento al
// azar. En las dos, las direcciones son uniformes en [0, 2pi).
enum class Placement { Random, Hexagonal };

Placement placementFromName(const std::string& name);
std::string placementName(Placement placement);

// Parametros del sistema 2 (billar circular). Los valores por defecto son los
// del enunciado. `obstacleOffset` es xo: los dos obstaculos van en (-xo, 0) y
// (+xo, 0); si `obstacles` es false el dominio queda vacio.
struct BilliardParameters {
  double domainRadius = 0.51;
  double radius = 0.0175;
  double mass = 0.025;
  double speed = 1.0;
  double stiffness = 1.0e4;
  double obstacleOffset = 0.0175;
  bool obstacles = true;
  int count = 100;
  unsigned int seed = 1;
  Placement placement = Placement::Random;
};

Obstacles obstaclesOf(const BilliardParameters& billiard);

// Condicion inicial del enunciado: posiciones al azar dentro del circulo sin
// solapar entre si, con los obstaculos ni con la pared, y direcciones
// uniformes en [0, 2pi) con rapidez v0.
Particles generateParticles(const BilliardParameters& billiard,
                            const Obstacles& obstacles, std::mt19937& generator);

// Fraccion de area ocupada por las particulas, N pi r^2 / (pi R^2).
double packingFraction(const BilliardParameters& billiard);
