#include "billiard.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr long kMaxAttemptsPerParticle = 1000000;

bool overlapsAny(const Vec2& position, double radius, const Particles& placed,
                 const Obstacles& obstacles) {
  for (const Particle& other : placed) {
    const double reach = 2.0 * radius;
    if (squaredNorm(position - other.position) < reach * reach) {
      return true;
    }
  }
  for (const Obstacle& obstacle : obstacles) {
    const double reach = radius + obstacle.radius;
    if (squaredNorm(position - obstacle.center) < reach * reach) {
      return true;
    }
  }
  return false;
}

bool overlapsObstacle(const Vec2& position, double radius, const Obstacles& obstacles) {
  for (const Obstacle& obstacle : obstacles) {
    const double reach = radius + obstacle.radius;
    if (squaredNorm(position - obstacle.center) < reach * reach) {
      return true;
    }
  }
  return false;
}

// Centros de una red triangular de paso `spacing` contenidos en el disco de
// radio R - r y que no tocan ningun obstaculo.
std::vector<Vec2> hexagonalSites(const BilliardParameters& billiard,
                                 const Obstacles& obstacles, double spacing) {
  const double reach = billiard.domainRadius - billiard.radius;
  const double rowHeight = spacing * std::sqrt(3.0) / 2.0;
  const int rows = static_cast<int>(std::floor(reach / rowHeight));
  const int columns = static_cast<int>(std::floor(reach / spacing)) + 1;
  std::vector<Vec2> sites;
  for (int row = -rows; row <= rows; ++row) {
    const double y = row * rowHeight;
    const double shift = (std::abs(row) % 2 == 0) ? 0.0 : 0.5 * spacing;
    for (int column = -columns; column <= columns; ++column) {
      const Vec2 position{column * spacing + shift, y};
      if (squaredNorm(position) > reach * reach) {
        continue;
      }
      if (!overlapsObstacle(position, billiard.radius, obstacles)) {
        sites.push_back(position);
      }
    }
  }
  return sites;
}

Particles randomPlacement(const BilliardParameters& billiard, const Obstacles& obstacles,
                          std::mt19937& generator) {
  // Posicion uniforme en el disco de radio R - r: el radio se sortea como
  // sqrt(u) para que la densidad sea uniforme en area y no se amontone en el
  // centro.
  const double reach = billiard.domainRadius - billiard.radius;
  std::uniform_real_distribution<double> unit(0.0, 1.0);
  std::uniform_real_distribution<double> angle(0.0, 2.0 * M_PI);

  Particles particles;
  particles.reserve(billiard.count);
  for (int index = 0; index < billiard.count; ++index) {
    Particle particle;
    long attempts = 0;
    do {
      if (++attempts > kMaxAttemptsPerParticle) {
        throw std::runtime_error(
            "no se pudo ubicar la particula " + std::to_string(index + 1) + " de " +
            std::to_string(billiard.count) +
            " sin solapamientos (probar --placement hexagonal)");
      }
      const double distance = reach * std::sqrt(unit(generator));
      const double theta = angle(generator);
      particle.position = {distance * std::cos(theta), distance * std::sin(theta)};
    } while (overlapsAny(particle.position, billiard.radius, particles, obstacles));
    particles.push_back(particle);
  }
  return particles;
}

Particles hexagonalPlacement(const BilliardParameters& billiard, const Obstacles& obstacles,
                             std::mt19937& generator) {
  const double minimum = 2.0 * billiard.radius * (1.0 + 1e-9);
  const double area = M_PI * (billiard.domainRadius - billiard.radius) *
                      (billiard.domainRadius - billiard.radius);
  double spacing = std::sqrt(2.0 * area / (std::sqrt(3.0) * std::max(billiard.count, 1)));
  std::vector<Vec2> sites;
  while (true) {
    if (spacing < minimum) {
      throw std::runtime_error("la red hexagonal no aloja " + std::to_string(billiard.count) +
                               " particulas sin que se toquen");
    }
    sites = hexagonalSites(billiard, obstacles, spacing);
    if (static_cast<int>(sites.size()) >= billiard.count) {
      break;
    }
    spacing *= 0.99;
  }
  std::shuffle(sites.begin(), sites.end(), generator);
  Particles particles;
  particles.reserve(billiard.count);
  for (int index = 0; index < billiard.count; ++index) {
    Particle particle;
    particle.position = sites[index];
    particles.push_back(particle);
  }
  return particles;
}

}

Placement placementFromName(const std::string& name) {
  if (name == "random") {
    return Placement::Random;
  }
  if (name == "hexagonal") {
    return Placement::Hexagonal;
  }
  throw std::invalid_argument("ubicacion desconocida: " + name + " (random|hexagonal)");
}

std::string placementName(Placement placement) {
  return placement == Placement::Hexagonal ? "hexagonal" : "random";
}

Obstacles obstaclesOf(const BilliardParameters& billiard) {
  if (!billiard.obstacles) {
    return {};
  }
  const double offset = billiard.obstacleOffset;
  if (offset < billiard.radius || offset > billiard.domainRadius - billiard.radius) {
    throw std::invalid_argument(
        "xo fuera de rango: debe estar entre r y R - r (los obstaculos no pueden "
        "solaparse entre si ni salir del dominio)");
  }
  return {{{-offset, 0.0}, billiard.radius}, {{offset, 0.0}, billiard.radius}};
}

Particles generateParticles(const BilliardParameters& billiard,
                            const Obstacles& obstacles, std::mt19937& generator) {
  if (billiard.count < 0) {
    throw std::invalid_argument("N no puede ser negativo");
  }
  Particles particles = billiard.placement == Placement::Hexagonal
                            ? hexagonalPlacement(billiard, obstacles, generator)
                            : randomPlacement(billiard, obstacles, generator);
  std::uniform_real_distribution<double> angle(0.0, 2.0 * M_PI);
  for (Particle& particle : particles) {
    const double theta = angle(generator);
    particle.velocity = {billiard.speed * std::cos(theta), billiard.speed * std::sin(theta)};
  }
  return particles;
}

double packingFraction(const BilliardParameters& billiard) {
  const double area = billiard.domainRadius * billiard.domainRadius;
  return billiard.count * billiard.radius * billiard.radius / area;
}
