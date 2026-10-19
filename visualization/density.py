"""Item 2.4.a: ⟨t90⟩ y ⟨t100⟩ contra la densidad.

Usa las mismas corridas del item 2.1.b (`billar bench`, obstaculos en contacto
y tf fijo): de cada realizacion saca t90 y t100 del registro de conversiones y
promedia sobre las M realizaciones de cada N, con el desvio estandar como
barra de error. La densidad es rho = N / (pi R^2) y en el eje de arriba va el
N correspondiente.

Si para un N alguna realizacion no llega a la fraccion pedida antes de tf, el
punto va con simbolo hueco, el promedio se toma sobre las que llegaron y en
resumen.csv queda cuantas llegaron y la Fu media a tf; si no llega ninguna, el
N no tiene punto y se informa su Fu(tf).

    python3 visualization/density.py
    python3 visualization/density.py --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

FRACTIONS = [(0.9, "$\\langle t_{90} \\rangle$", common.FRESH, "o"),
             (1.0, "$\\langle t_{100} \\rangle$", common.USED, "s")]


def summarize(root: Path) -> tuple[dict, list[dict]]:
    header, cases = common.read_explore(root)
    rows = []
    for name, case in cases.items():
        static = common.read_static(case["runs"][0])
        row = {"caso": name, "N": case["N"], "R": static["R"],
               "Fu_tf_medio": float(np.mean([len(common.read_conversions(run)) / case["N"]
                                             for run in case["runs"]])),
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
              "t90_desvio", "t100_alcanzan", "t100_medio", "t100_desvio", "Fu_tf_medio"]
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for row in rows:
            writer.writerow([row["caso"], row["N"], row["densidad"], row["fraccion"], row["M"],
                             row["t90_alcanzan"], row["t90_medio"], row["t90_desvio"],
                             row["t100_alcanzan"], row["t100_medio"], row["t100_desvio"],
                             row["Fu_tf_medio"]])


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
    incomplete_labelled = False
    for fraction, label, color, marker in FRACTIONS:
        key = f"t{int(round(100 * fraction))}"
        shown = [row for row in rows if row[f"{key}_alcanzan"] > 0]
        density = np.array([row["densidad"] for row in shown])
        means = np.array([row[f"{key}_medio"] for row in shown])
        stds = np.array([row[f"{key}_desvio"] for row in shown])
        complete = np.array([row[f"{key}_alcanzan"] == row["M"] for row in shown])
        axes.errorbar(density, means, yerr=stds, color=color, marker=marker, linestyle="-",
                      label=label)
        if not complete.all():
            axes.plot(density[~complete], means[~complete], marker=marker, linestyle="none",
                      color=color, markerfacecolor="white", zorder=5,
                      label=None if incomplete_labelled
                      else "hueco: no llegan todas")
            incomplete_labelled = True
        best = shown[int(np.nanargmin(means))]
        print(f"{key}: mínimo en N = {best['N']} (rho = {best['densidad']:.0f} 1/m²), "
              f"{best[f'{key}_medio']:.1f} ± {best[f'{key}_desvio']:.1f} s")
    # Por encima de cierta densidad ninguna realizacion llega a Fu = 0,9 antes
    # de tf y el observable deja de existir: la fraccion de usadas alcanzada en
    # tf, en el eje de la derecha, es lo que sigue informando al sistema ahi (y
    # es lo que pide el enunciado cuando no se alcanza la fraccion).
    right = axes.twinx()
    right.grid(False)
    right.plot([row["densidad"] for row in rows], [row["Fu_tf_medio"] for row in rows],
               color="#2ca02c", marker="^", linestyle="--",
               label=f"$F_u(t_f)$, $t_f$ = {common.decimal(header.get('tmax', 30.0))} s")
    right.set_ylabel("fracción de usadas $F_u(t_f)$")
    # Las dos series quedan en los dos tercios de abajo para que la leyenda
    # entre arriba sin tapar nada (el eje derecho solo se rotula hasta 1).
    right.set_ylim(0.0, 1.8)
    right.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    # El barrido de N cubre dos decadas de densidad y los puntos donde t90
    # existe estan todos en la primera: con eje lineal quedan amontonados
    # contra el borde izquierdo.
    axes.set_xscale("log")
    axes.set_xticks([10, 20, 50, 100, 200, 500])
    axes.set_xticklabels(["10", "20", "50", "100", "200", "500"])
    axes.set_xlabel(common.AXIS_DENSITY)
    axes.set_ylabel("tiempo de conversión (s)")
    common.headroom(axes, 0.33)
    # Arriba a la DERECHA: ahi no hay nada dibujado (<t90> y <t100> dejan de
    # existir pasado rho ~ 130 y la curva de Fu(tf) ya viene bajando), asi que
    # la leyenda no tapa ningun dato. Arriba a la izquierda rozaba los puntos
    # de <t100> y el maximo de Fu(tf). Sin marco, para que no corte la grilla.
    handles = axes.get_legend_handles_labels()
    extra = right.get_legend_handles_labels()
    axes.legend(handles[0] + extra[0], handles[1] + extra[1], loc="upper right",
                frameon=False, labelspacing=0.35, handletextpad=0.5, borderaxespad=0.4)

    # Eje de arriba con el N que corresponde a cada densidad.
    top = axes.secondary_xaxis("top", functions=(lambda d: d * np.pi * domain ** 2,
                                                 lambda n: n / (np.pi * domain ** 2)))
    # Las marcas automaticas del eje logaritmico solo dejan 10 y 100: se
    # rotulan los N del barrido.
    labelled = [n for n in (10, 20, 50, 100, 200, 500) if n <= max(row["N"] for row in rows)]
    top.set_xticks(labelled)
    top.set_xticklabels([str(n) for n in labelled])
    top.set_xlabel(common.AXIS_COUNT)
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
    print(arguments.bench / "densidad.csv")


if __name__ == "__main__":
    main()
