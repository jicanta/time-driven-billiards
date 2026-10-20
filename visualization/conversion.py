"""Item 2.2: Fu(t) para pocos valores tipicos de xo, en una sola figura.

El enunciado pide "graficar Fu(t) para pocos valores tipicos de xo y los
correspondientes <t90> con su barra de error en funcion de xo": las curvas de
los xo tipicos van JUNTAS, en un mismo par de ejes, porque lo que hay que leer
es como se corre Fu(t) al mover los obstaculos. Una figura por xo no deja
comparar nada.

Fu(t) de una realizacion es un escalon que sube 1/N en el instante exacto de
cada conversion (leido de events.txt). De cada caso (una carpeta con las M
realizaciones, cada una con static.txt y events.txt) se dibuja el promedio
sobre las realizaciones, evaluado en una grilla de tiempos comun, con una
banda de +-1 desvio estandar entre realizaciones; el punto marca <t90> y la
barra horizontal su desvio.

    python3 visualization/conversion.py --casos data/explore/2.2/n100_xo0.0175,\\
        data/explore/2.2/n100_xo0.2000,data/explore/2.2/n100_xo0.4925
    python3 visualization/conversion.py --casos ... --estilo diapositiva \\
        --figures data/figuras_diapositivas

Con --runs (en vez de --casos) dibuja las corridas sueltas, una curva por
carpeta: es la vista de apoyo para mirar una configuracion de cerca.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

# Un color por xo tipico, en el orden en que se pasan: centro, optimo, borde.
CASE_STYLES = [(common.FRESH, "o"), ("#2ca02c", "^"), (common.USED, "s"),
               ("#9467bd", "D"), ("#ff7f0e", "v")]
COLORS = ["#555555", common.FRESH, "#2ca02c", "#9467bd", common.USED, "#ff7f0e"]


def mean_curve(runs: list[Path], grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fu(t) promedio y desvio entre realizaciones sobre la grilla `grid`.

    Cada realizacion es un escalon con sus propios instantes: para promediar
    hay que evaluarlas todas en los mismos tiempos. Fu es constante entre
    conversiones, asi que la evaluacion es un `searchsorted` (el escalon vale,
    en t, la cantidad de conversiones con instante <= t, sobre N)."""
    curves = []
    for run in runs:
        times = common.read_conversions(run)
        count = common.read_static(run)["N"]
        curves.append(np.searchsorted(times, grid, side="right") / count)
    stacked = np.vstack(curves)
    return stacked.mean(axis=0), stacked.std(axis=0, ddof=1) if len(curves) > 1 else \
        np.zeros_like(stacked[0])


def case_label(case: Path) -> str:
    """'n100_xo0.2000' -> 'x_o = 0,20 m'."""
    offset = case.name.split("xo")[-1]
    return f"$x_o$ = {common.decimal(float(offset), 4).rstrip('0').rstrip(',')} m"


def plot_cases(axes, cases: list[Path], labels: list[str], tmax: float) -> list[str]:
    lines = []
    grid = np.linspace(0.0, tmax, 1000)
    for case, label, (color, marker) in zip(cases, labels, CASE_STYLES):
        runs = sorted(p for p in case.iterdir() if p.is_dir())
        mean, std = mean_curve(runs, grid)
        times = [common.conversion_time(run, 0.9) for run in runs]
        reached = [t for t in times if t is not None]
        axes.plot(grid, mean, color=color, label=label)
        axes.fill_between(grid, mean - std, mean + std, color=color, alpha=0.15, linewidth=0)
        if reached:
            # <t90> con su desvio, sobre la linea de 0,9: la barra lleva el
            # mismo estilo que las del resto de las figuras (common.ERRORBAR).
            center, spread = common.mean_std(reached)
            axes.errorbar([center], [0.9], xerr=[spread], color=color, marker=marker,
                          zorder=5, **common.ERRORBAR)
            lines.append(f"{case.name}: <t90> = {center:.2f} ± {spread:.2f} s "
                         f"({len(reached)}/{len(runs)} llegan a 0,9), "
                         f"Fu({tmax:g} s) = {mean[-1]:.2f}")
        else:
            lines.append(f"{case.name}: ninguna realización llega a 0,9, "
                         f"Fu({tmax:g} s) = {mean[-1]:.2f}")
    return lines


