# Consultas para la cátedra

Ordenadas por lo que puede costar nota. Cada una tiene **qué preguntar** y
**qué contestamos si nos devuelven la pregunta** (porque siempre la devuelven).

Lo primero, que no es una pregunta: **mostrarles el PDF**. La guía 3.4 dice
que se consulte lo que no quede claro, y las devoluciones del TP2 piden
"mostrar el trabajo intermedio al cuerpo docente antes de presentarlo". Llevar
`SdS_TP4_2026Q2G10S2_Presentación.pdf` abierto y pasarlo mientras se pregunta.

---

## Lo que se contestó en la consulta del 19/10

Idea de fondo que dieron, y que ordena el resto: **lo interesante es tomar
decisiones**, y cada decisión tiene que estar escrita como una viñeta corta, al
lado de lo que decide, para que se puedan comparar. De ahí sale que cada
esquema de integración lleve su "decisión: con qué v evalúa a(t+dt)".

| Consulta | Qué contestaron | Qué se hizo |
|---|---|---|
| **A1** Velocity Verlet | Está bien evaluar con la velocidad de medio paso | Queda como estaba; la decisión va escrita al lado de las ecuaciones de cada esquema |
| **A2** El exponente del ajuste | Si se dibuja la recta de regresión, hay que decir la pendiente | `t ∝ N^0,88` y `N^3,52`, escritos en las viñetas de la diapositiva 17 |
| **A4** `tf = 30 s` del 2.4.a | No hace falta atenerse a las corridas del 2.1.b | Barrido propio (`make densidad`): xo = r, las densidades del mapa, 20 realizaciones, hasta convertirlas todas. Las dos curvas existen en todas las densidades y la U se ve |
| **B3** El observable de la energía | Graficar el error en **porcentaje**, no la energía absoluta | `eps(t) = 100 (E − E0)/E0` y `eps_max` contra dt, las dos en % |
| **B7b** Las barras de error | Desvío, no error de la media (`σ/√M` tiende a cero) | Queda el desvío estándar entre realizaciones |
| **B7** La bolsa de `f(v)` | Un solo histograma con todas las realizaciones juntas | Bolsa de N × M muestras (y × cuadros en el estacionario); en los instantes sin barras (51 %, tapan la curva), en la gran bolsa con el desvío entre realizaciones (4,8 %) |
| **2.4.b** El mapa | Dibujar encima el xo óptimo de cada densidad | Línea negra con opacidad moderada sobre el mapa de calor |
| **Tabla** | Sacar dt2 y tf, corchetes en los intervalos, `10^4` y no `1 × 10^4` | Hecho |
| **Observables** | Definir `t_x` como el que cumple `Fu(t_x) = x/100` | Hecho, con t90 y t100 como los dos casos |

Lo que sigue abajo queda como registro de lo que se preguntó y de lo que se
contesta si vuelven sobre el tema en la defensa.

---

## A. Las que pueden cambiar un resultado o una figura

### A1. Velocity Verlet: ¿despejamos o usamos la velocidad de medio paso? — RESUELTO: la de medio paso

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

**Contestaron que está bien la de medio paso**, que es la que corre. La decisión
queda escrita en la diapositiva de integración, al lado de las ecuaciones de cada
esquema, para que se pueda comparar con la de los otros tres.

**Lo que tenemos medido**, por si lo piden: medio paso `p = 2,04` (orden 1);
despejada `p = 4,00` (orden 2); con la predicción de Euler `p = 4,00`; con
`v(t)` congelada `p = 2,02`. Hoy corre la de medio paso.

---

### A2. ¿El exponente del ajuste tiene que estar escrito en la diapositiva? — RESUELTO: sí

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

**Contestaron que sí**: si se dibuja la recta de regresión hay que decir qué
pendiente dio. Los dos exponentes están ahora en las viñetas.

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

### A4. Ítem 2.4.a: con `t_f = 30 s` casi nadie llega a `F_u = 0,9` — RESUELTO: barrido propio

