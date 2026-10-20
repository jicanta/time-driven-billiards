"""Item 2.1.a: energia total contra el tiempo y eleccion del paso temporal.

El sistema es conservativo (resorte lineal, sin friccion ni disipacion), asi
que la energia total

    E(t) = sum_i 1/2 m v_i^2 + sum_contactos 1/2 k xi^2

debe ser constante: lo que se mide es cuanto se aparta, que es el error del
esquema de integracion (Teorica 4, diapositiva 35). El motor no la calcula:
sale de los estados guardados en dynamic.txt, con las mismas xi del enunciado
(pares de particulas, obstaculos y la particula imagen de la pared).

Van dos figuras contra el tiempo. La primera es la EVOLUCION DEL SISTEMA, la
energia total en Joule tal como la pide el enunciado, con el dt que se despega
hacia arriba (5*10^-4 s, +2,6 %), el que se despega hacia abajo (2*10^-4 s) y
los dos que se quedan sobre E0 (10^-4 y 5*10^-5 s). La segunda es su **error
relativo en porcentaje**

    eps(t) = 100 (E(t) - E_0) / E_0,

que es lo que se decide: "me quedo con este paso porque el error es menor que
tanto por ciento". En Joule hay que leer la separacion contra la recta de E0 y
dividir mentalmente; en porcentaje el numero del eje ya es el numero de la
frase, y el cero -- la conservacion exacta -- queda en el medio. La del error
deja afuera el 5*10^-4 s, que ya se vio despegarse en la primera, y asi la
escala alcanza para distinguir 10^-4 s (0,1 %) del elegido (0,04 %).

El observable escalar que resume cada curva es el **maximo de ese error**

    eps_max(dt) = max_t |eps(t)|,

una sola cifra por corrida, que se grafica contra dt para elegir el paso: se
toma el dt mas grande cuyo error queda por debajo de la tolerancia (--cota),
porque es el que da el menor tiempo de ejecucion con el error aceptado.

    python3 visualization/energy.py
    python3 visualization/energy.py --estilo diapositiva --figures data/figuras_diapositivas

La figura del error dibuja un solo panel y solo los dt de --pasos: el barrido
entero son siete curvas y en una misma escala no se distinguen. El mas largo
(10^-3 s) se va al 1000 % y aplasta a todas las demas contra el cero; 10^-4 s y
los dos mas cortos (2*10^-5 y 10^-5 s) caen encima del elegido y no se
distinguen de el. Quedan tres, que es lo que pide el enunciado ("distintos
valores de dt") y se leen las tres en la misma escala: una que se va hacia
arriba, una hacia abajo y la elegida, que se queda sobre el cero. El barrido
completo igual se mide: va entero en la tabla, en resumen.csv y en la figura de
eps_max, que es la que elige el paso y lleva el ajuste de la ley de potencia
eps_max = c dt^a sobre los pasos estables, con el exponente en la leyenda.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

# Un color por dt, el MISMO en la figura de E(t) y en la de eps(t): las dos
# muestran las mismas corridas y un dt tiene que verse igual en las dos.
COLORS = {1e-3: "#9467bd", 5e-4: "#d62728", 2e-4: "#ff7f0e", 1e-4: "#2ca02c",
          5e-5: "#1f5fbf", 2e-5: "#8c564b", 1e-5: "#17becf"}


def color_of(step: float) -> str:
    return next(color for value, color in COLORS.items() if np.isclose(step, value))


def select(rows: list[dict], wanted: str) -> list[dict]:
    """Las filas de los dt pedidos (lista separada por coma), en el orden del
    barrido (dt decreciente)."""
    values = [float(value) for value in wanted.split(",") if value]
    missing = [value for value in values
               if not any(np.isclose(row["dt"], value) for row in rows)]
    if missing:
        raise SystemExit("no hay corrida con dt = " + ", ".join(f"{v:g}" for v in missing))
    return [row for row in rows if any(np.isclose(row["dt"], value) for value in values)]


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
    parser.add_argument("--pasos-energia", type=str, default="5e-4,2e-4,1e-4,5e-5",
                        help="los dt (s) de la figura de E(t) en Joule, separados por coma: "
                             "el que se despega para arriba, el que se despega para abajo "
                             "y los dos que se quedan sobre E0")
    parser.add_argument("--pasos", type=str, default="2e-4,1e-4,5e-5",
                        help="los dt (s) que se dibujan en la figura del error eps(t), "
                             "separados por coma: los que se leen en una misma escala "
                             "alrededor del elegido")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    rows = summarize(arguments.energia)
    out_dir = common.folder("2.1", arguments.figures)
    count = rows[0]["N"]
    write_csv(rows, arguments.energia / "resumen.csv")

    # LA EVOLUCION DEL SISTEMA: la energia total en Joule contra el tiempo,
    # que es lo que pide el enunciado ("graficar la energia total del sistema
    # en funcion del tiempo para distintos valores de dt"). Van los dt de
    # --pasos-energia: el que se despega hacia arriba, el que se despega hacia
    # abajo y los que se quedan sobre E0. El mas largo (10^-3 s) se va a 45 J y
    # aplastaria a todos contra E0: queda en la figura de eps_max, con el
    # barrido entero.
    shown_energy = select(rows, arguments.pasos_energia)
    figure, axes = plt.subplots()
    reach = 0.0
    for row in shown_energy:
        reach = max(reach, float(np.abs(row["E"] - row["E0"]).max()))
        axes.plot(row["t"], row["E"], color=color_of(row["dt"]),
                  label=f"$\\Delta t = {common.scientific(row['dt'])}$ s")
    base = rows[0]["E0"]
    axes.axhline(base, color="#111111", linestyle=":", linewidth=1.3,
                 label=f"$E_0$ = {common.decimal(base, 2)} J", zorder=1)
    axes.set_ylabel(common.AXIS_ENERGY)
    axes.set_xlabel(common.AXIS_TIME)
    # Simetrico alrededor de E0, que queda en el medio: la mitad que las
    # curvas no usan es donde entra la leyenda.
    axes.set_ylim(base - 1.3 * reach, base + 1.3 * reach)
    axes.legend(loc="lower left", ncol=2)
    value_figure = out_dir / f"energia_vs_t_N{count}.png"
    common.save(figure, value_figure)
    plt.close(figure)

    # EL ERROR, en porcentaje, con los dt de --pasos: los que se leen juntos en
    # una escala alrededor del elegido. El resto del barrido no se pierde,
    # sigue en la tabla, en resumen.csv y en la figura de eps_max.
    shown = select(rows, arguments.pasos)
    figure, axes = plt.subplots()
    reach = 0.0
    highest, lowest = 0.0, 0.0
    for row in shown:
        error = 100.0 * (row["E"] - row["E0"]) / row["E0"]
        reach = max(reach, float(np.abs(error).max()))
        highest, lowest = max(highest, float(error.max())), min(lowest, float(error.min()))
        axes.plot(row["t"], error, color=color_of(row["dt"]),
                  label=f"$\\Delta t = {common.scientific(row['dt'])}$ s")
    # La referencia es el CERO, que es la conservacion exacta, y el eje se abre
    # igual para los dos lados: queda en el medio de la figura, con las curvas
    # que se van hacia arriba de un lado y las que se van hacia abajo del otro.
    # Antes la referencia era la recta de E0 en Joule, que con estas curvas
    # caia contra el borde de abajo y habia que mirarla de costado.
    axes.axhline(0.0, color="#111111", linestyle=":", linewidth=1.3,
                 label="conservación exacta", zorder=1)
    axes.set_ylabel(common.AXIS_ENERGY_ERROR)
    axes.set_xlabel(common.AXIS_TIME)
    # Simetrico: el cero queda en el medio. Las curvas no lo son (la que mas
    # deriva lo hace hacia un solo lado), y la mitad que queda libre es donde
    # entra la leyenda sin tapar nada: arriba si la deriva grande es negativa,
    # abajo si es positiva.
    axes.set_ylim(-1.3 * reach, 1.3 * reach)
    axes.legend(loc="upper left" if abs(lowest) > highest else "lower left", ncol=2)
    energy_figure = out_dir / f"error_energia_vs_t_N{count}.png"
    common.save(figure, energy_figure)
    plt.close(figure)

    steps = np.array([row["dt"] for row in rows])
    # En porcentaje, la misma unidad que la figura de eps(t): la cota de la
    # linea de comandos viene en relativo y se convierte aca.
    drift = 100.0 * np.array([row["deriva"] for row in rows])
    limit = 100.0 * arguments.cota
    chosen = float(steps[drift <= limit].max()) if (drift <= limit).any() else None

    stable = drift <= 100.0 * arguments.estable
    exponent, intercept = np.polyfit(np.log(steps[stable]), np.log(drift[stable]), 1)

    figure, axes = plt.subplots()
    axes.plot(steps, drift, color=common.FRESH, marker="o", linestyle="none", markersize=8,
              label="error medido")
    line = np.geomspace(steps[stable].min(), steps[stable].max(), 100)
    axes.plot(line, np.exp(intercept) * line ** exponent, color=common.FRESH, linestyle="--",
              linewidth=1.6,
              label=f"ajuste $c\\,\\Delta t^{{a}}$, $a$ = {common.decimal(exponent, 1)}")
    # La cota va en gris punteado y no en rojo: es el criterio, no un
    # resultado. El rojo queda para el unico dato que la figura senala, que es
    # el paso elegido.
    axes.axhline(limit, color="#777777", linestyle=":", linewidth=1.4,
                 label=f"cota {common.decimal(limit)} %", zorder=1)
    if chosen is not None:
        axes.plot([chosen], [drift[steps == chosen][0]], marker="o", markersize=16,
                  markerfacecolor="none", markeredgecolor=common.USED, markeredgewidth=2,
                  linestyle="none",
                  label=f"$\\Delta t$ elegido = ${common.scientific(chosen)}$ s")
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel(common.AXIS_STEP)
    axes.set_ylabel(common.AXIS_DRIFT)
    # Los puntos suben en diagonal: la esquina libre es la de arriba a la
    # izquierda. El hueco que se le deja es chico a proposito: en escala
    # logaritmica cada punto de headroom son decadas enteras, y con el paso
    # inestable arriba (1000 %) y el mas corto abajo (0,001 %) el eje ya cubre
    # seis decadas; agregarle cuatro vacias dejaba todos los puntos aplastados
    # contra el borde de abajo.
    common.headroom(axes, 0.20)
    axes.legend(loc="upper left")
    drift_figure = out_dir / f"error_maximo_vs_dt_N{count}.png"
    common.save(figure, drift_figure)
    plt.close(figure)

    offset = rows[0]["xo"]
    where = "sin obstáculos" if offset < 0 else f"xo = {offset:g} m"
    print(f"N = {count}, {where}, E0 = {rows[0]['E0']:.6g} J")
    print(f"{'dt (s)':>10} {'cuadros':>8} {'|eps| máximo (%)':>18} {'eps final (%)':>15}")
    for row in rows:
        print(f"{row['dt']:10.1e} {row['cuadros']:8d} {100 * row['deriva']:18.4g} "
              f"{100 * row['deriva_final']:15.4g}")
    print("dt en la figura de E(t): " + ", ".join(f"{row['dt']:g} s" for row in shown_energy)
          + f" (de los {len(rows)} del barrido)")
    print("dt en la figura de eps(t): " + ", ".join(f"{row['dt']:g} s" for row in shown)
          + f" (de los {len(rows)} del barrido; el resto no se distingue en esa escala)")
    print(f"ajuste eps_max = c dt^a sobre los pasos estables: a = {exponent:.2f}")
    print(f"dt elegido (error ≤ {limit:g} %): {chosen:g} s" if chosen
          else "ningún dt del barrido queda por debajo de la cota")
    print(value_figure)
    print(energy_figure)
    print(drift_figure)
    print(arguments.energia / "resumen.csv")


if __name__ == "__main__":
    main()
