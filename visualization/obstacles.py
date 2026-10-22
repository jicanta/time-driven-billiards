"""Item 2.2: los dos obstaculos recorriendo todo el rango de x_o.

El parametro del item es la posicion de los obstaculos, con centros en
(-x_o, 0) y (+x_o, 0). Los extremos del rango son geometricos: x_o = r es el
minimo (los dos obstaculos se tocan y forman un solo blanco en el centro) y
x_o = R - r el maximo (tocan la pared). Las tres animaciones del sistema 2
muestran tres valores sueltos de ese rango; esta recorre el rango entero y
solo mueve los obstaculos, para que se vea de que se habla cuando se barre
x_o. No hay particulas: no es una simulacion, es la geometria del barrido.

Los tres x_o de las animaciones quedan marcados sobre la linea de recorrido,
asi que al pasar por cada uno se reconoce la configuracion que se vio
animada con las particulas.

    python3 visualization/obstacles.py
    python3 visualization/obstacles.py --cuadros 120 --estilo diapositiva
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle

import common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--R", type=float, default=0.51, help="radio del dominio (m)")
    parser.add_argument("--r", type=float, default=0.0175,
                        help="radio de los obstaculos, el mismo de las particulas (m)")
    parser.add_argument("--marcas", type=str, default="0.0175,0.20,0.4925",
                        help="los x_o (m) que llevan marca sobre el recorrido: los de "
                             "las tres animaciones del sistema 2")
    parser.add_argument("--cuadros", type=int, default=75,
                        help="cuadros de la ida; la vuelta son los mismos al reves, "
                             "asi el GIF cierra donde empezo")
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--name", type=str, default="obstaculos_xo.mp4")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    domain, radius = arguments.R, arguments.r
    # De los obstaculos tocandose en el centro a los obstaculos tocando la
    # pared, y de vuelta: el GIF se repite sin saltos.
    forward = np.linspace(radius, domain - radius, arguments.cuadros)
    offsets = np.concatenate([forward, forward[-2:0:-1]])

    figure, axes = plt.subplots(figsize=(5.6, 5.4))
    # Mismos margenes a mano que el resto de las animaciones: los cuadros se
    # guardan sin el recorte ajustado de common.save.
    figure.subplots_adjust(left=0.17, right=0.97, bottom=0.13, top=0.90)
    margin = 1.04 * domain
    axes.set_xlim(-margin, margin)
    axes.set_ylim(-margin, margin)
    axes.set_aspect("equal")
    axes.set_xlabel("posición $x$ (m)")
    axes.set_ylabel("posición $y$ (m)")
    axes.grid(False)
    axes.add_patch(Circle((0.0, 0.0), domain, facecolor="none", edgecolor=common.WALL,
                          linewidth=2.5, zorder=3))
    # El recorrido: el segmento que barren los centros, de r a R - r de cada
    # lado, con una marca en cada x_o animado.
    for sign in (-1.0, 1.0):
        axes.plot([sign * radius, sign * (domain - radius)], [0.0, 0.0],
                  color="#999999", linewidth=1.0, linestyle=":", zorder=2)
    for mark in (float(v) for v in arguments.marcas.split(",")):
        for sign in (-1.0, 1.0):
            axes.plot([sign * mark], [0.0], color="#999999", marker="|", markersize=10,
                      zorder=2)

    obstacles = [axes.add_patch(Circle((0.0, 0.0), radius, facecolor=common.OBSTACLE,
                                       edgecolor="none", zorder=4)) for _ in range(2)]
    # La cota de x_o, del centro al obstaculo de la derecha: es el parametro
    # que se barre y el numero que acompana a cada animacion.
    arrow = axes.annotate("", xy=(0.0, 0.0), xytext=(0.0, 0.0),
                          arrowprops={"arrowstyle": "<->", "color": "#1f5fbf", "lw": 1.6})
    label = axes.text(0.0, 0.05 * domain, "", color="#1f5fbf", ha="center", va="bottom",
                      fontsize=0.85 * plt.rcParams["font.size"])
    text = axes.text(0.0, 1.02, "", transform=axes.transAxes,
                     fontsize=plt.rcParams["font.size"], va="bottom")
    # Los dos extremos del recorrido, escritos debajo de la linea: es todo lo
    # que hay que saber para leer el barrido (arriba va solo el valor que se
    # mueve, y el dominio no deja esquina libre para una leyenda).
    for position, name, align in ((radius, "$r$", "center"),
                                  (domain - radius, "$R - r$", "right")):
        axes.text(position, -0.055 * domain, name, color="#777777",
                  ha=align, va="top", fontsize=0.8 * plt.rcParams["font.size"])

    def update(index):
        offset = offsets[index]
        obstacles[0].center = (-offset, 0.0)
        obstacles[1].center = (offset, 0.0)
        arrow.set_position((0.0, 0.0))
        arrow.xy = (offset, 0.0)
        label.set_position((0.5 * offset, 0.05 * domain))
        label.set_text("$x_o$")
        text.set_text(f"$x_o$ = {common.decimal(offset, 4)} m    "
                      f"(de $r$ a $R - r$)")
        return (*obstacles, arrow, label, text)

    common.comma_ticks(figure)
    out_dir = common.folder("anim", arguments.figures)
    animation = FuncAnimation(figure, update, frames=np.arange(len(offsets)),
                              interval=1000 / arguments.fps, blit=False)
    animation.save(out_dir / arguments.name,
                   writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(out_dir / arguments.name,
          f"({len(offsets)} cuadros, x_o de {radius:g} a {domain - radius:g} m)")


if __name__ == "__main__":
    main()
