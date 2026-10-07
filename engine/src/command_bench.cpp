#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

#include "commands.hpp"
#include "io.hpp"
#include "simulation.hpp"
#include "stopwatch.hpp"

// Item 2.1.b: tiempo de ejecucion contra N con los obstaculos en contacto
// (xo = r) y un tiempo absoluto fijo tf. No se escriben cuadros y el registro
// de conversiones se acumula en memoria y se vuelca al terminar la corrida:
// la escritura no entra en el tiempo medido (mismo acuerdo que en el TP3). Se
// cronometran por separado la generacion de la condicion inicial y el bucle de
// integracion. Las conversiones quedan guardadas porque el item 2.4.a usa
// estas mismas corridas para <t90> y <t100> contra la densidad.
int runBench(const Arguments& arguments) {
  BilliardParameters billiard = billiardFromArguments(arguments);
  const std::vector<int> counts = integerList("ns", arguments.text("ns", "50,100,200,300,400,500,600,700"));
  const double step = arguments.number("dt", 1e-4);
  const double tf = arguments.number("tf", 30.0);
  const int repeats = arguments.integer("repeats", 10);
  const int warmup = arguments.integer("warmup", 1);
  const unsigned int baseSeed = billiard.seed;
  const std::filesystem::path root = arguments.text("dir", "../data/bench");
  if (repeats <= 0 || warmup < 0) {
    throw std::invalid_argument("--repeats debe ser mayor que cero y --warmup no negativo");
  }

  std::filesystem::create_directories(root);
  std::ofstream times(root / "tiempos.txt");
  std::ofstream index(root / "index.txt");
  if (!times || !index) {
    throw std::invalid_argument("no se pudo abrir para escritura en " + root.string());
  }
  times << std::setprecision(10)
        << "# item 2.1.b: dinamica molecular regida por el paso temporal, tf = " << tf
        << " s, dt = " << step << " s, xo = r (obstaculos en contacto), " << repeats
        << " realizaciones por N mas " << warmup
        << " de calentamiento (descartada = 1), que no entran en el promedio\n"
        << "# N seed pasos t_final ms_generacion ms_simulacion descartada\n";
  index << std::setprecision(12) << "# tmax " << tf << " seeds " << repeats
        << " save_every 0 R " << billiard.domainRadius << " r " << billiard.radius << " k "
        << billiard.stiffness << "\n"
        << "# caso N xo dt semilla carpeta\n";

  const long total = std::lround(tf / step);
  for (const int count : counts) {
    billiard.count = count;
    billiard.obstacles = true;
    billiard.obstacleOffset = billiard.radius;
    const std::string name = "n" + std::to_string(count);
    std::cout << "N = " << count << std::flush;
    for (int repeat = -warmup; repeat < repeats; ++repeat) {
      const bool discarded = repeat < 0;
      billiard.seed =
          baseSeed + static_cast<unsigned int>(discarded ? repeats - repeat - 1 : repeat);
      std::mt19937 generator(billiard.seed);
      const Obstacles obstacles = obstaclesOf(billiard);

      Stopwatch generation;
      Particles particles = generateParticles(billiard, obstacles, generator);
      const double generationMs = generation.elapsedMilliseconds();

      std::vector<Conversion> conversions;
      conversions.reserve(count);
      Stopwatch loop;
      Simulation simulation(billiard, std::move(particles), step);
      for (long n = 1; n <= total; ++n) {
        simulation.step();
        for (const Conversion& conversion : simulation.conversions()) {
          conversions.push_back(conversion);
        }
      }
      const double loopMs = loop.elapsedMilliseconds();

      times << count << " " << billiard.seed << " " << simulation.steps() << " "
            << simulation.time() << " " << generationMs << " " << loopMs << " "
            << (discarded ? 1 : 0) << "\n"
            << std::flush;
      if (!discarded) {
        const std::filesystem::path directory =
            root / name / ("s" + std::to_string(billiard.seed));
        const OutputPaths paths = outputPathsIn(directory.string());
        writeStatic(paths.staticPath, simulation, tf, 0);
        writeConversions(paths.eventsPath, conversions);
        index << name << " " << count << " " << billiard.obstacleOffset << " " << step << " "
              << billiard.seed << " "
              << std::filesystem::relative(directory, root).string() << "\n"
              << std::flush;
      }
      std::cout << (discarded ? "x" : ".") << std::flush;
    }
    std::cout << "\n";
  }
  std::cout << "tiempos: " << (root / "tiempos.txt").string() << "\n";
  return 0;
}
