#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

#include "commands.hpp"

namespace {

void printUsage() {
  std::cerr
      << "uso: billar <comando> [opciones]\n\n"
      << "  oscillator [--methods verlet,velocity-verlet,beeman,euler-pc]\n"
      << "             [--dts 5e-3,...,1e-5] [--tf 5] [--m 70] [--k 1e4]\n"
      << "             [--gamma 100] [--a 1] [--save-every 1]\n"
      << "             [--dir ../data/oscilador]\n\n"
      << "  simulate   [--n 100] [--xo 0.0175|sin] [--dt 1e-4] [--tmax 30]\n"
      << "             [--save-every <dt2/dt>] [--seed 1] [--dir ../data/runs/prueba]\n\n"
      << "  bench      [--ns 50,...,700] [--tf 30] [--dt 1e-4] [--repeats 10]\n"
      << "             [--warmup 1] [--seed 1] [--dir ../data/bench]\n\n"
      << "  explore    [--ns 100] [--xos 0.0175,...|sin] [--dts 1e-4] [--seeds 5]\n"
      << "             [--seed 1] [--tmax 100] [--save-every 0] [--until-all-used]\n"
      << "             [--until-fraction 1]\n"
      << "             [--dir ../data/explore/prueba]\n\n"
      << "  Parametros del sistema 2 (por defecto los del enunciado): --radio 0.51\n"
      << "  --r 0.0175 --m 0.025 --v0 1 --k 1e4. Los dos obstaculos fijos van en\n"
      << "  (-xo, 0) y (+xo, 0), con el mismo radio que las particulas; --xo sin\n"
      << "  deja el dominio vacio. --placement elige la condicion inicial: al\n"
      << "  azar con rechazo (la del enunciado) o sobre una red hexagonal, que es\n"
      << "  la unica que entra por encima de N = 450.\n"
      << "  oscillator es el sistema 1 (oscilador amortiguado, solucion analitica):\n"
      << "  integra con cada esquema y cada paso y escribe la trayectoria completa\n"
      << "  (t x v por paso); el error cuadratico medio contra la solucion\n"
      << "  analitica se calcula despues, en visualization/oscillator.py.\n"
      << "  simulate escribe la salida primaria de una corrida: static.txt,\n"
      << "  dynamic.txt con el estado cada dt2 = save-every * dt y events.txt con\n"
      << "  una linea por conversion (fresca a usada). Ningun observable se\n"
      << "  calcula en el motor: la energia, Fu(t), t90 y la distribucion de\n"
      << "  velocidades salen de esos archivos, en visualization/ (check.py\n"
      << "  verifica energia y solapamientos).\n"
      << "  bench no escribe cuadros: cronometra por separado la generacion de la\n"
      << "  condicion inicial y el bucle de integracion, con los obstaculos en\n"
      << "  contacto (xo = r) y tf fijo; guarda ademas las conversiones de cada\n"
      << "  realizacion, que usa el item 2.4.a.\n"
      << "  explore corre el producto de --ns, --xos y --dts con --seeds semillas\n"
      << "  consecutivas desde --seed y escribe por corrida static.txt y las\n"
      << "  conversiones, mas un index.txt con una linea por corrida; con\n"
      << "  --save-every mayor que cero escribe tambien dynamic.txt, que es lo que\n"
      << "  usan los items 2.1.a (energia) y 2.3 (distribucion de velocidades).\n"
      << "  --until-all-used corta la corrida apenas se convierten todas las\n"
      << "  particulas, y --until-fraction baja ese corte a la fraccion que se va\n"
      << "  a medir (0.9 para un barrido del que solo se lee t90).\n";
}

}

BilliardParameters billiardFromArguments(const Arguments& arguments) {
  BilliardParameters billiard;
  billiard.domainRadius = arguments.number("radio", billiard.domainRadius);
  billiard.radius = arguments.number("r", billiard.radius);
  billiard.mass = arguments.number("m", billiard.mass);
  billiard.speed = arguments.number("v0", billiard.speed);
  billiard.stiffness = arguments.number("k", billiard.stiffness);
  billiard.count = arguments.integer("n", billiard.count);
  billiard.seed = static_cast<unsigned int>(arguments.integer("seed", 1));
  billiard.placement = placementFromName(arguments.text("placement", "random"));
  const std::string offset = arguments.text("xo", "");
  if (offset == "sin") {
    billiard.obstacles = false;
  } else if (!offset.empty()) {
    billiard.obstacles = true;
    billiard.obstacleOffset = arguments.number("xo", billiard.obstacleOffset);
  }
  if (billiard.count < 0) {
    throw std::invalid_argument("--n no puede ser negativo");
  }
  return billiard;
}

int main(int argc, char** argv) {
  try {
    const Arguments arguments(argc, argv);
    if (arguments.command() == "oscillator") {
      return runOscillator(arguments);
    }
    if (arguments.command() == "simulate") {
      return runSimulate(arguments);
    }
    if (arguments.command() == "bench") {
      return runBench(arguments);
    }
    if (arguments.command() == "explore") {
      return runExplore(arguments);
    }
    printUsage();
    return 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 1;
  }
}
