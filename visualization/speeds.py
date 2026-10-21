"""Item 2.3: distribucion del modulo de la velocidad y ajuste de Maxwell-Boltzmann.

Para el sistema sin obstaculos todas las particulas arrancan con el mismo
modulo v0, asi que f(v) es una delta en t = 0 y se va ensanchando hasta el
estado estacionario.

Cada histograma se arma de UNA SOLA BOLSA de muestras: los |v| de las N
particulas de las M realizaciones, todos juntos en el mismo histograma (N x M
muestras por instante, y N x M x cuadros en el estacionario). No es el promedio
de los M histogramas de cada realizacion con su desvio como barra: con N = 100
particulas repartidas en 40 intervalos, el histograma de una realizacion sola
es ruido, y promediar M curvas ruidosas con barras del 50 % tapa la forma de
f(v), que es lo que la figura tiene que mostrar. Juntando todo en una bolsa la
estadistica es M veces mayor y la curva se lee. Cuantas realizaciones y cuantos
cuadros entran en la bolsa va dicho en la figura y en la diapositiva: es lo que
hace falta para saber de donde sale.

El desvio entre realizaciones se sigue midiendo y este script lo imprime (es la
respuesta si preguntan por la dispersion), pero no se dibuja: la figura es el
histograma de la bolsa.

La figura de la evolucion muestra INSTANTES, cada uno con su t exacto,
incluido el ultimo: un "t >= algo" no es un instante sino un promedio sobre
muchos cuadros, y en una figura que se llama "f(v) para distintos instantes"
confunde. El promedio sobre cuadros se usa, pero donde hace falta, que es el
ajuste: la estacionaria junta todos los cuadros con t >= --estacionario
(promedio temporal, que para un estado estacionario es el mismo promedio de
ensamble) y asi tiene estadistica suficiente: su bolsa tiene 400 veces mas
muestras que la de un instante suelto.

Antes de la bolsa del estacionario va la rapidez media contra el tiempo: un
escalar por cuadro (la media de |v| de la bolsa de ese instante, con el desvio
entre realizaciones como banda) que dice cuando empieza el estacionario. Esa
banda existe porque <|v|> se calcula por realizacion y se promedia: el
histograma de la gran bolsa, en cambio, es UNO solo y no tiene desvio que
dibujar. Con el kT ajustado, Maxwell-Boltzmann predice <|v|> = sqrt(pi kT /
2m): es una verificacion independiente del ajuste.

La estacionaria (LA GRAN BOLSA: todos los cuadros con t >= --estacionario de
todas las realizaciones, en un solo histograma) se ajusta con la distribucion
de Maxwell-Boltzmann en dos dimensiones

    f(v) = (m v / kT) exp(-m v^2 / 2 kT),

con kT como unico parametro libre y por el metodo de la Teorica 0: se recorre
kT en una grilla y se toma el minimo del error cuadratico medio E(kT), que se
muestra en su propia figura. El valor ajustado se compara con m <v^2> / 2,
que para este sistema vale m v0^2 / 2.

    python3 visualization/speeds.py
    python3 visualization/speeds.py --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

# Un color por instante dibujado: el arranque en negro, los intermedios y el
# ultimo (el estacionario) en el rojo de las usadas, que es el que se compara
# con el ajuste de la figura siguiente.
COLORS = ["#111111", "#ff7f0e", common.USED]


def load(root: Path):
    """Devuelve (static, tiempos, |v| de forma (M, F, N)) con una realizacion
    por fila: todas comparten los mismos instantes guardados."""
    _, cases = common.read_explore(root)
    runs = [run for case in cases.values() for run in case["runs"]]
    speeds = []
    times = None
    static = None
    for run in runs:
        static, times, states = common.load_run(run)
        speeds.append(np.linalg.norm(states[:, :, 2:4], axis=2))
    frames = min(len(s) for s in speeds)
    return static, times[:frames], np.stack([s[:frames] for s in speeds]), len(runs)


def histogram(values: np.ndarray, edges: np.ndarray):
    density, _ = np.histogram(values, bins=edges, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), density


def relative(values: np.ndarray, errors: np.ndarray) -> float:
    """Barra de error relativa media, sobre los intervalos con densidad
    apreciable: en las colas vacias el cociente no significa nada (0 sobre 0)."""
    core = values > 0.1 * values.max()
    return float(np.mean(errors[core] / values[core]))


def pooled(samples: np.ndarray, edges: np.ndarray):
    """(centros, f(v), cuantas muestras) del histograma de LA BOLSA: todas las
    muestras del arreglo juntas, sin separar por realizacion.

    Es lo que se dibuja. Como todas las realizaciones tienen el mismo numero de
    particulas, el histograma de la bolsa coincide con el promedio de los
    histogramas de cada una, pero la bolsa es lo que la figura dice que es: un
    solo histograma de N x M muestras."""
    centers, density = histogram(samples.ravel(), edges)
    return centers, density, int(samples.size)


def spread_between_runs(samples: np.ndarray, edges: np.ndarray):
    """Desvio estandar entre realizaciones, intervalo por intervalo, con una
    realizacion por fila. No se dibuja: la figura es el histograma de la bolsa.
    Se mide y se imprime porque es la respuesta si preguntan por la dispersion
    de una realizacion suelta."""
    each = np.array([histogram(row, edges)[1] for row in samples])
    if len(each) < 2:
        return None
    return each.std(axis=0, ddof=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--velocidades", type=Path, default=common.SPEEDS)
    parser.add_argument("--instantes", type=str, default="0,0.15",
                        help="instantes (s) de las distribuciones intermedias; el "
                             "ultimo cuadro guardado se agrega siempre")
    parser.add_argument("--estacionario", type=float, default=20.0,
                        help="instante desde el cual se promedia para el ajuste")
    parser.add_argument("--bins", type=int, default=40)
    parser.add_argument("--ventana", type=float, default=2.0,
                        help="hasta que instante (s) se dibuja la rapidez media contra t: "
                             "el transitorio dura medio segundo y despues es plano")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    static, times, speeds, runs = load(arguments.velocidades)
    out_dir = common.folder("2.3", arguments.figures)
    mass, count = static["m"], static["N"]
    edges = np.linspace(0.0, max(2.6 * static["v0"], speeds.max()), arguments.bins + 1)

    # Evolucion: una curva por instante, con el ultimo cuadro guardado como
    # cierre (ahi el sistema ya es estacionario). En t = 0 todas las
    # particulas tienen el mismo modulo v0, asi que f(v) es una delta: el eje
    # se escala con el resto de las curvas y esa barra se sale de la figura,
    # que es justamente lo que hay que ver.
    figure, axes = plt.subplots()
    ceiling = 0.0
    last = None
    per_instant = 0
    targets = [float(v) for v in arguments.instantes.split(",")] + [times[-1]]
    for target, color in zip(targets, COLORS):
        frame = int(np.searchsorted(times, target, side="right") - 1)
        centers, density, per_instant = pooled(speeds[:, frame, :], edges)
        if frame > 0:
            ceiling = max(ceiling, density.max())
            last = density
            instant_density = density
            instant_spread = spread_between_runs(speeds[:, frame, :], edges)
        axes.step(centers, density, where="mid", color=color,
                  linewidth=2.4 if target == targets[-1] else 1.6,
                  label=f"$t$ = {common.decimal(times[frame], 2)} s")
    # De donde sale cada curva (M realizaciones x N particulas de ese cuadro) va
    # en la linea de condiciones de la diapositiva y no escrito dentro de la
    # figura, que es la convencion del resto del trabajo: los parametros al
    # costado, la figura con los datos. Este script imprime los numeros.
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    # El eje se corta en cuatro veces el maximo del ultimo instante: los
    # primeros, que todavia son casi la delta inicial, se salen de la figura y
    # asi se ve como el pico se derrumba y la curva se ensancha.
    axes.set_ylim(0.0, min(1.3 * max(ceiling, last.max()), 4.0 * last.max()))
    axes.legend(loc="upper right")
    evolution = out_dir / f"f_v_vs_t_N{count}_M{runs}.png"
    common.save(figure, evolution)
    plt.close(figure)

    # LA GRAN BOLSA: para el ajuste se juntan todos los cuadros con
    # t >= --estacionario de todas las realizaciones en un solo histograma
    # (runs x cuadros x N muestras), que es lo que le da la estadistica que un
    # instante suelto no tiene.
    per_run = speeds[:, times >= arguments.estacionario, :].reshape(runs, -1)
    stationary = per_run.ravel()
    frames = int((times >= arguments.estacionario).sum())
    centers, density, per_pool = pooled(per_run, edges)
    spread = spread_between_runs(per_run, edges)

    thermal, grid, error = common.fit_thermal_energy(centers, density, mass)
    reference = 0.5 * mass * float((stationary ** 2).mean())
    initial = 0.5 * mass * static["v0"] ** 2
    # Rapidez media que predice Maxwell-Boltzmann en 2D con el kT ajustado:
    # <|v|> = sqrt(pi kT / 2m). Es una verificacion independiente del ajuste,
    # porque el ajuste usa la forma de f(v) y esto un solo momento.
    predicted_mean = float(np.sqrt(np.pi * thermal / (2.0 * mass)))

    # Rapidez media contra el tiempo: un escalar por cuadro (la media de la
    # bolsa de ese instante, con el desvio entre realizaciones como banda) que
    # dice CUANDO empieza el estacionario. Arranca EXACTAMENTE en v0 en t = 0
    # (todas las particulas nacen con |v| = v0) y baja mientras f(v) se
    # ensancha a energia constante (la media de |v| no es la raiz de la media
    # de v^2). El eje t es lineal y corto (--ventana): en escala logaritmica el
    # punto t = 0 no se puede dibujar y la curva parecia arrancar por debajo de
    # v0, cuando lo que pasa es que en el primer cuadro guardado (0,05 s) ya
    # hubo choques. Lo que queda fuera de la ventana es plano hasta t_max: lo
    # dice la salida por consola.
    per_frame = speeds.mean(axis=2)                       # (M, F)
    mean_speed = per_frame.mean(axis=0)
    spread_speed = per_frame.std(axis=0, ddof=1) if runs > 1 else np.zeros_like(mean_speed)
    figure, axes = plt.subplots()
    axes.plot(times, mean_speed, color=common.FRESH,
              label="$\\langle |\\vec{v}| \\rangle$ por instante")
    axes.fill_between(times, mean_speed - spread_speed, mean_speed + spread_speed,
                      color=common.FRESH, alpha=0.15, linewidth=0)
    axes.axhline(static["v0"], color="#555555", linestyle=":", linewidth=1.4,
                 label="$v_0$")
    # La formula sqrt(pi kT / 2m) va en la vineta; en la leyenda, el numero.
    axes.axhline(predicted_mean, color=common.USED, linestyle="--", linewidth=1.8,
                 label=f"Maxwell-Boltzmann: {common.decimal(predicted_mean, 3)} m/s")
    axes.set_xlim(0.0, arguments.ventana)
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_MEAN_SPEED)
    low = min(mean_speed.min(), predicted_mean)
    axes.set_ylim(low - 0.2 * (static["v0"] - low), static["v0"] + 0.18 * (static["v0"] - low))
    # La leyenda, en el hueco entre v0 y el estacionario, a la derecha del
    # transitorio: ahi no hay nada dibujado.
    axes.legend(loc="upper right", bbox_to_anchor=(0.99, 0.93))
    mean_figure = out_dir / f"v_medio_vs_t_N{count}_M{runs}.png"
    common.save(figure, mean_figure)
    plt.close(figure)

    # La barra es la simulacion y la curva el ajuste: en la leyenda va solo el
    # nombre de cada una. El valor de kT no, porque es EL resultado del item y
    # se dice en la diapositiva, no escondido en un rotulo de la figura.
    figure, axes = plt.subplots()
    axes.bar(centers, density, width=np.diff(edges), color=common.FRESH, alpha=0.45,
             edgecolor=common.FRESH, label="gran bolsa (simulación)")
    fine = np.linspace(edges[0], edges[-1], 400)
    axes.plot(fine, common.maxwell_boltzmann(fine, thermal, mass), color=common.USED,
              linewidth=2.4, label="Maxwell-Boltzmann")
    axes.set_xlabel(common.AXIS_SPEED)
    axes.set_ylabel(common.AXIS_PDF)
    axes.set_xlim(0.0, 2.8 * static["v0"])
    axes.set_ylim(0.0, 1.32 * density.max())
    axes.legend(loc="upper right")
    fit = out_dir / f"f_v_gran_bolsa_ajuste_N{count}_M{runs}.png"
    common.save(figure, fit)
    plt.close(figure)

    figure, axes = plt.subplots()
    axes.plot(1000 * grid, error, color=common.FRESH)
    axes.plot([1000 * thermal], [error.min()], marker="o", color=common.USED, markersize=9,
              linestyle="none",
              label=f"mínimo en $k_BT$ = {common.decimal(1000 * thermal, 2)} mJ")
    # Los ejes llevan el simbolo y la unidad, como el resto de las figuras:
    # "energia termica" y "error cuadratico medio" estan definidos en la
    # diapositiva, no hace falta repetirlos en el rotulo.
    axes.set_xlabel(common.AXIS_THERMAL)
    axes.set_ylabel(common.AXIS_FIT_ERROR)
    common.headroom(axes, 0.22)
    axes.legend(loc="upper center")
    error_figure = out_dir / f"E_vs_kT_N{count}_M{runs}.png"
    common.save(figure, error_figure)
    plt.close(figure)

    print(f"N = {count}, sin obstáculos, {runs} realizaciones, "
          f"{len(times)} cuadros hasta t = {times[-1]:.1f} s")
    print(f"bolsa de un instante: {runs} realizaciones x {count} partículas = "
          f"{per_instant} muestras")
    print(f"bolsa del estacionario (t ≥ {arguments.estacionario:g} s): {runs} x {frames} "
          f"cuadros x {count} partículas = {per_pool} muestras "
          f"({per_run.shape[1]} por realización)")
    print(f"desvío entre realizaciones (NO se dibuja; intervalos con f(v) > 10 % del "
          f"máximo): instante suelto {relative(instant_density, instant_spread):.1%}, "
          f"estacionaria {relative(density, spread):.1%}")
    doubling = grid[error <= 2.0 * error.min()]
    print(f"kT ajustado        = {thermal:.6f} J  (el error cuadrático medio del ajuste se "
          f"duplica en {1000 * doubling.min():.2f} y {1000 * doubling.max():.2f} mJ)")
    print(f"m <v^2> / 2        = {reference:.6f} J  (diferencia "
          f"{100 * (thermal - reference) / reference:+.1f} %)")
    print(f"m v0^2 / 2         = {initial:.6f} J  (diferencia "
          f"{100 * (thermal - initial) / initial:+.1f} %)")
    first_flat = times[np.argmax(np.abs(mean_speed - mean_speed[times >= arguments.estacionario].mean())
                                 <= spread_speed)]
    print(f"<|v|> estacionario = {float(mean_speed[times >= arguments.estacionario].mean()):.4f} m/s "
          f"(desvío entre realizaciones {float(spread_speed[times >= arguments.estacionario].mean()):.4f}); "
          f"Maxwell-Boltzmann con el kT ajustado predice sqrt(pi kT / 2m) = {predicted_mean:.4f} m/s; "
          f"entra en la banda del estacionario desde t = {first_flat:.2f} s")
    print(evolution)
    print(mean_figure)
    print(fit)
    print(error_figure)


if __name__ == "__main__":
    main()
