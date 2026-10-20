"""Item 2.4.b (opcional): mapa de calor de ⟨t90⟩ en el plano (xo, N).

Lee data/mapa/ (un barrido de `billar explore` sobre el producto de --xos y
--ns) y dibuja, para cada punto (xo, N), el promedio del tiempo de conversion
sobre las realizaciones. Las celdas donde alguna realizacion no llega a la
fraccion pedida antes de tmax quedan en blanco y se informan por consola.

La figura tiene que contestar dos cosas: cual es el xo optimo y si ese optimo
se corre con la densidad. Por eso:

* El eje x es la posicion real de los obstaculos (no un eje categorico): las
  celdas tienen el ancho del intervalo que representan, asi que una fila se
  lee como la curva ⟨t90⟩(xo) que es, y dos filas se comparan mirando donde
  cae la banda baja de cada una.
* La escala de colores es logaritmica. ⟨t90⟩ crece mucho mas con N que con
  xo (de punta a punta del mapa es un factor 6, dentro de una fila hasta 2,7):
  en escala lineal el color lo gobierna la fila y adentro de cada fila queda
  todo del mismo tono. En logaritmica una fila se lleva casi un tercio de la
  barra de color y el minimo de cada densidad se ve.
* El optimo de cada densidad va DIBUJADO encima del mapa, como una linea
  negra con opacidad moderada que une un punto por fila: la CELDA MAS BAJA de
  esa fila (el argmin de ⟨t90⟩ sobre xo), o sea el cuadrado mas rojo. El color
  contesta "cuanto tarda" y la linea contesta "donde esta el minimo de esta
  fila"; que de N = 20 para arriba se quede entre 0,175 y 0,30 m contesta la
  segunda pregunta del item: el optimo no se corre con la densidad.

  La linea une celdas medidas y por eso zigzaguea: la curva ⟨t90⟩(xo) tiene un
  fondo ancho y plano, y cual de las celdas del fondo sale sorteada mas baja
  es en buena parte azar (a N = 50 cae en 0,175 m y a N = 150 en 0,275 m,
  cuando las dos filas son iguales dentro del desvio). El numero fino del
  optimo, con su error, sale del VERTICE DE LA PARABOLA ajustada a cada fila
  sobre el mismo tramo; se informa por consola y va en la vineta, no dibujado.

El barrido que escribe `make mapa` corta cada corrida apenas Fu llega a 0,9
(--until-fraction 0.9: esperar a que se conviertan todas cuesta el triple de
computo y el mapa no lo usa), asi que sobre esos datos --fraccion no puede
pasar de 0,9. Para el mapa de ⟨t100⟩ hay que correr el barrido sin ese corte.

    python3 visualization/heatmap.py
    python3 visualization/heatmap.py --estilo diapositiva --figures data/figuras_diapositivas
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.ticker import FuncFormatter

import common

# turbo dada vuelta y recortada. Dada vuelta porque lo que tiene que saltar a
# la vista es el OPTIMO, no el peor caso: con turbo tal cual, el color fuerte
# (rojo) se lo llevaban los bordes, que son justamente las posiciones que no
# interesan. Asi, el rojo es la conversion mas rapida y el azul la mas lenta.
# Recortada porque las dos puntas del mapa original son casi negras (violeta
# de un lado, bordo del otro) y entre dos oscuros no se distingue cual es
# cual de un vistazo.
COLORS = LinearSegmentedColormap.from_list(
    "turbo-invertida", plt.get_cmap("turbo")(np.linspace(0.90, 0.10, 256)))
# Hasta donde llega la escala de colores, en unidades del minimo mas alto de
# todas las filas. Las celdas mas lentas (los bordes de las densidades
# extremas) valen un factor 6 del minimo del mapa y se llevarian media escala
# de color ellas solas, dejando sin contraste justo la zona donde esta el
# optimo. Cortando en 1,3 veces el peor de los minimos, toda fila conserva su
# gradiente alrededor del propio minimo y lo que satura son los bordes, que
# es lo que no hace falta distinguir. La barra de color lo dice con la
# flecha.
CLIP = 1.3

# Tramo de xo (en metros) sobre el que se ajusta la parabola del minimo. Es
# el MISMO para todas las filas a proposito: si la ventana se eligiera fila
# por fila (las vecinas de la celda mas baja, por ejemplo), el corrimiento
# entre filas mezclaria el del optimo con el de la ventana, que es justo lo
# que se quiere medir. Deja afuera las dos puntas, donde la curva se dispara
# y no es parabolica, y adentro quedan 12 de las 16 posiciones.
FIT_RANGE = (0.10, 0.40)
# Celdas minimas para ajustar la parabola (tres parametros + una de sobra).
MINIMUM_CELLS = 4
# Realizaciones del remuestreo con el que se le pone error al vertice.
RESAMPLES = 2000


def summarize(root: Path, fraction: float):
    _, cases = common.read_explore(root)
    counts = sorted({case["N"] for case in cases.values()})
    offsets = sorted({case["xo"] for case in cases.values()})
    grid = np.full((len(counts), len(offsets)), np.nan)
    spread = np.full_like(grid, np.nan)
    reached = np.zeros_like(grid)
    for case in cases.values():
        times = [common.conversion_time(run, fraction) for run in case["runs"]]
        valid = [t for t in times if t is not None]
        row, column = counts.index(case["N"]), offsets.index(case["xo"])
        reached[row, column] = len(valid)
        if len(valid) == len(times):
            grid[row, column], spread[row, column] = common.mean_std(valid)
    return np.array(counts), np.array(offsets), grid, spread, reached


def cell_edges(values: np.ndarray) -> np.ndarray:
    """Bordes de las celdas de un eje de valores no equiespaciados: cada celda
    llega hasta la mitad del camino a su vecina, y las dos de las puntas se
    cierran con la mitad de su unico intervalo."""
    middle = 0.5 * (values[1:] + values[:-1])
    first = values[0] - (middle[0] - values[0])
    last = values[-1] + (values[-1] - middle[-1])
    return np.concatenate(([first], middle, [last]))


def vertex(offsets: np.ndarray, values: np.ndarray, errors: np.ndarray):
    """(xo del minimo, error) ajustando una parabola a la fila, pesada por el
    error de cada celda, sobre el tramo FIT_RANGE.

    La celda mas baja sola no sirve como respuesta: la curva ⟨t90⟩(xo) tiene
    un fondo ancho y plano, y con el error de la media que tienen estas
    mediciones cual de las celdas del fondo sale sorteada mas baja es en buena
    parte azar (por eso el minimo parece saltar entre columnas al cambiar N:
    a N = 50 cae en 0,175 m y a N = 150 en 0,275 m, y las dos filas tienen el
    mismo vertice dentro del error). La parabola usa las 12 posiciones del
    tramo y el vertice sale mucho mas estable que el argmin. El error es el
    desvio del vertice sobre RESAMPLES remuestreos en los que cada celda se
    sortea de una normal con su media y su error de la media."""
    if np.isnan(values).any():
        return None, None
    window = (offsets >= FIT_RANGE[0] - 1e-9) & (offsets <= FIT_RANGE[1] + 1e-9)
    x, y, e = offsets[window], values[window], errors[window]
    if len(x) < MINIMUM_CELLS:
        return None, None

    def fit(sample):
        a, b, _ = np.polyfit(x, sample, 2, w=1.0 / e)
        return -0.5 * b / a if a > 0 else np.nan

    centre = fit(y)
    if not np.isfinite(centre):
        return None, None
    draws = np.array([fit(y + e * np.random.standard_normal(len(y)))
                      for _ in range(RESAMPLES)])
    draws = draws[np.isfinite(draws)]
    # El remuestreo puede dar vertices fuera del tramo ajustado cuando la fila
    # es muy plana: se recortan, para que el desvio no lo fije un ajuste
    # degenerado.
    draws = np.clip(draws, *FIT_RANGE)
    return float(centre), float(np.std(draws)) if len(draws) else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mapa", type=Path, default=common.MAP)
    parser.add_argument("--fraccion", type=float, default=0.9)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)
    np.random.seed(0)

    counts, offsets, grid, spread, reached = summarize(arguments.mapa, arguments.fraccion)
    if np.all(np.isnan(grid)):
        raise SystemExit(f"ninguna celda de {arguments.mapa} llega a Fu = "
                         f"{arguments.fraccion:g}: el barrido se cortó antes (ver el campo "
                         "'corte' del index.txt). Para pedir una fracción mayor hay que "
                         "correrlo de nuevo sin --until-fraction.")
    out_dir = common.folder("2.4", arguments.figures)
    percent = int(round(100 * arguments.fraccion))
    error = spread / np.sqrt(np.maximum(reached, 1.0))

    with open(arguments.mapa / f"mapa_{percent}.csv", "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["N", "xo", f"t{percent}_medio", f"t{percent}_error", "alcanzan"])
        for row, count in enumerate(counts):
            for column, offset in enumerate(offsets):
                writer.writerow([count, offset, grid[row, column], error[row, column],
                                 int(reached[row, column])])

    # Lo que va dibujado encima del mapa es la celda mas baja de cada fila (el
    # cuadrado mas rojo); el vertice de la parabola es el numero fino con error
    # y se informa por consola.
    rows_with_vertex = []
    lowest_cells = []
    for row in range(len(counts)):
        if np.all(np.isnan(grid[row])):
            continue
        lowest_cells.append((row, float(offsets[int(np.nanargmin(grid[row]))])))
        centre, uncertainty = vertex(offsets, grid[row], error[row])
        if centre is not None:
            rows_with_vertex.append((row, int(counts[row]), centre, uncertainty))

    # Eje x: la posicion real de los obstaculos, con las celdas del ancho del
    # intervalo que representan (el barrido es mas fino donde esta el minimo).
    # Eje y: una fila por N, todas del mismo alto, porque los N del barrido
    # van de 10 a 300 y con eje lineal las filas de N chico se aplastan.
    figure, axes = plt.subplots()
    axes.grid(False)
    ceiling = CLIP * float(np.nanmax(np.nanmin(grid, axis=1)))
    mesh = axes.pcolormesh(cell_edges(offsets), np.arange(len(counts) + 1) - 0.5, grid,
                           cmap=COLORS, norm=LogNorm(vmin=np.nanmin(grid), vmax=ceiling),
                           shading="flat")
    bar = figure.colorbar(mesh, ax=axes, extend="max")
    bar.set_label(f"$\\langle t_{{{percent}}} \\rangle$ (s)")
    # Con escala logaritmica matplotlib rotula 10^1 y nada mas: el mapa abarca
    # una sola decada larga y los valores se quieren leer en segundos.
    ticks = [t for t in (10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 150)
             if np.nanmin(grid) <= t <= ceiling]
    bar.set_ticks(ticks)
    bar.ax.yaxis.set_minor_formatter(FuncFormatter(lambda value, _: ""))
    bar.ax.set_yticklabels([common.decimal(t) for t in ticks])

    # La celda mas baja de cada densidad, encima del mapa: negro con opacidad
    # moderada, que se lee sobre cualquier color de la escala sin tapar las
    # celdas por las que pasa. El punto cae en el centro de la celda (xo real,
    # fila entera). Sin entrada de leyenda: el mapa esta cubierto de datos y
    # una caja encima tapa celdas; que es la linea lo dice la vineta.
    if len(lowest_cells) > 1:
        axes.plot([offset for _, offset in lowest_cells],
                  [row for row, _ in lowest_cells],
                  color="#111111", alpha=0.6, linewidth=2.0, marker="o", markersize=5,
                  markerfacecolor="#111111", zorder=3)

    axes.set_yticks(np.arange(len(counts)))
    axes.set_yticklabels([str(int(n)) for n in counts])
    axes.set_xlabel(common.AXIS_OFFSET)
    axes.set_ylabel(common.AXIS_COUNT)
    out = out_dir / f"mapa_t{percent}_xo_N.png"
    common.save(figure, out)
    plt.close(figure)

    # La lectura fina, por consola: la celda mas baja de cada fila (la que une
    # la linea de la figura), el vertice de la parabola con su error, que
    # celdas son compatibles con el minimo y cuanto castiga la peor posicion.
    vertices = {row: (centre, uncertainty)
                for row, _, centre, uncertainty in rows_with_vertex}
    best_offsets = []
    for row, count in enumerate(counts):
        if np.all(np.isnan(grid[row])):
            continue
        best = int(np.nanargmin(grid[row]))
        compatible = [offsets[column] for column in range(len(offsets))
                      if not np.isnan(grid[row, column])
                      and grid[row, column] - error[row, column]
                      <= grid[row, best] + error[row, best]]
        centre, uncertainty = vertices.get(row, (None, None))
        worst = int(np.nanargmax(grid[row]))
        fitted = ("sin ajuste" if centre is None else
                  f"ajuste parabólico xo = {centre:.3f}"
                  + (f" ± {uncertainty:.3f} m" if uncertainty is not None else " m"))
        if centre is not None:
            best_offsets.append((count, centre, uncertainty))
        print(f"N = {count:3d}: celda más baja en xo = {offsets[best]:.4f} m, "
              f"<t{percent}> = {grid[row, best]:.1f} ± {error[row, best]:.1f} s; "
              f"{fitted}; peor xo = {offsets[worst]:.4f} m "
              f"({grid[row, worst] / grid[row, best]:.1f} veces el mínimo); "
              f"compatibles con el mínimo: {len(compatible)} celdas "
              f"({min(compatible):g}–{max(compatible):g} m)")

    if len(best_offsets) > 2:
        # Hay o no hay corrimiento del optimo con la densidad: se contesta con
        # una recta xo(log N) pesada por el error de cada vertice. Si la
        # pendiente es compatible con cero, el optimo no se corre dentro de lo
        # que mide este barrido, y el promedio pesado es el unico numero que
        # hace falta.
        ns = np.array([n for n, *_ in best_offsets], dtype=float)
        centres = np.array([c for _, c, _ in best_offsets])
        errors_of = np.array([u for *_, u in best_offsets])
        weights = 1.0 / errors_of ** 2
        average = float(np.average(centres, weights=weights))
        deviation = float(np.sqrt(1.0 / weights.sum()))
        (slope, _), covariance = np.polyfit(np.log10(ns), centres, 1, w=1.0 / errors_of,
                                            cov="unscaled")
        print(f"óptimo promedio sobre las {len(best_offsets)} densidades: "
              f"xo = {average:.3f} ± {deviation:.3f} m (dispersión de los vértices "
              f"{centres.std(ddof=1):.3f} m); corrimiento con la densidad: "
              f"{slope:+.3f} ± {np.sqrt(covariance[0, 0]):.3f} m por década de N")
        # El corrimiento, si lo hay, esta en las densidades mas bajas: de N = 20
        # para arriba los vertices caen todos en el mismo lugar. Se informan
        # los dos grupos por separado, que es como se lee el mapa.
        high = [(n, c) for n, c, _ in best_offsets if n >= 20]
        if len(high) > 1 and len(high) < len(best_offsets):
            values = np.array([c for _, c in high])
            print(f"  de N = {high[0][0]} en adelante ({len(high)} densidades): "
                  f"xo = {values.mean():.3f} ± {values.std(ddof=1):.3f} m; "
                  "por debajo: "
                  + ", ".join(f"N = {n}: {c:.3f} m"
                              for n, c, _ in best_offsets if n < 20))
        # Que fila se aparta del promedio mas de lo que admite su error: es la
        # forma directa de contestar si el optimo depende de la densidad sin
        # que la respuesta dependa de haber ajustado una recta.
        distance = np.abs(centres - average) / np.sqrt(errors_of ** 2 + deviation ** 2)
        odd = [(n, c, d) for (n, c, _), d in zip(best_offsets, distance) if d > 2.0]
        if odd:
            print("  vértices que NO son compatibles con ese promedio: "
                  + ", ".join(f"N = {n} (xo = {c:.3f} m, {d:.1f} σ)" for n, c, d in odd))
        else:
            print("  todas las densidades son compatibles con ese promedio "
                  "(ninguna se aparta más de 2 σ): el óptimo no se corre con N")

    missing = [(counts[r], offsets[c]) for r in range(len(counts)) for c in range(len(offsets))
               if np.isnan(grid[r, c])]
    if missing:
        print(f"celdas sin valor (alguna realización no llega a {percent} %): " +
              ", ".join(f"N = {n}, xo = {x:.4f}" for n, x in missing))
    saturated = int(np.sum(grid > ceiling))
    print(f"escala de colores hasta {ceiling:.1f} s ({common.decimal(CLIP)} veces el más "
          f"alto de los mínimos de cada fila): saturan {saturated} de "
          f"{int(np.sum(~np.isnan(grid)))} celdas, el máximo del mapa es "
          f"{np.nanmax(grid):.1f} s")
    print(f"{len(counts)} densidades x {len(offsets)} posiciones x "
          f"{int(reached.max())} realizaciones = {int(reached.sum())} corridas")
    print(out)
    print(arguments.mapa / f"mapa_{percent}.csv")


if __name__ == "__main__":
    main()
