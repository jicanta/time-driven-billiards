# PLAN — TP4: Dinámica molecular regida por el paso temporal (billar circular)

> Documento de trabajo. Consolida qué pide el enunciado, cómo se va a resolver,
> qué decisiones se tomaron y en qué orden se avanza. Fuentes:
> `docs/TP4_Enunciado_2026Q2.pdf`, `docs/Teorica_4.pdf`, `docs/Teorica_0.pdf`,
> la bibliografía de la cátedra (`docs/GearPaper_1.pdf`, el paper de dinámica
> browniana y Heermann), `../tp-2/GuiaPresentaciones.pdf` y las devoluciones de
> la cátedra sobre el TP2 y sobre el borrador del TP3 (`FEEDBACK.md`).

---

## 0. Datos de la entrega

**Materia:** Simulación de Sistemas (SdS) — 2026 Q2 · **Comisión:** S2 · **Grupo:** 10

| Integrante | Legajo | Correo |
|---|---|---|
| Javier Liu | 64332 | jaliu@itba.edu.ar |
| Juan Ignacio Cantarella | 64509 | jcantarella@itba.edu.ar |
| Nicolás Rivas | 64292 | nrivas@itba.edu.ar |

**Fecha límite:** 23/10/2026, 13:00 h (campus). Presentación oral de **13
minutos** con las secciones de la guía de presentaciones de la cátedra
(`../tp-2/GuiaPresentaciones.pdf`, fuera de este repositorio).

**Entregables** (este TP **no lleva informe**; el zip no lleva README ni
documentación extra y debe pesar **menos de 100 KB**):

```
SdS_TP4_2026Q2G10S2_Presentación.pdf   # cuadro fijo + link a YouTube por animación
SdS_TP4_2026Q2G10S2_Codigo.zip         # el motor final + animate.py y common.py, < 100 KB, sin datos
```

El TP3 (dinámica molecular dirigida por eventos, mismo grupo) se entregó el
28/09/2026 y obtuvo 10: se conserva la misma organización del repositorio, el
mismo reparto entre motor y post-procesamiento y las mismas convenciones de
figuras.

---

## 1. En qué consiste el trabajo

Hay **dos sistemas** independientes.

### 1.1 Sistema 1: oscilador puntual amortiguado (solución analítica)

Una sola partícula puntual con fuerza elástica y rozamiento viscoso
(Teórica 4, diapositiva 37):

```
m r̈ = −k r − γ ṙ
```

con `m = 70 kg`, `k = 10⁴ N/m`, `γ = 100 kg/s`, `tf = 5 s` y condiciones
iniciales `r(0) = A = 1 m`, `v(0) = −A γ / (2m) = −0,714286 m/s`. La solución
es conocida:

```
r(t) = A exp(−γ t / 2m) cos(ω t),     ω = √(k/m − γ²/4m²) = 11,9309 rad/s
```

El período es `2π/ω = 0,527 s` y la amplitud cae por `e` cada `2m/γ = 1,4 s`:
en 5 s entran 9,5 oscilaciones y la amplitud baja a un 2,8 %.

El sistema sirve para **medir el error de cada esquema de integración** contra
la solución exacta. El observable es el error cuadrático medio

```
ECM(dt) = (1/n) Σₙ [ r_num(tₙ) − r_an(tₙ) ]²
```

sumado sobre **todos** los pasos temporales y normalizado por el número total
de pasos.

### 1.2 Sistema 2: billar circular

Dominio circular de radio `R = 0,51 m` centrado en el origen, con pared fija e
indeformable. Su área, `πR² = 0,8171 m²`, es prácticamente la de la mesa de
metegol del TP3 (`1,20 × 0,68 = 0,816 m²`), así que **a igual N la densidad es
la misma en los dos trabajos** y la comparación de tiempos de ejecución del
ítem 2.1.b es justa.

Dentro hay **dos obstáculos circulares fijos** (masa infinita) del mismo radio
`r` que las partículas, con centros en `(−xo, 0)` y `(+xo, 0)`. El rango de
`xo` que permiten los radios va de `xo = r = 0,0175 m` (los obstáculos se
tocan entre sí en el centro) a `xo = R − r = 0,4925 m` (tocan la pared).

`N` partículas de radio `r = 0,0175 m` y masa `m = 0,025 kg`, ubicadas
aleatoriamente sin solaparse entre sí, con los obstáculos ni con la pared, con
rapidez `v0 = 1 m/s` y dirección uniforme en `[0, 2π)`.

