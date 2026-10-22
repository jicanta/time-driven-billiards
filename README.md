# TP4 — Dinámica Molecular Regida por el Paso Temporal: Billar Circular

Simulación de Sistemas — ITBA. Integración numérica de las ecuaciones de
Newton con paso temporal fijo, para dos sistemas: un oscilador puntual
amortiguado con solución analítica (sistema 1, para medir el error de los
esquemas de integración) y un billar circular de partículas que interactúan
por contacto mediante un resorte lineal (sistema 2).

## Sistemas

**Sistema 1 — oscilador amortiguado.** `m r̈ = −k r − γ ṙ` con `m = 70 kg`,
`k = 10⁴ N/m`, `γ = 100 kg/s`, `r(0) = A = 1 m`, `v(0) = −A γ/(2m)` y
`tf = 5 s`. La solución es `r(t) = A e^(−γt/2m) cos(ωt)` con
`ω = √(k/m − γ²/4m²) = 11,9309 rad/s`. Se integra con **Beeman**, **Verlet
original**, **Velocity Verlet** y **Euler predictor-corrector**, y se compara
el error cuadrático medio contra la solución exacta.

**Sistema 2 — billar circular.**

- Dominio circular de radio `R = 0,51 m`, pared fija e indeformable. Su área,
  `πR² = 0,8171 m²`, es prácticamente la de la mesa del TP3 (`0,816 m²`): a
  igual `N`, la misma densidad.
- Dos obstáculos circulares fijos de radio `r`, con centros en `(−xo, 0)` y
  `(+xo, 0)`, con `xo` entre `r` (se tocan en el centro) y `R − r` (tocan la
  pared).
- `N` partículas de radio `r = 0,0175 m` y masa `m = 0,025 kg`, con
  `|v0| = 1 m/s` y direcciones uniformes en `[0, 2π)`.
- Interacción sólo por contacto: resorte lineal normal de constante
  `k = 10⁴ N/m`, sin fricción ni disipación. El sistema es conservativo.
- Una partícula *fresca* pasa a *usada* al tocar por primera vez cualquiera de
  los dos obstáculos. `Fu(t)` es la fracción de usadas, `t90` y `t100` los
  instantes en que llega a 0,9 y a 1.

## Estructura

```
tp-4/
├── Makefile            # todo el flujo desde la raíz: build, oscilador, energia, bench, obstaculos, velocidades, mapa, animaciones, entrega
├── README.md           # este documento
├── PLAN.md             # plan de trabajo: ítems, modelo, decisiones y dudas a los docentes
├── FEEDBACK.md         # devoluciones de la cátedra (TP2 y borrador del TP3) aplicadas al TP4
├── requirements.txt    # matplotlib, numpy
├── docs/               # enunciado, Teórica 0 y 4, y la bibliografía de la cátedra (Gear, Heermann)
├── engine/             # C++17: motor regido por el paso temporal (va en el zip de entrega con animate.py y common.py)
├── visualization/      # Python: post-procesamiento (observables), figuras y animaciones
├── report/             # presentacion.tex (beamer 16:9, la presentación que se entrega), comun.tex, figuras/*.tikz y guion.md; build/ ignorado
├── youtube/            # titulos.md con título y descripción de cada video (los .mp4 no se versionan)
├── gif/                # los seis videos como GIF, para embeber en la presentación en vivo
├── slides-images/      # todas las imágenes de la presentación numeradas por diapositiva: figuras (las lee presentacion.tex) y esquemas TikZ renderizados
└── data/               # salidas de simulación y figuras (ignoradas por git)
    ├── oscilador/      #   sistema 1: una trayectoria por esquema y por dt
    ├── oscilador_gamma0/ # sistema 1: el control sin amortiguamiento (gamma = 0)
    ├── una_particula/  #   ítem 2.4.a: N = 1, conversión contra el parámetro de impacto
    ├── energia/        #   ítem 2.1.a: N = 300 sin obstáculos, un barrido de dt con cuadros
    ├── energia_densa/  #   ítem 2.1.a: la misma verificación a N = 700 con obstáculos
    ├── bench/          #   ítem 2.1.b: tiempos contra N (y los del TP3, en la misma computadora)
    ├── explore/2.2/    #   ítem 2.2: barrido de xo con N = 100 y N = 20
    ├── velocidades/    #   ítem 2.3: N = 100 sin obstáculos, cuadros hasta el estacionario
    ├── densidad/       #   ítem 2.4.a: barrido de N con xo = r, hasta convertirlas todas
    ├── mapa/           #   ítem 2.4.b: barrido (xo, N)
    ├── runs/           #   corridas con cuadros para las animaciones y la validación
    └── figures/, figuras_diapositivas/   # figuras por ítem, en estilo de revisión y de diapositiva
```

