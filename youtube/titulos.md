# Animaciones para YouTube (TP4, Grupo 10, comisión S2)

Cuatro videos, uno por caso mostrado en Resultados: los obstáculos **en el
centro** (`xo = r`, en contacto entre sí), en la **posición óptima**, en el
**borde** (`xo = R − r`, en contacto con la pared) y el dominio **sin
obstáculos** (el del ítem 2.3, donde se mide la distribución de velocidades).
Los cuatro con `N = 100` y los mismos 20 s simulados, para que se comparen a
simple vista. `make animations` los genera en `data/figures/animaciones/` y
`make youtube` los copia acá con el nombre de abajo (que queda como título por
defecto al subirlos). Una vez subidos, los links reemplazan a los
`PENDIENTE-nn` de `report/presentacion.tex`, en el orden de esta lista, y se
recompila con `make documentos`.

Requisitos que cumplen (GuiaPresentaciones 2.4.1 y 2.4.8; devolución D12 del
TP2): cada partícula es un disco azul (fresca) o rojo (usada), los obstáculos
son negros y la pared circular gris; **un cuadro por estado guardado**, es
decir cada `dt2 = 800 dt = 0,04 s`, con el instante `t` y las usadas en
pantalla. A diferencia del TP3 (dirigido por eventos), acá el tiempo entre
cuadros **es uniforme**: a 25 cuadros por segundo (`FPS` en el Makefile) el
video corre en tiempo real. El código que los arma, `visualization/animate.py`, va en el zip de
entrega junto con el motor. Los ejes van en palabras con la unidad y coma
decimal, como en las diapositivas. El cuadro fijo del PDF es el instante
`t = 10 s` y tiene el mismo lienzo y la misma tipografía que el video; en el
PDF sólo va el cuadro fijo con el link explícito debajo.

Los mismos cuatro videos están como GIF en `gif/` (`make gifs`, numerados
igual que acá): son para embeber en la presentación en vivo, que se proyecta
sin links, y corren en tiempo real como el video (la mitad de los cuadros a la
mitad de los cuadros por segundo). A YouTube se sube el `.mp4`.

En `gif/` hay además dos animaciones de apoyo que **no** son videos de
YouTube ni corridas del billar (`make animaciones-apoyo`): el `05` son los
cuatro resortes del sistema 1 oscilando a la vez, uno por esquema y todos con
`dt = 5·10⁻³ s`, sin la analítica (es la figura de `r(t)` mirada en la masa);
el `06` son los dos obstáculos recorriendo todo el rango de `xo`, de `r` a
`R − r`, que es el parámetro del barrido del ítem 2.2. Van a `FPS` enteros,
no a la mitad: el oscilador da una vuelta cada 0,53 s.

Común a todos: dominio circular de `R = 0,51 m`, `N = 100` partículas de
`r = 0,0175 m` y `m = 0,025 kg`, `v0 = 1 m/s`, `k = 10⁴ N/m`,
`dt = 5·10⁻⁵ s`, condición inicial al azar (semilla 7, la misma que la
primera realización de los barridos), 20 s simulados.

## 01 - SdS TP4 G10 - Obstaculos en el centro - N 100.mp4

- **Link**: PENDIENTE-01
- **Diapositiva**: 17 (Obstáculos en el centro).
- **Título sugerido**: SdS TP4 G10 — Billar circular, obstáculos en el centro (xo = r)
- **Sistema**: los dos obstáculos en contacto entre sí, en el centro del dominio.
- **Descripción**: Simulación de Sistemas (ITBA), TP4 — dinámica molecular regida por el paso temporal. Billar circular de radio R = 0,51 m con N = 100 partículas de radio r = 0,0175 m y masa m = 0,025 kg, que arrancan con rapidez v0 = 1 m/s y dirección al azar e interactúan sólo por contacto, con un resorte lineal normal de constante k = 10⁴ N/m. Los dos obstáculos fijos (negros) están en contacto entre sí, a x0 = ±r del centro. Una partícula azul (fresca) pasa a roja (usada) al tocar por primera vez un obstáculo. Paso de integración dt = 5·10⁻⁵ s con el esquema de Verlet original, un cuadro cada dt2 = 800 dt = 0,04 s: a 25 cuadros por segundo el video corre en tiempo real. 20 s simulados. Grupo 10, comisión S2.

## 02 - SdS TP4 G10 - Obstaculos en la posicion optima - N 100.mp4

- **Link**: PENDIENTE-02
- **Diapositiva**: 19 (Obstáculos en la posición óptima).
- **Título sugerido**: SdS TP4 G10 — Billar circular, obstáculos en la posición óptima
- **Sistema**: los dos obstáculos en la posición que minimiza ⟨t90⟩.
- **Descripción**: Simulación de Sistemas (ITBA), TP4 — dinámica molecular regida por el paso temporal. El mismo billar circular y las mismas N = 100 partículas que el video anterior, pero con los dos obstáculos separados en x0 = ±0,20 m, la posición que minimiza ⟨t90⟩. Comparado con los obstáculos en el centro se ve que las partículas rojas (usadas) aparecen antes: cada obstáculo barre su propia zona y ninguno queda a la sombra del otro. Paso de integración dt = 5·10⁻⁵ s (Verlet original), un cuadro cada 0,04 s, 25 cuadros por segundo, 20 s simulados. Grupo 10, comisión S2.

## 03 - SdS TP4 G10 - Obstaculos en el borde - N 100.mp4

- **Link**: PENDIENTE-03
- **Diapositiva**: 20 (Obstáculos en el borde).
- **Título sugerido**: SdS TP4 G10 — Billar circular, obstáculos en el borde (xo = R − r)
- **Sistema**: los dos obstáculos en contacto con la pared.
- **Descripción**: Simulación de Sistemas (ITBA), TP4 — dinámica molecular regida por el paso temporal. El mismo billar circular y las mismas N = 100 partículas, con los dos obstáculos en contacto con la pared, en x0 = ±(R − r) = ±0,4925 m. Es la posición de conversión más lenta del barrido: pegados a la pared los obstáculos quedan fuera del camino de casi todas las trayectorias y quedan partículas azules (frescas) mucho más tiempo. Paso de integración dt = 5·10⁻⁵ s (Verlet original), un cuadro cada 0,04 s, 25 cuadros por segundo, 20 s simulados. Grupo 10, comisión S2.

## 04 - SdS TP4 G10 - Sin obstaculos - N 100.mp4

- **Link**: PENDIENTE-04
- **Diapositiva**: 23 (Sin obstáculos).
- **Título sugerido**: SdS TP4 G10 — Billar circular sin obstáculos
- **Sistema**: el dominio vacío, el del ítem 2.3.
- **Descripción**: Simulación de Sistemas (ITBA), TP4 — dinámica molecular regida por el paso temporal. El mismo billar circular con N = 100 partículas pero sin obstáculos: no hay conversión y todas quedan frescas (azules). Es el sistema con el que se elige el paso de integración por conservación de la energía (ítem 2.1.a) y con el que se mide la distribución del módulo de la velocidad (ítem 2.3): las partículas arrancan todas con |v| = v0 = 1 m/s y en medio segundo los choques entre partículas y con la pared llevan f(v) a la distribución de Maxwell-Boltzmann en dos dimensiones. Paso de integración dt = 5·10⁻⁵ s (Verlet original), un cuadro cada 0,04 s, 25 cuadros por segundo, 20 s simulados. Grupo 10, comisión S2.