def plot_runs(axes, runs: list[Path], labels: list[str], realizations: bool) -> list[str]:
    lines = []
    colors = [common.FRESH] * len(runs) if realizations else COLORS
    if realizations:
        labels = [f"{len(runs)} realizaciones" if k == 0 else "_" for k in range(len(runs))]
    reached = []
    for run, label, color in zip(runs, labels, colors):
        times, fraction = common.used_fraction(run)
        t90 = common.conversion_time(run, 0.9)
        axes.step(times, fraction, where="post", color=color, label=label,
                  alpha=0.75 if realizations else 1.0)
        if t90 is not None:
            axes.plot([t90], [0.9], marker="o", color=color, markersize=8, linestyle="none")
            axes.vlines(t90, 0, 0.9, color=color, linestyle=":", linewidth=1.2)
            reached.append(t90)
            lines.append(f"{label}: t90 = {t90:.2f} s")
        else:
            lines.append(f"{label}: no llega a 0,9 (Fu(tmax) = {fraction[-1]:.2f})")
    if realizations and reached:
        mean, std = common.mean_std(reached)
        axes.axvspan(mean - std, mean + std, color=common.FRESH, alpha=0.12, linewidth=0)
        axes.axvline(mean, color=common.FRESH, linewidth=1.6, linestyle="--",
                     label=f"$\\langle t_{{90}}\\rangle$ = {common.decimal(mean, 1)} ± "
                           f"{common.decimal(std, 1)} s")
        lines.append(f"<t90> = {mean:.2f} ± {std:.2f} s ({len(reached)}/{len(runs)} llegan)")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--casos", type=str, default="",
                        help="carpetas de caso (cada una con sus realizaciones), separadas "
                             "por coma: una curva promedio por caso")
    parser.add_argument("--runs", type=str, default="",
                        help="carpetas de corrida sueltas, separadas por coma")
    parser.add_argument("--labels", type=str, default="")
    parser.add_argument("--name", type=str, default="")
    parser.add_argument("--tmax", type=float, default=0.0,
                        help="limite del eje t (0 = hasta la ultima conversion)")
    parser.add_argument("--realizaciones", action="store_true",
                        help="con --runs: las corridas son realizaciones de una misma "
                             "configuracion (mismo color, una sola entrada en la leyenda)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)
    if bool(arguments.casos) == bool(arguments.runs):
        raise SystemExit("hay que pasar --casos o --runs (uno de los dos)")

    out_dir = common.folder("2.2", arguments.figures)
    figure, axes = plt.subplots()
    if arguments.casos:
        cases = [Path(p) for p in arguments.casos.split(",")]
        labels = arguments.labels.split(",") if arguments.labels else \
            [case_label(case) for case in cases]
        if arguments.tmax <= 0.0:
            raise SystemExit("--casos necesita --tmax: las curvas se promedian sobre una "
                             "grilla de tiempos comun")
        lines = plot_cases(axes, cases, labels, arguments.tmax)
        default_name = "Fu_vs_t_" + "_".join(case.name for case in cases) + ".png"
    else:
        runs = [Path(p) for p in arguments.runs.split(",")]
        labels = arguments.labels.split(",") if arguments.labels else \
            [run.parent.name for run in runs]
        lines = plot_runs(axes, runs, labels, arguments.realizaciones)
        default_name = "Fu_vs_t_" + "_".join(run.parent.name for run in runs) + ".png"

    # La linea de 0,9 es la definicion de t90 y va en la leyenda como todo lo
    # que esta dibujado (igual que la "conservacion exacta" de la energia):
    # los simbolos sobre ella son <t90> y la barra su desvio.
    axes.axhline(0.9, color="#999999", linestyle="--", linewidth=1.2,
                 label="$F_u$ = 0,9: $\\langle t_{90} \\rangle$")
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_FU)
    axes.set_ylim(0, 1.02)
    if arguments.tmax > 0:
        axes.set_xlim(0, arguments.tmax)
    axes.legend(loc="lower right")
    out = out_dir / (arguments.name or default_name)
    common.save(figure, out)
    plt.close(figure)
    for line in lines:
        print(line)
    print(out)


if __name__ == "__main__":
    main()
