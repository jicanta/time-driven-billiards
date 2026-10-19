"""Sistema 1: por que Velocity Verlet pierde un orden con esta fuerza.

Prueba de la decision de implementacion del item 1.1. La Teorica 4 escribe
Velocity Verlet (diapositiva 17) con dos pasos intermedios sobre la velocidad:

    v(t + dt/2) = v(t) + a(t) dt/2                     (paso intermedio 1)
    v(t + dt)   = v(t + dt/2) + a(t + dt) dt/2         (paso intermedio 2)

Con una fuerza que NO depende de la velocidad eso es solo partir la patada en
dos mitades y no hay nada mas que decidir: a(t + dt) sale de r(t + dt). Pero
la del oscilador es f = -k r - gamma v, asi que a(t + dt) necesita v(t + dt),
que es justamente lo que el paso 2 esta por calcular: la recurrencia queda
implicita y hay que elegir con que velocidad se evalua. La diapositiva no dice
cual, porque no escribe el caso con fuerza dependiente de v; entre los dos
pasos intermedios la unica velocidad que existe es la de medio paso, y esa es
la que usa el motor.

Este script mide que cuesta esa eleccion. Reimplementa el oscilador en Python
y corre el mismo barrido de dt con cuatro variantes, que se diferencian SOLO
en con que velocidad evaluan a(t + dt):

    medio-paso   v(t + dt/2)            la del motor (y la que deja la Teorica)
    implicita    v(t + dt) exacta       se despeja: la fuerza es lineal en v
    euler        v(t) + a(t) dt         prediccion de Euler
    congelada    v(t)                   no se actualiza la velocidad

y le ajusta a cada una la ley de potencia ECM = c dt^p. Primero verifica que
la variante `medio-paso` reproduce las trayectorias que escribio el motor en
C++, para que lo que se compare sea lo que efectivamente corre.

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
    for n in range(steps + 1):
        positions[n] = x
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
    return positions


def squared_error(parameters: dict, step: float, steps: int, variant: str) -> float:
    positions = trajectory(parameters, step, steps, variant)
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
        mine = trajectory(parameters, step, steps, "medio-paso")
        # El motor guarda uno de cada save_every pasos: se comparan esos.
        taken = np.rint(t / step).astype(int)
        gap = float(np.abs(mine[taken] - x).max())
        lines.append(f"  dt = {step:7.1e}: máxima diferencia con el motor = {gap:.3e} m"
                     f"{'' if gap <= tolerance else '   <-- NO reproduce'}")
    return lines


def against_verlet(parameters: dict, root: Path) -> list[str]:
    """Compara la variante `implicita` contra Verlet original del motor.

    Las dos integran la misma recurrencia exacta, asi que la variante
    implicita deja de ser un esquema distinto: es el argumento de por que la
    eleccion de medio paso no es solo una aproximacion mas barata."""
    lines = []
    for step in STEPS:
        path = root / "verlet" / f"dt{step:.1e}.txt"
        if not path.exists():
            continue
        t, x, _ = common.read_trajectory(path)
        steps = int(round(parameters["tf"] / step))
        mine = trajectory(parameters, step, steps, "implicita")
        taken = np.rint(t / step).astype(int)
        gap = float(np.abs(mine[taken] - x).max())
        error = np.sqrt(squared_error(parameters, step, steps, "implicita"))
        lines.append(f"  dt = {step:7.1e}: |implícita − Verlet original| ≤ {gap:.1e} m, "
                     f"contra un error del esquema de {error:.1e} m "
                     f"({gap / error:.1e} veces)")
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

    print("\ndespejar v(t + dt) no da un esquema nuevo: es Verlet original")
    for line in against_verlet(parameters, arguments.oscilador):
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
