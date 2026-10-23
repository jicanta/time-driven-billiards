"""El guion de la presentacion, de Markdown a PDF para leerlo o imprimirlo.

El guion se escribe en Markdown (`presentacion/guion.md`) porque es lo que se
edita comodo mientras se arma la charla; esto lo pasa a LaTeX y lo compila con
el mismo motor que la beamer (tectonic), para tener una copia paginada,
legible en el celular y que se puede imprimir.

No es un conversor de Markdown completo: entiende lo que el guion usa
(titulos, vinetas, listas numeradas, citas, negrita, cursiva, codigo y las
reglas horizontales) y traduce a LaTeX los simbolos que el texto escribe en
Unicode (Delta, rho, los subindices de t90, 10^-5, las medias <|v|>...), que
es lo que no entraria de otra manera.

    python3 presentacion/guion_a_pdf.py
    python3 presentacion/guion_a_pdf.py --entrada report/guion.md --salida report/build/guion.pdf
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Los simbolos que el guion escribe en Unicode y su equivalente en LaTeX. Las
# letras acentuadas y los signos de interrogacion no estan: esos pasan tal
# cual (inputenc utf8).
SYMBOLS = {
    "Δ": r"\Delta", "ρ": r"\rho", "ε": r"\varepsilon", "π": r"\pi",
    "γ": r"\gamma", "ξ": r"\xi", "ω": r"\omega", "τ": r"\tau",
    "μ": r"\mu", "µ": r"\mu", "σ": r"\sigma",
    "±": r"\pm", "×": r"\times", "≥": r"\geq", "≤": r"\leq",
    "≈": r"\approx", "∝": r"\propto", "∈": r"\in", "→": r"\to",
    "−": "-", "·": r"\cdot", "½": r"\tfrac{1}{2}", "√": r"\sqrt{}",
    "⟨": r"\langle", "⟩": r"\rangle",
}
# Los signos de apertura del castellano no pasan por T1 + utf8 en este motor
# (salen como una libra): van con su comando.
PUNCTUATION = {"¿": r"\textquestiondown{}", "¡": r"\textexclamdown{}"}
SUPERSCRIPT = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
               "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-", "ᵖ": "p"}
SUBSCRIPT = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
             "₆": "6", "₇": "7", "₈": "8", "₉": "9"}
SPECIAL = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
           "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}


def escape(text: str) -> str:
    return "".join(SPECIAL.get(ch, ch) for ch in text)


def symbols(text: str) -> str:
    """Unicode -> LaTeX. Los exponentes y subindices seguidos se juntan en uno
    solo (10⁻⁵ -> $10^{-5}$, t₉₀ -> $t_{90}$), que es como se escriben."""
    text = re.sub(f"[{''.join(SUPERSCRIPT)}]+",
                  lambda m: "$^{" + "".join(SUPERSCRIPT[c] for c in m.group()) + "}$", text)
    text = re.sub(f"[{''.join(SUBSCRIPT)}]+",
                  lambda m: "$_{" + "".join(SUBSCRIPT[c] for c in m.group()) + "}$", text)
    for symbol, command in SYMBOLS.items():
        text = text.replace(symbol, f"${command}$")
    # Dos grupos matematicos pegados ($a$$b$) se funden en uno: asi no queda
    # un espacio raro entre el simbolo y su subindice.
    text = text.replace("$$", "")
    for sign, command in PUNCTUATION.items():
        text = text.replace(sign, command)
    # Exponentes escritos con acento circunflejo (N^0,88, Delta t^4): el
    # circunflejo ya viene escapado, asi que se reconoce por su comando.
    text = re.sub(r"([A-Za-z0-9])\\textasciicircum\{\}([0-9][0-9,.]*)",
                  r"$\1^{\2}$", text)
    return text.replace("n̂", r"$\hat{n}$").replace("—", "---")


def inline(text: str) -> str:
    """Negrita, cursiva y codigo de una linea de Markdown."""
    code = []

    def hold(match):
        # Dentro de `codigo` los exponentes y subindices van en ASCII, que es
        # como se escriben en una terminal: la tipografia de maquina de
        # escribir no tiene los caracteres de Unicode.
        text = match.group(1)
        for table, mark in ((SUPERSCRIPT, "^"), (SUBSCRIPT, "_")):
            for symbol, plain in table.items():
                text = text.replace(symbol, mark + plain)
        code.append(escape(text))
        return f"\0{len(code) - 1}\0"

    text = re.sub(r"`([^`]*)`", hold, text)
    # Los subindices de una letra (x_o, N_u, t_f, k_BT) van en matematica: en
    # el texto quedaban con el guion bajo escapado a la vista. Va ANTES de
    # traducir los simbolos, para que "-x_o" quede en una sola matematica.
    text = re.sub(r"(?<![\w\\$])([A-Za-z])\\_([A-Za-z0-9]{1,3})(?![\w])",
                  r"$\1_{\2}$", escape(text))
    text = symbols(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"\\textit{\1}", text)
    return re.sub(r"\0(\d+)\0", lambda m: r"\texttt{" + code[int(m.group(1))] + "}", text)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noquoting,es-noshorthands]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[a4paper,margin=2.2cm,top=2.0cm,bottom=2.0cm]{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{parskip}
\usepackage{microtype}

\definecolor{azul}{RGB}{23,66,110}
\definecolor{gris}{RGB}{110,118,128}

\titleformat{\section}{\large\bfseries\color{azul}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.1\baselineskip}{0.3\baselineskip}
\setlist[itemize]{leftmargin=1.2em,itemsep=0.25em,topsep=0.25em}
\setlist[enumerate]{leftmargin=1.5em,itemsep=0.35em,topsep=0.25em}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\small\color{gris}TP4 -- Billar circular, Grupo 10 S2}
\fancyhead[R]{\small\color{gris}Guion de la presentación}
\fancyfoot[C]{\small\color{gris}\thepage}

\begin{document}
"""


