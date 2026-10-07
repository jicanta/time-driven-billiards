#include "grid.hpp"

#include <algorithm>
#include <cmath>

Grid::Grid(double domainRadius, double interaction) {
  origin_ = -domainRadius;
  // El lado de la celda no puede ser menor que el alcance de la interaccion
  // (2r): con celdas mas chicas habria pares en contacto en celdas no vecinas.
  columns_ = std::max(1, static_cast<int>(std::floor(2.0 * domainRadius / interaction)));
  cell_ = 2.0 * domainRadius / columns_;
  buckets_.resize(static_cast<std::size_t>(columns_) * columns_);
}

int Grid::indexOf(const Vec2& position) const {
  const int column = std::clamp(static_cast<int>((position.x - origin_) / cell_), 0, columns_ - 1);
  const int row = std::clamp(static_cast<int>((position.y - origin_) / cell_), 0, columns_ - 1);
  return row * columns_ + column;
}

void Grid::rebuild(const Particles& particles) {
  for (std::vector<int>& bucket : buckets_) {
    bucket.clear();
  }
  for (int index = 0; index < static_cast<int>(particles.size()); ++index) {
    buckets_[indexOf(particles[index].position)].push_back(index);
  }
}
