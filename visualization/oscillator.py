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

import common


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
    puntos quedan fuera del ajuste de la ley de potencia, porque ahi ya no se
    mide el orden del esquema; en la figura van con simbolo hueco. `errors`
    viene ordenado por dt creciente."""
    keep = np.ones(len(errors), dtype=bool)
    for index in range(len(errors) - 2, -1, -1):
        if not keep[index + 1] or errors[index] >= errors[index + 1]:
            keep[index] = False
    return keep


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

    figure, axes = plt.subplots()
    exponents = {}
    saturated = {}
    floor_labelled = False
    for name in common.SCHEMES:
        if name not in schemes:
            continue
        series = schemes[name]
        steps = np.array(series["dt"])
        errors = np.array(series["ecm"])
        keep = converging(errors)
        saturated[name] = list(steps[~keep])
        color, marker = common.SCHEME_STYLE[name]
        exponent, intercept = np.polyfit(np.log(steps[keep]), np.log(errors[keep]), 1)
        exponents[name] = exponent
        axes.plot(steps, errors, color=color, marker=marker,
                  linestyle="--" if name == "verlet" else "-",
                  label=f"{common.SCHEME_LABEL[name]} ($p$ = {common.decimal(exponent, 1)})")
        if not keep.all():
            axes.plot(steps[~keep], errors[~keep], marker=marker, linestyle="none",
                      color=color, markerfacecolor="white", zorder=5,
                      label=None if floor_labelled else "piso de redondeo")
            floor_labelled = True
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel(common.AXIS_STEP)
    axes.set_ylabel(common.AXIS_ECM)
    common.headroom(axes, 0.44)
    axes.legend(loc="upper left")
    out = out_dir / "ECM_vs_dt.png"
    common.save(figure, out)
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
    for name, steps in saturated.items():
        if steps:
            print(f"  {common.SCHEME_LABEL[name]}: el ECM deja de bajar en dt ≤ "
                  f"{max(steps):.0e} s ({len(steps)} punto(s) fuera del ajuste)")
    wins = {name: sum(1 for k in range(len(series["ecm"]))
                      if all(series["ecm"][k] <= other["ecm"][k] for other in schemes.values()))
            for name, series in schemes.items()}
    best = max(wins, key=lambda name: wins[name])
    print(f"menor ECM: {common.SCHEME_LABEL[best]} en {wins[best]} de "
          f"{len(schemes[best]['ecm'])} pasos del barrido")
    print(out)
    print(arguments.oscilador / "ecm.csv")

    if arguments.trayectoria > 0:
        print(trajectory_figure(arguments.oscilador, parameters, arguments.trayectoria, out_dir))


if __name__ == "__main__":
    main()
