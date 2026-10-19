#include "oscillator.hpp"

#include <cmath>
#include <stdexcept>

namespace {

// f = m a = -k r - gamma v. La fuerza depende de la velocidad, que es lo que
// obliga a cada esquema a tratarla de una manera distinta.
inline double acceleration(const OscillatorParameters& oscillator, double x, double v) {
  return (-oscillator.stiffness * x - oscillator.damping * v) / oscillator.mass;
}

using Emit = std::function<void(long, double, double, double)>;

// Verlet original (diapositiva 13). Como f depende de v y v(t) es la
// diferencia centrada (r(t+dt) - r(t-dt)) / (2 dt) (diapositiva 15), la
// ecuacion del paso queda implicita en r(t+dt); para esta fuerza es lineal y
// se despeja:
//
//   r(t+dt) = [(2 - k dt^2/m) r(t) - (1 - b) r(t-dt)] / (1 + b),  b = gamma dt / 2m
//
// La posicion anterior del primer paso sale de Euler evaluado en -dt
// (diapositiva 14), y con ella v(0) reproduce exactamente la condicion
// inicial. Se adelanta un paso de posiciones para que r(t) y v(t) queden en el
// mismo instante.
void verlet(const OscillatorParameters& oscillator, double step, long steps,
            long saveEvery, const Emit& emit) {
  const double beta = oscillator.damping * step / (2.0 * oscillator.mass);
  const double kappa = oscillator.stiffness * step * step / oscillator.mass;
  double current = oscillator.amplitude;
  const double initialSpeed = -oscillator.amplitude * oscillator.damping /
                              (2.0 * oscillator.mass);
  double previous = current - initialSpeed * step +
                    0.5 * step * step * acceleration(oscillator, current, initialSpeed);
  double next = ((2.0 - kappa) * current - (1.0 - beta) * previous) / (1.0 + beta);
  for (long n = 0; n <= steps; ++n) {
    if (n % saveEvery == 0 || n == steps) {
      emit(n, n * step, current, (next - previous) / (2.0 * step));
    }
    previous = current;
    current = next;
    next = ((2.0 - kappa) * current - (1.0 - beta) * previous) / (1.0 + beta);
  }
}

// Velocity Verlet (diapositiva 17), con los dos pasos intermedios sobre la
// velocidad que da la propia diapositiva:
//
//   v(t + dt/2) = v(t) + a(t) dt/2
//   v(t + dt)   = v(t + dt/2) + a(t + dt) dt/2
//
// Con una fuerza que depende solo de la posicion eso es partir la patada en
// dos mitades y no hay nada que decidir: a(t + dt) sale de r(t + dt). Aca la
// fuerza es f = -k r - gamma v, asi que a(t + dt) necesita v(t + dt), que es
// justo lo que la ecuacion esta calculando: queda implicita y hay que elegir
// como resolverla. La diapositiva no escribe ese caso, y hay DOS lecturas:
//
//   (a) evaluar a(t + dt) con v(t + dt/2), la unica velocidad que aparece
//       entre los dos pasos intermedios. Es la que corre aca.
//   (b) despejar v(t + dt), que se puede porque f es lineal en v, igual que
//       en Verlet original (ver arriba).
//
// Lo que las separa esta medido en `make velocity-verlet-variantes`:
//   (a) da ECM ~ dt^2,04, o sea primer orden: v(t + dt/2) se aparta de
//       v(t + dt) en O(dt) y ese error entra en a(t + dt) multiplicado por
//       dt/2. No es un atajo ni un error de codigo, es lo que le cuesta al
//       esquema tratar de forma explicita una fuerza que depende de v, y es
//       el resultado del item 1.2.
//   (b) da ECM ~ dt^4,00, segundo orden, pero el esquema que queda ES Verlet
//       original: sumando pasos consecutivos de las dos formulas de arriba se
//       llega a r(t+dt) - 2r(t) + r(t-dt) = (dt^2/m) f(t) y a
//       v(t) = (r(t+dt) - r(t-dt)) / (2 dt), sin usar de que depende f. O sea
//       que quedarian 3 esquemas distintos en vez de los 4 del enunciado.
//
// Ninguna de las dos es "la correcta": se consulto a la catedra (PLAN.md,
// seccion 9, duda 4) y mientras tanto corre (a). Pasar a (b) es reemplazar la
// linea marcada abajo por el despeje.
void velocityVerlet(const OscillatorParameters& oscillator, double step, long steps,
                    long saveEvery, const Emit& emit) {
  double x = oscillator.amplitude;
  double v = -oscillator.amplitude * oscillator.damping / (2.0 * oscillator.mass);
  for (long n = 0; n <= steps; ++n) {
    if (n % saveEvery == 0 || n == steps) {
      emit(n, n * step, x, v);
    }
    const double a = acceleration(oscillator, x, v);
    const double nextX = x + step * v + 0.5 * step * step * a;
    const double half = v + 0.5 * step * a;
    // Lectura (a): a(t + dt) evaluada con la velocidad de medio paso.
    v = half + 0.5 * step * acceleration(oscillator, nextX, half);
    x = nextX;
  }
}

// Beeman en su variante predictor-corrector (diapositiva 20): predice la
// velocidad, evalua la aceleracion con esa prediccion y corrige.
void beeman(const OscillatorParameters& oscillator, double step, long steps,
            long saveEvery, const Emit& emit) {
  double x = oscillator.amplitude;
  double v = -oscillator.amplitude * oscillator.damping / (2.0 * oscillator.mass);
  double a = acceleration(oscillator, x, v);
  // Estado en -dt con Euler, para tener a(t - dt) en el primer paso.
  const double previousX = x - v * step + 0.5 * step * step * a;
  const double previousV = v - a * step;
  double previousA = acceleration(oscillator, previousX, previousV);
  for (long n = 0; n <= steps; ++n) {
    if (n % saveEvery == 0 || n == steps) {
      emit(n, n * step, x, v);
    }
    a = acceleration(oscillator, x, v);
    const double nextX = x + v * step + (2.0 / 3.0) * a * step * step -
                         (1.0 / 6.0) * previousA * step * step;
    const double predicted = v + 1.5 * a * step - 0.5 * previousA * step;
    const double nextA = acceleration(oscillator, nextX, predicted);
    v += (1.0 / 3.0) * nextA * step + (5.0 / 6.0) * a * step - (1.0 / 6.0) * previousA * step;
    previousA = a;
    x = nextX;
  }
}

// Euler predictor-corrector (diapositiva 23): predecir con Euler, evaluar la
// fuerza con lo predicho y corregir; la posicion corregida usa la velocidad ya
// corregida.
void eulerPredictorCorrector(const OscillatorParameters& oscillator, double step,
                             long steps, long saveEvery, const Emit& emit) {
  double x = oscillator.amplitude;
  double v = -oscillator.amplitude * oscillator.damping / (2.0 * oscillator.mass);
  for (long n = 0; n <= steps; ++n) {
    if (n % saveEvery == 0 || n == steps) {
      emit(n, n * step, x, v);
    }
    const double a = acceleration(oscillator, x, v);
    const double predictedV = v + a * step;
    const double predictedX = x + v * step;
    const double nextA = acceleration(oscillator, predictedX, predictedV);
    v += nextA * step;
    x += v * step;
  }
}

}

