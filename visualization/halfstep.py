"""Sistema 1: por que Velocity Verlet pierde un orden con esta fuerza.

Prueba de la decision de implementacion del item 1.1. La Teorica 4 escribe
Velocity Verlet (diapositiva 17) con dos pasos intermedios sobre la velocidad:

    v(t + dt/2) = v(t) + a(t) dt/2                     (paso intermedio 1)
    v(t + dt)   = v(t + dt/2) + a(t + dt) dt/2         (paso intermedio 2)

Con una fuerza que NO depende de la velocidad eso es solo partir la patada en
dos mitades y no hay nada mas que decidir: a(t + dt) sale de r(t + dt). Pero
la del oscilador es f = -k r - gamma v, asi que a(t + dt) necesita v(t + dt),
que es justamente lo que la ecuacion esta calculando: queda implicita y hay
que elegir como resolverla. La diapositiva no escribe ese caso, y hay DOS
lecturas, las dos defendibles:

    (a) evaluar a(t + dt) con v(t + dt/2), la unica velocidad que aparece
        entre los dos pasos intermedios. Es la que corre en el motor.
    (b) despejar v(t + dt), que se puede porque f es lineal en v, igual que
        se hizo con Verlet original.

Ninguna es "la correcta" y esta consultado a la catedra (PLAN.md, seccion 9,
duda 4). Este script mide que da cada una, para poder decidir con datos.
Reimplementa el oscilador en Python y corre el mismo barrido de dt con cuatro
variantes, que se diferencian SOLO en con que velocidad evaluan a(t + dt):

    medio-paso   v(t + dt/2)            la del motor (y la que deja la Teorica)
    implicita    v(t + dt) exacta       se despeja: la fuerza es lineal en v
    euler        v(t) + a(t) dt         prediccion de Euler
    congelada    v(t)                   no se actualiza la velocidad

y le ajusta a cada una la ley de potencia ECM = c dt^p. Primero verifica que
la variante `medio-paso` reproduce las trayectorias que escribio el motor en
C++, para que lo que se compare sea lo que efectivamente corre; al final mide
cuanto se aparta cada lectura de la recurrencia de Verlet original, que es lo
que decide si (b) es un esquema distinto o el mismo.

    python3 visualization/halfstep.py
    python3 visualization/halfstep.py --figura
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common

# Los dt del barrido del trabajo (Makefile, DTS_OSC).
STEPS = (5e-3, 2e-3, 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5)
VARIANTS = ("medio-paso", "implicita", "euler", "congelada")
LABEL = {
    "medio-paso": "$v(t + \\Delta t/2)$ (el motor)",
    "implicita": "$v(t + \\Delta t)$ exacta (implícita)",
    "euler": "$v(t) + a(t)\\,\\Delta t$ (Euler)",
    "congelada": "$v(t)$ (congelada)",
}


def trajectory(parameters: dict, step: float, steps: int, variant: str):
    """Velocity Verlet con una de las cuatro maneras de evaluar a(t + dt).

    Las tres primeras lineas del paso son identicas en las cuatro: r(t + dt),
    a(t) y la media patada v(t + dt/2). Lo unico que cambia es el argumento de
    velocidad con el que se evalua a(t + dt)."""
    mass, stiffness, damping = parameters["m"], parameters["k"], parameters["gamma"]

    def acceleration(x: float, v: float) -> float:
        return (-stiffness * x - damping * v) / mass

    x = parameters["A"]
    v = -parameters["A"] * damping / (2.0 * mass)
    positions = np.empty(steps + 1)
    speeds = np.empty(steps + 1)
    for n in range(steps + 1):
        positions[n] = x
        speeds[n] = v
        a = acceleration(x, v)
        next_x = x + step * v + 0.5 * step * step * a
        half = v + 0.5 * step * a
        if variant == "medio-paso":
            v = half + 0.5 * step * acceleration(next_x, half)
        elif variant == "implicita":
            # v(t+dt) = half + (dt/2)(-k r(t+dt) - gamma v(t+dt))/m, lineal en
            # v(t+dt): se despeja sin aproximar nada.
            v = ((half - 0.5 * step * stiffness * next_x / mass) /
                 (1.0 + 0.5 * step * damping / mass))
        elif variant == "euler":
            v = half + 0.5 * step * acceleration(next_x, v + step * a)
        else:
            v = half + 0.5 * step * acceleration(next_x, v)
        x = next_x
    return positions, speeds


def squared_error(parameters: dict, step: float, steps: int, variant: str) -> float:
    positions, _ = trajectory(parameters, step, steps, variant)
    times = np.arange(steps + 1) * step
    return float(np.mean((positions - common.analytic_position(parameters, times)) ** 2))


def engine_check(parameters: dict, root: Path, tolerance: float = 1e-12) -> list[str]:
    """Compara la variante `medio-paso` contra lo que escribio el motor.

    Sin esto el experimento mediria otro programa: lo que se quiere probar es
    el esquema que corre en C++, no una reimplementacion parecida."""
    lines = []
    for step in STEPS:
        path = root / "velocity-verlet" / f"dt{step:.1e}.txt"
        if not path.exists():
            continue
        t, x, _ = common.read_trajectory(path)
        steps = int(round(parameters["tf"] / step))
        mine, _ = trajectory(parameters, step, steps, "medio-paso")
        # El motor guarda uno de cada save_every pasos: se comparan esos.
        taken = np.rint(t / step).astype(int)
        gap = float(np.abs(mine[taken] - x).max())
        lines.append(f"  dt = {step:7.1e}: máxima diferencia con el motor = {gap:.3e} m"
                     f"{'' if gap <= tolerance else '   <-- NO reproduce'}")
    return lines


def verlet_residual(parameters: dict, step: float, steps: int, variant: str):
    """Cuanto se aparta una variante de la recurrencia de Verlet original.

    Sumando pasos consecutivos de las dos formulas de Velocity Verlet sale

        r(t+dt) - 2 r(t) + r(t-dt) = (dt^2/m) f(t)    y
        v(t) = (r(t+dt) - r(t-dt)) / (2 dt),

    que es exactamente Verlet original. La cuenta no usa de que depende f, asi
    que vale tambien con fuerza dependiente de la velocidad siempre que f(t)
    sea consistente con el propio v(t) del esquema: justo lo que impone el
    despeje. Si el residuo da redondeo, la variante ES Verlet original; si
    escala con dt, es un esquema distinto. Devuelve (residuo de la
    recurrencia, diferencia entre v(t) y la velocidad centrada)."""
    mass, stiffness, damping = parameters["m"], parameters["k"], parameters["gamma"]
    positions, speeds = trajectory(parameters, step, steps, variant)
    force = -stiffness * positions[1:-1] - damping * speeds[1:-1]
    residual = (positions[2:] - 2.0 * positions[1:-1] + positions[:-2] -
                step * step * force / mass)
    centred = (positions[2:] - positions[:-2]) / (2.0 * step)
    return float(np.abs(residual).max()), float(np.abs(speeds[1:-1] - centred).max())


def against_verlet(parameters: dict) -> list[str]:
    """Residuo de la recurrencia de Verlet original para las dos lecturas."""
    lines = []
    for step in STEPS:
        steps = int(round(parameters["tf"] / step))
        for variant in ("implicita", "medio-paso"):
            residual, centred = verlet_residual(parameters, step, steps, variant)
            lines.append(f"  dt = {step:7.1e} {variant:>11}: |residuo| ≤ {residual:.1e} m, "
                         f"|v(t) − centrada| ≤ {centred:.1e} m/s")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--oscilador", type=Path, default=common.OSCILLATOR)
    parser.add_argument("--figura", action="store_true",
                        help="además de la tabla, dibuja el ECM de las cuatro variantes")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    parameters, _ = common.read_oscillator_index(arguments.oscilador)
    print(f"m = {parameters['m']:g} kg, k = {parameters['k']:g} N/m, "
          f"gamma = {parameters['gamma']:g} kg/s, A = {parameters['A']:g} m, "
          f"tf = {parameters['tf']:g} s")

    print("\nla variante `medio-paso` contra las trayectorias del motor en C++:")
    for line in engine_check(parameters, arguments.oscilador):
        print(line)

    errors = {}
    for variant in VARIANTS:
        errors[variant] = np.array([squared_error(parameters, step,
                                                  int(round(parameters["tf"] / step)), variant)
                                    for step in STEPS])

    print(f"\n{'dt (s)':>10}" + "".join(f"{v:>16}" for v in VARIANTS))
    for index, step in enumerate(STEPS):
        print(f"{step:10.1e}" + "".join(f"{errors[v][index]:16.4e}" for v in VARIANTS))

    print("\najuste ECM = c dt^p (sin los dt en los que el ECM ya dejó de bajar):")
    exponents = {}
    for variant in VARIANTS:
        keep = np.ones(len(STEPS), dtype=bool)
        series = errors[variant]
        for index in range(len(STEPS) - 2, -1, -1):
            # STEPS va de mayor a menor: el piso de redondeo está al final.
            if not keep[index + 1] or series[index + 1] >= series[index]:
                keep[index + 1] = False
        steps = np.array(STEPS)[keep]
        exponent, _ = np.polyfit(np.log(steps), np.log(series[keep]), 1)
        exponents[variant] = exponent
        print(f"  {variant:>12}: p = {exponent:.2f}   "
              f"(orden del esquema: {exponent / 2:.1f})")

    print("\ncuánto se aparta cada lectura de la recurrencia de Verlet original")
    print("(redondeo = es Verlet original; si escala con dt, es otro esquema):")
    for line in against_verlet(parameters):
        print(line)

    if arguments.figura:
        import matplotlib.pyplot as plt
        out_dir = common.folder("1", arguments.figures)
        figure, axes = plt.subplots()
        for variant, (color, marker) in zip(VARIANTS, common.SCHEME_STYLE.values()):
            axes.plot(STEPS, errors[variant], color=color, marker=marker,
                      label=f"{LABEL[variant]} ($p$ = "
                            f"{common.decimal(exponents[variant], 1)})")
        axes.set_xscale("log")
        axes.set_yscale("log")
        axes.set_xlabel(common.AXIS_STEP)
        axes.set_ylabel(common.AXIS_ECM)
        common.headroom(axes, 0.42)
        axes.legend(loc="upper left")
        out = out_dir / "ECM_vs_dt_variantes_velocity_verlet.png"
        common.save(figure, out)
        plt.close(figure)
        print(out)


if __name__ == "__main__":
    main()
