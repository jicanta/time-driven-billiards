"""Item 2.4.a: ⟨t90⟩ y ⟨t100⟩ contra la densidad.

Usa las mismas corridas del item 2.1.b (`billar bench`, obstaculos en contacto
y tf fijo): de cada realizacion saca t90 y t100 del registro de conversiones y
promedia sobre las M realizaciones de cada N, con el desvio estandar como
barra de error. La densidad es rho = N / (pi R^2).

La figura del item tiene DOS ejes, que es lo que pide: la densidad y el
tiempo de conversion. El eje de la densidad se corta donde termina el ultimo
punto medido: de ahi para arriba ninguna realizacion llega a la fraccion
antes de tf, asi que no hay tiempo de conversion que dibujar, y una cota
dibujada con flechas suma simbolos que no son datos. Que esas densidades no
tengan punto es el resultado, y lo que queda de ellas es su Fu(tf). Un eje
de arriba con el N y otro a la derecha con Fu(tf) hacen cuatro escalas en un
solo panel y el ojo no sabe cual leer; el N de cada densidad esta en la tabla
de la consola y en densidad.csv, y Fu(tf) va en su propia figura (misma
densidad en el eje x), que es material de analisis y no entra en la charla.

Si para un N alguna realizacion no llega a la fraccion pedida antes de tf, el
punto va con simbolo hueco y el promedio se toma sobre las que llegaron: es
un promedio sesgado (solo las realizaciones afortunadas) y tiene que verse
que lo es. Si no llega ninguna, el N no tiene punto, y lo que queda de ese
sistema es su Fu(tf).

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
    parser.add_argument("--bench", type=Path, default=common.BENCH / "hexagonal")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    header, rows = summarize(arguments.bench)
    out_dir = common.folder("2.4", arguments.figures)
    domain = rows[0]["R"]
    radius = header.get("r", 0.0175)
    for row in rows:
        row["densidad"] = row["N"] / (np.pi * domain ** 2)
        row["fraccion"] = row["N"] * radius ** 2 / domain ** 2
    write_csv(rows, arguments.bench / "densidad.csv")
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
    # Abajo a la DERECHA: ahi no hay nada dibujado, asi que la leyenda no
    # tapa ningun dato. La entrada del simbolo blanco va al final: no es una
    # serie, es que significa ese simbolo.
    handles, labels = axes.get_legend_handles_labels()
    if incomplete:
        handles.append(Line2D([], [], marker="o", color="#777777", linestyle="none",
                              markerfacecolor="white"))
        labels.append("no llegan todas")
    axes.legend(handles, labels, loc="lower right", labelspacing=0.35, handletextpad=0.5)
    out = out_dir / f"t90_t100_vs_densidad_M{repeats}.png"
    common.save(figure, out)
    plt.close(figure)

    # Figura aparte (misma densidad en el eje x): la fraccion de usadas que se
    # alcanza en tf. Es lo unico que queda del sistema donde t90 y t100 ya no
    # existen -- de rho = 245 para arriba ninguna realizacion llega al 90 % --
    # y es con lo que se contesta la segunda parte del item (por que hay una
    # densidad optima). No va a la presentacion: la diapositiva lleva la
    # figura que pide el enunciado y estos numeros se dicen.
    figure, axes = plt.subplots()
    axes.errorbar([row["densidad"] for row in rows], [row["Fu_tf_medio"] for row in rows],
                  yerr=[row["Fu_tf_desvio"] for row in rows], color="#2ca02c", marker="^",
                  linestyle="--")
    density_ticks(axes, rows)
    axes.set_ylabel(f"$F_u(t_f)$, $t_f$ = {common.decimal(header.get('tmax', 30.0))} s")
    axes.set_ylim(0.0, 1.05)
    used_figure = out_dir / f"Fu_tf_vs_densidad_M{repeats}.png"
    common.save(figure, used_figure)
    plt.close(figure)

    print(f"{'N':>5} {'ρ (1/m²)':>10} {'φ':>6} {'<t90> (s)':>20} {'<t100> (s)':>20} "
          f"{'Fu(tf)':>7}")
    for row in rows:
        print(f"{row['N']:5d} {row['densidad']:10.0f} {row['fraccion']:6.2f} "
              f"{row['t90_medio']:9.2f} ± {row['t90_desvio']:5.2f} ({row['t90_alcanzan']:2d}) "
              f"{row['t100_medio']:9.2f} ± {row['t100_desvio']:5.2f} ({row['t100_alcanzan']:2d}) "
              f"{row['Fu_tf_medio']:7.2f}")
    print(out)
    print(used_figure)
    print(arguments.bench / "densidad.csv")


if __name__ == "__main__":
    main()
