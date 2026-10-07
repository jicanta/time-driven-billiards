#pragma once

#include <vector>

#include "geometry.hpp"

// Obstaculo circular fijo (masa infinita) del mismo radio que las particulas.
struct Obstacle {
  Vec2 center;
  double radius = 0.0;
};

using Obstacles = std::vector<Obstacle>;