## Flujo

```bash
pip install -r requirements.txt
make build                 # engine/build/billar
make check                 # validación: deriva de energía, solapamientos y escapes (visualization/check.py)
make una-particula         # N = 1: sin choques sólo se convierte si el parámetro de impacto es < 3r (ítem 2.4.a)
make oscilador             # sistema 1: los 4 esquemas y los 9 dt
make oscilador-figuras     # r(t) del oscilador y ECM vs dt (las dos figuras del sistema 1)
make energia               # ítem 2.1.a: N = 300 sin obstáculos, barrido de dt con cuadros
make energia-figuras       # E(t) en Joule y su error en % (los 3 dt que se leen juntos) y el error máximo vs dt con su ajuste
make energia-densa         # verifica el dt elegido en el caso más denso (N = 700 con obstáculos)
make bench                 # ítem 2.1.b: tiempos contra N (máquina descargada)
make bench-tp3             # los mismos tiempos con el motor del TP3, en esta computadora
make bench-figuras         # tiempo de ejecución vs N de los dos paradigmas
make obstaculos            # ítem 2.2: barrido de xo con N = 100 y N = 20
make obstaculos-figuras    # ⟨t90⟩ vs xo y Fu(t) de los tres xo típicos, en una sola figura
make velocidades           # ítem 2.3: N = 100 sin obstáculos, cuadros hasta el estacionario
make velocidades-figuras   # rapidez media vs t, f(v) por instante, la gran bolsa con el ajuste de Maxwell-Boltzmann y E(kT)
make densidad              # ítem 2.4.a: barrido propio de N con xo = r, 20 realizaciones, hasta convertirlas todas
make densidad-figuras      # ítem 2.4.a: ⟨t90⟩ y ⟨t100⟩ vs densidad
make mapa                  # ítem 2.4.b: barrido (xo, N)
make mapa-figuras          # mapa de calor de ⟨t90⟩ en el plano (xo, N)
make animations            # corridas características, videos y cuadro fijo de cada una, más las de apoyo
make animaciones-apoyo     # los 4 resortes del sistema 1 oscilando a la vez y los obstáculos recorriendo xo
make youtube               # copia los videos con nombres legibles en youtube/
make gifs                  # los seis videos como GIF en gif/
make oscilador-sin-amortiguamiento  # control: con gamma = 0 Beeman y Verlet dan la misma constante
make figuras-diapositivas  # las figuras de las diapositivas (data/figuras_diapositivas/);
                           # los 4 cuadros fijos de animación salen de make animations
make slides-images         # las 24 imágenes de la presentación numeradas por diapositiva (slides-images/, versionadas)
make todo                  # todas las simulaciones (densidad y una-particula se corren aparte); make all es su alias
make clean-figures         # borra data/figures/ y data/figuras_diapositivas/
make slides-images-tikz    # sólo los esquemas TikZ de las diapositivas (report/figuras/*.tikz) renderizados a PNG
make documentos            # report/presentacion.tex → report/build/presentacion.pdf (lee slides-images/)
make entrega               # SdS_TP4_2026Q2G10S2_Codigo.zip (motor + animate.py y common.py, < 100 KB) y SdS_TP4_2026Q2G10S2_Presentación.pdf
```

## Motor

Dinámica molecular regida por el paso temporal con el **esquema de Verlet
original** (Teórica 4, diapositivas 13 a 15):

```
r(t + dt) = 2 r(t) − r(t − dt) + dt² F(t) / m
v(t)      = [r(t + dt) − r(t − dt)] / (2 dt)
```