def blocks(source: str) -> list[str]:
    """Junta las lineas que el Markdown parte por ancho.

    El guion esta escrito con los parrafos cortados a 75 columnas, y un
    **resaltado** puede empezar en una linea y terminar en la siguiente: si se
    traduce linea por linea, esos asteriscos quedan a la vista. Aca cada
    parrafo, vineta o linea de cita vuelve a ser UNA linea antes de traducir."""
    out: list[str] = []
    for raw in source.splitlines():
        line = raw.rstrip()
        quoted = line.startswith(">")
        body = line.lstrip("> ").strip() if quoted else line.strip()
        opens = (not body
                 or body.startswith(("#", "- ", "---", "***", "___", "|"))
                 or re.match(r"\d+\.\s", body)
                 or quoted != (bool(out) and out[-1].startswith(">")))
        if out and out[-1].strip() and not opens:
            out[-1] += " " + body
        else:
            out.append(line)
    return out


def convert(source: str) -> str:
    out = [PREAMBLE]
    mode = None          # 'itemize', 'enumerate' o None
    quote = False

    def close(target=None):
        nonlocal mode
        if mode and mode != target:
            out.append(f"\\end{{{mode}}}")
            mode = None

    def open_list(kind):
        nonlocal mode
        close(kind)
        if mode != kind:
            out.append(f"\\begin{{{kind}}}")
            mode = kind

    for raw in blocks(source):
        line = raw.rstrip()
        stripped = line.lstrip()
        inside = line.startswith(">")
        if inside and not quote:
            close()
            out.append(r"\begin{quote}\color{azul!85!black}")
            quote = True
        if not inside and quote:
            close()
            out.append(r"\end{quote}")
            quote = False
        if inside:
            stripped = line.lstrip("> ").strip()
        if not stripped:
            close()
            out.append("")
            continue
        if stripped.startswith("# "):
            close()
            out.append(r"\begin{center}{\LARGE\bfseries\color{azul} "
                       + inline(stripped[2:]) + r"}\end{center}")
            out.append(r"\vspace{0.4em}")
            continue
        if stripped.startswith("## "):
            close()
            out.append(r"\section*{" + inline(stripped[3:]) + "}")
            continue
        if stripped.startswith("### "):
            close()
            out.append(r"\subsection*{" + inline(stripped[4:]) + "}")
            continue
        if stripped in ("---", "***", "___"):
            close()
            out.append(r"\vspace{0.2em}{\color{gris}\hrule}\vspace{0.6em}")
            continue
        numbered = re.match(r"(\d+)\.\s+(.*)", stripped)
        if stripped.startswith("- "):
            open_list("itemize")
            out.append(r"\item " + inline(stripped[2:]))
            continue
        if numbered:
            open_list("enumerate")
            out.append(r"\item " + inline(numbered.group(2)))
            continue
        close()
        out.append(inline(stripped))
    close()
    if quote:
        out.append(r"\end{quote}")
    out.append(r"\end{document}")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entrada", type=Path, default=ROOT / "presentacion/guion.md")
    parser.add_argument("--salida", type=Path, default=ROOT / "presentacion/guion.pdf")
    parser.add_argument("--motor", type=str, default="tectonic -X compile")
    arguments = parser.parse_args()

    # El .tex intermedio va a report/build (ignorado por git) y no a /tmp:
    # tectonic viene empaquetado como snap y no ve los temporales del sistema.
    work = ROOT / "report/build"
    work.mkdir(parents=True, exist_ok=True)
    source = work / f"{arguments.salida.stem}.tex"
    source.write_text(convert(arguments.entrada.read_text()))
    subprocess.run(arguments.motor.split() + [str(source), "--outdir", str(work)],
                   check=True, stdout=subprocess.DEVNULL)
    arguments.salida.parent.mkdir(parents=True, exist_ok=True)
    arguments.salida.write_bytes((work / f"{arguments.salida.stem}.pdf").read_bytes())
    print(f"{arguments.salida}  ({arguments.salida.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
