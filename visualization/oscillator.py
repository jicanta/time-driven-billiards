"""Sistema 1: la energia contra el tiempo y el error cuadratico medio contra
el paso de integracion.

Son las dos figuras del sistema 1 en la presentacion. El enunciado pedia una
sola diapositiva, la del ECM; la catedra pidio ademas la energia del oscilador
tal cual, en valor absoluto, a lo largo del tiempo, con los cuatro esquemas
sobre la solucion analitica. Esa va primero (es la evolucion) y el ECM
despues (es el escalar).

La energia es E = m v^2 / 2 + k x^2 / 2 y NO se conserva: el amortiguamiento
la disipa como exp(-gamma t / m), con ondulaciones porque la potencia
disipada es gamma v^2 y v oscila. Se dibuja con UN solo dt (--energia, el mas
largo del barrido): a ese paso Euler predictor-corrector pierde energia mucho
mas rapido que la analitica (le agrega disipacion numerica) y los otros tres
caen encima de la curva exacta; con pasos mas cortos Euler se acerca y la
figura deja de distinguir nada, que es justamente lo que mide el ECM. Eje
lineal: es el valor absoluto de la energia lo que se pidio ver.

Lee las trayectorias que escribe `billar oscillator` (una linea por paso de
integracion) y calcula, para cada esquema y cada dt,

    ECM(dt) = (1/n) sum_n [ r_num(t_n) - r_an(t_n) ]^2,

la suma de las diferencias al cuadrado contra la solucion analitica sobre
TODOS los pasos temporales, normalizada por el numero total de pasos. La
figura va en doble logaritmica (el ECM abarca diez ordenes de magnitud) y a
cada esquema se le ajusta una ley de potencia ECM = c dt^p por cuadrados
minimos en log-log. La leyenda nombra los cuatro esquemas y nada mas: el
exponente del ajuste no va ahi (el enunciado pide la figura de ECM vs dt "ni
ninguna otra informacion", y una letra suelta no se entiende sin explicarla).
Sale por consola, esta en la diapositiva escrito como pendiente y se dice en
la charla.

Todos los dt medidos se dibujan iguales, con el simbolo lleno de su esquema:
son todos mediciones y ninguno vale menos que los otros. Lo que si cambia es
el ajuste: los dt en los que el ECM ya dejo de bajar quedan afuera, porque
ahi el error del esquema cayo por debajo del ruido de redondeo del doble y el
punto mide la precision de la aritmetica y no el orden del esquema. Con el
barrido de este trabajo es uno solo, Verlet original en dt = 1e-5 s, y es
justamente el paso en el que Verlet se separa de Beeman en la figura.

    python3 visualization/oscillator.py
    python3 visualization/oscillator.py --estilo diapositiva --figures data/figuras_diapositivas
    python3 visualization/oscillator.py --trayectoria 1e-3

Con --trayectoria se agrega la figura de la posicion contra el tiempo de los
cuatro esquemas y la solucion analitica con ese dt (figura de apoyo, fuera de
la presentacion).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

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
    asi que quedan fuera del ajuste de la ley de potencia, pero se dibujan
    como todos los demas: son mediciones y el paso en el que aparecen es
    parte del resultado (es donde Verlet original se separa de Beeman).
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


def energy_figure(root: Path, parameters: dict, step: float, out_dir: Path):
    """E(t) de los cuatro esquemas con el paso `step`, sobre la analitica.
    Devuelve (ruta, {esquema: E / E_analitica en t = 1 s}, E0)."""
    figure, axes = plt.subplots()
    reference = None
    ratio_at_one = {}
    initial = None
    for name in common.SCHEMES:
        path = root / name / f"dt{step:.1e}.txt"
        if not path.exists():
            continue
        t, x, v = common.read_trajectory(path)
        energy = common.oscillator_energy(parameters, x, v)
        color, _ = common.SCHEME_STYLE[name]
        axes.plot(t, energy, color=color, linewidth=1.8, label=common.SCHEME_LABEL[name])
        reference = t
        initial = float(energy[0])
        exact = common.oscillator_energy(parameters, common.analytic_position(parameters, t),
                                         common.analytic_velocity(parameters, t))
        one = int(np.searchsorted(t, 1.0))
        ratio_at_one[name] = float(energy[one] / exact[one])
    if reference is not None:
        exact = common.oscillator_energy(parameters, common.analytic_position(parameters, reference),
                                         common.analytic_velocity(parameters, reference))
        # La analitica punteada y encima de todas: donde un esquema la sigue,
        # se ve la raya sobre su curva; donde no, queda el hueco.
        axes.plot(reference, exact, color="#111111", linestyle="--", linewidth=1.4,
                  label="analítica", zorder=3)
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_ENERGY)
    axes.set_xlim(0.0, float(reference[-1]))
    axes.set_ylim(bottom=0.0)
    # La energia cae desde la esquina superior izquierda: la derecha queda libre.
    axes.legend(loc="upper right")
    out = out_dir / f"energia_vs_t_dt{step:.1e}.png"
    common.save(figure, out)
    plt.close(figure)
    return out, ratio_at_one, initial


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--oscilador", type=Path, default=common.OSCILLATOR)
    parser.add_argument("--energia", type=float, default=5e-3,
                        help="dt de la figura de energia contra tiempo (el mas largo del "
                             "barrido: es donde los esquemas se distinguen a ojo)")
    parser.add_argument("--trayectoria", type=float, default=0.0,
                        help="dt de la figura de posicion contra tiempo (0 = no hacerla)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    parameters, schemes = summarize(arguments.oscilador)
    out_dir = common.folder("1", arguments.figures)
    write_csv(schemes, arguments.oscilador / "ecm.csv")

    # Primera figura: la energia contra el tiempo con el dt de --energia.
    energy_out, ratio_at_one, initial = energy_figure(arguments.oscilador, parameters,
                                                      arguments.energia, out_dir)

    # Segunda figura: ECM contra dt de los cuatro esquemas en doble
    # logaritmica, un solo panel, que es lo que pide el enunciado del sistema 1
    # ("esta ultima figura de ECM vs dt para los 4 metodos [...] ni ninguna
    # otra informacion"). Lo que distingue a Beeman de Verlet original es la
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
        # Se dibujan TODOS los dt medidos, con el mismo simbolo lleno: el que
        # queda fuera del ajuste (Verlet original en dt = 1e-5 s, donde el ECM
        # ya toco el piso de redondeo) es un punto mas de su serie. Que no
        # entre en el ajuste es cosa del ajuste, no del dato, y distinguirlo
        # en la figura obliga a explicar un simbolo extra en una diapositiva
        # en la que el enunciado no quiere nada de mas.
        axes.plot(steps, errors, color=color, marker=marker,
                  linestyle="--" if name == "verlet" else "-",
                  label=common.SCHEME_LABEL[name])
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
    common.headroom(axes, 0.45)
    axes.legend(loc="upper left")
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
    print(f"energía contra el tiempo con dt = {arguments.energia:g} s: E0 = {initial:.1f} J, "
          f"decae como exp(-t / {parameters['m'] / parameters['gamma']:.2f} s); en t = 1 s cada "
          "esquema tiene, respecto de la analítica, "
          + ", ".join(f"{common.SCHEME_LABEL[n]} {100 * (r - 1):+.1f} %" for n, r in ratio_at_one.items()))
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
                  f"{max(dropped):.0e} s ({len(dropped)} punto(s) dibujados como todos "
                  f"los demás, fuera del ajuste)")
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
    print(energy_out)
    print(out)
    if zoom is not None:
        print(zoom)
    print(arguments.oscilador / "ecm.csv")

    if arguments.trayectoria > 0:
        print(trajectory_figure(arguments.oscilador, parameters, arguments.trayectoria, out_dir))


if __name__ == "__main__":
    main()
