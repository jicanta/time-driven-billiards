"""Item 2.4.b (opcional): mapa de calor de ⟨t90⟩ en el plano (xo, N).

Lee data/mapa/ (un barrido de `billar explore` sobre el producto de --xos y
--ns) y dibuja, para cada punto (xo, N), el promedio del tiempo de conversion
sobre las realizaciones. Las celdas donde alguna realizacion no llega a la
fraccion pedida antes de tmax quedan en blanco y se informan por consola.

La respuesta del item (si la posicion que minimiza ⟨t90⟩ depende o no de la
densidad) se lee de la banda oscura, no de una marca sobre la celda mas baja:
con 6 realizaciones por punto el minimo de cada fila casi nunca se distingue
de sus vecinas, asi que marcarlo haria parecer que salta entre 0,2 y 0,3
cuando eso es ruido. El listado por consola da el error de la media de cada
minimo y que celdas son compatibles con el.

    python3 visualization/heatmap.py
    python3 visualization/heatmap.py --fraccion 1 --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common


def summarize(root: Path, fraction: float):
    _, cases = common.read_explore(root)
    counts = sorted({case["N"] for case in cases.values()})
    offsets = sorted({case["xo"] for case in cases.values()})
    grid = np.full((len(counts), len(offsets)), np.nan)
    spread = np.full_like(grid, np.nan)
    reached = np.zeros_like(grid)
    for case in cases.values():
        times = [common.conversion_time(run, fraction) for run in case["runs"]]
        valid = [t for t in times if t is not None]
        row, column = counts.index(case["N"]), offsets.index(case["xo"])
        reached[row, column] = len(valid)
        if len(valid) == len(times):
            grid[row, column], spread[row, column] = common.mean_std(valid)
    return np.array(counts), np.array(offsets), grid, spread, reached


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mapa", type=Path, default=common.MAP)
    parser.add_argument("--fraccion", type=float, default=0.9)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    counts, offsets, grid, spread, reached = summarize(arguments.mapa, arguments.fraccion)
    out_dir = common.folder("2.4", arguments.figures)
    percent = int(round(100 * arguments.fraccion))

    with open(arguments.mapa / f"mapa_{percent}.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["N", "xo", f"t{percent}_medio", "alcanzan"])
        for row, count in enumerate(counts):
            for column, offset in enumerate(offsets):
                writer.writerow([count, offset, grid[row, column], int(reached[row, column])])

    # Celdas de igual tamano (ejes categoricos): los N y los xo del barrido no
    # estan igualmente espaciados y con ejes lineales las filas de N chico
    # quedan aplastadas contra el borde.
    figure, axes = plt.subplots()
    axes.grid(False)
    mesh = axes.pcolormesh(np.arange(len(offsets) + 1) - 0.5,
                           np.arange(len(counts) + 1) - 0.5, grid, cmap="viridis",
                           shading="flat")
    bar = figure.colorbar(mesh, ax=axes)
    bar.set_label(f"$\\langle t_{{{percent}}} \\rangle$ (s)")
    # La celda mas baja de cada fila NO se marca en la figura. Con 6
    # realizaciones por punto casi nunca se distingue de sus vecinas (a N = 50
    # son compatibles desde xo = 0,1 hasta 0,4), asi que un circulo sobre una
    # sola celda afirmaria una precision que la medicion no tiene y haria
    # parecer que el optimo salta entre 0,2 y 0,3 cuando eso es ruido. El mapa
    # muestra la banda oscura y la lectura la hacemos nosotros. Por consola si
    # va, con el error de la media y que celdas son compatibles con el minimo.
    for row, count in enumerate(counts):
        if np.all(np.isnan(grid[row])):
            continue
        best = int(np.nanargmin(grid[row]))
        error = spread[row] / np.sqrt(np.maximum(reached[row], 1.0))
        compatible = [offsets[column] for column in range(len(offsets))
                      if not np.isnan(grid[row, column])
                      and grid[row, column] - error[column] <= grid[row, best] + error[best]]
        print(f"N = {count}: mínimo en xo = {offsets[best]:.4f} m, "
              f"<t{percent}> = {grid[row, best]:.1f} ± {error[best]:.1f} s; "
              "compatibles dentro del error: "
              + ", ".join(f"{value:g}" for value in compatible))
    axes.set_xticks(np.arange(len(offsets)))
    axes.set_xticklabels([common.decimal(round(x, 4)) for x in offsets])
    axes.set_yticks(np.arange(len(counts)))
    axes.set_yticklabels([str(int(n)) for n in counts])
    axes.set_xlabel(common.AXIS_OFFSET)
    axes.set_ylabel(common.AXIS_COUNT)
    out = out_dir / f"mapa_t{percent}_xo_N.png"
    common.save(figure, out)
    plt.close(figure)

    missing = [(counts[r], offsets[c]) for r in range(len(counts)) for c in range(len(offsets))
               if np.isnan(grid[r, c])]
    if missing:
        print(f"celdas sin valor (alguna realización no llega a {percent} %): " +
              ", ".join(f"N = {n}, xo = {x:.4f}" for n, x in missing))
    print(out)
    print(arguments.mapa / f"mapa_{percent}.csv")


if __name__ == "__main__":
    main()