La posición anterior del primer paso se estima con Euler evaluado en `−dt`
(diapositiva 14). La velocidad de un paso necesita `r(t + dt)`, así que el
motor mantiene **tres posiciones consecutivas** por partícula: el estado que
se guarda lleva siempre `r(t)` y `v(t)` del mismo instante, no la velocidad
retrasada un paso. La fuerza del sistema 2 depende sólo de las posiciones, así
que Verlet es explícito.

```bash
cd engine && make
./build/billar simulate --n 100 --xo 0.0175 --dt 5e-5 --tmax 20 --save-every 800 --seed 7 --dir ../data/runs/centro
./build/billar simulate --n 100 --xo sin --dt 5e-5 --tmax 10 --save-every 200 --dir ../data/runs/validacion
./build/billar oscillator --dts 5e-3,2e-3,1e-3,5e-4,2e-4,1e-4,5e-5,2e-5,1e-5 --tf 5 --dir ../data/oscilador
./build/billar bench --ns 5,10,20,30,50,100,200,300,400,500,600,700 --tf 30 --dt 5e-5 --repeats 10 --placement hexagonal --dir ../data/bench/hexagonal
./build/billar explore --ns 100,20 --xos 0.0175,0.20,0.4925 --dts 5e-5 --seeds 15 --seed 7 --tmax 100 --until-all-used --dir ../data/explore/2.2
```

Parámetros del sistema por defecto: los del enunciado (`--radio 0.51
--r 0.0175 --m 0.025 --v0 1 --k 1e4`). `--xo sin` deja el dominio vacío.

`--placement` elige cómo se genera la condición inicial: `random` (la del
enunciado: adición secuencial al azar con rechazo de solapamientos) o
`hexagonal` (centros sobre una red triangular con el mayor paso que aloja `N`
sitios dentro del círculo, descartando los que tocan un obstáculo y eligiendo
`N` al azar). Las direcciones son uniformes en `[0, 2π)` en ambos casos. La
aleatoria se traba cerca de `N = 450` (fracción de área 0,53, el límite del
empaquetamiento al azar), igual que en el TP3 porque el área es la misma; la
hexagonal llega a 700 (82 % del área ocupada), que es el tope del barrido.

El motor **no calcula ningún observable**: ni el error del oscilador, ni la
energía, ni `Fu`, ni `t90`, ni `f(v)`. Escribe estados y conversiones; todo lo
demás sale de esos archivos, en `visualization/`. Lo único que decide es el
cambio de color de una partícula, que es parte del estado.

### Salida

`simulate` y `explore` escriben, en instantes `t = n dt2`:

- `static.txt` — parámetros, un `clave valor` por línea, y una línea
  `obstacle xk yk Rk` por obstáculo.
- `dynamic.txt` — por cuadro: una línea con `t` y luego `N` líneas
  `x y vx vy estado` (`0` fresca, `1` usada). Un cuadro cada
  `dt2 = save_every · dt`.
- `events.txt` — una línea por conversión: `t uso i k` (instante, partícula y
  obstáculo que la convirtió). De acá salen `Fu(t)`, `t90` y `t100` en
  post-proceso (`common.used_fraction`, `common.conversion_time`).

`oscillator` escribe una carpeta por esquema y, dentro, un archivo por `dt`
con la trayectoria completa (`t x v`, **una línea por paso de integración**) y
un `index.txt` con los parámetros. El ECM se calcula de esos archivos, sobre
todos los pasos, como pide el enunciado.

`bench` no escribe cuadros (acuerdo con la cátedra: la escritura no cuenta en
el tiempo de ejecución) y cronometra por separado la generación de la
condición inicial y el bucle de integración: una línea `N seed pasos t_final
ms_generacion ms_simulacion descartada` por realización en `tiempos.txt`. Por
cada `N` corre `--repeats` + `--warmup` realizaciones (10 + 1 por defecto): la
primera de un proceso tarda más por memoria y cachés frías, así que se escribe
igual pero marcada con `descartada = 1` y queda fuera del promedio y del
desvío. Las conversiones de cada realización se acumulan en memoria y se
vuelcan al terminar la corrida, para que el ítem 2.4.a pueda usar estas mismas
corridas.

