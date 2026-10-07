#include <cmath>
#include <cstdio>
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

namespace {

struct Case {
  std::string name;
  int count = 0;
  double offset = -1.0;  // xo; negativo = sin obstaculos
  double step = 0.0;
};

std::string format(const char* pattern, double value) {
  char buffer[32];
  std::snprintf(buffer, sizeof(buffer), pattern, value);
  return buffer;
}

// El nombre de la corrida lleva solo los parametros que se barren; si no se
// barre ninguno, lleva la posicion de los obstaculos, que es la variable del
// item 2.2.
std::string caseName(int count, const std::string& offset, double step, bool varyCount,
                     bool varyOffset, bool varyStep) {
  std::string name;
  const auto append = [&name](const std::string& piece) {
    name += name.empty() ? piece : "_" + piece;
  };
  if (varyCount) {
    append("n" + std::to_string(count));
  }
  if (varyOffset || (!varyCount && !varyStep)) {
    append(offset == "sin" ? "sin" : "xo" + format("%.4f", std::stod(offset)));
  }
  if (varyStep) {
    append("dt" + format("%.1e", step));
  }
  return name;
}

}

// Barrido del sistema 2: corre el producto de --ns, --xos y --dts con --seeds
// realizaciones consecutivas desde --seed y escribe por corrida static.txt y
// el registro de conversiones, mas un index.txt con una linea por corrida. Sin
// cuadros salvo que se pida --save-every (item 2.3). Ningun observable: Fu(t),
// t90, la energia y la distribucion de velocidades salen de los archivos.
int runExplore(const Arguments& arguments) {
  BilliardParameters billiard = billiardFromArguments(arguments);
  const std::vector<int> counts = integerList("ns", arguments.text("ns", "100"));
  const std::vector<std::string> offsets = textList(arguments.text("xos", "0.0175"));
  const std::vector<double> stepsList = numberList("dts", arguments.text("dts", "1e-4"));
  const int seeds = arguments.integer("seeds", 5);
  const double tmax = arguments.number("tmax", 100.0);
  // El intervalo entre estados guardados se puede pedir en pasos
  // (--save-every) o en segundos (--dt2): con --dt2 cada dt del barrido usa el
  // numero entero de pasos que da el mismo dt2, que es lo que hace falta para
  // comparar la energia de corridas con distinto dt sobre el mismo eje.
  const long requestedSaveEvery = arguments.integer("save-every", 0);
  const double frameStep = arguments.number("dt2", 0.0);
  const bool untilAllUsed = arguments.flag("until-all-used");
  const std::filesystem::path root = arguments.text("dir", "../data/explore/prueba");
  const unsigned int baseSeed = billiard.seed;
  if (seeds <= 0) {
    throw std::invalid_argument("--seeds debe ser mayor que cero");
  }
  if (requestedSaveEvery < 0 || frameStep < 0.0) {
    throw std::invalid_argument("--save-every y --dt2 no pueden ser negativos");
  }
  if (offsets.empty()) {
    throw std::invalid_argument("--xos necesita al menos un valor (numero o \"sin\")");
  }

  std::vector<Case> cases;
  for (const int count : counts) {
    for (const std::string& offset : offsets) {
      for (const double step : stepsList) {
        cases.push_back({caseName(count, offset, step, counts.size() > 1, offsets.size() > 1,
                                  stepsList.size() > 1),
                         count, offset == "sin" ? -1.0 : std::stod(offset), step});
      }
    }
  }

  std::filesystem::create_directories(root);
  std::ofstream index(root / "index.txt");
  if (!index) {
    throw std::invalid_argument("no se pudo abrir para escritura: " +
                                (root / "index.txt").string());
  }
  index << std::setprecision(12) << "# tmax " << tmax << " seeds " << seeds << " dt2 "
        << frameStep << " R " << billiard.domainRadius << " r " << billiard.radius << " k "
        << billiard.stiffness << "\n"
        << "# caso N xo dt semilla carpeta\n";

  for (const Case& item : cases) {
    billiard.count = item.count;
    billiard.obstacles = item.offset > 0.0;
    billiard.obstacleOffset = billiard.obstacles ? item.offset : billiard.radius;
    const long saveEvery = frameStep > 0.0 ? std::lround(frameStep / item.step)
                                           : requestedSaveEvery;
    WriterOptions options;
    options.frames = saveEvery > 0;
    std::cout << item.name << " " << std::flush;
    for (int repeat = 0; repeat < seeds; ++repeat) {
      billiard.seed = baseSeed + static_cast<unsigned int>(repeat);
      std::mt19937 generator(billiard.seed);
      const Obstacles obstacles = obstaclesOf(billiard);
      Simulation simulation(billiard, generateParticles(billiard, obstacles, generator),
                            item.step);

      const std::filesystem::path directory =
          root / item.name / ("s" + std::to_string(billiard.seed));
      RunWriter writer(outputPathsIn(directory.string()), simulation, tmax,
                       options.frames ? saveEvery : 1, options);
      writer.writeFrame(simulation);
      const long total = std::lround(tmax / item.step);
      for (long n = 1; n <= total; ++n) {
        simulation.step();
        writer.writeConversions(simulation);
        if (options.frames && n % saveEvery == 0) {
          writer.writeFrame(simulation);
        }
        if (untilAllUsed && simulation.used() == billiard.count) {
          break;
        }
      }
      index << item.name << " " << item.count << " " << item.offset << " " << item.step << " "
            << billiard.seed << " "
            << std::filesystem::relative(directory, root).string() << "\n"
            << std::flush;
      std::cout << "." << std::flush;
    }
    std::cout << "\n";
  }
  std::cout << "indice: " << (root / "index.txt").string() << "\n";
  return 0;
}
