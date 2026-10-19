# Consultas para la cátedra — última oportunidad antes de entregar

Ordenadas por lo que puede costar nota. Cada una tiene **qué preguntar** y
**qué contestamos si nos devuelven la pregunta** (porque siempre la devuelven).

Lo primero, que no es una pregunta: **mostrarles el PDF**. La guía 3.4 dice
que se consulte lo que no quede claro, y las devoluciones del TP2 piden
"mostrar el trabajo intermedio al cuerpo docente antes de presentarlo". Llevar
`SdS_TP4_2026Q2G10S2_Presentación.pdf` abierto y pasarlo mientras se pregunta.

---

## A. Las que pueden cambiar un resultado o una figura

### A1. Velocity Verlet: ¿despejamos o usamos la velocidad de medio paso?

> La fuerza del oscilador es `f = −k r − γ v`, o sea que depende de la
> velocidad. En Velocity Verlet, `v(t+Δt) = v(t) + (Δt/2m)(f(t) + f(t+Δt))`, y
> `f(t+Δt)` necesita `v(t+Δt)`, que es justo lo que la ecuación está
> calculando: queda implícita. Vemos dos salidas y dan resultados distintos:
>
> 1. **Despejar `v(t+Δt)`**, como hicimos con Verlet original, que también
>    queda implícito. Da segundo orden, pero el esquema que queda es
>    **idéntico a Verlet original**: las dos recurrencias coinciden
>    exactamente, así que en la figura de ECM vs Δt se superponen y nos quedan
>    3 esquemas distintos en vez de 4.
> 2. **Evaluar `f(t+Δt)` con la velocidad de medio paso `v(t+Δt/2)`**, la que
>    aparece en los pasos intermedios de la diapositiva 17. Velocity Verlet
>    queda distinto de Verlet original, pero pierde un orden: `ECM ∝ Δt^2,04`.
>
> ¿Cuál de las dos esperan?

**Versión corta, si hay apuro:** "en Velocity Verlet con fuerza que depende de
la velocidad, ¿despejamos `v(t+Δt)` o usamos la de medio paso? Porque si
despejamos nos da exactamente Verlet original y quedan 3 esquemas en vez de 4."

**Lo que tenemos medido**, por si lo piden: medio paso `p = 2,04` (orden 1);
despejada `p = 4,00` (orden 2); con la predicción de Euler `p = 4,00`; con
`v(t)` congelada `p = 2,02`. Hoy corre la de medio paso.

---

### A2. ¿El exponente del ajuste tiene que estar escrito en la diapositiva?

> En la figura de tiempo de ejecución contra `N` dibujamos los puntos con su
> desvío y la recta del ajuste `t = c N^a` punteada, pero sacamos el exponente
> de la leyenda y de las viñetas, con la idea de decirlo oralmente.
> ¿Hace falta que el número esté escrito en la diapositiva?

**Por qué preguntamos esto:** la guía 1.1 dice que la presentación es
autocontenida y la 1.4 que hay que responder todos los puntos del enunciado;
el ítem 2.1.b pide "comparar y discutir cómo escala el costo computacional",
y hoy los exponentes (`0,88` y `3,52`) no están en ninguna parte del PDF. Si
dicen que tienen que estar, se vuelven a poner en las viñetas: son dos
números.

---

### A3. Condición inicial por encima de `N ≈ 450`

> El ítem 2.1.b pide llegar a `N > 600`. Con `N = 600` la fracción de área es
> 0,71 y con `N = 700` es 0,82, y la adición secuencial al azar que indica el
> enunciado se traba cerca de `N = 450` (fracción de área 0,53, el límite del
> empaquetamiento al azar). Usamos una red triangular por encima de `N = 400`,
> como en el TP3. ¿Está bien así?

**Si preguntan si cambia el resultado:** corrimos el barrido con las dos
condiciones iniciales donde las dos entran. La del enunciado llega hasta
`N = 300` y ahí los tiempos coinciden dentro del 3 % (`6,43 s` la red contra
`6,60 s` al azar); de `N = 400` en adelante el generador al azar ya no
termina. Está en `make bench-figuras`, figura
`tiempo_total_vs_N_condiciones-iniciales`.

---

### A4. Ítem 2.4.a: con `t_f = 30 s` casi nadie llega a `F_u = 0,9`

> El 2.4.a pide tomar los outputs del 2.1.b y reportar `⟨t90⟩` y `⟨t100⟩` en
> función de la densidad. Esas corridas son con los obstáculos en contacto y
> `t_f = 30 s`, y con esa configuración sólo los `N` chicos llegan: a `N = 10`
> llegan 5 de 10 realizaciones, a `N = 20` llegan 8 de 10, y **desde `N = 200`
> no llega ninguna** (`F_u(t_f)` medio: 0,84 a `N = 200` y 0,01 a `N = 700`).
> Informamos `⟨t90⟩` y `⟨t100⟩` donde existen, con símbolo hueco cuando no
> llegan todas, y `F_u(t_f)` en todo el rango sobre el eje derecho.
> ¿Alcanza así, o esperan que alarguemos `t_f` sólo para este ítem?

---

### A5. Sistema 1: ¿se puede agregar un segundo panel?