> El 2.4.a pide tomar los outputs del 2.1.b y reportar `⟨t90⟩` y `⟨t100⟩` en
> función de la densidad. Esas corridas son con los obstáculos en contacto y
> `t_f = 30 s`, y con esa configuración sólo los `N` chicos llegan: a `N = 10`
> llegan 5 de 10 realizaciones, a `N = 20` llegan 8 de 10, y **desde `N = 200`
> no llega ninguna** (`F_u(t_f)` medio: 0,84 a `N = 200` y 0,01 a `N = 700`).
> Informamos `⟨t90⟩` y `⟨t100⟩` donde existen, con símbolo hueco cuando no
> llegan todas, y la escala de la densidad cortada en el último punto medido
> (`ρ = 122`, que es `N = 100`); de ahí para arriba lo único medido es
> `F_u(t_f)`, que tenemos en una figura aparte y decimos de palabra.
> ¿Alcanza así, o esperan que alarguemos `t_f` sólo para este ítem?

**Si preguntan por qué el eje se corta y no se ve el rango completo:** porque
ahí no hay tiempo de conversión que graficar. Lo probamos con flechas de cota
saliendo de `t_f` y eran doce símbolos que no son datos medidos, con la escala
abierta hasta `ρ = 857` para que entraran. `F_u(t_f)` contra la misma densidad
está en `data/figures/2.4_densidad/Fu_tf_vs_densidad_M10.png` y la mostramos si
la piden.

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

### B3. El observable escalar del 2.1.a y la cota, que el enunciado no fija — RESUELTO: en porcentaje

> El 2.1.a pide proponer un observable escalar que caracterice la evolución de
> la energía. Propusimos la **deriva relativa máxima**
> `D(Δt) = máx_t |E(t) − E₀| / E₀`. Pero el enunciado **no da una cota de error
> objetivo**, así que el criterio lo pusimos nosotros: el `Δt` más largo con
> `D ≤ 10⁻³` (0,1 %), que es el más barato con el error aceptado. Nos queda
> `Δt = 5·10⁻⁵ s`, con `D = 3,8·10⁻⁴`. ¿Les parece bien el observable y esa
> cota, o esperan otro criterio?

### B4. La figura de energía muestra 3 de los 7 `Δt` medidos — ACTUALIZADO el 20/10: son dos figuras

Hoy van dos diapositivas: la **evolución del sistema**, `E(t)` en Joule con
4 `Δt` (`5·10⁻⁴`, `2·10⁻⁴`, `10⁻⁴` y `5·10⁻⁵ s`, diapositiva 14), que es lo que
pide el ítem 2.1.a textual, y el **error** `ε(t)` en porcentaje con 3 (sin el
`5·10⁻⁴ s`, que ya se vio despegarse en Joule; diapositiva 15). Lo de abajo es
lo que se preguntó.


> Medimos 7 pasos pero dibujamos 3, los que se leen en una misma escala: uno
> que deriva hacia arriba (`5·10⁻⁴ s`, 2,6 %), uno hacia abajo (`2·10⁻⁴ s`,
> 0,6 %) y el elegido (`5·10⁻⁵ s`), que se queda sobre `E₀`. Con
> `Δt = 10⁻³ s` la energía se dispara a 45 J y aplasta a todas las demás
> contra `E₀`, y `10⁻⁴`, `2·10⁻⁵` y `10⁻⁵` caen encima de `5·10⁻⁵` y no se
> distinguen. El barrido completo está en la figura de la deriva, que es la
> que elige el paso. ¿Está bien mostrar sólo los tres?

### B5. El mapa de calor: cómo decimos dónde está el óptimo — RESUELTO, no hace falta preguntarlo

Era una pregunta cuando el barrido tenía 6 posiciones y 6 realizaciones y el
mínimo de cada fila no se distinguía de sus vecinos. Se corrió de nuevo con
**16 posiciones × 10 densidades × 20 realizaciones** (3200 corridas, cortando
cada una en `Fu = 0,9`, que es lo único que mide el mapa) y ahora sí se
resuelve:

- El fondo del valle es ancho: entre `x_o = 0,15` y `0,30 m`, `⟨t90⟩` queda
  dentro del 20 % del mínimo de su fila.
- Ajustando una parábola a cada fila **sobre el mismo tramo** (`0,10`–`0,40 m`)
  y tomando el vértice: de `N = 20` a `N = 300` (ocho densidades) da
  `0,237 ± 0,011 m`. **En todo ese rango el óptimo no se corre con `N`.**
