"""Sistema 1: error cuadratico medio contra el paso de integracion.

Lee las trayectorias que escribe `billar oscillator` (una linea por paso de
integracion) y calcula, para cada esquema y cada dt,

    ECM(dt) = (1/n) sum_n [ r_num(t_n) - r_an(t_n) ]^2,

la suma de las diferencias al cuadrado contra la solucion analitica sobre
TODOS los pasos temporales, normalizada por el numero total de pasos. La
figura va en doble logaritmica (el ECM abarca diez ordenes de magnitud) y a
cada esquema se le ajusta una ley de potencia ECM = c dt^p por cuadrados
minimos en log-log; el exponente va en la leyenda, porque es el que dice el
orden del esquema (ECM ~ dt^p con error ~ dt^(p/2)).

Los dt en los que el ECM ya dejo de bajar se dibujan con simbolo hueco y
quedan fuera del ajuste: ahi el error del esquema quedo por debajo del ruido
de redondeo del doble, asi que el punto mide la precision de la aritmetica y
no el orden del esquema. Con el barrido de este trabajo es uno solo, Verlet
original en dt = 1e-5 s, y es justamente el paso en el que Verlet se separa
de Beeman en la figura.

    python3 visualization/oscillator.py
    python3 visualization/oscillator.py --estilo diapositiva --figures data/figuras_diapositivas
    python3 visualization/oscillator.py --trayectoria 1e-3

Con --trayectoria se agrega la figura de la posicion contra el tiempo de los
cuatro esquemas y la solucion analitica con ese dt (figura de apoyo: en la
presentacion el sistema 1 lleva una sola diapositiva, la del ECM).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import common

# Los dos esquemas que comparten la pendiente dt^4 y que por eso se superponen
# en el panel de arriba: son los que lleva la ampliacion.
FOURTH_ORDER = ("beeman", "verlet")


def summarize(root: Path) -> tuple[dict, dict]:
    """(parametros, {esquema: {'dt': [...], 'ecm': [...], 'pasos': [...]}})."""
    parameters, rows = common.read_oscillator_index(root)
    schemes: dict = {}
    for row in rows:
        series = schemes.setdefault(row["esquema"], {"dt": [], "ecm": [], "pasos": []})
        series["dt"].append(row["dt"])
        series["ecm"].append(common.mean_squared_error(parameters, row["archivo"]))
        series["pasos"].append(row["pasos"])
    for series in schemes.values():
        order = np.argsort(series["dt"])
        for key in series:
            series[key] = list(np.array(series[key])[order])
    return parameters, schemes


def converging(errors: np.ndarray) -> np.ndarray:
    """Máscara de los dt en los que el ECM todavía baja al bajar el paso.

    Con los dt más chicos el error de truncamiento cae por debajo del ruido de
    redondeo del doble y el ECM deja de bajar (en Verlet original incluso
    vuelve a subir: la recurrencia resta dos numeros casi iguales). Esos
    puntos no miden el orden del esquema sino la precision de la aritmetica,
    asi que quedan fuera del ajuste de la ley de potencia, pero SI se
    dibujan, con simbolo hueco: son mediciones y el paso en el que aparecen
    es parte del resultado (es donde Verlet original se separa de Beeman).
    `errors` viene ordenado por dt creciente."""
    keep = np.ones(len(errors), dtype=bool)
    for index in range(len(errors) - 2, -1, -1):
        if not keep[index + 1] or errors[index] >= errors[index + 1]:
            keep[index] = False
    return keep


def flat(constant: np.ndarray, tolerance: float = 0.10) -> np.ndarray:
    """Mascara de los dt en los que ECM/dt^4 se mantiene en su valor tipico.

    Dividir el ECM por dt^4 saca la pendiente comun a los dos esquemas de
    cuarto orden y deja la constante del error, que es lo unico que los
    separa. La constante es plana mientras la medicion sea el error del
    esquema; cuando el redondeo del doble empieza a correrla, el punto se va.
    Pasa antes de llegar al piso: en dt = 2e-5 s el ECM de Verlet original ya
    queda un 20 % por debajo de su ley de potencia (se verifico recalculando
    la trayectoria en precision extendida), una distorsion del orden de la
    diferencia que se quiere mostrar. Se descartan los dt que se apartan mas
    de `tolerance` de la mediana."""
    return np.abs(constant / np.median(constant) - 1.0) <= tolerance


def write_csv(schemes: dict, path: Path) -> None:
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["esquema", "dt", "pasos", "ecm"])
        for name, series in schemes.items():
            for step, count, error in zip(series["dt"], series["pasos"], series["ecm"]):
                writer.writerow([name, step, count, error])


def trajectory_figure(root: Path, parameters: dict, step: float, out_dir: Path) -> Path:
    figure, axes = plt.subplots()
    reference = None
    for name in common.SCHEMES:
        path = root / name / f"dt{step:.1e}.txt"
        if not path.exists():
            continue
        t, x, _ = common.read_trajectory(path)
        color, _ = common.SCHEME_STYLE[name]
        axes.plot(t, x, color=color, linewidth=1.4, label=common.SCHEME_LABEL[name])
        reference = t
    if reference is not None:
        axes.plot(reference, common.analytic_position(parameters, reference), color="#111111",
                  linestyle="--", linewidth=1.2, label="analítica")
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_POSITION)
    axes.legend(loc="upper right", ncol=2)
    out = out_dir / f"posicion_vs_t_dt{step:.1e}.png"
    common.save(figure, out)
    plt.close(figure)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--oscilador", type=Path, default=common.OSCILLATOR)
    parser.add_argument("--trayectoria", type=float, default=0.0,
                        help="dt de la figura de posicion contra tiempo (0 = no hacerla)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    parameters, schemes = summarize(arguments.oscilador)
    out_dir = common.folder("1", arguments.figures)
    write_csv(schemes, arguments.oscilador / "ecm.csv")

    # La figura de la diapositiva es UNA sola: ECM contra dt de los cuatro
    # esquemas en doble logaritmica, que es exactamente lo que pide el
    # enunciado del sistema 1 ("solo se debe mostrar una diapositiva [...] con
    # esta ultima figura de ECM vs dt para los 4 metodos [...] ni ninguna otra
    # informacion"). Lo que distingue a Beeman de Verlet original es la
    # constante del error, no la pendiente, y en diez ordenes de magnitud una
    # diferencia del 15 % no se ve: eso va en su propia figura (abajo), que es
    # material de analisis y no entra en la charla.
    figure, axes = plt.subplots()
    exponents = {}
    saturated = {}
    constants = {}
    outside_zoom = {}
    for name in common.SCHEMES:
        if name not in schemes:
            continue
        series = schemes[name]
        steps = np.array(series["dt"])
        errors = np.array(series["ecm"])
        keep = converging(errors)
        saturated[name] = list(steps[~keep])
        color, marker = common.SCHEME_STYLE[name]
        exponent, _ = np.polyfit(np.log(steps[keep]), np.log(errors[keep]), 1)
        exponents[name] = exponent
        axes.plot(steps[keep], errors[keep], color=color, marker=marker,
                  linestyle="--" if name == "verlet" else "-",
                  label=f"{common.SCHEME_LABEL[name]} ($p$ = {common.decimal(exponent, 1)})")
        # Los dt saturados se dibujan huecos: son mediciones y marcan donde
        # el esquema toca el piso de redondeo, pero no entran en el ajuste.
        if (~keep).any():
            axes.plot(steps[~keep], errors[~keep], color=color, marker=marker,
                      linestyle="none", markerfacecolor="white", zorder=5)
        if name not in FOURTH_ORDER:
            continue
        constant = errors[keep] / steps[keep] ** 4
        flat_mask = flat(constant)
        constants[name] = (steps[keep][flat_mask], constant[flat_mask])
        outside_zoom[name] = list(steps[keep][~flat_mask])
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel(common.AXIS_STEP)
    axes.set_ylabel(common.AXIS_ECM)
    # Los puntos suben en diagonal: la esquina superior izquierda queda libre.
    common.headroom(axes, 0.52)
    handles, labels = axes.get_legend_handles_labels()
    if any(dropped for dropped in saturated.values()):
        handles.append(Line2D([], [], marker="o", color="#777777", linestyle="none",
                              markerfacecolor="white"))
        labels.append("piso de redondeo (fuera del ajuste)")
    axes.legend(handles, labels, loc="upper left")
    out = out_dir / "ECM_vs_dt.png"
    common.save(figure, out)
    plt.close(figure)

    # Figura de analisis, aparte: la constante del error de los dos esquemas de
    # cuarto orden. Dividir el ECM por dt^4 saca la pendiente que comparten y
    # deja lo unico que los separa. Escala propia, ajustada a los datos.
    zoom = None
    if len(constants) == len(FOURTH_ORDER):
        figure, axes = plt.subplots()
        for name, (steps, constant) in constants.items():
            color, marker = common.SCHEME_STYLE[name]
            axes.plot(steps, constant, color=color, marker=marker,
                      linestyle="--" if name == "verlet" else "-",
                      label=common.SCHEME_LABEL[name])
        axes.set_xscale("log")
        axes.set_xlabel(common.AXIS_STEP)
        axes.set_ylabel(common.AXIS_ECM_CONSTANT)
        # Las dos rectas son planas y difieren un 15 %: el rango se fija a los
        # datos mas un margen del 10 % de la separacion arriba y abajo, que es
        # lo que las deja bien separadas sin dejar la mitad del panel vacio.
        low = min(constant.min() for _, constant in constants.values())
        high = max(constant.max() for _, constant in constants.values())
        span = high - low
        axes.set_ylim(low - 0.35 * span, high + 0.35 * span)
        axes.legend(loc="center right")
        zoom = out_dir / "ECM_constante_vs_dt.png"
        common.save(figure, zoom)
        plt.close(figure)

    print(f"m = {parameters['m']:g} kg, k = {parameters['k']:g} N/m, "
          f"gamma = {parameters['gamma']:g} kg/s, A = {parameters['A']:g} m, "
          f"tf = {parameters['tf']:g} s, w = {common.angular_frequency(parameters):.4f} rad/s")
    print(f"{'dt (s)':>10}" + "".join(f"{common.SCHEME_LABEL[n]:>28}" for n in schemes))
    every = sorted({s for series in schemes.values() for s in series["dt"]}, reverse=True)
    for step in every:
        row = f"{step:10.1e}"
        for series in schemes.values():
            index = series["dt"].index(step) if step in series["dt"] else None
            row += f"{series['ecm'][index]:28.6e}" if index is not None else f"{'':>28}"
        print(row)
    print("ajuste ECM = c dt^p (cuadrados mínimos en log-log, sin los dt que ya están en el "
          "piso de redondeo): " +
          ", ".join(f"{common.SCHEME_LABEL[n]} p = {p:.2f}" for n, p in exponents.items()))
    if len(constants) == len(FOURTH_ORDER):
        reference, compared = FOURTH_ORDER
        median = {name: float(np.median(constants[name][1])) for name in FOURTH_ORDER}
        print("constante del error ECM/dt^4 (m²/s⁴): "
              + ", ".join(f"{common.SCHEME_LABEL[n]} = {median[n]:.0f}" for n in FOURTH_ORDER)
              + f"; {common.SCHEME_LABEL[compared]} mide "
                f"{median[compared] / median[reference] - 1:+.0%} de ECM respecto de "
                f"{common.SCHEME_LABEL[reference]} con el mismo paso")
    for name, dropped in saturated.items():
        if dropped:
            print(f"  {common.SCHEME_LABEL[name]}: el ECM deja de bajar en dt ≤ "
                  f"{max(dropped):.0e} s ({len(dropped)} punto(s) dibujados huecos, "
                  f"fuera del ajuste)")
    for name, dropped in outside_zoom.items():
        if dropped:
            print(f"  {common.SCHEME_LABEL[name]}: fuera de la ampliación en dt ≤ "
                  f"{max(dropped):.0e} s ({len(dropped)} punto(s): la constante se "
                  f"aparta más del 10 % de su mediana, el redondeo ya la corre)")
    wins = {name: sum(1 for k in range(len(series["ecm"]))
                      if all(series["ecm"][k] <= other["ecm"][k] for other in schemes.values()))
            for name, series in schemes.items()}
    best = max(wins, key=lambda name: wins[name])
    print(f"menor ECM: {common.SCHEME_LABEL[best]} en {wins[best]} de "
          f"{len(schemes[best]['ecm'])} pasos del barrido")
    print(out)
    if zoom is not None:
        print(zoom)
    print(arguments.oscilador / "ecm.csv")

    if arguments.trayectoria > 0:
        print(trajectory_figure(arguments.oscilador, parameters, arguments.trayectoria, out_dir))


if __name__ == "__main__":
    main()
