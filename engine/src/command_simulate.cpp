#include <cmath>
#include <iostream>
#include <random>
#include <stdexcept>

#include "commands.hpp"
#include "forces.hpp"
#include "io.hpp"
#include "simulation.hpp"

// Sistema 2: una corrida con cuadros. Imprime el estado cada dt2 = n dt (un
// numero entero de pasos, Teorica 4 diapositiva 33) para no llenar el disco:
// las animaciones y los analisis salen despues de esos estados.
int runSimulate(const Arguments& arguments) {
  const BilliardParameters billiard = billiardFromArguments(arguments);
  const double step = arguments.number("dt", 1e-4);
  const double tmax = arguments.number("tmax", 30.0);
  const long saveEvery = arguments.integer("save-every", static_cast<int>(std::lround(0.01 / step)));
  if (saveEvery <= 0) {
    throw std::invalid_argument("save-every debe ser mayor que cero");
  }

  std::mt19937 generator(billiard.seed);
  const Obstacles obstacles = obstaclesOf(billiard);
  Simulation simulation(billiard, generateParticles(billiard, obstacles, generator), step);

  const OutputPaths paths = outputPathsIn(arguments.text("dir", "../data/runs/prueba"));
  RunWriter writer(paths, simulation, tmax, saveEvery);
  writer.writeFrame(simulation);

  const long total = std::lround(tmax / step);
  for (long n = 1; n <= total; ++n) {
    simulation.step();
    writer.writeConversions(simulation);
    if (n % saveEvery == 0) {
      writer.writeFrame(simulation);
    }
  }

  std::cout << "N: " << billiard.count << "\n"
            << "obstaculos: " << obstacles.size()
            << (billiard.obstacles ? " (xo = " + std::to_string(billiard.obstacleOffset) + " m)"
                                   : "")
            << "\n"
            << "fraccion de area: " << packingFraction(billiard) << "\n"
            << "pasos: " << simulation.steps() << " (dt = " << step << " s, dt2 = "
            << saveEvery * step << " s)\n"
            << "tiempo final: " << simulation.time() << " s\n"
            << "usadas: " << simulation.used() << "/" << billiard.count << "\n";
  std::cout << "salida: " << paths.staticPath << ", " << paths.dynamicPath << ", "
            << paths.eventsPath << "\n";
  return 0;
}
