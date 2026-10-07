"""Item 2.3: distribucion del modulo de la velocidad y ajuste de Maxwell-Boltzmann.

Para el sistema sin obstaculos todas las particulas arrancan con el mismo
modulo v0, asi que f(v) es una delta en t = 0 y se va ensanchando hasta el
estado estacionario. La distribucion de un instante se arma juntando los
|v| de las N particulas de todas las realizaciones en ese cuadro; la
estacionaria junta ademas todos los cuadros con t >= --estacionario (promedio
temporal, que para un estado estacionario es el mismo promedio de ensamble) y
asi tiene estadistica suficiente para el ajuste.

La estacionaria se ajusta con la distribucion de Maxwell-Boltzmann en dos
dimensiones

    f(v) = (m v / kT) exp(-m v^2 / 2 kT),

con kT como unico parametro libre y por el metodo de la Teorica 0: se recorre
kT en una grilla y se toma el minimo del error cuadratico medio E(kT), que se
muestra en su propia figura. El valor ajustado se compara con m <v^2> / 2,
que para este sistema vale m v0^2 / 2.

    python3 visualization/speeds.py
    python3 visualization/speeds.py --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

COLORS = ["#111111", "#9467bd", "#ff7f0e", "#2ca02c", common.FRESH]


def load(root: Path):
    """Devuelve (static, tiempos, |v| de forma (F, M*N)) juntando todas las
    realizaciones del barrido, que comparten los mismos instantes guardados."""
    _, cases = common.read_explore(root)
    runs = [run for case in cases.values() for run in case["runs"]]
    speeds = []
    times = None
    static = None
    for run in runs:
        static, times, states = common.load_run(run)
        speeds.append(np.linalg.norm(states[:, :, 2:4], axis=2))
    frames = min(len(s) for s in speeds)
    return static, times[:frames], np.concatenate([s[:frames] for s in speeds], axis=1), len(runs)


def histogram(values: np.ndarray, edges: np.ndarray):
    density, _ = np.histogram(values, bins=edges, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), density


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--velocidades", type=Path, default=common.SPEEDS)
    parser.add_argument("--instantes", type=str, default="0,0.05,0.15,0.5",
                        help="instantes (s) de las distribuciones intermedias")
    parser.add_argument("--estacionario", type=float, default=20.0,
                        help="instante desde el cual se considera estacionario")
    parser.add_argument("--bins", type=int, default=40)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    static, times, speeds, runs = load(arguments.velocidades)
    out_dir = common.folder("2.3", arguments.figures)
    mass, count = static["m"], static["N"]
    edges = np.linspace(0.0, max(2.6 * static["v0"], speeds.max()), arguments.bins + 1)

    # Evolucion: una curva por instante pedido, mas la estacionaria. En t = 0
    # todas las particulas tienen el mismo modulo v0, asi que f(v) es una
    # delta: el eje se escala con el resto de las curvas y esa barra se sale
    # de la figura, que es justamente lo que hay que ver.
    figure, axes = plt.subplots()
    ceiling = 0.0
    for target, color in zip([float(v) for v in arguments.instantes.split(",")], COLORS):
        frame = int(np.searchsorted(times, target, side="right") - 1)
        centers, density = histogram(speeds[frame], edges)
        if frame > 0:
            ceiling = max(ceiling, density.max())
        axes.step(centers, density, where="mid", color=color,
                  label=f"$t$ = {common.decimal(times[frame], 2)} s")
    stationary = speeds[times >= arguments.estacionario].ravel()
    centers, density = histogram(stationary, edges)
    axes.step(centers, density, where="mid", color=common.USED, linewidth=2.4,
              label=f"$t \\geq$ {common.decimal(arguments.estacionario)} s (estacionario)")
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    # El eje se corta en cuatro veces el maximo de la estacionaria: los
    # primeros instantes, que todavia son casi la delta inicial, se salen de
    # la figura y asi se ve como el pico se derrumba y la curva se ensancha.
    axes.set_ylim(0.0, min(1.3 * max(ceiling, density.max()), 4.0 * density.max()))
    axes.legend(loc="upper right")
    evolution = out_dir / f"f_v_vs_t_N{count}_M{runs}.png"
    common.save(figure, evolution)
    plt.close(figure)

    thermal, grid, error = common.fit_thermal_energy(centers, density, mass)
    reference = 0.5 * mass * float((stationary ** 2).mean())
    initial = 0.5 * mass * static["v0"] ** 2

    figure, axes = plt.subplots()
    axes.bar(centers, density, width=np.diff(edges), color=common.FRESH, alpha=0.45,
             edgecolor=common.FRESH, label="simulación (estacionario)")
    fine = np.linspace(edges[0], edges[-1], 400)
    axes.plot(fine, common.maxwell_boltzmann(fine, thermal, mass), color=common.USED,
              linewidth=2.4,
              label=f"Maxwell-Boltzmann, $k_BT$ = {common.decimal(1000 * thermal, 2)} mJ")
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    axes.set_ylim(0.0, 1.32 * density.max())
    axes.legend(loc="upper right")
    fit = out_dir / f"f_v_estacionaria_ajuste_N{count}_M{runs}.png"
    common.save(figure, fit)
    plt.close(figure)

    figure, axes = plt.subplots()
    axes.plot(1000 * grid, error, color=common.FRESH)
    axes.plot([1000 * thermal], [error.min()], marker="o", color=common.USED, markersize=9,
              linestyle="none",
              label=f"mínimo en $k_BT$ = {common.decimal(1000 * thermal, 2)} mJ")
    axes.set_xlabel("energía térmica $k_B T$ (mJ)")
    axes.set_ylabel(common.AXIS_FIT_ERROR)
    axes.legend(loc="upper center")
    error_figure = out_dir / f"E_vs_kT_N{count}_M{runs}.png"
    common.save(figure, error_figure)
    plt.close(figure)

    print(f"N = {count}, sin obstáculos, {runs} realizaciones, "
          f"{len(times)} cuadros hasta t = {times[-1]:.1f} s")
    print(f"muestras del estado estacionario (t ≥ {arguments.estacionario:g} s): "
          f"{stationary.size}")
    print(f"kT ajustado        = {thermal:.6f} J")
    print(f"m <v^2> / 2        = {reference:.6f} J  (diferencia "
          f"{100 * (thermal - reference) / reference:+.1f} %)")
    print(f"m v0^2 / 2         = {initial:.6f} J  (diferencia "
          f"{100 * (thermal - initial) / initial:+.1f} %)")
    print(evolution)
    print(fit)
    print(error_figure)


if __name__ == "__main__":
    main()