Las partículas interactúan **sólo por contacto**, con un resorte lineal en la
dirección normal, sin fricción ni disipación. El sistema es conservativo.

Todas nacen **frescas** (azules). Cuando una fresca toca por primera vez
cualquiera de los dos obstáculos pasa a **usada** (roja). Sólo cuenta el
primer contacto: la usada sigue moviéndose e interactuando igual, así que `N`
y la densidad no cambian.

Observables:

- `Nu(t)`: número acumulado de partículas usadas.
- `Fu(t) = Nu(t)/N`: fracción de usadas.
- `t90`: instante en que `Fu` alcanza 0,9. `t100`: en que alcanza 1.
- `E(t)`: energía total (cinética + elástica de los contactos).
- `f(v)`: distribución de probabilidad del módulo de la velocidad.

### 1.3 El paradigma: dinámica molecular regida por el paso temporal

A diferencia del TP3 (dirigido por eventos, sin reloj fijo), acá **hay un paso
temporal fijo `dt`**: se integran numéricamente las ecuaciones de Newton
`m r̈ᵢ = Fᵢ` de todas las partículas a la vez. El estado se imprime cada
`dt2 = n dt`, con `n` entero (Teórica 4, diapositiva 33), para no llenar el
disco.

El contacto ya no es instantáneo: dura un tiempo finito y hay solapamiento
mientras dura. Para un resorte lineal de constante `k` y masa efectiva `μ`, el
choque dura media oscilación del sistema masa-resorte:

```
τ = π √(μ/k)
```

Con `k = 10⁴ N/m`: entre dos partículas (`μ = m/2 = 0,0125 kg`) `τ = 3,51 ms`;
contra un obstáculo o la pared (`μ = m`, masa infinita del otro lado)
`τ = 4,97 ms`. **El paso de integración tiene que resolver ese choque**: de ahí
que el barrido del ítem 2.1.a arranque en `dt = 10⁻³ s` (apenas 3 o 4 pasos por
choque, que es donde el método explota) y llegue a `10⁻⁵ s`.

El solapamiento máximo esperable en un choque frontal a velocidad relativa
`v_rel` es `ξ_max = v_rel √(μ/k)`: 2,2 mm entre dos partículas a 2 m/s y 1,6 mm
contra la pared a 1 m/s, o sea entre el 9 % y el 13 % de `r`. No es un error:
es el modelo de contacto.

---

## 2. Modelo matemático

### 2.1 Esquemas de integración (sistema 1)

Los cuatro los da la Teórica 4. La fuerza del oscilador **depende de la
velocidad**, que es lo que obliga a cada esquema a tratarla de una manera
distinta; esa diferencia es el resultado del ítem 1.2.

**Verlet original** (diapositivas 13 a 15):

```
r(t+dt) = 2 r(t) − r(t−dt) + dt² f(t)/m
v(t)    = [r(t+dt) − r(t−dt)] / (2 dt)
```

Al reemplazar la segunda en la primera (porque `f` depende de `v`) la ecuación
del paso queda **implícita** en `r(t+dt)`; para esta fuerza es lineal y se
despeja exactamente, con `β = γ dt / 2m`:

```
r(t+dt) = [ (2 − k dt²/m) r(t) − (1 − β) r(t−dt) ] / (1 + β)
```

La posición anterior del primer paso sale de Euler evaluado en `−dt`
(diapositiva 14), `r(−dt) = r(0) − v(0) dt + dt² f(0)/(2m)`; se verifica que con
ella la diferencia centrada devuelve exactamente `v(0)`.

**Velocity Verlet** (diapositiva 17), con los dos pasos intermedios sobre la
velocidad que la propia teórica indica para fuerzas que dependen de `v`:

```
r(t+dt)    = r(t) + dt v(t) + dt² f(t)/(2m)
v(t+dt/2)  = v(t) + a(t) dt/2
a(t+dt)    = f(r(t+dt), v(t+dt/2)) / m
v(t+dt)    = v(t+dt/2) + a(t+dt) dt/2
```

**Beeman, variante predictor-corrector** (diapositiva 20), que es la que
corresponde cuando la fuerza depende de la velocidad:

```
r(t+dt)   = r(t) + v(t) dt + (2/3) a(t) dt² − (1/6) a(t−dt) dt²
vᵖ(t+dt)  = v(t) + (3/2) a(t) dt − (1/2) a(t−dt) dt
a(t+dt)   = f(r(t+dt), vᵖ(t+dt)) / m
v(t+dt)   = v(t) + (1/3) a(t+dt) dt + (5/6) a(t) dt − (1/6) a(t−dt) dt
```