- Las dos densidades más bajas sí se corren hacia afuera (`0,287 ± 0,020 m` en
  `N = 5` y `0,350 ± 0,031 m` en `N = 10`), y tiene explicación física: casi no
  hay choques y la conversión la decide el parámetro de impacto, que es el
  mismo argumento del ítem 2.4.a.

Lo que la cátedra pidió el 19/10 (dibujar encima el `x_o` óptimo de cada
densidad) va como una línea negra que une la **celda más baja de cada fila**,
calculada de los datos. Zigzaguea dentro del fondo del valle porque cuál de las
celdas del fondo sale la más baja es azar (a `N = 50` cae en `0,175 m` y a
`N = 150` en `0,275 m`, con el mismo vértice dentro del error); el número fino,
`0,237 ± 0,011 m`, sale del ajuste de la parábola y va en la viñeta, no
dibujado.

### B6. La explicación de la densidad óptima, ¿necesita figura propia?

> En el 2.4.a decimos que hay densidad óptima porque sin choques cada
> partícula conserva el momento angular respecto del centro y no llega a los
> obstáculos: lo probamos con una corrida dedicada de `N = 1`, donde convierten
> 40 de 300 realizaciones (13 %), exactamente las de parámetro de impacto
> `b < 3r`. Está como viñeta, sin figura. La guía 2.5 dice que una hipótesis
> que explique lo observado tiene que estar probada y **mostrada en
> resultados**. ¿Hace falta una figura, o alcanza con decirlo?

### B7. `f(v)` estacionaria: cómo juntamos las muestras — RESUELTO: una sola bolsa

> Para la distribución estacionaria juntamos **todos los cuadros con
> `t ≥ 10 s`** de las 30 realizaciones. Los cuadros de una misma realización
> están correlacionados entre sí. ¿Está bien juntarlos así, o esperan un solo
> instante por realización?

### B7b. Las barras de error: ¿desvío estándar o error de la media? — RESUELTO: el desvío

> En **todas** las figuras que promedian sobre realizaciones —`f(v)` intervalo
> por intervalo, `⟨t90⟩`, el tiempo de ejecución— la barra es el **desvío
> estándar muestral entre realizaciones** (`ddof = 1`), sin dividir por `√M`.
> Lo elegimos así porque el enunciado dice "incluyendo su desvío estándar" y
> porque σ describe la dispersión de **una** corrida, que es lo que se informa
> junto al promedio. ¿Es lo que esperan, o prefieren el error de la media
> (`σ/√M`)?

**Por qué preguntarlo una sola vez para todas:** es la misma convención en
todo el trabajo, así que la respuesta cambia varias figuras a la vez, no una.
Con `σ/√M` las barras quedarían entre 3 y 5,5 veces más chicas (`√10` en los
tiempos y en la densidad, `√30` en `f(v)`), y en la figura de tiempos de
ejecución, donde ya hoy no se ven, desaparecerían del todo.

**Lo que da en `f(v)`**: en un instante suelto el desvío es del 51 % de cada intervalo
(cada realización reparte sus 100 partículas en 40 intervalos); en la
estacionaria, que junta todos los cuadros desde `t = 10 s`, baja al 4,8 %. Las
dos figuras dibujan la barra con el mismo estilo, justamente para que esa
diferencia de tamaño se lea como lo que es.

### B8. El enunciado dice `m⟨v²⟩/2 = m v₀²/2`, y nos dan distinto

> El 2.3 pide comparar el `k_BT` ajustado con `m⟨v²⟩/2 = m v₀²/2`. En la
> simulación esas dos **no** son iguales: nos da `m⟨v²⟩/2 = 12,32 mJ` contra
> `m v₀²/2 = 12,50 mJ`, un 1,4 % menos, porque en el estacionario parte de la
> energía está guardada en los resortes de los contactos (el sistema conserva
> la energía total, no la cinética). El ajuste da `k_BT = 12,41 mJ`, entre las dos.
> ¿Es eso lo que esperan que discutamos?

### B9. Cifras significativas del error

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
- **Verlet para el billar**: lo usamos porque el enunciado del sistema 2 lo
  pide textualmente, aunque en el sistema 1 gane Beeman. La ventaja de Beeman
  es con fuerza dependiente de la velocidad; en el billar la fuerza depende
  sólo de las posiciones y la diferencia desaparece (con `γ = 0` las dos
  constantes del error coinciden). ¿Está bien el razonamiento?
