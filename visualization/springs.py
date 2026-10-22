"""Sistema 1: los cuatro resortes oscilando a la vez, uno por esquema.

Es la version animada de la figura de r(t): en vez de cuatro curvas sobre el
tiempo, cuatro masas colgadas del mismo resorte que se mueven al mismo tiempo,
cada una integrada con su esquema y todas con el mismo paso. Las cuatro
arrancan juntas en r = A y van perdiendo amplitud porque el sistema esta
amortiguado; lo que se ve es que Beeman, Verlet original y Velocity Verlet se
mueven como una sola (con dt = 5e-3 s se apartan 1, 1 y 6 mm sobre A = 1 m) y
que Euler predictor-corrector se queda corto en cada extremo, que es el mismo
resultado de la figura de posicion contra el tiempo pero mirando la masa.

La analitica no se dibuja: el GIF es para la charla, se proyecta al lado de la
figura de r(t) (que si la lleva) y una quinta masa gris encima de las otras
tres no agrega nada.

Cada carril es un esquema, con su nombre y su color a la izquierda; el eje de
abajo es la misma r de la figura, asi que la posicion de cada masa se lee en
metros. La masa va al ritmo real: se dibuja un cuadro cada 1/fps segundos de
simulacion, tomando un paso de cada n de la trayectoria que escribio
`billar oscillator`.

    python3 visualization/springs.py
    python3 visualization/springs.py --paso 1e-3 --tmax 3 --estilo diapositiva
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation

import common

# Geometria del dibujo, en las mismas unidades que r: la pared esta a WALL_X
# de la posicion de equilibrio (r = 0) y el resorte va de la pared a la masa.
WALL_X = -1.65
COILS = 9
COIL_HEIGHT = 0.16
LEAD = 0.10


def spring(start: float, end: float, lane: float, points: int = 241):
    """Zigzag de la pared (`start`) a la masa (`end`) en el carril `lane`.

    Los dos extremos son rectos (`LEAD`) y el medio es una onda triangular de
    `COILS` vueltas, estirada o comprimida con la distancia: el resorte se ve
    mas abierto cuanto mas lejos esta la masa, que es lo que pasa de verdad."""
    body = np.linspace(0.0, 1.0, points)
    inner = (start + LEAD) + body * (end - LEAD - (start + LEAD))
    wave = lane + COIL_HEIGHT * (2.0 / np.pi) * np.arcsin(np.sin(2.0 * np.pi * COILS * body))
    x = np.concatenate([[start], inner, [end]])
    y = np.concatenate([[lane], wave, [lane]])
    return x, y


def read_schemes(root: Path, step: float, tmax: float) -> tuple[np.ndarray, dict]:
    """(t, {esquema: r(t)}) con el paso `step`, hasta `tmax`."""
    times = None
    tracks = {}
    for name in common.SCHEMES:
        path = root / name / f"dt{step:.1e}.txt"
        if not path.exists():
            continue
        t, x, _ = common.read_trajectory(path)
        shown = t <= tmax
        times = t[shown]
        tracks[name] = x[shown]
    if times is None:
        raise SystemExit(f"no hay trayectorias con dt = {step:g} s en {root}")
    return times, tracks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--oscilador", type=Path, default=common.OSCILLATOR)
    parser.add_argument("--paso", type=float, default=5e-3,
                        help="dt de las trayectorias que se animan (el mismo de la "
                             "figura de posicion: es donde Euler p-c se despega a ojo)")
    parser.add_argument("--tmax", type=float, default=5.0,
                        help="hasta que instante (s) corre la animacion")
    parser.add_argument("--fps", type=int, default=25,
                        help="cuadros por segundo; el video corre en tiempo real")
    parser.add_argument("--name", type=str, default="oscilador_esquemas.mp4")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    times, tracks = read_schemes(arguments.oscilador, arguments.paso, arguments.tmax)
    # Un cuadro cada 1/fps segundos de simulacion: la masa se mueve en tiempo
    # real, como en las animaciones del sistema 2.
    every = max(1, int(round(1.0 / (arguments.fps * arguments.paso))))
    indices = np.arange(0, len(times), every)
    lanes = {name: len(tracks) - 1 - position for position, name in enumerate(tracks)}

    figure, axes = plt.subplots(figsize=(6.6, 4.2))
    # Margenes a mano: el video no pasa por common.save (no hay recorte
    # ajustado cuadro a cuadro), asi que el nombre del eje y el instante de
    # arriba tienen que entrar en el lienzo tal como se fija aca.
    figure.subplots_adjust(left=0.035, right=0.985, bottom=0.17, top=0.88)
    axes.set_xlim(WALL_X - 0.05, 1.3)
    axes.set_ylim(-0.6, len(tracks) - 0.3)
    axes.set_xlabel(common.AXIS_POSITION)
    axes.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    axes.set_yticks([])
    axes.grid(False)
    # El nombre del esquema va DENTRO de su carril, en su color y arriba del
    # resorte: de rotulo del eje y las cuatro frases ("Euler predictor-
    # corrector" es la mas larga) se comen un tercio del ancho del dibujo.
    for name, lane in lanes.items():
        axes.text(WALL_X + 0.06, lane + 0.30, common.SCHEME_LABEL[name],
                  color=common.SCHEME_STYLE[name][0], va="bottom",
                  fontsize=0.78 * plt.rcParams["font.size"])
    # La pared de la que cuelgan los cuatro resortes y la vertical del
    # equilibrio (r = 0), que es contra la que se lee el apartamiento.
    axes.axvline(WALL_X, color=common.WALL, linewidth=3.0)
    axes.axvline(0.0, color="#999999", linewidth=1.0, linestyle=":")

    coils = {}
    masses = {}
    for name, lane in lanes.items():
        color, _ = common.SCHEME_STYLE[name]
        coils[name], = axes.plot([], [], color=color, linewidth=1.6, alpha=0.9)
        masses[name], = axes.plot([], [], color=color, marker="o", markersize=16,
                                  linestyle="none")
    # Arriba va solo el instante: el paso es el mismo con el que esta hecha la
    # figura de r(t) que se proyecta al lado, asi que se escribe una sola vez
    # en la diapositiva y vale para las dos.
    text = axes.text(0.0, 1.02, "", transform=axes.transAxes,
                     fontsize=plt.rcParams["font.size"], va="bottom")

    def update(index):
        for name, lane in lanes.items():
            position = tracks[name][index]
            coils[name].set_data(*spring(WALL_X, position, lane))
            masses[name].set_data([position], [lane])
        text.set_text(f"$t$ = {common.decimal(times[index], 2):>5} s")
        return tuple(coils.values()) + tuple(masses.values()) + (text,)

    common.comma_ticks(figure)
    out_dir = common.folder("anim", arguments.figures)
    animation = FuncAnimation(figure, update, frames=indices,
                              interval=1000 / arguments.fps, blit=False)
    animation.save(out_dir / arguments.name,
                   writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(out_dir / arguments.name, f"({len(indices)} cuadros, {len(tracks)} esquemas)")


if __name__ == "__main__":
    main()