El estado en `−dt` para tener `a(t−dt)` en el primer paso sale de Euler.

**Euler predictor-corrector** (diapositiva 23):

```
predecir:  vᵖ(t+dt) = v(t) + a(t) dt ;  rᵖ(t+dt) = r(t) + v(t) dt
evaluar:   a(t+dt) = f(rᵖ, vᵖ) / m
corregir:  v(t+dt) = v(t) + a(t+dt) dt ;  r(t+dt) = r(t) + v(t+dt) dt
```

### 2.2 Fuerzas de contacto (sistema 2)

```
Fᵢ = Σⱼ −k ξᵢⱼ êᵢⱼ ,    ξᵢⱼ = rᵢ + rⱼ − |rⱼ − rᵢ| > 0 ,    êᵢⱼ = (rⱼ − rᵢ)/|rⱼ − rᵢ|
```

La suma se extiende sólo a los `j` en contacto (`ξᵢⱼ > 0`): otras partículas,
los dos obstáculos fijos (de radio `r`) y la partícula imagen de la pared.

**Contacto con la pared: partícula imagen.** La normal saliente en el punto de
contacto `C` es radial, `n̂ = rᵢ/|rᵢ|`, y hay contacto si `|rᵢ| > R − r`. El
choque se trata contra una partícula virtual fija de radio `r` cuyo centro cae
sobre la normal, fuera del círculo, de modo que su borde toca la pared en
`C = R n̂`:

```
r_img = (R + r) n̂ ,    ξ_iw = 2r − |r_img − rᵢ| = |rᵢ| + r − R
```

Como `rᵢ`, `C` y `r_img` están alineados, la fuerza resulta puramente normal.
La posición de la imagen **se recalcula todos los `dt`**, porque durante el
choque la partícula se desplaza tangencialmente.

### 2.3 Energía (sistema 2)

El resorte es conservativo y no hay disipación, así que

```
E(t) = Σᵢ ½ m vᵢ² + Σ_contactos ½ k ξ²
```

debe ser constante. La suma de contactos recorre cada par de partículas una
sola vez, más los obstáculos y la pared. Con `v0 = 1 m/s` y sin solapamientos
iniciales, `E(0) = N ½ m v0² = 0,0125 N` J.

### 2.4 Maxwell-Boltzmann en dos dimensiones (ítem 2.3)

```
f(v) = (m v / kT) exp(−m v² / 2 kT)
```

De ahí `⟨v²⟩ = 2 kT/m`, es decir `kT = m ⟨v²⟩ / 2`. Como la energía se
conserva y la elástica es despreciable en promedio, el valor esperado es
`kT = m v0² / 2 = 0,0125 J`.

El ajuste se hace **con `kT` como único parámetro libre y por el método de la
Teórica 0**: se recorre `kT` en una grilla y se toma el mínimo del error
cuadrático medio `E(kT) = (1/n) Σᵢ [fᵢ − f(vᵢ; kT)]²`, que se muestra en su
propia figura con el mínimo marcado.

---

## 3. Estructura del repositorio

```
tp-4/
├── Makefile            # todo el flujo desde la raíz
├── README.md           # este repositorio, el motor y el post-procesamiento
├── PLAN.md             # este documento
├── FEEDBACK.md         # devoluciones de la cátedra aplicadas al TP4
├── requirements.txt    # matplotlib, numpy
├── docs/               # enunciado, Teórica 0 y 4, y la bibliografía de la cátedra
├── engine/             # C++17: motor regido por el paso temporal (va en el zip)
├── visualization/      # Python: post-procesamiento, figuras y animaciones
├── report/             # presentacion.tex (beamer 16:9, la presentación que se entrega), comun.tex, figuras/*.tikz y guion.md; build/ ignorado
├── youtube/            # titulos.md (los .mp4 no se versionan)
├── slides-images/      # todas las imágenes de la presentación numeradas por diapositiva: figuras (las lee presentacion.tex) y esquemas TikZ renderizados
└── data/               # salidas de simulación y figuras (ignoradas por git)
                        #   oscilador[_gamma0]/, energia[_densa]/, bench/, explore/,
                        #   velocidades/, mapa/, una_particula/, runs/, figures*/
```

---

## 4. Motor (`engine/`)

### 4.1 Módulos

