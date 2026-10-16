"""Una sola partícula: por qué sin choques casi nadie llega a los obstáculos.

Prueba de la explicación del ítem 2.4.a. La fuerza de la pared es puramente
radial (partícula imagen sobre la normal), así que una partícula que no choca
con otras conserva su momento angular respecto del centro, L = x v_y - y v_x,
y nunca se acerca al centro más que su radio cáustico b = |L| / |v|. Con los
obstáculos en contacto (xo = r) la zona de contacto llega hasta 3 r del
centro: la partícula se convierte si y sólo si b < 3 r.

Lee un barrido de `billar explore --ns 1` con un solo cuadro guardado (el de
t = 0, con --save-every mayor que el número de pasos), calcula b de la
condición inicial de cada realización y lo compara con si se convirtió.

    python3 visualization/single.py --una data/una_particula
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--una", type=Path, default=common.DATA / "una_particula")
    arguments = parser.parse_args()

    _, cases = common.read_explore(arguments.una)
    impact, converted, when = [], [], []
    for case in cases.values():
        for run in case["runs"]:
            static, _, states = common.load_run(run)
            if static["N"] != 1:
                raise SystemExit(f"{run}: este análisis es para N = 1")
            x, y, vx, vy = states[0, 0, :4]
            impact.append(abs(x * vy - y * vx) / np.hypot(vx, vy))
            events = common.read_conversions(run)
            converted.append(len(events) > 0)
            when.append(events[0] if len(events) else np.nan)
    radius, domain = static["r"], static["R"]
    impact, converted = np.array(impact), np.array(converted)
    predicted = impact < 3.0 * radius

    # Fracción esperada para posiciones uniformes en el disco de radio R - r y
    # direcciones isótropas, por Monte Carlo directo de la misma distribución.
    rng = np.random.default_rng(1)
    rho = (domain - radius) * np.sqrt(rng.random(10 ** 6))
    theta, phi = rng.random(10 ** 6) * 2 * np.pi, rng.random(10 ** 6) * 2 * np.pi
    sample = np.abs(rho * np.cos(theta) * np.sin(phi) - rho * np.sin(theta) * np.cos(phi))

    print(f"realizaciones con N = 1: {len(impact)}, tmax = {static['tmax']:g} s")
    print(f"se convierten: {converted.sum()} ({100 * converted.mean():.1f} %)")
    print(f"con b < 3r:    {predicted.sum()} ({100 * predicted.mean():.1f} %)")
    print(f"se convierten con b >= 3r: {(converted & ~predicted).sum()}; "
          f"con b < 3r y no se convierten: {(predicted & ~converted).sum()}")
    print(f"fracción esperada P(b < 3r): {(sample < 3.0 * radius).mean():.3f}")
    if converted.any():
        print(f"instante medio de conversión de las que llegan: {np.nanmean(when):.1f} s")


if __name__ == "__main__":
    main()
