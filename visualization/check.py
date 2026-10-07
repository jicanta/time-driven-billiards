"""Validacion del motor a partir de los estados guardados.

Mide, sobre los cuadros de dynamic.txt:

* la **deriva de la energia total** respecto del cuadro inicial, en valor
  absoluto y relativo. El sistema es conservativo, asi que es el error del
  esquema de integracion y es lo que decide el paso temporal (item 2.1.a);
* el **solapamiento maximo** entre particulas, con los obstaculos y con la
  pared. A diferencia del TP3, aca el solapamiento no es un error: es lo que
  activa el resorte de contacto. Lo que se verifica es que se mantenga chico
  frente al radio (si se acerca a r el modelo de contacto deja de tener
  sentido y el paso es demasiado largo);
* que ninguna particula se haya **escapado del dominio** (|r| > R).

El motor no calcula nada de esto: solo escribe estados.

    python3 visualization/check.py --run data/runs/validacion
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


def largest_overlaps(states: np.ndarray, static: dict) -> dict:
    radius, domain = static["r"], static["R"]
    obstacles = np.array(static["obstacles"], dtype=float).reshape(-1, 3)
    upper = np.triu_indices(states.shape[1], k=1)
    worst = {"partículas": 0.0, "obstáculos": 0.0, "pared": 0.0}
    escape = 0.0
    for state in states:
        positions = state[:, :2]
        separation = np.linalg.norm(positions[:, None, :] - positions[None, :, :], axis=2)
        worst["partículas"] = max(worst["partículas"], (2.0 * radius - separation[upper]).max())
        if len(obstacles):
            distance = np.linalg.norm(positions[:, None, :] - obstacles[None, :, :2], axis=2)
            worst["obstáculos"] = max(worst["obstáculos"],
                                      (radius + obstacles[None, :, 2] - distance).max())
        reach = np.linalg.norm(positions, axis=1)
        worst["pared"] = max(worst["pared"], (reach + radius - domain).max())
        escape = max(escape, (reach - domain).max())
    worst["escape"] = escape
    return worst


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--deriva", type=float, default=1e-3,
                        help="cota de la deriva relativa de energia")
    parser.add_argument("--solapamiento", type=float, default=0.5,
                        help="cota del solapamiento maximo, en unidades del radio")
    arguments = parser.parse_args()

    static, times, states = common.load_run(arguments.run)
    energy = common.total_energy(states, static)
    drift = float(np.abs(energy - energy[0]).max())
    relative = drift / energy[0]
    worst = largest_overlaps(states, static)
    radius = static["r"]

    print(f"cuadros: {len(times)} (hasta t = {times[-1]:.6g} s, N = {static['N']}, "
          f"K = {static['K']}, dt = {static['dt']:g} s, dt2 = {static['dt2']:g} s)")
    print(f"energía inicial: {energy[0]:.12g} J")
    print(f"deriva máxima de energía: {drift:.6g} J ({relative:.3e} relativa)")
    for name in ("partículas", "obstáculos", "pared"):
        print(f"solapamiento máximo con {name}: {worst[name]:.6g} m "
              f"({100 * worst[name] / radius:.1f} % de r)")
    print(f"escape máximo fuera del dominio: {worst['escape']:.6g} m")
    contact = max(worst["partículas"], worst["obstáculos"], worst["pared"]) / radius
    ok = relative <= arguments.deriva and contact <= arguments.solapamiento
    print("OK" if ok else
          f"FALLA: supera la tolerancia (deriva {arguments.deriva:g}, "
          f"solapamiento {arguments.solapamiento:g} r)")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