| Archivo | Qué hace |
|---|---|
| `geometry.hpp` | `Vec2` y las operaciones de vector |
| `particle.hpp` | partícula: `r(t−dt)`, `r(t)`, `r(t+dt)`, `v(t)`, `F(t)` y el color |
| `obstacle.hpp` | obstáculo circular fijo |
| `billiard.hpp/cpp` | parámetros del dominio, los dos obstáculos y la condición inicial (al azar o sobre una red hexagonal) |
| `grid.hpp/cpp` | método de la celda de índice: el contacto alcanza a `2r`, así que basta mirar las 9 celdas vecinas |
| `forces.hpp/cpp` | fuerza de contacto (partícula, obstáculo y partícula imagen de la pared) y energía elástica |
| `simulation.hpp/cpp` | el bucle de Verlet y la conversión de fresca a usada |
| `oscillator.hpp/cpp` | sistema 1: los cuatro esquemas y la solución analítica |
| `io.hpp/cpp` | salida primaria: `static.txt`, `dynamic.txt`, `events.txt` |
| `arguments.hpp/cpp` | línea de comandos |
| `commands.hpp`, `command_*.cpp`, `main.cpp` | los cuatro comandos |

### 4.2 Comandos

- `oscillator` — sistema 1. Integra con cada esquema y cada `dt` y escribe la
  trayectoria completa (`t x v` por paso).
- `simulate` — una corrida del sistema 2 con cuadros cada `dt2 = n dt`.
- `bench` — ítem 2.1.b: tiempos contra `N` sin escribir cuadros, con el
  registro de conversiones acumulado en memoria y volcado al final.
- `explore` — barrido del producto `--ns × --xos × --dts` con `--seeds`
  realizaciones consecutivas.

### 4.3 Qué NO hace el motor

Como en el TP3, **el motor no calcula ningún observable**: ni el ECM, ni la
energía, ni `Fu`, ni `t90`, ni `f(v)`. Escribe estados y conversiones; todo lo
demás sale de esos archivos en `visualization/`. Lo único que el motor decide
es el cambio de color de una partícula, que es parte del estado.

---

## 5. Post-procesamiento (`visualization/`)

| Script | Ítem | Qué hace |
|---|---|---|
| `common.py` | — | lectura de las corridas, observables, estilos y `save()` |
| `oscillator.py` | 1.1, 1.2 | `r(t)` del oscilador con los cuatro esquemas sobre la analítica y ECM contra `dt` |
| `energy.py` | 2.1.a | `E(t)` en Joule y su error relativo en % por `dt`, y el error máximo contra `dt` |
| `bench.py` | 2.1.b | tiempo de ejecución contra `N` de los dos paradigmas |
| `explore.py` | 2.2 | `⟨t90⟩` contra `xo`, una curva por `N` |
| `conversion.py` | 2.2 | `Fu(t)` de los `xo` típicos en una figura (`--casos`), con `⟨t90⟩ ± σ` marcado |
| `speeds.py` | 2.3 | `f(v)` por instante (un histograma por bolsa), ajuste de Maxwell-Boltzmann y `E(kT)` |
| `density.py` | 2.4.a | `⟨t90⟩` y `⟨t100⟩` contra la densidad, del barrido propio del ítem |
| `heatmap.py` | 2.4.b | mapa de calor de `⟨t90⟩` en `(xo, N)`, con el óptimo de cada fila dibujado encima |
| `single.py` | 2.4.a | `N = 1`: conversión contra el parámetro de impacto (`make una-particula`) |
| `halfstep.py` | 1.1 | las 4 maneras de evaluar `a(t+dt)` en Velocity Verlet y el orden de cada una (`make velocity-verlet-variantes`) |
| `animate.py` | — | animación y cuadro fijo |
| `springs.py` | 1.1 | animación de apoyo: los 4 resortes oscilando a la vez, uno por esquema (sin la analítica) |
| `obstacles.py` | 2.2 | animación de apoyo: los obstáculos recorriendo todo el rango de `xo` (geometría, sin partículas) |
| `check.py` | — | validación: deriva de energía, solapamientos y escapes |

---

## 6. Plan por ítem

### Ítem 1.1 y 1.2 — Esquemas de integración y ECM

- Cuatro esquemas, `dt` de `5·10⁻³` a `10⁻⁵` con espaciado 1-2-5 (9 valores,
  tres décadas). Por debajo de `10⁻⁵` la trayectoria de un solo `dt` pasa los
  200 MB de texto y los esquemas de segundo orden ya están en el ruido de
  redondeo del doble.
- Figura: ECM contra `dt` en doble logarítmica, con el exponente `p` de
  `ECM = c dtᵖ` ajustado por cuadrados mínimos en log-log en la leyenda. Es
  **un solo panel**, con los cuatro esquemas y nada más: el enunciado pide una
  diapositiva con esa figura y «ninguna otra información».
