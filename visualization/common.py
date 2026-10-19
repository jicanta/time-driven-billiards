"""Utilidades compartidas por las figuras del TP4.

El motor de C++ escribe archivos de texto en data/ y este modulo es el unico
lugar donde se los interpreta: el resto de los scripts solo grafica. Los
observables (la energia total, el ECM del oscilador, Fu, t90, f(v), los
tiempos) se calculan aca, fuera del motor.

Convenciones (las mismas en todas las figuras):

* El estado del sistema 2 se guarda cada dt2 = n dt, con n entero (Teorica 4,
  diapositiva 33): todo lo que se mide son esos estados, no instantes
  intermedios.
* Lo que se promedia sobre realizaciones lleva como barra de error el desvio
  estandar entre realizaciones (ddof = 1), tanto si es un escalar (t90, el
  tiempo de ejecucion) como si es un histograma (f(v), intervalo por
  intervalo). Una barra se lee como el desvio: no se aclara en la figura.
* Los ajustes de un parametro se hacen como en la Teorica 0: se recorre el
  parametro en una grilla y se toma el minimo del error cuadratico medio, que
  se muestra en su propia figura.
* Las figuras no llevan titulo: los parametros van en el nombre del archivo y
  al costado de la figura en la diapositiva.
* El nombre de cada eje es el simbolo del enunciado con su unidad (N, rho,
  x_o, t, f(v), ...), no la frase que lo describe: el simbolo esta definido en
  las diapositivas de observables y de parametros, y asi el rotulo no se come
  el ancho del eje. Solo van en palabras los que no tienen simbolo (el tiempo
  de ejecucion, el ECM del ajuste).
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.ticker import FuncFormatter, ScalarFormatter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BENCH = DATA / "bench"
OSCILLATOR = DATA / "oscilador"
ENERGY = DATA / "energia"
EXPLORE = DATA / "explore"
SPEEDS = DATA / "velocidades"
DENSITY = DATA / "densidad"
MAP = DATA / "mapa"
FIGURES = DATA / "figures"

FOLDER_NAME = {
    "1": "1_oscilador",
    "2.1": "2.1_paso_y_tiempos",
    "2.2": "2.2_obstaculos",
    "2.3": "2.3_velocidades",
    "2.4": "2.4_densidad",
    "anim": "animaciones",
}


def folder(item: str, root: Path = FIGURES) -> Path:
    path = Path(root) / FOLDER_NAME[item]
    path.mkdir(parents=True, exist_ok=True)
    return path


AXIS_TIME = "$t$ (s)"
AXIS_STEP = "$\\Delta t$ (s)"
AXIS_ECM = "ECM (m$^2$)"
AXIS_ECM_CONSTANT = "ECM / $\\Delta t^4$ (m$^2$/s$^4$)"
AXIS_POSITION = "$r$ (m)"
AXIS_ENERGY = "$E$ (J)"
# El error de la energia va en PORCENTAJE y no en Joule ni en relativo a secas:
# lo que se decide con estas dos figuras es "me quedo con este paso porque el
# error es menor que tanto por ciento", y asi el numero del eje es el numero de
# la frase. epsilon esta definido en la diapositiva de observables.
AXIS_ENERGY_ERROR = "$\\varepsilon$ (%)"
AXIS_DRIFT = "$\\varepsilon_{\\max}$ (%)"
AXIS_COUNT = "$N$"
AXIS_WALL = "tiempo de ejecución (s)"
AXIS_FU = "$F_u$"
AXIS_T90 = "$\\langle t_{90} \\rangle$ (s)"
AXIS_OFFSET = "$x_o$ (m)"
AXIS_SPEED = "$v = |\\vec{v}|$ (m/s)"
AXIS_PDF = "$f(v)$ (s/m)"
AXIS_DENSITY = "$\\rho$ (partículas/m$^2$)"
AXIS_FIT_ERROR = "error cuadrático medio $E$ (s$^2$/m$^2$)"

SCHEME_LABEL = {
    "beeman": "Beeman",
    "verlet": "Verlet original",
    "velocity-verlet": "Velocity Verlet",
    "euler-pc": "Euler predictor-corrector",
}
SCHEME_STYLE = {
    "beeman": ("#1f5fbf", "o"),
    "verlet": ("#2ca02c", "s"),
    "velocity-verlet": ("#ff7f0e", "^"),
    "euler-pc": ("#d62728", "v"),
}
SCHEMES = list(SCHEME_LABEL)

# Las barras de error que van DIBUJADAS APARTE de la curva (f(v): la curva es
# el promedio sobre realizaciones y la barra, el desvio) llevan todas este
# mismo estilo, en el color de su serie: dos figuras del mismo item con barras
# de distinto grosor o unas con capucha y otras sin, se leen como si midieran
# cosas distintas.
ERRORBAR = {"linestyle": "none", "elinewidth": 1.2, "capsize": 2.5, "capthick": 1.2}

FRESH = "#1f5fbf"
USED = "#d62728"
OBSTACLE = "#1a1a1a"
WALL = "#555555"

STYLE = "informe"
STYLES = ("informe", "diapositiva")


def use_style(style: str = "informe") -> None:
    """Tipografia y tamanos de figura para revision o para la presentacion.

    La guia pide que las letras dentro de la figura se lean del tamano del
    texto de la diapositiva (al menos 20 pt): el estilo "diapositiva" usa
    menos pulgadas y tipografia mas grande, y sans serif como beamer. El
    nombre del eje va mas chico que el resto para entrar en una sola linea.
    """
    if style not in STYLES:
        raise SystemExit(f"estilo desconocido: {style}; hay {', '.join(STYLES)}")
    global STYLE
    STYLE = style
    matplotlib.rcParams.update(
        {
            "figure.figsize": (7.2, 4.8),
            "figure.dpi": 120,
            "savefig.dpi": 220,
            "savefig.bbox": "tight",
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman"],
            "font.size": 13,
            "axes.labelsize": 15,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "lines.linewidth": 1.6,
            "lines.markersize": 5,
            "errorbar.capsize": 3,
        }
    )
    if style == "diapositiva":
        # Lienzo mas chico con la misma tipografia: al meterlo en la
        # diapositiva (poco mas de la mitad del ancho util) las letras de la
        # figura quedan del tamano del texto de al lado, como pide la guia.
        matplotlib.rcParams.update(
            {
                "figure.figsize": (6.3, 4.0),
                "font.family": "sans-serif",
                "font.sans-serif": ["DejaVu Sans"],
                "font.size": 17,
                "axes.labelsize": 16,
                "xtick.labelsize": 15,
                "ytick.labelsize": 15,
                "legend.fontsize": 13,
                "lines.linewidth": 2.2,
                "lines.markersize": 7,
            }
        )


def decimal(value: float, digits: int | None = None) -> str:
    """Numero con coma decimal, como en el texto de las diapositivas."""
    text = f"{value:.{digits}f}" if digits is not None else f"{value:g}"
    return text.replace(".", ",")


def scientific(value: float, digits: int = 0) -> str:
    """Numero en notacion cientifica para los rotulos de las figuras, sin los
    delimitadores de matematica: 5e-4 -> "5 \\cdot 10^{-4}", 1e-4 -> "10^{-4}".
    Los pasos de integracion barren varios ordenes y con %g quedarian mezclados
    ("0,0005" junto a "2e-05")."""
    if value == 0.0:
        return "0"
    exponent = int(np.floor(np.log10(abs(value))))
    mantissa = value / 10.0 ** exponent
    if abs(mantissa - 1.0) < 1e-9:
        return f"10^{{{exponent}}}"
    return f"{decimal(mantissa, digits)} \\cdot 10^{{{exponent}}}"


def comma_ticks(figure) -> None:
    """Coma decimal en las marcas de los ejes lineales con formato automatico
    (los ejes logaritmicos y las marcas fijadas a mano quedan como estan)."""
    formatter = FuncFormatter(lambda value, _: decimal(value))
    for axes in figure.get_axes():
        for axis in (axes.xaxis, axes.yaxis):
            if axis.get_scale() == "linear" and type(axis.get_major_formatter()) is ScalarFormatter:
                axis.set_major_formatter(formatter)


def fit_axis_labels(figure, minimum: float = 11.0) -> None:
    """Achica el nombre de un eje hasta que entre en UNA linea dentro del
    largo de ese eje (devolucion del 18/09 sobre el TP3: el nombre del eje no
    debe ocupar dos lineas ni salirse). Sin efecto si ya entra."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for axes in figure.get_axes():
        box = axes.get_window_extent(renderer)
        for label, room in ((axes.xaxis.label, box.width), (axes.yaxis.label, box.height)):
            if not label.get_text():
                continue
            size = label.get_fontsize()
            while size > minimum:
                extent = label.get_window_extent(renderer)
                if max(extent.width, extent.height) <= room:
                    break
                size -= 0.5
                label.set_fontsize(size)


