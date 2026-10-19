"""Animacion de una corrida y cuadros sueltos para la presentacion.

Cada particula es un disco azul (fresca) o rojo (usada); los dos obstaculos
fijos van en negro y la pared circular en gris. Un cuadro por estado guardado
en dynamic.txt, es decir cada dt2 = n dt: el tiempo entre cuadros es uniforme
y el instante se muestra en pantalla.

    python3 visualization/animate.py --run data/runs/xo0.0175
    python3 visualization/animate.py --run data/runs/xo0.0175 --snapshots 0,5,10,20
    python3 visualization/animate.py --run data/runs/xo0.0175 --cuadro 10 --estilo diapositiva --figures data/figuras_diapositivas

Con --cuadro se guarda un solo cuadro con el mismo lienzo, tipografia y
rotulo que el video: es el fotograma representativo que va en el PDF.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.collections import EllipseCollection
from matplotlib.patches import Circle

import common


def draw_domain(axes, static: dict) -> None:
    domain = static["R"]
    margin = 1.04 * domain
    axes.set_xlim(-margin, margin)
    axes.set_ylim(-margin, margin)
    axes.set_aspect("equal")
    axes.set_xlabel("posición $x$ (m)")
    axes.set_ylabel("posición $y$ (m)")
    axes.grid(False)
    axes.add_patch(Circle((0.0, 0.0), domain, facecolor="none", edgecolor=common.WALL,
                          linewidth=2.5, zorder=3))
    for xk, yk, rk in static["obstacles"]:
        axes.add_patch(Circle((xk, yk), rk, facecolor=common.OBSTACLE, edgecolor="none",
                              zorder=4))


def particle_collection(axes, state: np.ndarray, radius: float):
    colors = np.where(state[:, 4] > 0.5, common.USED, common.FRESH)
    collection = EllipseCollection(
        widths=2 * radius, heights=2 * radius, angles=0, units="xy",
        offsets=state[:, :2], transOffset=axes.transData, facecolors=colors,
        edgecolors="none", zorder=5)
    axes.add_collection(collection)
    return collection


def frame_index(times: np.ndarray, target: float) -> int:
    """Ultimo cuadro guardado cuyo instante no supera target."""
    return int(np.searchsorted(times, target, side="right") - 1)


def caption(static: dict, t: float, state: np.ndarray) -> str:
    used = int(state[:, 4].sum())
    return f"$t$ = {common.decimal(t, 2):>6} s    usadas: {used}/{static['N']}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--frames", type=int, default=0,
                        help="cuadros del video (0 = todos los guardados)")
    parser.add_argument("--fps", type=int, default=30,
                        help="cuadros por segundo; para que el video corra en tiempo "
                             "real tiene que ser 1/dt2 (con el dt2 = 0,04 s de las "
                             "animaciones del trabajo da 25, que es el que pasa el "
                             "Makefile en FPS)")
    parser.add_argument("--snapshots", type=str, default="",
                        help="instantes (s) de los cuadros sueltos, separados por coma")
    parser.add_argument("--cuadro", type=float, default=-1.0,
                        help="instante (s) de un cuadro unico con el lienzo del video")
    parser.add_argument("--name", type=str, default="")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    static, times, states = common.load_run(arguments.run)
    # Las corridas de un barrido viven en <caso>/s<semilla>: el nombre del
    # caso es el de la carpeta de arriba.
    case = (arguments.run.parent.name if re.fullmatch(r"s\d+", arguments.run.name)
            else arguments.run.name)
    out_dir = common.folder("anim", arguments.figures)

    if arguments.snapshots:
        targets = [float(v) for v in arguments.snapshots.split(",")]
        figure, panels = plt.subplots(1, len(targets), figsize=(3.6 * len(targets), 3.8),
                                      squeeze=False, layout="constrained")
        for position, (axes, target) in enumerate(zip(panels[0], targets)):
            index = frame_index(times, target)
            draw_domain(axes, static)
            particle_collection(axes, states[index], static["r"])
            axes.set_title(caption(static, times[index], states[index]), fontsize=10)
            if position > 0:
                axes.set_ylabel("")
                axes.set_yticklabels([])
        name = arguments.name or f"cuadros_{case}_t{'-'.join(f'{t:g}' for t in targets)}.png"
        common.save(figure, out_dir / name)
        print(out_dir / name)
        return

    if arguments.cuadro >= 0:
        index = frame_index(times, arguments.cuadro)
        figure, axes = plt.subplots(figsize=(5.6, 5.4))
        draw_domain(axes, static)
        particle_collection(axes, states[index], static["r"])
        axes.text(0.0, 1.02, caption(static, times[index], states[index]),
                  transform=axes.transAxes, fontsize=plt.rcParams["font.size"], va="bottom")
        name = arguments.name or f"cuadro_{case}_t{arguments.cuadro:g}.png"
        common.save(figure, out_dir / name)
        print(out_dir / name, f"(t = {times[index]:.3f} s)")
        return

    step = max(1, len(times) // arguments.frames) if arguments.frames else 1
    indices = np.arange(0, len(times), step)

    figure, axes = plt.subplots(figsize=(5.6, 5.4))
    draw_domain(axes, static)
    collection = particle_collection(axes, states[0], static["r"])
    text = axes.text(0.0, 1.02, caption(static, times[0], states[0]),
                     transform=axes.transAxes, fontsize=plt.rcParams["font.size"], va="bottom")

    def update(index):
        state = states[index]
        collection.set_offsets(state[:, :2])
        collection.set_facecolors(np.where(state[:, 4] > 0.5, common.USED, common.FRESH))
        text.set_text(caption(static, times[index], state))
        return collection, text

    common.comma_ticks(figure)
    animation = FuncAnimation(figure, update, frames=indices, interval=1000 / arguments.fps,
                              blit=False)
    name = arguments.name or f"{case}.mp4"
    animation.save(out_dir / name, writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(out_dir / name, f"({len(indices)} cuadros)")


if __name__ == "__main__":
    main()