- Beeman y Verlet original se superponen ahí, porque lo que los separa es la
  constante del error y no la pendiente. Eso va en una figura **aparte**,
  `ECM_constante_vs_dt.png`, que grafica `ECM/dt⁴`: `330` contra `380 m²/s⁴`,
  un 15 % más de ECM para Verlet con el mismo paso. No entra en la charla (las
  cifras sí, en la viñeta). La diferencia sale de que la fuerza depende de la
  velocidad y se verifica con `make oscilador-sin-amortiguamiento`
  (`gamma = 0`: las constantes coinciden).
- Los `dt` en los que la medición ya es ruido de redondeo del doble y no error
  del esquema quedan fuera de la figura y del ajuste.
- Son **dos diapositivas del sistema 1**: antes del ECM va `r(t)` del oscilador
  con `dt = 5·10⁻³ s` en los primeros 2 s (los cuatro esquemas sobre la
  analítica; la pidió la cátedra: la posición, no la energía, que no se
  conserva). El enunciado pedía sólo la del ECM.

### Ítem 2.1.a — Elección del paso temporal

- `N = 300`, sin obstáculos, `tf = 5 s`, `dt` de `10⁻³` a `10⁻⁵`, el mismo
  `dt2 = 0,01 s` para todos (`make energia`).
- Lo que se grafica es el **error relativo de la energía en porcentaje**,
  `eps(t) = 100 (E(t) − E₀)/E₀`, con el cero en el medio de la figura (la
  cátedra, 19/10: el porcentaje es más ilustrativo que la energía absoluta,
  porque es el número con el que se justifica el paso elegido).
- Observable escalar: **el máximo de ese error**,
  `eps_max(dt) = maxₜ |eps(t)|`.
- Criterio: el `dt` más largo con `eps_max ≤ 0,1 %`, porque es el que da el
  menor tiempo de ejecución con el error aceptado.
- Se verifica que el `dt` elegido sigue cumpliendo la cota en la condición más
  exigente del trabajo (`N = 700`, con obstáculos): `make energia-densa`.

### Ítem 2.1.b — Tiempo de ejecución contra N

- Obstáculos en contacto (`xo = r`), `tf = 30 s`, `N` de 50 a 700, 10
  realizaciones por `N` más una de calentamiento descartada. El barrido
  también se corrió por debajo (`N` de 5 a 30), pero el ajuste de la ley de
  potencia y la figura se hacen sobre `N ≥ 50`, donde el costo ya está
  dominado por las partículas y no por el barrido fijo de la grilla. El ítem
  2.4.a ya no usa estas corridas: tiene su barrido propio (consulta A4).
- En el mismo gráfico, los tiempos del ítem 1.1 del TP3 (dirigido por
  eventos) **corridos en esta misma computadora**.
- Se ajusta `t = c Nᵃ` a cada serie y se compara el exponente.

### Ítem 2.2 — Posición de los obstáculos

- `N = 100`, `tmax = 100 s`, 11 valores de `xo` de `r` a `R − r`, 15
  realizaciones cada uno (el enunciado pide al menos 5); y lo mismo con
  `N = 20` (densidad menor).
- Figuras: `Fu(t)` de los tres `xo` típicos (centro, `xo = 0,20 m` que es el
  mínimo medido, y borde) **en una sola figura**, que es como lo pide el
  enunciado («graficar `Fu(t)` para pocos valores típicos de `xo`»): una curva
  por `xo`, promedio de las 15 realizaciones, con banda de `± σ` y `⟨t90⟩ ± σ`
  marcado sobre la línea de `0,9`. Y `⟨t90⟩ ± σ` contra `xo` con una curva por
  `N`.
- Si alguna realización no llega a `Fu = 0,9` antes de `tmax`, el punto va con
  símbolo hueco y se informa `Fu(tmax)`.

### Ítem 2.3 — Distribución de velocidades

- `N = 100`, sin obstáculos, `tmax = 30 s`, `dt2 = 0,05 s`, 30 realizaciones.
- `f(v)` en varios instantes desde `t = 0` y la estacionaria (todos los
  cuadros con `t ≥ 10 s` de todas las realizaciones).
