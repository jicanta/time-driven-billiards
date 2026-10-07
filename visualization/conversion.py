"""Fraccion de usadas contra el tiempo, con la marca de t90.

Fu(t) es un escalon que sube 1/N en el instante exacto de cada conversion
(leido de events.txt): cuando una particula fresca toca por primera vez uno de
los obstaculos. Cada corrida es una carpeta con static.txt y events.txt (de
`billar simulate`, `billar explore` o `billar bench`).

    python3 visualization/conversion.py --runs data/explore/2.2/xo0.0175/s7 --labels "x_o = 0,0175 m"
    python3 visualization/conversion.py --runs data/explore/2.2/xo0.2500/s7,...,s11 --realizaciones
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

import common

COLORS = ["#555555", common.FRESH, "#2ca02c", "#9467bd", common.USED, "#ff7f0e"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=str, required=True, help="carpetas separadas por coma")
    parser.add_argument("--labels", type=str, default="")
    parser.add_argument("--name", type=str, default="")
    parser.add_argument("--tmax", type=float, default=0.0,
                        help="limite del eje t (0 = hasta la ultima conversion)")
    parser.add_argument("--realizaciones", action="store_true",
                        help="las corridas son realizaciones de una misma configuracion: "
                             "mismo color y una sola entrada en la leyenda")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    runs = [Path(p) for p in arguments.runs.split(",")]
    labels = arguments.labels.split(",") if arguments.labels else [run.parent.name for run in runs]
    out_dir = common.folder("2.2", arguments.figures)

    if arguments.realizaciones:
        colors = [common.FRESH] * len(runs)
        labels = [f"{len(runs)} realizaciones" if k == 0 else "_" for k in range(len(runs))]
    else:
        colors = COLORS

    figure, axes = plt.subplots()
    reached = []
    for run, label, color in zip(runs, labels, colors):
        times, fraction = common.used_fraction(run)
        t90 = common.conversion_time(run, 0.9)
        axes.step(times, fraction, where="post", color=color, label=label,
                  alpha=0.75 if arguments.realizaciones else 1.0)
        if t90 is not None:
            axes.plot([t90], [0.9], marker="o", color=color, markersize=8, linestyle="none")
            axes.vlines(t90, 0, 0.9, color=color, linestyle=":", linewidth=1.2)
            reached.append(t90)
            print(f"{label}: t90 = {t90:.2f} s")
        else:
            print(f"{label}: no llega a 0.9 (Fu(tmax) = {fraction[-1]:.2f})")
    if arguments.realizaciones and reached:
        mean, std = common.mean_std(reached)
        axes.axvspan(mean - std, mean + std, color=common.FRESH, alpha=0.12, linewidth=0)
        axes.axvline(mean, color=common.FRESH, linewidth=1.6, linestyle="--",
                     label=f"$\\langle t_{{90}}\\rangle$ = {common.decimal(mean, 1)} ± "
                           f"{common.decimal(std, 1)} s")
        print(f"<t90> = {mean:.2f} ± {std:.2f} s ({len(reached)}/{len(runs)} llegan a 0,9)")
    axes.axhline(0.9, color="#999999", linestyle="--", linewidth=1)
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_FU)
    axes.set_ylim(0, 1.02)
    if arguments.tmax > 0:
        axes.set_xlim(0, arguments.tmax)
    axes.legend(loc="lower right")
    name = arguments.name or "Fu_vs_t_" + "_".join(run.parent.name for run in runs) + ".png"
    common.save(figure, out_dir / name)
    print(out_dir / name)


if __name__ == "__main__":
    main()