`explore` corre el producto de `--ns`, `--xos` y `--dts` con `--seeds`
semillas consecutivas desde `--seed` y escribe por corrida
`<dir>/<caso>/s<semilla>/{static.txt, events.txt}`, más un `index.txt` con una
línea `caso N xo dt semilla carpeta` por corrida, volcada en cuanto la corrida
termina (así un barrido interrumpido deja un índice consistente con lo que
alcanzó a correr). Un barrido largo se puede partir en varios procesos, uno
por subcarpeta (es lo que hace `make mapa`, un proceso por celda `(N, xo)`): el
post-procesamiento junta los `index.txt` de las subcarpetas y antepone el
nombre de cada una al del caso, de modo que el resultado es el mismo que
correrlo de una sola vez. Sin cuadros salvo que se pida
`--save-every k` (en pasos) o `--dt2 s` (en segundos, que es lo que hace falta
cuando el barrido es sobre `dt` y las curvas tienen que compartir el eje).
Con `--until-all-used` la corrida termina apenas se convierten todas las
partículas, y `--until-fraction f` baja ese corte a la fracción que se va a
medir: el mapa del ítem 2.4.b sólo lee `t90`, y seguir hasta que se convierten
todas cuesta el triple de cómputo (a `N = 300`, `t90 ≈ 29 s` contra
`t100 ≈ 98 s`) sin cambiar nada de lo que se grafica.

### Costo por paso

La interacción alcanza a `2r = 0,035 m`, así que el motor usa el **método de
la celda de índice**: una grilla de `29 × 29` celdas sobre el cuadrado
`[−R, R]²` (lado de celda `0,0352 m ≥ 2r`) y, por partícula, sólo las 9 celdas
vecinas. El costo de un paso es `O(N)` en vez de `O(N²)`, que es lo que
permite llegar a `N = 700` con `dt = 5·10⁻⁵ s` y `tf = 30 s` (600 000 pasos).

## Ítem 1: esquemas de integración y ECM

La fuerza del oscilador **depende de la velocidad**, y cada esquema de la
Teórica 4 la trata de una manera distinta; esa diferencia es el resultado del
ítem. Las fórmulas están en `PLAN.md` §2.1. Dos puntos de implementación:

- **Verlet original**: la velocidad es la diferencia centrada
  (diapositiva 15), así que al meterla en la fuerza la ecuación del paso queda
  implícita en `r(t+dt)`; para esta fuerza es lineal y se despeja de forma
  exacta. Con la posición anterior de Euler en `−dt`, la diferencia centrada
  devuelve exactamente `v(0)`.
- **Velocity Verlet**: la diapositiva 17 escribe
  `v(t+dt) = v(t) + (dt/2m)(f(t) + f(t+dt))` y, aparte, los dos pasos
  intermedios `v(t+dt/2) = v(t) + a(t) dt/2` y
  `v(t+dt) = v(t+dt/2) + a(t+dt) dt/2`. Con una fuerza que no depende de `v`
  eso es sólo partir la patada en dos mitades. Acá `a(t+dt)` necesita
  `v(t+dt)`, que es lo que la propia ecuación está calculando: queda
  **implícita**, y la diapositiva no escribe ese caso. Hay **dos lecturas y
  las dos se defienden** —evaluar `f(t+dt)` con la velocidad de medio paso, o
  despejar `v(t+dt)` como se hizo con Verlet original—, con consecuencias
  distintas. Se consultó a la cátedra (`PLAN.md` §9, duda 4) y el 19/10
  contestaron que está bien la de medio paso, que es la que corre. Ver abajo.
- **Beeman**: la variante **predictor-corrector** de la diapositiva 20, que
  es la que la teórica da explícitamente para fuerzas que dependen de `v`.
  Ahí sí la diapositiva dice qué velocidad entra en `a(t+dt)`: la predicha.

### Las dos lecturas de Velocity Verlet y qué da cada una

`make velocity-verlet-variantes` (`visualization/halfstep.py`) reimplementa el
oscilador en Python y corre el mismo barrido de `dt` con las cuatro maneras
posibles de evaluar `a(t+dt)`, que es lo único en lo que se diferencian.
Primero verifica que la variante de medio paso reproduce las trayectorias que
escribió el motor en C++ (máxima diferencia `5·10⁻¹⁵ m` en los nueve `dt`), así
que lo que compara es el esquema que efectivamente corre; al final mide cuánto
se aparta cada lectura de la recurrencia de Verlet original:

