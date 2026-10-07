#include "io.hpp"

#include <filesystem>
#include <iomanip>
#include <stdexcept>

namespace {

std::ofstream openForWriting(const std::string& path) {
  std::ofstream stream(path);
  if (!stream) {
    throw std::invalid_argument("no se pudo abrir para escritura: " + path);
  }
  stream << std::setprecision(12);
  return stream;
}

}

OutputPaths outputPathsIn(const std::string& directory) {
  const std::filesystem::path base = directory;
  std::filesystem::create_directories(base);
  return {(base / "static.txt").string(), (base / "dynamic.txt").string(),
          (base / "events.txt").string()};
}

void writeStatic(const std::string& path, const Simulation& simulation, double tmax,
                 long saveEvery) {
  const BilliardParameters& billiard = simulation.billiard();
  std::ofstream stream = openForWriting(path);
  stream << "N " << billiard.count << "\n"
         << "R " << billiard.domainRadius << "\n"
         << "r " << billiard.radius << "\n"
         << "m " << billiard.mass << "\n"
         << "v0 " << billiard.speed << "\n"
         << "k " << billiard.stiffness << "\n"
         << "dt " << simulation.timeStep() << "\n"
         << "dt2 " << saveEvery * simulation.timeStep() << "\n"
         << "save_every " << saveEvery << "\n"
         << "xo " << (billiard.obstacles ? billiard.obstacleOffset : -1.0) << "\n"
         << "seed " << billiard.seed << "\n"
         << "placement " << placementName(billiard.placement) << "\n"
         << "tmax " << tmax << "\n"
         << "K " << simulation.obstacles().size() << "\n";
  for (const Obstacle& obstacle : simulation.obstacles()) {
    stream << "obstacle " << obstacle.center.x << " " << obstacle.center.y << " "
           << obstacle.radius << "\n";
  }
}

void writeConversions(const std::string& path, const std::vector<Conversion>& conversions) {
  std::ofstream stream = openForWriting(path);
  for (const Conversion& conversion : conversions) {
    stream << conversion.time << " uso " << conversion.index << " " << conversion.obstacle
           << "\n";
  }
}

RunWriter::RunWriter(const OutputPaths& paths, const Simulation& simulation, double tmax,
                     long saveEvery, WriterOptions options)
    : options_(options) {
  writeStatic(paths.staticPath, simulation, tmax, options.frames ? saveEvery : 0);
  if (options_.frames) {
    dynamic_ = openForWriting(paths.dynamicPath);
  }
  events_ = openForWriting(paths.eventsPath);
}

void RunWriter::writeFrame(const Simulation& simulation) {
  if (!options_.frames) {
    return;
  }
  dynamic_ << simulation.time() << "\n";
  for (const Particle& particle : simulation.particles()) {
    dynamic_ << particle.position.x << " " << particle.position.y << " "
             << particle.velocity.x << " " << particle.velocity.y << " "
             << (particle.fresh ? 0 : 1) << "\n";
  }
}

void RunWriter::writeConversions(const Simulation& simulation) {
  for (const Conversion& conversion : simulation.conversions()) {
    events_ << conversion.time << " uso " << conversion.index << " " << conversion.obstacle
            << "\n";
  }
}