def headroom(axes, fraction: float = 0.3) -> None:
    """Deja libre la fraccion de arriba del area de dibujo, para que la leyenda
    entre adentro de la figura sin taparla (devolucion del TP2, D13: la leyenda
    va dentro del grafico y sin tapar datos). Funciona en escala lineal y
    logaritmica."""
    low, high = axes.get_ylim()
    if axes.get_yscale() == "log":
        if low <= 0.0 or high <= 0.0:
            return
        span = np.log10(high) - np.log10(low)
        axes.set_ylim(low, 10.0 ** (np.log10(high) + fraction / (1.0 - fraction) * span))
    else:
        span = high - low
        axes.set_ylim(low, high + fraction / (1.0 - fraction) * span)


def save(figure, path) -> None:
    comma_ticks(figure)
    fit_axis_labels(figure)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)


def add_common_arguments(parser) -> None:
    parser.add_argument("--figures", type=Path, default=FIGURES,
                        help="carpeta raiz de las figuras")
    parser.add_argument("--estilo", choices=STYLES, default="informe")


# --------------------------------------------------------------------------
# Sistema 1: oscilador amortiguado
# --------------------------------------------------------------------------

def read_oscillator_index(root: Path) -> tuple[dict, list[dict]]:
    """index.txt de `billar oscillator` -> (parametros, [{'esquema', 'dt',
    'pasos', 'archivo'}, ...]) en el orden del indice."""
    root = Path(root)
    header: dict = {}
    rows = []
    for line in (root / "index.txt").read_text().splitlines():
        pieces = line.split()
        if not pieces:
            continue
        if pieces[0] == "#":
            if len(pieces) % 2 == 1:
                header.update({k: float(v) for k, v in zip(pieces[1::2], pieces[2::2])
                               if _is_number(v)})
            continue
        rows.append({"esquema": pieces[0], "dt": float(pieces[1]), "pasos": int(pieces[2]),
                     "archivo": root / pieces[3]})
    return header, rows


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def read_trajectory(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Trayectoria del oscilador: (t, x, v), una fila por paso guardado."""
    values = np.loadtxt(path)
    return values[:, 0], values[:, 1], values[:, 2]


def angular_frequency(parameters: dict) -> float:
    m, k, gamma = parameters["m"], parameters["k"], parameters["gamma"]
    return float(np.sqrt(k / m - gamma ** 2 / (4.0 * m ** 2)))


def analytic_position(parameters: dict, t: np.ndarray) -> np.ndarray:
    """r(t) = A exp(-gamma t / 2m) cos(w t) (Teorica 4, diapositiva 37)."""
    m, gamma, amplitude = parameters["m"], parameters["gamma"], parameters["A"]
    return amplitude * np.exp(-gamma * t / (2.0 * m)) * np.cos(angular_frequency(parameters) * t)


def mean_squared_error(parameters: dict, path: Path) -> float:
    """ECM(dt): suma de las diferencias al cuadrado entre la solucion numerica
    y la analitica sobre TODOS los pasos temporales, dividida por el numero
    total de pasos."""
    t, x, _ = read_trajectory(path)
    return float(np.mean((x - analytic_position(parameters, t)) ** 2))


# --------------------------------------------------------------------------
# Sistema 2: billar circular
# --------------------------------------------------------------------------

def read_static(run: Path) -> dict:
    """static.txt: 'clave valor' por linea; los obstaculos en 'obstacles'."""
    info: dict = {"obstacles": []}
    for line in (Path(run) / "static.txt").read_text().splitlines():
        pieces = line.split()
        if not pieces:
            continue
        if pieces[0] == "obstacle":
            info["obstacles"].append(tuple(float(v) for v in pieces[1:4]))
        elif pieces[0] in ("N", "K", "seed", "save_every"):
            info[pieces[0]] = int(pieces[1])
        elif pieces[0] == "placement":
            info[pieces[0]] = pieces[1]
        else:
            info[pieces[0]] = float(pieces[1])
    return info


def load_run(run: Path):
    """Devuelve (static, tiempos (F,), estados (F, N, 5)): cada cuadro de
    dynamic.txt es una linea con t y N lineas 'x y vx vy usada'."""
    static = read_static(run)
    count = static["N"]
    with open(Path(run) / "dynamic.txt") as handle:
        values = np.fromfile(handle, sep=" ")
    frames = values.size // (1 + 5 * count)
    values = values[:frames * (1 + 5 * count)].reshape(frames, 1 + 5 * count)
    return static, values[:, 0].copy(), values[:, 1:].reshape(frames, count, 5).copy()


def read_conversions(run: Path) -> np.ndarray:
    """events.txt -> instantes de las conversiones de fresca a usada, en
    orden. Una linea por conversion: 't uso i k'."""
    text = (Path(run) / "events.txt").read_text().split()
    return np.array([float(v) for v in text[0::4]]) if text else np.array([])


def used_fraction(run: Path):
    """Fu(t) como escalon: (instantes de conversion, Fu justo despues de cada
    conversion). Arranca en (0, 0): todas las particulas nacen frescas."""
    static = read_static(run)
    times = read_conversions(run)
    return (np.concatenate([[0.0], times]),
            np.arange(0, len(times) + 1) / static["N"])


def conversion_time(run: Path, fraction: float = 0.9):
    """Instante de la conversion con la que Fu alcanza `fraction`, o None si
    no llega antes de tmax. t90 es fraction = 0.9 y t100 es fraction = 1."""
    static = read_static(run)
    times = read_conversions(run)
    needed = int(np.ceil(fraction * static["N"] - 1e-9))
    return float(times[needed - 1]) if len(times) >= needed else None


def kinetic_energy(states: np.ndarray, mass: float) -> np.ndarray:
    """Energia cinetica total en cada cuadro guardado."""
    return 0.5 * mass * (states[:, :, 2:4] ** 2).sum(axis=2).sum(axis=1)


def potential_energy(states: np.ndarray, static: dict) -> np.ndarray:
    """Energia potencial elastica en cada cuadro: 1/2 k xi^2 sumada sobre los
    contactos (pares de particulas una sola vez, obstaculos y pared). Es la
    misma xi del enunciado, con la particula imagen para la pared:
    xi_iw = |r_i| + r - R."""
    radius, domain, stiffness = static["r"], static["R"], static["k"]
    obstacles = np.array(static["obstacles"], dtype=float).reshape(-1, 3)
    count = states.shape[1]
    upper = np.triu_indices(count, k=1)
    energy = np.empty(len(states))
    for frame, state in enumerate(states):
        positions = state[:, :2]
        separation = np.linalg.norm(positions[:, None, :] - positions[None, :, :], axis=2)
        overlap = np.clip(2.0 * radius - separation[upper], 0.0, None)
        total = (overlap ** 2).sum()
        if len(obstacles):
            distance = np.linalg.norm(positions[:, None, :] - obstacles[None, :, :2], axis=2)
            total += (np.clip(radius + obstacles[None, :, 2] - distance, 0.0, None) ** 2).sum()
        total += (np.clip(np.linalg.norm(positions, axis=1) + radius - domain, 0.0, None) ** 2).sum()
        energy[frame] = 0.5 * stiffness * total
    return energy


def total_energy(states: np.ndarray, static: dict) -> np.ndarray:
    return kinetic_energy(states, static["m"]) + potential_energy(states, static)


def read_explore(root: Path) -> tuple[dict, dict]:
    """index.txt de `billar explore` (y de `billar bench`) -> (cabecera,
    {caso: {'N', 'xo', 'dt', 'runs': [carpeta, ...]}}), en el orden del
    indice. xo = -1 significa sin obstaculos.

    Si la carpeta no tiene index.txt propio, se juntan los de sus subcarpetas:
    un barrido largo se puede partir en varios procesos (uno por N, por
    ejemplo) y leerse despues como uno solo. Cada parte nombra sus casos con
    lo que ella barre, asi que dos partes pueden repetir el nombre con otro N;
    por eso al unirlas el nombre del caso lleva adelante el de su subcarpeta,
    que es lo que las distingue (n20/xo0.2000 -> n20_xo0.2000, el mismo nombre
    que tendria el barrido corrido de una sola vez)."""
    root = Path(root)
    if not (root / "index.txt").exists():
        header, cases = {}, {}
        for index in sorted(root.glob("*/index.txt")):
            part_header, part_cases = read_explore(index.parent)
            header.update(part_header)
            for name, case in part_cases.items():
                key = f"{index.parent.name}_{name}"
                cases.setdefault(key, {**case, "runs": []})["runs"].extend(case["runs"])
        if not cases:
            raise SystemExit(f"no hay ningún index.txt en {root}")
        return header, cases
    header: dict = {}
    cases: dict = {}
    for line in (root / "index.txt").read_text().splitlines():
        pieces = line.split()
        if not pieces:
            continue
        if pieces[0] == "#":
            if len(pieces) % 2 == 1:
                header.update({k: float(v) for k, v in zip(pieces[1::2], pieces[2::2])
                               if _is_number(v)})
            continue
        name, count, offset, step, _, directory = pieces[:6]
        case = cases.setdefault(name, {"N": int(count), "xo": float(offset),
                                       "dt": float(step), "runs": []})
        case["runs"].append(root / directory)
    return header, cases


def read_bench(path: Path, discarded: bool = False) -> dict:
    """tiempos.txt -> {N: {'steps': [...], 'generation': [...], 'loop': [...]}}
    (milisegundos). Solo las mediciones que entran en el promedio; con
    discarded=True, solo las marcadas como descartadas (la primera de cada N,
    que paga el arranque en frio del proceso)."""
    rows = defaultdict(lambda: {"steps": [], "final": [], "generation": [], "loop": []})
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        pieces = line.split()
        n, _, steps, final, generation, loop = pieces[:6]
        flagged = len(pieces) > 6 and pieces[6] == "1"
        if flagged != discarded:
            continue
        rows[int(n)]["steps"].append(int(steps))
        rows[int(n)]["final"].append(float(final))
        rows[int(n)]["generation"].append(float(generation))
        rows[int(n)]["loop"].append(float(loop))
    return dict(sorted(rows.items()))


def maxwell_boltzmann(speed: np.ndarray, thermal: float, mass: float) -> np.ndarray:
    """Distribucion de Maxwell-Boltzmann del modulo de la velocidad en dos
    dimensiones: f(v) = (m v / kT) exp(-m v^2 / 2 kT)."""
    return mass * speed / thermal * np.exp(-mass * speed ** 2 / (2.0 * thermal))


def fit_thermal_energy(speed: np.ndarray, density: np.ndarray, mass: float,
                       points: int = 4001):
    """Ajuste de f(v) con kT como unico parametro libre, a la manera de la
    Teorica 0: se recorre kT en una grilla y se toma el minimo del error
    cuadratico medio E(kT) = (1/n) sum_i [f_i - f(v_i; kT)]^2. Devuelve
    (kT, grilla, E)."""
    # El valor de referencia, m <v^2> / 2, centra la grilla.
    weights = density / density.sum()
    reference = 0.5 * mass * float((speed ** 2 * weights).sum())
    grid = np.linspace(0.2 * reference, 2.5 * reference, points)
    model = maxwell_boltzmann(speed[None, :], grid[:, None], mass)
    error = ((density[None, :] - model) ** 2).mean(axis=1)
    best = int(np.argmin(error))
    return float(grid[best]), grid, error


def mean_std(values) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    return float(values.mean()), float(values.std(ddof=1)) if len(values) > 1 else 0.0