| velocidad con la que se evalúa `a(t+dt)` | `ECM ∝ dtᵖ` | orden |
|---|---|---|
| `v(t+dt/2)`, la de medio paso (**el motor**) | `p = 2,04` | 1 |
| `v(t+dt)` exacta, despejada | `p = 4,00` | 2 |
| `v(t) + a(t) dt`, predicción de Euler | `p = 4,00` | 2 |
| `v(t)`, congelada | `p = 2,02` | 1 |

La pérdida de orden de la primera es del predictor: `v(t+dt/2)` se aparta de
`v(t+dt)` en `O(dt)`, y ese error entra en `a(t+dt)` multiplicado por `dt/2`,
así que el error global queda en `O(dt)` en vez de `O(dt²)`. Beeman no lo
pierde porque su predictor es una extrapolación de `O(dt²)`. **Es una
propiedad del esquema con esta fuerza, no un error de código.**

Despejar `v(t+dt)` es perfectamente posible —`f` es lineal en `v`, igual que
en Verlet original— y respeta la fórmula principal de la diapositiva al pie
de la letra. Lo que hay que saber antes de elegirla es que **el esquema que
queda es Verlet original**, no una variante suya. Sale de sumar pasos
consecutivos de las dos fórmulas de Velocity Verlet:

```
r(t+dt) − r(t)  = dt v(t)    + (dt²/2m) f(t)
r(t) − r(t−dt)  = dt v(t−dt) + (dt²/2m) f(t−dt)
v(t) = v(t−dt) + (dt/2m)(f(t−dt) + f(t))
⟹ r(t+dt) − 2r(t) + r(t−dt) = (dt²/m) f(t)   y   v(t) = (r(t+dt) − r(t−dt))/(2dt)
```

La cuenta no usa de qué depende `f`, así que vale también con fuerza
dependiente de la velocidad, siempre que `f(t)` sea consistente con el propio
`v(t)` del esquema: justo lo que impone el despeje. Numéricamente, con el
despeje el residuo de la recurrencia de Verlet original es `2·10⁻¹⁶` (puro
redondeo) y `v(t)` coincide con la diferencia centrada en `10⁻¹³`; con la de
medio paso el residuo escala como `dt²`.

**El trade-off**: despejar respeta la fórmula al pie de la letra y da segundo
orden, pero deja 3 esquemas distintos en vez de 4 (en la figura de ECM vs
`dt` se superpone con Verlet original); la de medio paso mantiene los cuatro
separados, que es lo que el enunciado pide comparar, al precio de un orden.
Ninguna es "la correcta" a priori: se consultó a la cátedra (`PLAN.md` §9,
duda 4) y el 19/10 validaron la de medio paso, que es la que corre.

El barrido va de `dt = 5·10⁻³` a `10⁻⁵ s` con espaciado 1-2-5 (nueve valores,
tres décadas). Por debajo de `10⁻⁵` el archivo de trayectorias de un solo `dt`
pasa los 200 MB de texto y los esquemas de segundo orden ya están en el ruido
de redondeo del doble.

A la presentación van **dos figuras**. La primera es la **posición del
oscilador contra el tiempo**, `r(t)` de los cuatro esquemas con la analítica
encima, para un solo paso (`dt = 5·10⁻³ s`, el más largo del barrido) y en los
primeros 2 s: la pidió la cátedra además del ECM, y pidió la posición y no la
energía porque lo que se estima es `r(t)` y la energía de este sistema no se
conserva. Beeman y los dos Verlet caen sobre la exacta (como mucho 1, 1 y
6 mm) y Euler predictor-corrector pierde amplitud: se aparta hasta 15 cm. La
segunda es el ECM de los cuatro esquemas en doble
logarítmica, literalmente lo que pide el enunciado del sistema 1 (*«con esta
última figura de ECM vs dt para los 4 métodos [...] ni ninguna otra
información»*), así que no lleva paneles de más.

