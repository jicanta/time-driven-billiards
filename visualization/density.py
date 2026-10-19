"""Item 2.4.a: ⟨t90⟩ y ⟨t100⟩ contra la densidad.

Lee el barrido propio del item (`make densidad`): obstaculos en contacto
(xo = r, la misma configuracion del item 2.1.b), las mismas densidades que la
columna xo = r del mapa del item 2.4.b, y cada corrida hasta que se convierten
TODAS. De cada realizacion saca t90 y t100 del registro de conversiones y
promedia sobre las M realizaciones de cada N, con el desvio estandar como
barra de error. La densidad es rho = N / (pi R^2).

NO usa las corridas del item 2.1.b, con la catedra de acuerdo. Esas tienen
tf = 30 s fijo y con los obstaculos en contacto el corte llega antes que la
conversion: de N = 200 para arriba ninguna realizacion alcanzaba Fu = 0,9 y a
N = 5 llegaba una sola de diez (promedio de una muestra, sin desvio). Con ese
corte la figura era plana en 21 s y despues se cortaba: no mostraba ninguna
densidad optima, que es justo lo que el item pregunta. Con el barrido propio
las dos curvas existen en todas las densidades, estan promediadas sobre las M
realizaciones y la U se ve.

La figura del item tiene DOS ejes, que es lo que pide: la densidad y el tiempo
de conversion. Un eje de arriba con el N y otro a la derecha con Fu hacen
cuatro escalas en un solo panel y el ojo no sabe cual leer; el N de cada
densidad esta en la tabla de la consola y en densidad.csv.

El simbolo hueco (alguna realizacion no llego antes de tmax, promedio sesgado
hacia abajo) se mantiene por si en algun barrido vuelve a pasar; con el
barrido de `make densidad` no pasa en ninguna densidad.

    python3 visualization/density.py
    python3 visualization/density.py --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import common

FRACTIONS = [(0.9, "$\\langle t_{90} \\rangle$", common.FRESH, "o"),
             (1.0, "$\\langle t_{100} \\rangle$", common.USED, "s")]


def summarize(root: Path) -> tuple[dict, list[dict]]:
    header, cases = common.read_explore(root)
    rows = []
    for name, case in cases.items():
        static = common.read_static(case["runs"][0])
        used = [len(common.read_conversions(run)) / case["N"] for run in case["runs"]]
        mean_used, spread_used = common.mean_std(used)
        row = {"caso": name, "N": case["N"], "R": static["R"],
               "Fu_tf_medio": mean_used, "Fu_tf_desvio": spread_used,
               "M": len(case["runs"])}
        for fraction, *_ in FRACTIONS:
            times = [common.conversion_time(run, fraction) for run in case["runs"]]
            reached = [t for t in times if t is not None]
            mean, std = common.mean_std(reached) if reached else (float("nan"), float("nan"))
            key = f"t{int(round(100 * fraction))}"
            row[f"{key}_medio"] = mean
            row[f"{key}_desvio"] = std
            row[f"{key}_alcanzan"] = len(reached)
        rows.append(row)
    rows.sort(key=lambda row: row["N"])
    return header, rows


def write_csv(rows: list[dict], path: Path) -> None:
    fields = ["caso", "N", "densidad", "fraccion_de_area", "M", "t90_alcanzan", "t90_medio",
              "t90_desvio", "t100_alcanzan", "t100_medio", "t100_desvio", "Fu_tf_medio",
              "Fu_tf_desvio"]
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([row["caso"], row["N"], row["densidad"], row["fraccion"], row["M"],
                             row["t90_alcanzan"], row["t90_medio"], row["t90_desvio"],
                             row["t100_alcanzan"], row["t100_medio"], row["t100_desvio"],
                             row["Fu_tf_medio"], row["Fu_tf_desvio"]])


def density_ticks(axes, rows: list[dict]) -> None:
    """Eje x de densidad: logaritmico y rotulado en los valores medidos."""
    axes.set_xscale("log")
    axes.set_xticks([10, 20, 50, 100, 200, 500])
    axes.set_xticklabels(["10", "20", "50", "100", "200", "500"])
    axes.set_xlabel(common.AXIS_DENSITY)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--densidad", type=Path, default=common.DENSITY)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    header, rows = summarize(arguments.densidad)
    out_dir = common.folder("2.4", arguments.figures)
    domain = rows[0]["R"]
    radius = header.get("r", 0.0175)
    for row in rows:
        row["densidad"] = row["N"] / (np.pi * domain ** 2)
        row["fraccion"] = row["N"] * radius ** 2 / domain ** 2
    write_csv(rows, arguments.densidad / "densidad.csv")
    repeats = min(row["M"] for row in rows)

    figure, axes = plt.subplots()
    incomplete = False
    plotted: list[float] = []
    for fraction, label, color, marker in FRACTIONS:
        key = f"t{int(round(100 * fraction))}"
        shown = [row for row in rows if row[f"{key}_alcanzan"] > 0]
        density = np.array([row["densidad"] for row in shown])
        means = np.array([row[f"{key}_medio"] for row in shown])
        stds = np.array([row[f"{key}_desvio"] for row in shown])
        complete = np.array([row[f"{key}_alcanzan"] == row["M"] for row in shown])
        plotted.extend(density)
        axes.errorbar(density, means, yerr=stds, color=color, marker=marker, linestyle="-",
                      label=label)
        if not complete.all():
            axes.plot(density[~complete], means[~complete], marker=marker, linestyle="none",
                      color=color, markerfacecolor="white", zorder=5, label="_nolegend_")
            incomplete = True
        best = shown[int(np.nanargmin(means))]
        print(f"{key}: mínimo en N = {best['N']} (rho = {best['densidad']:.0f} 1/m²), "
              f"{best[f'{key}_medio']:.1f} ± {best[f'{key}_desvio']:.1f} s")
    # El barrido de N cubre dos decadas de densidad y los puntos donde t90
    # existe estan todos en la primera: con eje lineal quedan amontonados
    # contra el borde izquierdo.
    density_ticks(axes, rows)
    axes.set_ylabel("$\\langle t \\rangle$ (s)")
    # El eje se corta en el ultimo punto medido: a la derecha de ahi no hay
    # tiempo de conversion (ninguna realizacion llega antes de tf), asi que
    # dejar la escala abierta es dejar un hueco que no se puede llenar.
    axes.set_xlim(0.8 * min(plotted), 1.25 * max(plotted))
    # Las dos curvas son una U: el fondo del panel lo ocupa la de t90 y las dos
    # puntas suben. No queda ninguna esquina libre, asi que la leyenda va
    # arriba a la izquierda sobre una franja que se abre a proposito. La
    # entrada del simbolo blanco va al final: no es una serie, es que
    # significa ese simbolo.
    common.headroom(axes, 0.26)
    handles, labels = axes.get_legend_handles_labels()
    if incomplete:
        handles.append(Line2D([], [], marker="o", color="#777777", linestyle="none",
                              markerfacecolor="white"))
        labels.append("no llegan todas")
    axes.legend(handles, labels, loc="upper left", labelspacing=0.35, handletextpad=0.5,
                ncol=2 if not incomplete else 1)
    out = out_dir / f"t90_t100_vs_densidad_M{repeats}.png"
    common.save(figure, out)
    plt.close(figure)

    print(f"{'N':>5} {'ρ (1/m²)':>10} {'φ':>6} {'<t90> (s)':>20} {'<t100> (s)':>20} "
          f"{'Fu(tf)':>7}")
    for row in rows:
        print(f"{row['N']:5d} {row['densidad']:10.0f} {row['fraccion']:6.2f} "
              f"{row['t90_medio']:9.2f} ± {row['t90_desvio']:5.2f} ({row['t90_alcanzan']:2d}) "
              f"{row['t100_medio']:9.2f} ± {row['t100_desvio']:5.2f} ({row['t100_alcanzan']:2d}) "
              f"{row['Fu_tf_medio']:7.2f}")
    print(out)
    print(arguments.densidad / "densidad.csv")


if __name__ == "__main__":
    main()