- Cada histograma es **uno solo sobre la bolsa** de `N × M` muestras (y
  `× cuadros` en el estacionario), una sola bolsa (la cátedra, 19/10): el
  histograma de una realización sola es ruido y promediar `M` curvas ruidosas
  tapa la forma de `f(v)`. **Ninguno de los dos lleva barras**: la bolsa es
  una medición con `M` veces más muestras, no el promedio de `M` mediciones
  (es el sentido de juntarlas). El desvío entre realizaciones se mide y se
  imprime igual: 51 % en un instante suelto, 4,8 % en la gran bolsa.
- Los instantes van en dos figuras: superpuestos y uno por panel, con el
  estacionario de fondo en gris (la cátedra viene pidiendo los paneles).
- Ajuste de `kT` por el mínimo del error cuadrático medio (Teórica 0) y
  comparación con `m ⟨v²⟩/2 = m v0²/2`.

### Ítem 2.4 — Efecto de la densidad

- Por qué hay densidad óptima: la fuerza de la pared es radial (partícula
  imagen sobre la normal), así que una partícula que no choca con otras
  conserva su momento angular respecto del centro y nunca se acerca más que
  su radio cáustico `b = |L|/|v|`; con los obstáculos en contacto se convierte
  si y sólo si `b < 3r`. **Probado** con `make una-particula` (`N = 1`, 300
  realizaciones, `tmax = 60 s`): se convierten 40 de 300 (13 %), exactamente
  las 40 con `b < 3r`, contra el 13,6 % que predice la distribución de `b`
  para posiciones uniformes y direcciones isótropas; `L` se conserva a
  `6·10⁻¹¹` relativo en 20 s con 21 rebotes. A densidad alta el camino libre
  se achica y el blanco queda rodeado. Las dos cosas juntas dan la U medida:
  `⟨t90⟩` mínimo en `ρ = 86` (`N = 70`) y creciendo hacia las dos puntas.

- (a) **Barrido propio** (`make densidad`), con la cátedra de acuerdo (19/10:
  "no es necesario atenerse a las del 2.1.b"): la misma configuración
  (`xo = r`) y las mismas densidades que la columna `xo = r` del mapa del
  2.4.b, 20 realizaciones y cada corrida hasta convertirlas todas. `⟨t90⟩` y
  `⟨t100⟩` contra `ρ = N/(πR²)`, dos ejes y nada más.
  Con las corridas del 2.1.b (`tf = 30 s` fijo) la figura era plana en 21 s y
  después se cortaba: de `N = 200` para arriba ninguna realización llegaba a
  `Fu = 0,9` y a `N = 5` llegaba una sola de diez, así que no mostraba
  ninguna densidad óptima, que es justo lo que el ítem pregunta. Con el
  barrido propio las dos curvas son una U: `⟨t90⟩` mínimo en `ρ = 86`
  (`N = 70`), 21,8 s, contra 66 s en `ρ = 6` y 54 s en `ρ = 367`.
- (b) (opcional, se hace) mapa de calor de `⟨t90⟩` en `(xo, N)` con
  10 densidades (`N` de 5 a 300) y 16 valores de `xo`, 20 realizaciones por
  punto (3200 corridas), con un proceso por celda `(N, xo)`.

### Ítem 2.5 — Declaración sobre uso de agentes de IA

Diapositiva final, después de las conclusiones, con el agente y el modelo
usados y de qué manera.

---

## 7. Presentación (13 min)

Secciones de la guía de presentaciones de la cátedra, con el esquema que funcionó en el
TP3: Introducción (sistema y parámetros), Implementación (esquema de Verlet,
UML del motor y el bucle del paso temporal, como el bucle de eventos del TP3),
Simulaciones (observables y casos),
Resultados (un bloque por ítem, cada diapositiva con la figura grande y dos o
tres viñetas) y Conclusiones (un punteo corto, una línea por ítem). Las
**dos diapositivas del sistema 1** abren Resultados. Al final, la
declaración de uso de IA.

---

## 8. Decisiones tomadas por defecto

Se cambian si los profesores indican otra cosa.

1. **El motor no calcula observables.** Igual que en el TP3. El ECM, la
   energía, `Fu`, `t90`, `f(v)` y los ajustes salen de los archivos de texto
   en `visualization/`. La única consecuencia visible es que la trayectoria
   del sistema 1 se escribe entera (un renglón por paso), que es lo que
   permite calcular el ECM "sobre todos los pasos temporales" como pide el
   enunciado.
2. **Verlet original con la fuerza dependiente de la velocidad.** Se usa la
   velocidad por diferencia centrada que da la propia teórica, lo que deja la
   ecuación del paso implícita; para esta fuerza es lineal y se despeja de
   forma exacta. La alternativa (evaluar la fuerza con una velocidad predicha
   hacia atrás) le quitaría un orden de convergencia al esquema por una
   decisión de implementación, no por el esquema.