Ahí Beeman y Verlet original se superponen, porque lo que los separa no es la
pendiente sino la **constante del error**, y una diferencia del 15 % no se ve
en diez órdenes de magnitud. Esa comparación tiene su propia figura,
`ECM_constante_vs_dt.png`: dividir el ECM por `dt⁴` saca la pendiente que
comparten y deja `380` contra `330 m²/s⁴` (un 15 % más de ECM para Verlet con
el mismo paso). Es material de análisis y queda fuera de la charla; las cifras
van en la viñeta y en `report/guion.md`, por si las preguntan. La diferencia
sale entera de que la fuerza depende de la velocidad, que es lo único en lo
que los esquemas difieren: `make oscilador-sin-amortiguamiento` rehace el
barrido con `gamma = 0` y las dos constantes coinciden.

Hay dos descartes, y el script lista los dos al correr: los `dt` en los que el
ECM ya dejó de bajar salen de la figura y del ajuste, porque ahí se mide la
precisión de la aritmética y no el error del esquema; y de la figura de la
constante salen además aquellos en los que se aparta más del 10 % de su
mediana, porque el redondeo ya la corre más que la diferencia que esa figura
quiere mostrar.

## Ítem 2.1.a: elección del paso temporal

El choque de dos partículas con un resorte lineal dura media oscilación del
sistema masa-resorte, `τ = π √(μ/k)`: 3,51 ms entre dos partículas
(`μ = m/2`) y 4,97 ms contra un obstáculo o la pared (`μ = m`). El paso tiene
que resolver ese choque.

Se grafican las dos cosas: `E(t)` en Joule, que es la evolución del sistema
que pide el ítem, y su **error relativo en porcentaje**,
`eps(t) = 100 (E(t) − E₀) / E₀`, con el cero (la conservación
exacta) en el medio de la figura: así el número del eje es el número de la
frase con la que se elige el paso. El observable escalar que resume cada curva
es `eps_max(dt) = maxₜ |eps(t)|`, una sola cifra por corrida. Se elige el `dt`
más largo con `eps_max ≤ 0,1 %`, porque es el que da el menor tiempo de
ejecución con el error aceptado: `dt = 5·10⁻⁵ s`, que deja `0,04 %` a
`N = 300` y `0,03 %` a `N = 700` con obstáculos.

## Ítem 2.3: distribución de velocidades

Cada histograma es **uno solo, sobre una bolsa de muestras**: los `|v|` de las
`N` partículas de las `M` realizaciones, todos juntos (`N × M = 3000` por
instante); la estacionaria suma además todos los cuadros con `t ≥ 10 s`
(promedio temporal, que para un estado estacionario es el mismo promedio de
ensamble): `30 × 401 × 100 = 1,2·10⁶` muestras. No es el promedio de los `M`
histogramas de cada realización con su desvío como barra: con 100 partículas en
40 intervalos, el histograma de una realización sola es ruido, y promediar `M`
curvas ruidosas con barras del 50 % tapa la forma de `f(v)`. El desvío entre
realizaciones se sigue midiendo y se imprime; en la figura de los instantes no
se dibuja.

La figura de la evolución muestra **instantes**, cada uno con su `t` exacto
(el último cuadro guardado hace de estacionario): un `t ≥ algo` es un promedio
sobre cuadros, no un instante. La gran bolsa lleva barra de error por
intervalo, y es el **desvío estándar entre realizaciones** (el histograma de
cada una por separado), la misma convención que el resto del trabajo y la
misma dispersión que la banda de la rapidez media. En un instante suelto ese
desvío es grande (51 % en promedio: cada realización reparte `N = 100`
partículas en 40 intervalos) y por eso ahí no se dibuja; en la gran bolsa,
que junta todos los cuadros desde `t = 10 s`, baja al 4,8 %.

La estacionaria se ajusta con Maxwell-Boltzmann en dos dimensiones,
`f(v) = (m v / kT) exp(−m v²/2kT)`, con `kT` como único parámetro libre y por
el método de la Teórica 0: se recorre `kT` en una grilla y se toma el mínimo
del error cuadrático medio `E(kT)`, que va en su propia figura con el mínimo
marcado. El valor ajustado se compara con `m ⟨v²⟩/2`, que para este sistema
vale `m v0²/2 = 0,0125 J`.

## Post-procesamiento