Scheme schemeFromName(const std::string& name) {
  if (name == "verlet") {
    return Scheme::Verlet;
  }
  if (name == "velocity-verlet") {
    return Scheme::VelocityVerlet;
  }
  if (name == "beeman") {
    return Scheme::Beeman;
  }
  if (name == "euler-pc") {
    return Scheme::EulerPredictorCorrector;
  }
  throw std::invalid_argument("esquema desconocido: " + name +
                              " (verlet|velocity-verlet|beeman|euler-pc)");
}

std::string schemeName(Scheme scheme) {
  switch (scheme) {
    case Scheme::Verlet:
      return "verlet";
    case Scheme::VelocityVerlet:
      return "velocity-verlet";
    case Scheme::Beeman:
      return "beeman";
    case Scheme::EulerPredictorCorrector:
      return "euler-pc";
  }
  return "?";
}

double angularFrequency(const OscillatorParameters& oscillator) {
  const double squared = oscillator.stiffness / oscillator.mass -
                         oscillator.damping * oscillator.damping /
                             (4.0 * oscillator.mass * oscillator.mass);
  if (squared <= 0.0) {
    throw std::invalid_argument("el oscilador no es subamortiguado: k/m <= gamma^2/4m^2");
  }
  return std::sqrt(squared);
}

double analyticPosition(const OscillatorParameters& oscillator, double t) {
  return oscillator.amplitude *
         std::exp(-oscillator.damping * t / (2.0 * oscillator.mass)) *
         std::cos(angularFrequency(oscillator) * t);
}

double analyticVelocity(const OscillatorParameters& oscillator, double t) {
  const double rate = oscillator.damping / (2.0 * oscillator.mass);
  const double omega = angularFrequency(oscillator);
  return -oscillator.amplitude * std::exp(-rate * t) *
         (rate * std::cos(omega * t) + omega * std::sin(omega * t));
}

void integrate(const OscillatorParameters& oscillator, Scheme scheme, double step,
               double tf, long saveEvery, const Emit& emit) {
  if (step <= 0.0) {
    throw std::invalid_argument("dt debe ser mayor que cero");
  }
  if (saveEvery <= 0) {
    throw std::invalid_argument("save-every debe ser mayor que cero");
  }
  const long steps = std::lround(tf / step);
  switch (scheme) {
    case Scheme::Verlet:
      verlet(oscillator, step, steps, saveEvery, emit);
      return;
    case Scheme::VelocityVerlet:
      velocityVerlet(oscillator, step, steps, saveEvery, emit);
      return;
    case Scheme::Beeman:
      beeman(oscillator, step, steps, saveEvery, emit);
      return;
    case Scheme::EulerPredictorCorrector:
      eulerPredictorCorrector(oscillator, step, steps, saveEvery, emit);
      return;
  }
}
