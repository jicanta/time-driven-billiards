#pragma once

#include <fstream>
#include <string>
#include <vector>

#include "simulation.hpp"

struct OutputPaths {
  std::string staticPath;
  std::string dynamicPath;
  std::string eventsPath;
};

struct WriterOptions {
  bool frames = true;
};

OutputPaths outputPathsIn(const std::string& directory);

// Escribe la salida primaria de una corrida del sistema 2: los parametros
// (static.txt), el estado del sistema cada dt2 = n dt (dynamic.txt) y el
// registro de conversiones (events.txt). Ningun observable: Fu(t), t90, la
// energia y la distribucion de velocidades salen de estos archivos en
// visualization/.
class RunWriter {
 public:
  RunWriter(const OutputPaths& paths, const Simulation& simulation, double tmax,
            long saveEvery, WriterOptions options = {});

  void writeFrame(const Simulation& simulation);
  void writeConversions(const Simulation& simulation);

 private:
  WriterOptions options_;
  std::ofstream dynamic_;
  std::ofstream events_;
};

// Igual que el registro de conversiones de RunWriter, pero acumulado en
// memoria y volcado al final: lo usa `bench`, donde la escritura no debe
// entrar en el tiempo de ejecucion medido.
void writeStatic(const std::string& path, const Simulation& simulation, double tmax,
                 long saveEvery);
void writeConversions(const std::string& path, const std::vector<Conversion>& conversions);