| Script | Ítem | Qué hace |
|---|---|---|
| `common.py` | — | lectura de las corridas, observables (energía, `Fu`, `t90`, ECM, ajuste de `kT`), estilos `informe`/`diapositiva` y `save()` con coma decimal en los ejes |
| `oscillator.py` | 1.1, 1.2 | `r(t)` del oscilador con los cuatro esquemas sobre la analítica para el `dt` de `--posicion`, en los primeros `--ventana` segundos (la primera figura del sistema 1), ECM contra `dt` de los cuatro esquemas, en doble logarítmica y con el exponente de `ECM = c dtᵖ` ajustado en log-log (la figura de la presentación), más `ECM/dt⁴` de los dos de cuarto orden como figura aparte |
| `energy.py` | 2.1.a | `E(t)` en Joule para los `dt` de `--pasos-energia`, error relativo de la energía en % contra `t` para los `dt` de `--pasos` (los representativos, los que se leen en una misma escala, con el cero en el medio) y `eps_max` en % contra `dt` sobre el barrido entero, con la cota y el `dt` elegido marcados |
| `bench.py` | 2.1.b | tiempo de ejecución contra `N` con el desvío entre las 10 realizaciones (dibujado; en cuatro décadas queda dentro del símbolo, y el script lo imprime por consola), una serie por archivo de tiempos, ajuste `t = c Nᵃ` punteado y sin entrada propia en la leyenda, ejes doble logarítmicos |
| `explore.py` | 2.2 | `t90` de cada corrida desde el registro de conversiones, `resumen.csv` con `⟨t90⟩ ± σ`, cuántas realizaciones llegan y `Fu(tmax)`; figura `⟨t90⟩` contra `xo` con una curva por `N`; `--fraccion 1` hace lo mismo con `t100` |
| `conversion.py` | 2.2 | `--casos`: `Fu(t)` promedio de varios `xo` en una misma figura, con banda de `± σ` entre realizaciones y `⟨t90⟩ ± σ` marcado sobre la línea de `0,9` (es la figura que pide el ítem); `--runs` dibuja corridas sueltas como escalón, para mirar una configuración de cerca |
| `speeds.py` | 2.3 | rapidez media `⟨|v|⟩` contra `t` (un escalar por cuadro, dice desde cuándo es estacionario y verifica el ajuste con `√(πkT/2m)`), `f(v)` en varios instantes exactos, un histograma por bolsa (`N × M` muestras), **la gran bolsa** (todos los cuadros del estacionario de todas las realizaciones en un solo histograma, `f_v_gran_bolsa_ajuste_*.png`) ajustada con Maxwell-Boltzmann por el mínimo de `E(kT)` (cuyo ancho da el error del ajuste) y comparación con `m ⟨v²⟩/2` y `m v₀²/2` |
| `density.py` | 2.4.a | `⟨t90⟩` y `⟨t100⟩` contra la densidad, en dos ejes y nada más, desde el barrido propio del ítem (`make densidad`: `xo = r`, las densidades del mapa, 20 realizaciones, cada corrida hasta convertirlas todas). No usa las corridas del 2.1.b: con su `tf = 30 s` fijo la mayoría de las densidades no llega a `Fu = 0,9` y la figura no muestra ninguna densidad óptima |
| `heatmap.py` | 2.4.b | mapa de calor de `⟨t90⟩` en el plano `(xo, N)`: eje `x` con la posición real de los obstáculos, una fila por `N` y escala de colores logarítmica (⟨t90⟩ crece más con `N` que con `xo`; en escala lineal el color lo gobierna la fila y adentro de cada una queda todo del mismo tono). Encima va el `xo` óptimo de cada densidad como una línea negra con opacidad moderada: un punto por fila, en la celda más baja de esa fila (el cuadrado más rojo). Por consola salen esa celda, el vértice de la parábola ajustada a la fila con su error (el número fino del óptimo, que va en la viñeta), qué celdas son compatibles con el mínimo y cuánto castiga la peor posición |
| `animate.py` | — | animación (un cuadro por estado guardado, `t` y las usadas en pantalla), tira de cuadros `--snapshots` y cuadro único con el lienzo del video `--cuadro` |
| `springs.py` | 1.1 | animación de apoyo: los cuatro resortes del sistema 1 oscilando a la vez, un carril por esquema y todos con el mismo `dt`, sin la analítica (la figura de `r(t)` ya la lleva). Es la misma trayectoria de `oscillator.py` mirada en la masa: tres esquemas se mueven como uno y Euler p-c se queda corto en cada extremo |
| `obstacles.py` | 2.2 | animación de apoyo: los dos obstáculos recorriendo todo el rango de `xo`, de `r` (se tocan en el centro) a `R − r` (tocan la pared), con marcas en los tres `xo` de las animaciones. No es una simulación: es la geometría del barrido, y no lee ninguna corrida |
| `single.py` | 2.4.a | `N = 1`: compara si cada realización se convierte con su parámetro de impacto inicial `b = |L|/|v|` (sin choques, `L` se conserva y sólo llega al centro si `b < 3r`) |
| `halfstep.py` | 1.1 | prueba de la decisión de Velocity Verlet: verifica contra el motor y mide el orden que da cada una de las 4 maneras de evaluar `a(t+dt)` |
| `check.py` | — | validación desde los estados guardados: deriva de energía, solapamiento máximo con partículas, obstáculos y pared, y escape fuera del dominio |