> El enunciado dice que la diapositiva del sistema 1 lleve la figura de ECM vs
> Δt de los 4 métodos y "ninguna otra información". Beeman y Verlet original
> se superponen ahí, porque lo que los separa es la constante del error y no
> la pendiente: dividiendo el ECM por Δt⁴ queda 330 contra 380 m²/s⁴, un 15 %.
> ¿Se puede mostrar eso como segundo panel de la misma figura, o lo dejamos
> afuera y lo decimos sólo si preguntan?

**Hoy está afuera** (un solo panel), por la lectura literal del enunciado. La
figura existe por si la piden: `data/figures/1_oscilador/ECM_constante_vs_dt.png`.

---

## B. Las de criterio y formato

### B1. `F_u(t)` del ítem 2.2: ¿una figura con los tres `x_o` o una por caso?

> El ítem 2.2 pide "graficar `F_u(t)` para pocos valores típicos de `x_o`", y
> lo hicimos en **una sola figura** con los tres (centro, óptimo y borde), cada
> curva el promedio de sus 15 realizaciones con banda de ±1 desvío. La guía
> 2.4.2, en cambio, sugiere mostrar la evolución del observable después de
> cada animación. ¿Está bien la figura única?

**Por qué la hicimos así:** la guía 1.4 dice que el enunciado tiene máxima
prioridad sobre las guías genéricas, y la 2.4.2 dice que las evoluciones "no
son los resultados definitivos, por lo tanto no debe ser extenso lo que se
muestre de las mismas". Las tres juntas es lo único que deja comparar.

### B2. ¿Tres animaciones para el ítem 2.2 o dos?

> Mostramos tres animaciones del barrido de `x_o`: centro (`x_o = r`), óptimo
> (`0,20 m`) y borde (`x_o = R − r`). La guía 2.4.1 dice una, o dos con los
> valores extremos. ¿Dejamos las tres o sacamos la del óptimo?

Sacarla ahorra una diapositiva y ayuda con los 13 minutos.

### B3. El observable escalar del ítem 2.1.a

> El 2.1.a pide proponer un observable escalar que caracterice la evolución de
> la energía. Propusimos la **deriva relativa máxima**
> `D(Δt) = máx_t |E(t) − E₀| / E₀`, y elegimos el `Δt` más largo con
> `D ≤ 10⁻³`. ¿Les parece bien el observable y la cota?

### B4. La figura de energía muestra 4 de los 7 `Δt` medidos

> Medimos 7 pasos pero dibujamos 4: con `Δt = 10⁻³ s` la energía se dispara a
> 45 J y aplasta a todas las demás contra `E₀`, y `2·10⁻⁵` y `10⁻⁵` caen
> encima de `5·10⁻⁵`. El barrido completo está en la figura de la deriva, que
> es la que elige el paso. ¿Está bien mostrar sólo los cuatro?

### B5. La explicación de la densidad óptima, ¿necesita figura propia?

> En el 2.4.a decimos que hay densidad óptima porque sin choques cada
> partícula conserva el momento angular respecto del centro y no llega a los
> obstáculos: lo probamos con una corrida dedicada de `N = 1`, donde convierten
> 40 de 300 realizaciones (13 %), exactamente las de parámetro de impacto
> `b < 3r`. Está como viñeta, sin figura. La guía 2.5 dice que una hipótesis
> que explique lo observado tiene que estar probada y **mostrada en
> resultados**. ¿Hace falta una figura, o alcanza con decirlo?

### B6. `f(v)` estacionaria: cómo juntamos las muestras

> Para la distribución estacionaria juntamos **todos los cuadros con
> `t ≥ 10 s`** de las 10 realizaciones: 4·10⁵ muestras. Los cuadros de una
> misma realización están correlacionados entre sí. ¿Está bien juntarlos así,
> o esperan un solo instante por realización?

### B7. El enunciado dice `m⟨v²⟩/2 = m v₀²/2`, y nos dan distinto

> El 2.3 pide comparar el `k_BT` ajustado con `m⟨v²⟩/2 = m v₀²/2`. En la
> simulación esas dos **no** son iguales: nos da `m⟨v²⟩/2 = 12,32 mJ` contra
> `m v₀²/2 = 12,50 mJ`, un 1,4 % menos, porque en el estacionario parte de la
> energía está guardada en los resortes de los contactos (el sistema conserva
> la energía total, no la cinética). El ajuste da `k_BT = 12,42 mJ`.
> ¿Es eso lo que esperan que discutamos?

### B8. Cifras significativas del error

> Escribimos los promedios como `⟨t90⟩ = 26,5 ± 3,4 s`. Por el criterio de la
> Teórica 0, ¿lo quieren con el error a una cifra significativa
> (`27 ± 3 s`) o está bien así?

---

## C. Confirmaciones rápidas (si queda tiempo)

- **Beeman**: usamos la variante **predictor-corrector** (diapositiva 20),
  que es la que corresponde a una fuerza con rozamiento, y no la de la
  diapositiva 19. ¿Correcto?
- **ECM del sistema 1**: lo calculamos sobre la **posición** contra `r(t)`
  analítica, en todos los pasos de integración. ¿Esperan que incluya también
  la velocidad?
- **Qué cronometramos en el 2.1.b**: generación de la condición inicial más el
  bucle de integración, **sin** la escritura de archivos, con el mismo
  criterio para el motor del TP3. ¿Sigue valiendo lo acordado?
- **Energía total**: cinética más la elástica de los contactos
  (`Σ ½ k ξ²`), incluidos los de pared y obstáculos. ¿Correcto?
