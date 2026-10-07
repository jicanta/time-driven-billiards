#pragma once

#include <vector>

#include "particle.hpp"

// Metodo de la celda de indice: el contacto solo alcanza a 2r, asi que basta
// mirar las 9 celdas vecinas en vez de las N - 1 particulas. La grilla cubre
// el cuadrado [-R, R]^2 que contiene al dominio circular y el lado de la celda
// nunca es menor que 2r.
class Grid {
 public:
  Grid(double domainRadius, double interaction);

  void rebuild(const Particles& particles);

  int columns() const { return columns_; }
  double cellSize() const { return cell_; }

  // Llama a `visit(i, j)` una sola vez por par de particulas en contacto
  // potencial (celdas vecinas), con i < j.
  template <typename Visitor>
  void forEachNeighbourPair(Visitor visit) const {
    for (int cell = 0; cell < columns_ * columns_; ++cell) {
      const int row = cell / columns_;
      const int column = cell % columns_;
      for (const int i : buckets_[cell]) {
        for (int dRow = 0; dRow <= 1; ++dRow) {
          for (int dColumn = (dRow == 0 ? 0 : -1); dColumn <= 1; ++dColumn) {
            const int otherRow = row + dRow;
            const int otherColumn = column + dColumn;
            if (otherRow >= columns_ || otherColumn < 0 || otherColumn >= columns_) {
              continue;
            }
            for (const int j : buckets_[otherRow * columns_ + otherColumn]) {
              if (dRow == 0 && dColumn == 0 && j <= i) {
                continue;
              }
              visit(i, j);
            }
          }
        }
      }
    }
  }

 private:
  int indexOf(const Vec2& position) const;

  double origin_;
  double cell_;
  int columns_;
  std::vector<std::vector<int>> buckets_;
};