3. **Velocity Verlet con la velocidad de medio paso.** Consultado a la
   cátedra (duda 4 de §9) y **validado el 19/10**. La diapositiva 17 escribe
   `v(t+dt) = v(t) + (dt/2m)(f(t) + f(t+dt))` y, aparte, los dos pasos
   intermedios `v(t+dt/2)` y `v(t+dt)`. Con una fuerza que sólo depende de la
   posición no hay nada que elegir. Acá `f` depende de `v`, así que `f(t+dt)`
   necesita `v(t+dt)`, que es lo que la propia ecuación está calculando: queda
   **implícita** y hay dos lecturas, las dos defendibles:
   - **(a) la de medio paso**, la que corre hoy: evaluar `f(t+dt)` con
     `v(t+dt/2)`, que es la única velocidad que aparece entre los dos pasos
     intermedios de la diapositiva.
   - **(b) despejar `v(t+dt)`**, que se puede porque `f` es lineal en `v`, y es
     lo mismo que se hizo con Verlet original (decisión 2). Es la fórmula
     principal de la diapositiva al pie de la letra.

   Beeman no tiene esta ambigüedad: la diapositiva 20 da la variante
   predictor-corrector explícitamente para fuerzas que dependen de `v`.

   **Qué da cada una** (`make velocity-verlet-variantes`,
   `visualization/halfstep.py`, que antes de comparar verifica que la variante
   (a) reproduce las trayectorias del motor en C++ con `5·10⁻¹⁵ m` de
   diferencia máxima en los nueve `dt`):

   | `f(t+dt)` evaluada con | `ECM ∝ dtᵖ` | orden | ¿distinto de Verlet original? |
   |---|---|---|---|
   | **(a)** `v(t+dt/2)` | `p = 2,04` | 1 | sí |
   | **(b)** `v(t+dt)` despejada | `p = 4,00` | 2 | **no, es el mismo esquema** |
   | `v(t) + a(t) dt` (Euler) | `p = 4,00` | 2 | sí |
   | `v(t)` congelada | `p = 2,02` | 1 | sí |

   El orden que pierde (a) es del predictor: `v(t+dt/2)` se aparta de `v(t+dt)`
   en `O(dt)` y ese error entra en `f(t+dt)` multiplicado por `dt/2`. No es un
   error de código.

   Que (b) **sea** Verlet original sale de sumar pasos consecutivos de las dos
   fórmulas de Velocity Verlet:

   ```
   r(t+dt) − r(t)  = dt v(t)   + (dt²/2m) f(t)
   r(t) − r(t−dt)  = dt v(t−dt) + (dt²/2m) f(t−dt)
   v(t) = v(t−dt) + (dt/2m)(f(t−dt) + f(t))
   ⟹ r(t+dt) − 2r(t) + r(t−dt) = (dt²/m) f(t)   y   v(t) = (r(t+dt) − r(t−dt))/(2dt)
   ```

   La cuenta no usa de qué depende `f`, así que vale también con fuerza
   dependiente de la velocidad, siempre que `f(t)` sea consistente con el
   propio `v(t)` del esquema: justo lo que impone el despeje. Comprobado
   numéricamente: con (b) el residuo de la recurrencia de Verlet original es
   `2·10⁻¹⁶` (redondeo) y `v(t)` coincide con la diferencia centrada en
   `10⁻¹³`; con (a) el residuo escala como `dt²`.

   **El trade-off, entonces**: (b) respeta la fórmula principal al pie de la
   letra y da segundo orden, pero deja 3 esquemas distintos en vez de 4 (en la
   figura de ECM vs `dt` se superpone con Verlet original); (a) mantiene los 4
   esquemas separados, que es lo que el enunciado pide comparar, al precio de
   un orden. La cátedra validó (a) el 19/10. Pasar a (b) sería una línea en
   `velocityVerlet()` más rehacer el barrido y las figuras, y pediría una
   viñeta en la diapositiva del sistema 1 explicando por qué hay 3 curvas.
4. **`dt = 5·10⁻⁵ s` para todo el sistema 2**, elegido en el ítem 2.1.a con la
   cota de deriva de 0,1 %: da `D = 3,8·10⁻⁴` a `N = 300` sin obstáculos y
   `2,6·10⁻⁴` a `N = 700` con los obstáculos en contacto (`make energia-densa`),
   con un solapamiento máximo del 23 % de `r` y ninguna partícula fuera del
   dominio (`visualization/check.py`).
