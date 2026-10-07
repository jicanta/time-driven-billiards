#pragma once

#include <functional>
#include <string>

// Sistema 1: oscilador puntual amortiguado (Teorica 4, diapositiva 37).
//
//   m r'' = -k r - gamma r'
//   r(t) = A exp(-gamma t / 2m) cos(w t),  w = sqrt(k/m - gamma^2 / 4m^2)
//   r(0) = A,  v(0) = -A gamma / (2m)
//
// Es el unico caso con solucion analitica del trabajo: sirve para medir el
// error de cada esquema de integracion.
struct OscillatorParameters {
  double mass = 70.0;
  double stiffness = 1.0e4;
  double damping = 100.0;
  double amplitude = 1.0;
};

enum class Scheme { Verlet, VelocityVerlet, Beeman, EulerPredictorCorrector };

Scheme schemeFromName(const std::string& name);
std::string schemeName(Scheme scheme);

double angularFrequency(const OscillatorParameters& oscillator);
double analyticPosition(const OscillatorParameters& oscillator, double t);
double analyticVelocity(const OscillatorParameters& oscillator, double t);

// Integra desde t = 0 hasta tf con paso `step` y llama a `emit(n, t, x, v)` en
// el paso 0 y cada `saveEvery` pasos. La fuerza depende de la velocidad, asi
// que cada esquema la trata como indica la Teorica 4 (ver oscillator.cpp).
void integrate(const OscillatorParameters& oscillator, Scheme scheme, double step,
               double tf, long saveEvery,
               const std::function<void(long, double, double, double)>& emit);
