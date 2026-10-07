"""Item 2.2: ⟨t90⟩ con su desvio contra la posicion de los obstaculos.

Lee data/explore/<carpeta>/ (salida de `billar explore`): por cada caso y cada
semilla calcula t90 del registro de conversiones (el instante exacto de la
conversion con la que Fu llega a 0.9) y promedia sobre las M realizaciones,
con el desvio estandar como barra de error. Si alguna realizacion no llega a
0.9 antes de tmax, el punto se dibuja con simbolo hueco, el promedio se toma
sobre las que llegaron y en resumen.csv queda cuantas llegaron y la Fu media a
tmax. Si el barrido tiene mas de un N, va una curva por N: asi se compara la
posicion optima a dos densidades.

Las posiciones extremas del barrido son las dos que permiten los radios:
xo = r (los obstaculos se tocan en el centro) y xo = R - r (tocan la pared).

    python3 visualization/explore.py --explore data/explore/2.2
    python3 visualization/explore.py --explore data/explore/2.2 --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

SERIES_COLORS = [common.FRESH, common.USED, "#2ca02c", "#9467bd", "#ff7f0e"]
SERIES_MARKERS = ["o", "s", "^", "D", "v"]


def summarize(root: Path, fraction: float = 0.9) -> tuple[dict, list[dict]]:
    header, cases = common.read_explore(root)
    rows = []
    for name, case in cases.items():
        times = [common.conversion_time(run, fraction) for run in case["runs"]]
        used = [len(common.read_conversions(run)) / case["N"] for run in case["runs"]]
        reached = [t for t in times if t is not None]
        mean, std = common.mean_std(reached) if reached else (float("nan"), float("nan"))
        rows.append({
            "caso": name,
            "N": case["N"],
            "xo": case["xo"],
            "dt": case["dt"],
            "M": len(times),
            "alcanzan": len(reached),
            "t_medio": mean,
            "t_desvio": std,
            "Fu_tmax_medio": float(np.mean(used)),
        })
    rows.sort(key=lambda row: (row["N"], row["xo"]))
    return header, rows


def write_csv(rows: list[dict], path: Path, fraction: float) -> None:
    label = f"t{int(round(100 * fraction))}"
    fields = ["caso", "N", "xo", "dt", "M", "alcanzan", f"{label}_medio", f"{label}_desvio",
              "Fu_tmax_medio"]
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([row["caso"], row["N"], row["xo"], row["dt"], row["M"],
                             row["alcanzan"], row["t_medio"], row["t_desvio"],
                             row["Fu_tmax_medio"]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--explore", type=Path, default=common.EXPLORE / "2.2")
    parser.add_argument("--fraccion", type=float, default=0.9,
                        help="fraccion de usadas del observable (0.9 para t90, 1 para t100)")
    parser.add_argument("--name", type=str, default="")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    header, rows = summarize(arguments.explore, arguments.fraccion)
    out_dir = common.folder("2.2", arguments.figures)
    label = f"t_{{{int(round(100 * arguments.fraccion))}}}"
    repeats = int(header.get("seeds", rows[0]["M"]))
    write_csv(rows, arguments.explore / f"resumen_{int(round(100 * arguments.fraccion))}.csv",
              arguments.fraccion)

    counts = sorted({row["N"] for row in rows})
    figure, axes = plt.subplots()
    incomplete_labelled = False
    for count, color, marker in zip(counts, SERIES_COLORS, SERIES_MARKERS):
        subset = [row for row in rows if row["N"] == count]
        offsets = np.array([row["xo"] for row in subset])
        means = np.array([row["t_medio"] for row in subset])
        stds = np.array([row["t_desvio"] for row in subset])
        complete = np.array([row["alcanzan"] == row["M"] for row in subset])
        axes.errorbar(offsets, means, yerr=stds, color=color, marker=marker, linestyle="-",
                      label=f"$N$ = {count}")
        if not complete.all():
            axes.plot(offsets[~complete], means[~complete], marker=marker, linestyle="none",
                      color=color, markerfacecolor="white", zorder=5,
                      label=None if incomplete_labelled
                      else "alguna realización no llega a 0,9")
            incomplete_labelled = True
        best = subset[int(np.nanargmin(means))]
        print(f"N = {count}: mínimo en xo = {best['xo']:.4f} m, "
              f"<t{int(round(100 * arguments.fraccion))}> = {best['t_medio']:.1f} ± "
              f"{best['t_desvio']:.1f} s")
    axes.set_xlabel(common.AXIS_OFFSET)
    axes.set_ylabel(f"$\\langle {label} \\rangle$ (s)")
    axes.legend(loc="best")
    name = arguments.name or (f"t{int(round(100 * arguments.fraccion))}_vs_xo_"
                              f"N{'-'.join(str(c) for c in counts)}_M{repeats}.png")
    out = out_dir / name
    common.save(figure, out)
    plt.close(figure)

    print(f"{'caso':>14} {'N':>4} {'xo (m)':>8} {'llegan':>7} "
          f"{'<t' + str(int(round(100 * arguments.fraccion))) + '> (s)':>18} {'Fu(tmax)':>9}")
    for row in rows:
        print(f"{row['caso']:>14} {row['N']:4d} {row['xo']:8.4f} "
              f"{row['alcanzan']:3d}/{row['M']:<3d} {row['t_medio']:8.2f} ± {row['t_desvio']:6.2f} "
              f"{row['Fu_tmax_medio']:9.2f}")
    print(out)
    print(arguments.explore / f"resumen_{int(round(100 * arguments.fraccion))}.csv")


if __name__ == "__main__":
    main()