5. **Condición inicial.** La del enunciado (adición secuencial al azar con
   rechazo) hasta `N = 400`; por encima de `N ≈ 450` la fracción de área pasa
   el límite del empaquetamiento al azar y no entra (verificado: con
   `--placement random` la partícula 446 no encuentra lugar tras 10⁶ intentos,
   sea `N = 450`, `470` o `500`; `N = 430` entra en 0,05 s), así que el barrido de
   `N` del 2.1.b usa una **red triangular** con el mayor paso que aloja `N`
   sitios, igual que en el TP3 y con la misma distribución uniforme de
   direcciones. La figura de apoyo muestra las dos condiciones iniciales para
   ver que no cambian el tiempo de ejecución.
6. **Las corridas del 2.2 y del 2.4.b terminan apenas se convierten todas las
   partículas**: después de eso no cambia ningún observable de esos ítems.
7. **La escritura de archivos no cuenta en el tiempo de ejecución** (mismo
   acuerdo que en el TP3): `bench` no escribe cuadros y vuelca las
   conversiones recién al terminar la corrida.
8. **`xo = 0,20 m` es la "posición óptima"** que llevan la animación y la
   figura de `Fu(t)`: es el mínimo medido de la curva de `N = 100`
   (`⟨t90⟩ = 14,8 ± 1,7 s` sobre 15 realizaciones). El mínimo es en realidad
   un plateau ancho (de `xo ≈ 0,15` a `0,35 m`, todas empatadas dentro del
   desvío), y así se dice en la diapositiva: lo que el ítem 2.2 responde es
   que **hay** un óptimo y dónde cae, no un valor con tres cifras.
9. **El ajuste de la ley de potencia del 2.1.b se hace sobre `N ≥ 50`.** Por
   debajo, el costo de un paso lo domina el barrido de las 29 × 29 celdas de
   la grilla, que no depende de `N`, y la curva se aplana: ajustar ahí mide
   el piso de la implementación, no cómo escala el paradigma. Los `N`
   chicos quedan medidos pero fuera de la figura.

---

## 9. Dudas para plantear a los profesores

La lista con la que se va a la consulta, ordenada por lo que puede costar
nota y con lo que contestamos si nos devuelven la pregunta, está en
`report/consultas.md`. Acá quedan las dudas de fondo:

1. El ítem 2.1.b pide llegar a `N > 600`: a esa cantidad la fracción de área
   es 0,71 (0,82 con `N = 700`) y la condición inicial al azar del enunciado
   ya no entra. ¿Está bien usar una red triangular por encima de `N = 400`,
   como en el TP3?
2. ~~El ítem 2.4.a pide tomar las corridas del 2.1.b~~ **RESUELTO (19/10)**: la
   cátedra dijo que no hace falta atenerse a esas corridas. Con su `tf = 30 s`
   fijo, de `N = 200` para arriba ninguna realización llegaba a `Fu = 0,9` y a
   `N = 5` llegaba una sola de diez, así que la figura no mostraba ninguna
   densidad óptima. El ítem corre ahora su propio barrido (`make densidad`).
3. Para el sistema 1, ¿se espera la variante predictor-corrector de Beeman
   (diapositiva 20) o la de fuerza independiente de la velocidad
   (diapositiva 19)? Se usó la primera, que es la que corresponde a una
   fuerza con rozamiento.
4. **RESUELTO (19/10): va la velocidad de medio paso.** Velocity Verlet con la
   fuerza que depende de la velocidad (la que
   decide el resultado del ítem 1.2; ver la decisión 3 de §8). En
   `v(t+dt) = v(t) + (dt/2m)(f(t) + f(t+dt))`, el `f(t+dt)` necesita
   `v(t+dt)`, que es lo que la ecuación está calculando: queda implícita. Dos
   salidas, las dos defendibles:
   - despejar `v(t+dt)` (se puede, `f` es lineal en `v`), que es lo mismo que
     se hizo con Verlet original. Da segundo orden, pero el esquema que queda
     **es Verlet original**: las recurrencias coinciden exactamente, así que
     en la figura de ECM vs `dt` se superponen y quedan 3 esquemas distintos
     en vez de 4;
   - evaluar `f(t+dt)` con la velocidad de medio paso `v(t+dt/2)`, la que
     aparece en los pasos intermedios de la diapositiva 17. Velocity Verlet
     queda distinto de Verlet original, pero pierde un orden
     (`ECM ∝ dt^2,04`).

   ¿Cuál de las dos se espera? Respuesta del 19/10: la segunda está bien, y es la que corre.