El nombre de cada eje es el **símbolo del enunciado con su unidad** (`N`,
`ρ (partículas/m²)`, `x_o (m)`, `⟨t90⟩ (s)`, `f(v) (s/m)`), no la frase que lo
describe: el símbolo está definido en las diapositivas de observables y de
parámetros, y así el rótulo no se come el ancho del eje. Sólo van en palabras
los que no tienen símbolo (el tiempo de ejecución, el ECM del ajuste). El
nombre entra siempre en **una sola línea** (`common.fit_axis_labels()` lo
achica hasta que entre), los números llevan coma decimal y la leyenda va
adentro del gráfico sin tapar datos: donde son varias entradas largas,
`common.legend_inside()` mide cuánto ocupa, le saca columnas o le achica la
letra hasta que entre a lo ancho del eje y recién entonces estira el eje
hacia arriba lo que la leyenda mide de alto.

## Presentación

`report/presentacion.tex` es la presentación en beamer 16:9 (la que se entrega) y sigue
la guía de presentaciones de la cátedra (`../tp-2/GuiaPresentaciones.pdf`,
fuera de este repositorio), las devoluciones recogidas en
`FEEDBACK.md` y el esquema que funcionó en el TP3: sin diapositiva de
contenido, sólo separadores de sección; UML del motor sin archivos ni
post-proceso; tabla de parámetros en tres bloques, **fijos, variables y
simulación**, con símbolo y valor como la del TP3, angosta para que el
esquema del dominio sea grande; una diapositiva define la
**conversión** y los observables. El **sistema 1 ocupa dos diapositivas**: la
posición del oscilador contra el tiempo (la pidió la cátedra: es lo que se
estima, y la energía no se conserva) y la figura de ECM contra `dt` de los
cuatro esquemas, como pide el enunciado, sin nada más. Resultados va un bloque por ítem, cada diapositiva con **el
gráfico grande más dos o tres viñetas** con lo que se lee en él, y las
conclusiones son un punteo corto, una línea por ítem, sólo con cifras que
estén en las figuras mostradas. La última diapositiva es la **declaración de uso de agentes de IA**
(ítem 2.5).

Los esquemas de las diapositivas de introducción e implementación (sistema,
pared como partícula imagen, UML del motor, bucle del paso temporal y
dominio) y la **tabla de parámetros** están en
`report/figuras/*.tikz`; `presentacion.tex` los lee con `\input` y
`make slides-images-tikz` los renderiza sueltos a PNG en `slides-images/`,
con los mismos colores (`report/comun.tex`), así que en
`slides-images/` está **toda** imagen que aparece en la presentación. La
diapositiva de parámetros entera, tal como queda compilada, está además en
`capturas/` (`make capturas` la recorta del PDF).
`report/guion.md` tiene dos o tres puntos para decir en cada diapositiva.

El zip de código que se entrega es el **motor de simulación** (`engine/`) más
**el código con el que se hacen las animaciones** a partir de las salidas
primarias (`visualization/animate.py` y `common.py`, del que depende), como
pidió la cátedra en el TP3.
