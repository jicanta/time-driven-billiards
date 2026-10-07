#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "commands.hpp"
#include "oscillator.hpp"

namespace {

std::string stepName(double step) {
  char buffer[32];
  std::snprintf(buffer, sizeof(buffer), "dt%.1e", step);
  return buffer;
}

}

// Sistema 1: integra el oscilador amortiguado con cada esquema y cada paso, y
// escribe la trayectoria completa (una linea por paso de integracion). El ECM
// contra la solucion analitica se calcula despues, de estos archivos, en
// visualization/oscillator.py: el motor no calcula ningun observable.
int runOscillator(const Arguments& arguments) {
  OscillatorParameters oscillator;
  oscillator.mass = arguments.number("m", oscillator.mass);
  oscillator.stiffness = arguments.number("k", oscillator.stiffness);
  oscillator.damping = arguments.number("gamma", oscillator.damping);
  oscillator.amplitude = arguments.number("a", oscillator.amplitude);

  const double tf = arguments.number("tf", 5.0);
  const long saveEvery = arguments.integer("save-every", 1);
  const std::vector<double> steps =
      numberList("dts", arguments.text("dts", "5e-3,2e-3,1e-3,5e-4,2e-4,1e-4,5e-5,2e-5,1e-5"));
  const std::vector<std::string> names =
      textList(arguments.text("methods", "verlet,velocity-verlet,beeman,euler-pc"));
  const std::filesystem::path root = arguments.text("dir", "../data/oscilador");
  if (names.empty()) {
    throw std::invalid_argument("--methods necesita al menos un esquema");
  }

  std::filesystem::create_directories(root);
  std::ofstream index(root / "index.txt");
  if (!index) {
    throw std::invalid_argument("no se pudo abrir para escritura: " +
                                (root / "index.txt").string());
  }
  index << std::setprecision(12) << "# m " << oscillator.mass << " k " << oscillator.stiffness
        << " gamma " << oscillator.damping << " A " << oscillator.amplitude << " tf " << tf
        << " save_every " << saveEvery << "\n"
        << "# esquema dt pasos archivo\n";

  for (const std::string& name : names) {
    const Scheme scheme = schemeFromName(name);
    std::filesystem::create_directories(root / name);
    std::cout << name << " " << std::flush;
    for (const double step : steps) {
      const std::filesystem::path path = root / name / (stepName(step) + ".txt");
      std::ofstream out(path);
      if (!out) {
        throw std::invalid_argument("no se pudo abrir para escritura: " + path.string());
      }
      out << std::setprecision(14) << "# esquema " << name << "\n"
          << "# dt " << step << "\n"
          << "# t x v\n";
      long written = 0;
      integrate(oscillator, scheme, step, tf, saveEvery,
                [&](long, double t, double x, double v) {
                  out << t << " " << x << " " << v << "\n";
                  ++written;
                });
      index << name << " " << step << " " << written << " "
            << std::filesystem::relative(path, root).string() << "\n";
      std::cout << "." << std::flush;
    }
    std::cout << "\n";
  }
  std::cout << "indice: " << (root / "index.txt").string() << "\n";
  return 0;
}
