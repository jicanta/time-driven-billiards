"""Item 2.1.b: tiempo de ejecucion contra N, y comparacion con el TP3.

Lee la salida de `billar bench` (dinamica molecular regida por el paso
temporal, con los obstaculos en contacto y tf fijo) y la de `metegol bench`
del TP3 (dinamica molecular regida por eventos), que tienen el mismo formato
de columnas y se corren en la misma computadora. Grafica el tiempo total
(generacion de la condicion inicial + bucle de integracion o de eventos)
contra N, con el desvio estandar entre las M realizaciones como barra de
error, y le ajusta a cada serie una ley de potencia t = c N^a por cuadrados
minimos en log-log. Por acuerdo con la catedra no se cuenta la escritura de
archivos. La primera medicion de cada N (marcada como descartada por el motor)
no entra en el promedio ni en el desvio: paga el arranque en frio del proceso.

La leyenda nombra solo las dos series medidas: las rectas punteadas son el
ajuste de cada una y no necesitan entrada propia (se ve de que serie es cada
una por el color). El exponente se dice en la charla y esta en esta salida.

El desvio estandar se dibuja igual, pero en una figura que abarca cuatro
decadas una barra del 4 % mide un pixel: el rotulo informa el desvio relativo
maximo, que es la unica forma de que se lea. Dice sigma/<t> y no "del valor"
a proposito: sigma es el desvio entre realizaciones, no una cota de cuanto se
aparta la peor. El rango completo (max - min) llega al 12 % en el barrido del
TP3; este script lo imprime por si lo preguntan.

    python3 visualization/bench.py --bench data/bench/hexagonal/tiempos.txt,data/bench/tp3_hexagonal.txt \\
        --labels "paso temporal (TP4),eventos (TP3)"
    python3 visualization/bench.py --bench data/bench/hexagonal/tiempos.txt --labels "paso temporal (TP4)"

Los ejes van en doble logaritmica: los tiempos de los dos paradigmas abarcan
varios ordenes de magnitud.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogFormatterSciNotation, NullFormatter

import common

STYLES = [(common.FRESH, "o"), (common.USED, "s"), ("#2ca02c", "^"), ("#ff7f0e", "v")]
FIGURES = {
    "total": {"name": "tiempo_total_vs_N", "ylabel": common.AXIS_WALL},
    "generation": {"name": "tiempo_generacion_vs_N",
                   "ylabel": "tiempo de generación inicial (s)"},
}


def summarize(path: Path, smallest: int = 0):
    """Tiempos medios por N, desde N = `smallest`.

    Por debajo de N ~ 50 el costo de un paso lo domina el barrido de las
    29 x 29 celdas de la grilla, que no depende de N, y la curva se aplana:
    ahi la ley de potencia mide el piso de la implementacion y no como escala
    el paradigma. Esas corridas se hacen igual porque el item 2.4.a usa las
    mismas, pero quedan fuera de esta figura."""
    rows = {n: row for n, row in common.read_bench(path).items() if n >= smallest}
    if not rows:
        raise SystemExit(f"{path}: no hay mediciones con N >= {smallest}")
    counts = np.array(list(rows))
    repeats = min(len(row["loop"]) for row in rows.values())
    series = {"total": [], "generation": []}
    for row in rows.values():
        loop = np.array(row["loop"]) / 1000.0
        generation = np.array(row["generation"]) / 1000.0
        series["total"].append(common.mean_std(loop + generation))
        series["generation"].append(common.mean_std(generation))
    return counts, series, repeats


def log_axes(axes, counts) -> None:
    """Doble logaritmica con las marcas del eje x en los N medidos: con las
    marcas automaticas solo se ve 10^2 y no se leen los valores del barrido."""
    axes.set_xscale("log")
    axes.set_yscale("log")
    # Con las marcas automaticas del eje logaritmico solo se ve 10^2 y no se
    # leen los N del barrido: se rotulan los N medidos, salteando los que
    # quedarian pegados al anterior (menos de un 30 % de separacion).
    labelled: list = []
    for n in counts:
        if not labelled or n / labelled[-1] >= 1.45:
            labelled.append(n)
    top = max(counts)
    if top not in labelled:
        labelled[-1] = top
    axes.set_xticks(labelled)
    axes.set_xticklabels([str(int(n)) for n in labelled])
    axes.set_xticks([n for n in counts if n not in labelled], minor=True)
    axes.xaxis.set_minor_formatter(NullFormatter())
    axes.yaxis.set_minor_formatter(LogFormatterSciNotation(labelOnlyBase=False,
                                                           minor_thresholds=(2.0, 0.5)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bench", type=str,
                        default=str(common.BENCH / "hexagonal" / "tiempos.txt"),
                        help="archivos de tiempos separados por coma, uno por serie")
    parser.add_argument("--labels", type=str, default="",
                        help="etiquetas de las series, separadas por coma")
    parser.add_argument("--name", type=str, default="",
                        help="sufijo del nombre de las figuras")
    parser.add_argument("--desde", type=int, default=0,
                        help="N mínimo que entra en la figura y en el ajuste")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    paths = [Path(p) for p in arguments.bench.split(",") if p]
    labels = arguments.labels.split(",") if arguments.labels else [p.parent.name for p in paths]
    benches = [(label, *summarize(path, arguments.desde)) for label, path in zip(labels, paths)]
    every = sorted({int(n) for _, counts, _, _ in benches for n in counts})
    repeats = min(repeats for *_, repeats in benches)
    suffix = arguments.name or "-".join(label.split()[0] for label in labels)
    out_dir = common.folder("2.1", arguments.figures)

    for key, style in FIGURES.items():
        figure, axes = plt.subplots()
        handles = []
        spread = 0.0
        for (label, counts, series, _), (color, marker) in zip(benches, STYLES):
            means = np.array([m for m, _ in series[key]])
            stds = np.array([s for _, s in series[key]])
            spread = max(spread, float((stds / means).max()))
            handles.append(axes.errorbar(counts, means, yerr=stds, color=color, marker=marker,
                                         linestyle="none", label=label))
            exponent, intercept = np.polyfit(np.log(counts), np.log(means), 1)
            line = np.linspace(counts.min(), counts.max(), 200)
            # La recta punteada es el ajuste de la serie de su mismo color: no
            # lleva entrada en la leyenda (el exponente se dice en la charla).
            axes.plot(line, np.exp(intercept) * line ** exponent, color=color,
                      linestyle="--", linewidth=1.6, label="_nolegend_")
            print(f"{style['name']} [{label}]: t = c N^a, a = {exponent:.2f}, "
                  f"c = {np.exp(intercept):.3g} s")
        axes.set_xlabel(common.AXIS_COUNT)
        axes.set_ylabel(style["ylabel"])
        log_axes(axes, np.array(every))
        axes.legend(handles=handles, loc="lower right")
        # Las barras de desvio estan dibujadas, pero en cuatro decadas de eje
        # no se ven: cuanto valen va escrito, que es lo que pide el enunciado
        # ("incluyendo su desvío estándar").
        axes.text(0.02, 0.97, f"barras: desvío estándar de {repeats} realizaciones\n"
                              f"($\\sigma/\\langle t \\rangle \\leq$ {100 * spread:.0f} %, "
                              "menor que el símbolo)",
                  transform=axes.transAxes, ha="left", va="top", color="#555555",
                  fontsize=plt.rcParams["legend.fontsize"])
        out = out_dir / f"{style['name']}_{suffix}_M{repeats}_log.png"
        common.save(figure, out)
        plt.close(figure)
        print(out)

    print(f"M = {repeats} realizaciones por N, más la primera medición, descartada del "
          "promedio (arranque en frío)")
    # sigma no es una cota de cuanto se aparta la peor realizacion: el rango
    # completo es bastante mayor y conviene tenerlo a mano por si lo preguntan.
    for path, (label, *_) in zip(paths, benches):
        rows = {n: row for n, row in common.read_bench(path).items() if n >= arguments.desde}
        worst = max((((np.array(row["loop"]) + np.array(row["generation"])).max() -
                      (np.array(row["loop"]) + np.array(row["generation"])).min()) /
                     (np.array(row["loop"]) + np.array(row["generation"])).mean(), n)
                    for n, row in rows.items())
        print(f"  [{label}] rango completo máximo (máx − mín)/⟨t⟩ = "
              f"{worst[0]:.1%} (en N = {worst[1]}); σ es bastante menor")
    header = f"{'N':>5}" + "".join(f"{label:>26}" for label, *_ in benches)
    print(header)
    for n in every:
        row = f"{n:5d}"
        for _, counts, series, _ in benches:
            index = list(counts).index(n) if n in counts else None
            if index is None:
                row += f"{'':>26}"
            else:
                mean, std = series["total"][index]
                row += f"{mean:16.4f} ± {std:7.4f}"
        print(row)


if __name__ == "__main__":
    main()
