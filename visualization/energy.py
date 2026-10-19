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

La figura de la energia dibuja un solo panel y solo los dt de --pasos: el
barrido entero son siete curvas y en una misma escala no se distinguen. El
mas largo (10^-3 s) explota dos ordenes de magnitud por encima de E0 y aplasta
a todas las demas contra la recta de E0; 10^-4 s y los dos mas cortos (2*10^-5
y 10^-5 s) caen encima del elegido y no se distinguen de el. Quedan tres, que
es lo que pide el enunciado ("distintos valores de dt") y se leen las tres en
la misma escala: una que deriva hacia arriba, una hacia abajo y la elegida,
que no se despega de E0. El barrido
completo igual se mide: va entero en la tabla, en resumen.csv y en la figura
de la deriva, que es la que elige el paso y lleva el ajuste de la ley de
potencia D = c dt^a sobre los pasos estables, con el exponente en la leyenda.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

COLORS = ["#d62728", "#ff7f0e", "#2ca02c", "#1f5fbf", "#9467bd", "#8c564b", "#17becf"]


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
                             "inestable: queda fuera del ajuste de la ley de potencia")
    parser.add_argument("--pasos", type=str, default="5e-4,2e-4,5e-5",
                        help="los dt (s) que se dibujan en la figura de E(t), separados por "
                             "coma: los representativos, los que se leen en una misma escala")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    rows = summarize(arguments.energia)
    out_dir = common.folder("2.1", arguments.figures)
    count = rows[0]["N"]
    write_csv(rows, arguments.energia / "resumen.csv")

    # Un solo panel y una sola escala, con los dt de --pasos: los que se leen
    # juntos. El resto del barrido no se pierde, sigue en la tabla, en
    # resumen.csv y en la figura de la deriva.
    wanted = [float(value) for value in arguments.pasos.split(",") if value]
    shown = [row for row in rows if any(np.isclose(row["dt"], value) for value in wanted)]
    missing = [value for value in wanted
               if not any(np.isclose(row["dt"], value) for row in rows)]
    if missing:
        raise SystemExit("no hay corrida con dt = " + ", ".join(f"{v:g}" for v in missing))
    figure, axes = plt.subplots()
    for row, color in zip(shown, COLORS):
        axes.plot(row["t"], row["E"], color=color,
                  label=f"$\\Delta t = {common.scientific(row['dt'])}$ s")
    axes.axhline(rows[0]["E0"], color="#111111", linestyle="--", linewidth=1.2,
                 label=f"$E_0$ = {common.decimal(rows[0]['E0'], 2)} J")
    axes.set_ylabel(common.AXIS_ENERGY)
    axes.set_xlabel(common.AXIS_TIME)
    # Las curvas ocupan todo el ancho: la leyenda va arriba, en el hueco que
    # deja el margen, y en dos columnas para no robarle alto a la figura.
    common.headroom(axes, 0.34)
    axes.legend(loc="upper left", ncol=2)
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
    print("dt en la figura de E(t): " + ", ".join(f"{row['dt']:g} s" for row in shown)
          + f" (de los {len(rows)} del barrido; el resto no se distingue en esa escala)")
    print(f"ajuste deriva = c dt^a sobre los pasos estables: a = {exponent:.2f}")
    print(f"dt elegido (deriva ≤ {arguments.cota:g}): {chosen:g} s" if chosen
          else "ningún dt del barrido queda por debajo de la cota")
    print(energy_figure)
    print(drift_figure)
    print(arguments.energia / "resumen.csv")


if __name__ == "__main__":
    main()
