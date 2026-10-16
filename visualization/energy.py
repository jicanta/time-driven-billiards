"""Item 2.1.a: energia total contra el tiempo y eleccion del paso temporal.

El sistema es conservativo (resorte lineal, sin friccion ni disipacion), asi
que la energia total

    E(t) = sum_i 1/2 m v_i^2 + sum_contactos 1/2 k xi^2

debe ser constante: lo que se mide es cuanto se aparta, que es el error del
esquema de integracion (Teorica 4, diapositiva 35). El motor no la calcula:
sale de los estados guardados en dynamic.txt, con las mismas xi del enunciado
(pares de particulas, obstaculos y la particula imagen de la pared).

El observable escalar que resume cada curva es la **deriva relativa maxima**

    D(dt) = max_t |E(t) - E(0)| / E(0),

una sola cifra por corrida, que se grafica contra dt para elegir el paso: se
toma el dt mas grande cuya deriva queda por debajo de la tolerancia (--cota),
porque es el que da el menor tiempo de ejecucion con el error aceptado.

    python3 visualization/energy.py
    python3 visualization/energy.py --estilo diapositiva --figures data/figuras_diapositivas

La figura de la energia tiene dos paneles con el mismo eje de tiempos: toda la
escala (donde se ve que el paso mas largo explota) y la ampliacion sobre los
pasos estables, como las dos vistas de la Teorica 4 (diapositiva 38). La de la
deriva lleva el ajuste de la ley de potencia D = c dt^a sobre los pasos
estables, con el exponente en la leyenda.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

COLORS = ["#d62728", "#ff7f0e", "#2ca02c", "#1f5fbf", "#9467bd", "#8c564b", "#17becf"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X"]


def summarize(root: Path) -> list[dict]:
    """Una fila por paso de integracion: la curva E(t) y su deriva relativa."""
    _, cases = common.read_explore(root)
    rows = []
    for name, case in cases.items():
        run = case["runs"][0]
        static, times, states = common.load_run(run)
        energy = common.total_energy(states, static)
        rows.append({
            "caso": name,
            "dt": case["dt"],
            "N": case["N"],
            "xo": case["xo"],
            "t": times,
            "E": energy,
            "E0": float(energy[0]),
            "deriva": float(np.abs(energy - energy[0]).max() / energy[0]),
            "deriva_final": float(abs(energy[-1] - energy[0]) / energy[0]),
            "cuadros": len(times),
        })
    rows.sort(key=lambda row: row["dt"], reverse=True)
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dt", "N", "cuadros", "E0", "deriva_relativa_maxima",
                         "deriva_relativa_final"])
        for row in rows:
            writer.writerow([row["dt"], row["N"], row["cuadros"], row["E0"], row["deriva"],
                             row["deriva_final"]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--energia", type=Path, default=common.ENERGY)
    parser.add_argument("--cota", type=float, default=1e-3,
                        help="tolerancia de la deriva relativa para elegir el paso")
    parser.add_argument("--estable", type=float, default=0.1,
                        help="deriva por encima de la cual se considera que el paso es "
                             "inestable: queda fuera de la ampliacion y del ajuste")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    rows = summarize(arguments.energia)
    out_dir = common.folder("2.1", arguments.figures)
    count = rows[0]["N"]
    write_csv(rows, arguments.energia / "resumen.csv")

    # Dos vistas de la misma curva, como en la Teorica 4 (diapositiva 38), en
    # una sola figura: arriba toda la escala, donde se ve que el paso mas largo
    # explota; abajo la ampliacion sobre los pasos que si conservan la energia,
    # donde se ordenan de mayor a menor dt. Comparten el eje de tiempos.
    stable_rows = [row for row in rows if row["deriva"] <= arguments.estable]
    width, height = plt.rcParams["figure.figsize"]
    figure, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(width, 1.55 * height),
                                         gridspec_kw={"height_ratios": [1.0, 1.0],
                                                      "hspace": 0.08})
    for row, color in zip(rows, COLORS):
        label = f"$\\Delta t = {common.scientific(row['dt'])}$ s"
        top.plot(row["t"], row["E"], color=color, label=label)
        if row in stable_rows:
            bottom.plot(row["t"], row["E"], color=color, label=label)
    for axes in (top, bottom):
        axes.axhline(rows[0]["E0"], color="#111111", linestyle="--", linewidth=1.2,
                     label=f"$E_0$ = {common.decimal(rows[0]['E0'], 2)} J" if axes is top else None)
        axes.set_ylabel(common.AXIS_ENERGY)
    bottom.set_xlabel(common.AXIS_TIME)
    common.headroom(top, 0.30)
    top.legend(loc="upper left", ncol=2)
    # La ampliacion muestra lo que la escala completa aplasta: el rango es el
    # de los pasos estables (la deriva puede ser hacia arriba o hacia abajo),
    # con un margen arriba para el rotulo.
    low = min(row["E"].min() for row in stable_rows)
    high = max(row["E"].max() for row in stable_rows)
    bottom.set_ylim(low - 0.08 * (high - low), high + 0.18 * (high - low))
    bottom.text(0.985, 0.95, "ampliación", transform=bottom.transAxes, ha="right", va="top",
                color="#555555", fontsize=plt.rcParams["legend.fontsize"])
    energy_figure = out_dir / f"energia_vs_t_N{count}.png"
    common.save(figure, energy_figure)
    plt.close(figure)

    steps = np.array([row["dt"] for row in rows])
    drift = np.array([row["deriva"] for row in rows])
    chosen = float(steps[drift <= arguments.cota].max()) if (drift <= arguments.cota).any() else None

    stable = drift <= arguments.estable
    exponent, intercept = np.polyfit(np.log(steps[stable]), np.log(drift[stable]), 1)

    figure, axes = plt.subplots()
    axes.plot(steps, drift, color=common.FRESH, marker="o", linestyle="none", markersize=8,
              label="deriva medida")
    line = np.geomspace(steps[stable].min(), steps[stable].max(), 100)
    axes.plot(line, np.exp(intercept) * line ** exponent, color=common.FRESH, linestyle="--",
              linewidth=1.6,
              label=f"ajuste $c\\,\\Delta t^{{a}}$, $a$ = {common.decimal(exponent, 1)}")
    axes.axhline(arguments.cota, color=common.USED, linestyle="--", linewidth=1.4,
                 label=f"cota {common.decimal(arguments.cota)}")
    if chosen is not None:
        axes.plot([chosen], [drift[steps == chosen][0]], marker="o", markersize=16,
                  markerfacecolor="none", markeredgecolor=common.USED, markeredgewidth=2,
                  linestyle="none",
                  label=f"$\\Delta t$ elegido = ${common.scientific(chosen)}$ s")
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel(common.AXIS_STEP)
    axes.set_ylabel(common.AXIS_DRIFT)
    # Los puntos suben en diagonal: la esquina superior izquierda queda libre.
    common.headroom(axes, 0.36)
    axes.legend(loc="upper left")
    drift_figure = out_dir / f"deriva_vs_dt_N{count}.png"
    common.save(figure, drift_figure)
    plt.close(figure)

    offset = rows[0]["xo"]
    where = "sin obstáculos" if offset < 0 else f"xo = {offset:g} m"
    print(f"N = {count}, {where}, E0 = {rows[0]['E0']:.6g} J")
    print(f"{'dt (s)':>10} {'cuadros':>8} {'deriva máxima':>16} {'deriva final':>14}")
    for row in rows:
        print(f"{row['dt']:10.1e} {row['cuadros']:8d} {row['deriva']:16.3e} "
              f"{row['deriva_final']:14.3e}")
    print(f"ajuste deriva = c dt^a sobre los pasos estables: a = {exponent:.2f}")
    print(f"dt elegido (deriva ≤ {arguments.cota:g}): {chosen:g} s" if chosen
          else "ningún dt del barrido queda por debajo de la cota")
    print(energy_figure)
    print(drift_figure)
    print(arguments.energia / "resumen.csv")


if __name__ == "__main__":
    main()
