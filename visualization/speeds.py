"""Item 2.3: distribucion del modulo de la velocidad y ajuste de Maxwell-Boltzmann.

Para el sistema sin obstaculos todas las particulas arrancan con el mismo
modulo v0, asi que f(v) es una delta en t = 0 y se va ensanchando hasta el
estado estacionario. La distribucion de un instante se arma juntando los
|v| de las N particulas de todas las realizaciones en ese cuadro, y la barra
de error de cada intervalo es el error de la media sobre las realizaciones
(cada realizacion da su propio histograma; la curva es el promedio de los M y
la barra, sigma/sqrt(M)).

La figura de la evolucion muestra INSTANTES, cada uno con su t exacto,
incluido el ultimo: un "t >= algo" no es un instante sino un promedio sobre
muchos cuadros, y en una figura que se llama "f(v) para distintos instantes"
confunde. El promedio sobre cuadros se usa, pero donde hace falta, que es el
ajuste: la estacionaria junta todos los cuadros con t >= --estacionario
(promedio temporal, que para un estado estacionario es el mismo promedio de
ensamble) y asi tiene estadistica suficiente. Por eso sus barras de error son
varias veces mas chicas que las de un instante suelto.

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

# Un color por instante dibujado: el arranque en negro, los intermedios y el
# ultimo (el estacionario) en el rojo de las usadas, que es el que se compara
# con el ajuste de la figura siguiente.
COLORS = ["#111111", "#ff7f0e", common.USED]


def load(root: Path):
    """Devuelve (static, tiempos, |v| de forma (M, F, N)) con una realizacion
    por fila: todas comparten los mismos instantes guardados."""
    _, cases = common.read_explore(root)
    runs = [run for case in cases.values() for run in case["runs"]]
    speeds = []
    times = None
    static = None
    for run in runs:
        static, times, states = common.load_run(run)
        speeds.append(np.linalg.norm(states[:, :, 2:4], axis=2))
    frames = min(len(s) for s in speeds)
    return static, times[:frames], np.stack([s[:frames] for s in speeds]), len(runs)


def histogram(values: np.ndarray, edges: np.ndarray):
    density, _ = np.histogram(values, bins=edges, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), density


def relative(values: np.ndarray, errors: np.ndarray) -> float:
    """Barra de error relativa media, sobre los intervalos con densidad
    apreciable: en las colas vacias el cociente no significa nada (0 sobre 0)."""
    core = values > 0.1 * values.max()
    return float(np.mean(errors[core] / values[core]))


def histograms(samples: np.ndarray, edges: np.ndarray):
    """(centros, f(v) promedio, error de la media) de un conjunto de muestras
    con una realizacion por fila.

    El promedio de los histogramas normalizados de las M realizaciones es el
    histograma de todas juntas (son todas del mismo tamano) y es lo que pide
    el enunciado: f(v) promediada sobre realizaciones. La barra es el error de
    ESA media, sigma/sqrt(M), que es lo que dice cuan bien se la conoce. El
    desvio entre realizaciones a secas (sigma) no serviria aca: en un
    histograma mide el ruido de contar N particulas en un intervalo, no una
    propiedad del sistema, y no baja aunque se corran mas realizaciones."""
    each = np.array([histogram(row, edges)[1] for row in samples])
    centers = 0.5 * (edges[:-1] + edges[1:])
    if len(each) < 2:
        return centers, each.mean(axis=0), None
    return centers, each.mean(axis=0), each.std(axis=0, ddof=1) / np.sqrt(len(each))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--velocidades", type=Path, default=common.SPEEDS)
    parser.add_argument("--instantes", type=str, default="0,0.15",
                        help="instantes (s) de las distribuciones intermedias; el "
                             "ultimo cuadro guardado se agrega siempre")
    parser.add_argument("--estacionario", type=float, default=20.0,
                        help="instante desde el cual se promedia para el ajuste")
    parser.add_argument("--bins", type=int, default=40)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    static, times, speeds, runs = load(arguments.velocidades)
    out_dir = common.folder("2.3", arguments.figures)
    mass, count = static["m"], static["N"]
    edges = np.linspace(0.0, max(2.6 * static["v0"], speeds.max()), arguments.bins + 1)

    # Evolucion: una curva por instante, con el ultimo cuadro guardado como
    # cierre (ahi el sistema ya es estacionario). En t = 0 todas las
    # particulas tienen el mismo modulo v0, asi que f(v) es una delta: el eje
    # se escala con el resto de las curvas y esa barra se sale de la figura,
    # que es justamente lo que hay que ver.
    figure, axes = plt.subplots()
    ceiling = 0.0
    last = None
    targets = [float(v) for v in arguments.instantes.split(",")] + [times[-1]]
    for target, color in zip(targets, COLORS):
        frame = int(np.searchsorted(times, target, side="right") - 1)
        centers, density, spread = histograms(speeds[:, frame, :], edges)
        if frame > 0:
            ceiling = max(ceiling, density.max())
            last, instant_density, instant_spread = density, density, spread
        axes.errorbar(centers, density, yerr=spread, color=color, drawstyle="steps-mid",
                      elinewidth=0.9, capsize=0, linewidth=2.4 if target == targets[-1] else 1.6,
                      label=f"$t$ = {common.decimal(times[frame], 2)} s")
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    # El eje se corta en cuatro veces el maximo del ultimo instante: los
    # primeros, que todavia son casi la delta inicial, se salen de la figura y
    # asi se ve como el pico se derrumba y la curva se ensancha.
    axes.set_ylim(0.0, min(1.3 * max(ceiling, last.max()), 4.0 * last.max()))
    axes.legend(loc="upper right")
    evolution = out_dir / f"f_v_vs_t_N{count}_M{runs}.png"
    common.save(figure, evolution)
    plt.close(figure)

    # Para el ajuste si se promedia sobre cuadros: cada realizacion aporta
    # todos sus cuadros con t >= --estacionario, que es lo que le da al
    # histograma la estadistica que un instante suelto no tiene.
    per_run = speeds[:, times >= arguments.estacionario, :].reshape(runs, -1)
    stationary = per_run.ravel()
    centers, density, spread = histograms(per_run, edges)

    thermal, grid, error = common.fit_thermal_energy(centers, density, mass)
    reference = 0.5 * mass * float((stationary ** 2).mean())
    initial = 0.5 * mass * static["v0"] ** 2

    # La barra es la simulacion y la curva el ajuste: en la leyenda va solo el
    # nombre de cada una. El valor de kT no, porque es EL resultado del item y
    # se dice en la diapositiva, no escondido en un rotulo de la figura.
    figure, axes = plt.subplots()
    axes.bar(centers, density, width=np.diff(edges), color=common.FRESH, alpha=0.45,
             edgecolor=common.FRESH, label="simulación")
    axes.errorbar(centers, density, yerr=spread, color=common.FRESH, linestyle="none",
                  elinewidth=0.9, capsize=0, label="_nolegend_")
    fine = np.linspace(edges[0], edges[-1], 400)
    axes.plot(fine, common.maxwell_boltzmann(fine, thermal, mass), color=common.USED,
              linewidth=2.4, label="Maxwell-Boltzmann")
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    axes.set_ylim(0.0, 1.32 * density.max())
    axes.legend(loc="upper right")
    # Las barras estan dibujadas pero no se ven: juntando todos los cuadros
    # del estacionario de las M realizaciones el error de la media es de
    # menos del 1 % en todos los intervalos. Que sean chicas es el resultado,
    # asi que se dice cuanto valen (igual que en la figura de tiempos).
    worst = relative(density, spread)
    axes.text(0.02, 0.97, "barras: error de la media\n"
                          f"({common.decimal(100 * worst, 1)} % en promedio)",
              transform=axes.transAxes, ha="left", va="top", color="#555555",
              fontsize=plt.rcParams["legend.fontsize"])
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
    common.headroom(axes, 0.22)
    axes.legend(loc="upper center")
    error_figure = out_dir / f"E_vs_kT_N{count}_M{runs}.png"
    common.save(figure, error_figure)
    plt.close(figure)

    print(f"N = {count}, sin obstáculos, {runs} realizaciones, "
          f"{len(times)} cuadros hasta t = {times[-1]:.1f} s")
    print(f"muestras del estado estacionario (t ≥ {arguments.estacionario:g} s): "
          f"{stationary.size} ({per_run.shape[1]} por realización)")
    print(f"barra de error relativa media (error de la media, intervalos con "
          f"f(v) > 10 % del máximo): instante suelto "
          f"{relative(instant_density, instant_spread):.1%}, estacionaria "
          f"{relative(density, spread):.1%}")
    doubling = grid[error <= 2.0 * error.min()]
    print(f"kT ajustado        = {thermal:.6f} J  (el error cuadrático medio del ajuste se "
          f"duplica en {1000 * doubling.min():.2f} y {1000 * doubling.max():.2f} mJ)")
    print(f"m <v^2> / 2        = {reference:.6f} J  (diferencia "
          f"{100 * (thermal - reference) / reference:+.1f} %)")
    print(f"m v0^2 / 2         = {initial:.6f} J  (diferencia "
          f"{100 * (thermal - initial) / initial:+.1f} %)")
    print(evolution)
    print(fit)
    print(error_figure)


if __name__ == "__main__":
    main()
