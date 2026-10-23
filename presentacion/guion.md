# Guion de la presentación final (`TP4SDS.pdf`, 26 diapositivas)

Esta es la presentación **que se expone**: la de Google Slides exportada a
`presentacion/TP4SDS.pdf`. El guion está ordenado por **título de
diapositiva** (no por número) para que siga sirviendo si se reordena el mazo;
entre paréntesis va el número que tiene hoy en el PDF.

`report/guion.md` es el guion de la beamer de `report/presentacion.tex`, que
tiene más diapositivas (una animación por configuración, la energía en Joule,
ε_máx contra Δt y f(v) por instante). Los números son los mismos: salen de
los mismos scripts, y cada uno se puede reproducir con el `make` que se
nombra al lado.

**Antes de exponer**, ver "Revisión del mazo" al final: **falta la diapositiva
de uso de agentes de IA que pide el ítem 2.5 del enunciado**, hay un
reordenamiento recomendado y seis correcciones chicas de texto.

Reparto sugerido (tres expositores, ~12 min): Introducción + Implementación,
Simulaciones + sistema 1 + paso y costo, y de obstáculos en adelante. El que
cierra dice las conclusiones.

---

## Portada (1)

- Billar circular: dinámica molecular **regida por el paso temporal**, TP4 de Simulación de Sistemas. Grupo 10, comisión S2.
- La diferencia con el TP3 es el paradigma: ahí el tiempo avanzaba de evento en evento, acá avanza de a un Δt fijo.

## Introducción (4, separador)

- Qué es el sistema y cómo se modela el contacto.

## Introducción — ecuaciones (5)

- Billar circular de radio R con la pared fija e indeformable y **dos obstáculos fijos** de radio r en (−x_o, 0) y (+x_o, 0); N partículas del mismo radio, todas con rapidez inicial v0 y dirección al azar.
- Sólo interactúan **por contacto**: resorte lineal normal de constante k, que actúa únicamente mientras hay solapamiento ξ > 0. Sin fricción ni disipación, así que el sistema es **conservativo**: eso es lo que después se usa para elegir el paso.
- La pared se trata como una **partícula imagen** fija de radio r centrada en (R + r)·n̂: así la fuerza queda puramente normal y es la misma fórmula que entre partículas. La imagen se recalcula en cada paso porque durante el choque la partícula se corre tangencialmente.
- Una partícula nace **fresca** y pasa a **usada** la primera vez que toca cualquiera de los dos obstáculos; sigue moviéndose igual, N no cambia. Eso es lo que se mide.

## Implementación (6, separador)

## Implementación — UML (7)

- C++17: `Simulation` lleva el paso, `Forces` suma las fuerzas (pares vecinos, obstáculos e imagen de la pared) y `Grid` es la **celda de índice**.
- El contacto alcanza a 2r, así que la celda deja el costo de un paso en **O(N)**: por eso se llegó a N = 700. Esto es lo que explica la diapositiva de tiempos.
- El motor **no calcula observables**: escribe el estado cada Δt₂ y el instante de cada conversión. Todo lo demás es post-proceso en Python.

## Implementación — el bucle (8)

- Lo que hace `step()` una vez, en orden: correr las posiciones, rearmar la grilla, sumar las fuerzas, aplicar Verlet, convertir lo que toque un obstáculo y, cada Δt₂ = n·Δt, escribir el estado.
- El arranque necesita r(−Δt): sale de un Euler en −Δt. De ahí en adelante la recurrencia es explícita, porque la fuerza depende **sólo de las posiciones**.
- La diferencia con el TP3: ahí el bucle decidía cuándo avanzar (el próximo evento de la cola) y acá el paso es siempre Δt. Por eso el costo por paso no depende de cuántos choques haya, y el de eventos sí.

## Simulaciones (9, separador)

## Sistema de partículas — parámetros (10)

- **Fijos**: R = 0,51 m, r = 0,0175 m, m = 0,025 kg, v0 = 1 m/s, k = 10⁴ N/m. πR² = 0,817 m², prácticamente la mesa del TP3: a igual N, la misma densidad, así que los tiempos de las dos implementaciones se comparan directo.
- **Variables**, escritos como intervalo porque son rangos barridos: N ∈ [5, 700], la densidad que le corresponde ρ = N/πR² ∈ [6, 857] partículas/m² (es el parámetro con el que el ítem 2.4 pide los resultados) y x_o ∈ [r, R − r], de obstáculos en contacto entre sí a obstáculos contra la pared.
- **Simulación**: Δt = 5·10⁻⁵ s, que no es del sistema sino de la integración y **se elige en Resultados**; Δt₂ (cada cuánto se guarda el estado) y t_f van por caso, según qué mide cada figura.

## Observables — fresca y usada (11)

- Fresca: azul, nunca tocó un obstáculo. Usada: roja, ya lo tocó. El color es el mismo en todas las animaciones.

## Observables — conversión (12)

- N_u(t), la cantidad de usadas, y F_u(t) = N_u(t)/N, la fracción.
- **t_x es el instante en que la conversión llega al x %**, el que cumple F_u(t_x) = x/100. Los dos observables del trabajo son el mismo con distinto x: **t₉₀** y **t₁₀₀**.

## Observables — energía y error (13)

- Energía total: cinética más la elástica de **todos** los contactos abiertos (partículas, obstáculos y pared), ½kξ² por contacto.
- Error relativo porcentual ε(t) = 100·(E − E₀)/E₀: así el número del eje es el número de la frase con la que se elige el paso ("me quedo con éste porque el error es menor que tanto por ciento").
- Error cuadrático medio: para el sistema 1, contra la solución analítica, promediado sobre **todos** los pasos de integración.

## Resultados (14, separador)

## Evolución del sistema — sistema 1 (hoy la 2; va acá)

- El sistema 1 es el oscilador amortiguado con solución exacta: sirve para **medir** el error de cada esquema. r(t) = A·e^(−γt/2m)·cos(ωt), con ω = √(k/m − γ²/4m²) = 11,93 rad/s, o sea período 0,53 s.
- Las dos cosas son lo mismo con **Δt = 5·10⁻³ s**, el paso más largo del barrido: a la derecha r(t) de los cuatro esquemas con la analítica punteada encima, a la izquierda las cuatro masas moviéndose a la vez, una por esquema.
- **Beeman, Verlet original y Velocity Verlet caen sobre la analítica**: se apartan como mucho 0,9, 1,0 y 6,4 mm sobre una amplitud de 1 m. **Euler predictor-corrector pierde amplitud**: se aparta hasta 15 cm y a 1 s ya está 13 cm por debajo. En la animación es la masa roja, que se queda corta en cada extremo.
- Que Velocity Verlet se superponga **es esperado** aunque pierda un orden: perder un orden es cómo *escala* el error con Δt, no cuánto vale. Con este paso su ECM es 40 veces el de Verlet, y eso son 6 mm contra 1 mm: menos que el grosor del trazo. Los órdenes se ven en la figura siguiente, que es logarítmica.
- Con pasos más cortos Euler se acerca (3 cm con 10⁻³ s) y la figura deja de distinguir nada: por eso el escalar que compara los esquemas es el ECM.
- Ojo al decirlo: la figura muestra los **primeros 2 s** y la animación corre los **5 s** completos.

## ECM vs dt (hoy la 3; va después de la anterior)

- El ECM contra el paso, en doble logarítmica, para los cuatro esquemas. Cada serie ajusta una ley de potencia ECM = c·Δtᵖ: **p = 4,00 (Beeman), 4,02 (Verlet original), 2,04 (Velocity Verlet) y 1,92 (Euler p-c)**. Los exponentes no están escritos en la figura porque el enunciado la pide sin más información que la curva; se dicen.
- Beeman y Verlet van como Δt⁴ y **se superponen**; Velocity Verlet y Euler p-c, un orden menos. Lo que los separa es **con qué velocidad evalúa cada uno a(t + Δt)**, porque acá la fuerza depende de la velocidad: ésas son las dos viñetas de la izquierda. Verlet la despeja (es lineal en v, sale algebraicamente); Velocity Verlet usa la de medio paso, v(t + Δt/2), y eso es lo que le cuesta el orden.
- **Beeman es el mejor**: menor ECM en 8 de los 9 pasos del barrido. A Δt = 10⁻⁴ s hay **ocho órdenes de magnitud** entre Beeman y Euler p-c.
- El último punto de Verlet, en Δt = 10⁻⁵ s, es donde se separa de Beeman: ahí ya no mide el error del esquema sino el **piso de redondeo del doble** (su recurrencia resta dos números casi iguales) y queda 50 veces por encima. Está dibujado como todos los demás porque es una medición; lo único que cambia es que no entra en el ajuste.
- Si preguntan por qué Beeman y no Verlet, que se superponen: lo que los separa es la **constante**, no la pendiente. ECM/Δt⁴ da 330 contra 380, un 15 % más con el mismo paso. Y es toda de la fuerza que depende de la velocidad: con γ = 0 dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).
- Si preguntan por Velocity Verlet: la fórmula de la Teórica necesita f(t + Δt), que necesita v(t + Δt), que es lo que se está calculando. Se puede despejar —pero entonces el esquema **es** Verlet original, no uno nuevo— o evaluar con v(t + Δt/2), que es la única velocidad que hay entre los dos pasos intermedios. Se eligió la segunda para mantener los cuatro esquemas separados; **la cátedra la validó el 19/10**. Las dos están medidas (`make velocity-verlet-variantes`).

## Conservación de la energía (15)

- El sistema es conservativo: E tiene que quedarse en E₀ = N·½mv0² = 3,75 J. Todo lo que se aparta es **error del integrador**, y con eso se elige el paso. N = 300, sin obstáculos.
- En error relativo: **Δt = 2·10⁻⁴ s se va al −0,6 %**, 10⁻⁴ s roza el 0,1 % y **5·10⁻⁵ s se queda en el 0,04 %**. Criterio: el Δt más largo que queda por debajo del **0,1 %**, el más barato con el error aceptado.
- Son 3 de los 7 Δt medidos: 5·10⁻⁴ s sube al 2,6 % y 10⁻³ s al 1100 %, y con cualquiera de los dos adentro estas tres quedaban pegadas al cero. La razón es física: el choque dura τ = π√(μ/k) = 3,5 ms, así que con 10⁻³ s entran **tres pasos por choque** y el resorte no se integra.
- El error no crece sin parar: cada curva deriva en el primer segundo y se estabiliza. Por eso el escalar que resume una corrida es el máximo, ε_máx.
- Verificado en el caso más exigente del trabajo, N = 700 **con** obstáculos: 0,03 %. Con eso queda fijo Δt = 5·10⁻⁵ s para todo el resto.

## Tiempo ejecución (16)

- Mismo problema, dos paradigmas, la misma computadora descargada: 10 realizaciones por N, t_f = 30 s, x_o = r.
- **Paso temporal: t ∝ N^0,88**, casi lineal, porque siempre son 600 000 pasos y la celda de índice deja cada paso en O(N). **Eventos (TP3): t ∝ N^3,52**, porque cada choque rehace parte del calendario y los choques crecen con N. Las punteadas son esos dos ajustes.
- **Se cruzan cerca de N = 470**: por debajo conviene eventos, por arriba conviene paso temporal. A N = 600 los eventos cuestan **2,9 veces más** (42,3 s contra 14,8 s).
- Las barras de desvío están dibujadas pero no se ven: la figura abarca cuatro décadas y σ/⟨t⟩ es como mucho el 4 %, que en logarítmica queda adentro del marcador. **Decirlo**, porque no está escrito en la figura. Y es el desvío entre realizaciones, no el error de la media.
- Si preguntan por qué el desvío es tan chico: con paso fijo todas las realizaciones de un mismo N hacen **exactamente el mismo trabajo** (600 000 pasos, el mismo barrido de celdas); lo único que cambia es la condición inicial. En eventos el trabajo sí depende de la semilla, y por eso ahí el desvío es mayor.

## Animación (17)

- A la izquierda, de qué se habla cuando se barre x_o: los dos obstáculos recorriendo **todo el rango**, de x_o = r (se tocan en el centro, un solo blanco de 4r) a x_o = R − r (tocan la pared). Es el parámetro del ítem que viene.
- A la derecha, una corrida con N = 100 en la **posición óptima**, x_o = 0,20 m: 20 s de simulación, en tiempo real (un cuadro por estado guardado, cada 0,04 s, a 25 cuadros por segundo). Azules frescas, rojas usadas, negros los obstáculos.
- A los 10 s ya hay **75 usadas** con los obstáculos acá, contra 56 con los dos en el centro y 51 contra la pared. Eso es lo que las dos figuras siguientes miden bien.

## F_u en función de t (18)

- Las tres configuraciones típicas juntas, como pide el ítem: N = 100, 15 realizaciones por curva, la banda es ±1 desvío entre realizaciones.
- Misma forma, corrida en el tiempo: el **óptimo llega a 0,9 en 14,8 s**, el centro en 26,5 s y el borde en 31,2 s. El símbolo sobre la línea de 0,9 es ⟨t₉₀⟩ y la barra horizontal, su desvío.
- El óptimo es además el de **menos dispersión**: ±1,7 s contra ±3,4 y ±3,1.
- La cola es larga en los tres: ⟨t₁₀₀⟩ ≈ 2,3·⟨t₉₀⟩. Ninguna realización se quedó sin convertir antes de t_max = 100 s.

## t₉₀ en función de x₀ (19)

- **Sí hay posición óptima**: ⟨t₉₀⟩ cae de 26,5 s en x_o = r a 14,8 s en 0,20 m y vuelve a subir a 31,2 s contra la pared.
- El mínimo es un **plateau ancho**, de 0,15 a 0,35 m: esos puntos empatan dentro del desvío. No es un punto, es una zona.
- Con N = 20 la curva baja entera (menos partículas, más tiempo por partícula, pero menos bloqueo) y **el mínimo cae en el mismo lugar**: la posición óptima no depende de la frecuencia de choques.

## Distribución de f(v) (20)

> **Cambiar la figura de esta diapositiva**: el ítem 2.3 pide "la distribución
> de probabilidad del módulo de la velocidad f(v) **para distintos instantes
> de tiempo, desde t = 0 hasta alcanzar el estado estacionario**", o sea los
> **histogramas**. Hoy la diapositiva muestra la rapidez media contra el
> tiempo, que es un observable de apoyo y no lo que el ítem pide. Va
> `slides-images/slide-26-f-v-vs-t.png` (los cuatro instantes superpuestos) o
> `slides-images/slide-26b-f-v-paneles.png` (los mismos cuatro, uno por panel,
> con el estacionario de fondo en gris). Las dos están hechas: la superpuesta
> compara de un vistazo, la de paneles deja ver cada histograma solo y es el
> formato que la cátedra viene pidiendo.
> La rapidez media conviene dejarla como diapositiva de respaldo, después del
> "Muchas gracias": contesta "¿desde cuándo es estacionario?".

- **f(v) en cuatro instantes**, cada uno un histograma de la bolsa de ese instante (30 realizaciones × 100 partículas = 3000 muestras). Sistema **sin obstáculos**, N = 100.
- En **t = 0** todas tienen |v| = v0: f(v) es una **delta** en 1 m/s que se sale de la figura (mide 11,3 s/m, que es 1 sobre el ancho del intervalo).
- A los **0,15 s** el pico ya se derrumbó a 2,45 s/m —2,7 veces el del estacionario— y apareció la **cola de velocidades bajas**.
- A los **0,5 s** la curva ya cae **sobre la de 30 s**: el transitorio dura medio segundo y de ahí en adelante todas se superponen. Por eso son cuatro instantes y no más.
- f(v) se **ensancha sin que cambie E**: el sistema es conservativo, lo que se redistribuye entre partículas es la energía, no se pierde.
- Cada curva es **un solo histograma de la bolsa** del instante —todas las partículas de todas las realizaciones juntas, como si fuera una única realización grande—, no el promedio de 30 histogramas: el histograma de una realización sola (100 partículas en 40 intervalos) es ruido, y el desvío entre realizaciones en un instante suelto es del 41 %, que taparía la forma. En la gran bolsa baja al 4,8 % y ahí sí va dibujado como barra.

## Rapidez media según t — **pasarla a respaldo**

- Sistema **sin obstáculos**, N = 100, 30 realizaciones. Un escalar por instante: la rapidez media de la bolsa de ese instante, con el desvío entre realizaciones como banda.
- Arranca **exactamente en v0 = 1 m/s** (todas nacen con |v| = v0) y baja hasta 0,88: la energía no cambia —el sistema es conservativo—, pero f(v) se **ensancha**, y la media de |v| no es la raíz de la media de v². Desde 0,4 s ya está en el estacionario y queda plana hasta los 30 s.
- La punteada roja es una **verificación independiente**: Maxwell-Boltzmann en 2D con el k_BT que se ajusta en la diapositiva siguiente predice ⟨|v|⟩ = √(πk_BT/2m) = 0,883 m/s, y lo medido en el estacionario es 0,881 m/s, 0,2 % de diferencia. El ajuste usa la forma entera de f(v); esto usa un solo momento.
- Es la figura que contesta **desde cuándo es estacionario**, que es lo que hace falta para justificar la bolsa del ajuste (t ≥ 10 s). Como diapositiva de respaldo alcanza con eso.

## Ajuste Maxwell-Boltzmann (21)

- A la derecha, la **gran bolsa**: un solo histograma con todos los |v| del estacionario (t ≥ 10 s) de todas las realizaciones, **30 realizaciones × 401 cuadros × 100 partículas = 1,2·10⁶ muestras**, 40 intervalos y área 1. Encima, Maxwell-Boltzmann en 2D con k_BT como único parámetro libre. La barra de cada intervalo es el desvío entre realizaciones: 4,8 %, la misma dispersión que la banda de la figura anterior.
- A la izquierda, cómo se ajusta, a la manera de la Teórica 0: se recorre k_BT en una grilla y se toma el **mínimo del error cuadrático medio** E(k_BT). Da **k_BT = 12,41 mJ**.
- Cada punto azul **es un k_BT probado**: la grilla son 4001 valores entre 2,5 y 30,8 mJ, uno cada 7 µJ, y en cada uno se evalúa el error contra el histograma medido. En la figura va uno de cada 66, porque los 4001 enteros serían una banda maciza (hay casi cuatro por píxel); **decirlo**, porque no está escrito en la figura. No es una curva ajustada ni un método iterativo: es un **barrido**, y el mínimo es el menor de esos valores.
- El **ancho del mínimo es el error del ajuste**: E se duplica ya en 12,31 y 12,53 mJ, o sea 12,41 ± 0,11 mJ, un 0,9 %.
- Las tres energías: la inicial ½mv0² = **12,50 mJ** (exacta, todas arrancan con v0), la del estacionario ½m⟨v²⟩ = **12,32 mJ** y el ajuste **12,41 mJ**, que cae justo entre las dos (−0,7 % y +0,7 %).
- Por qué ½m⟨v²⟩ es 1,4 % menor que ½mv0²: E se conserva, pero no toda es cinética. En promedio ese 1,4 % está en los resortes de los contactos abiertos. Por eso el ajuste no tiene por qué dar exactamente ninguna de las dos.

## Densidad óptima (22)

- Barrido propio del ítem: x_o = r, 10 densidades, 20 realizaciones por punto y cada corrida hasta convertirlas **todas**, sin corte. Por eso todos los puntos tienen desvío.
- **Las dos curvas son una U: hay densidad óptima.** ⟨t₉₀⟩ baja de 66,3 ± 40,3 s en ρ = 6 (N = 5) hasta **21,8 ± 3,0 s en ρ = 86 (N = 70)** y vuelve a subir a 54,3 ± 3,7 s en ρ = 367 (N = 300).
- El fondo es **ancho**: de ρ = 24 a 86 las cuatro densidades dan 22,0, 22,6, 22,3 y 21,8 s, iguales dentro del desvío.
- Por qué sube de los dos lados: **abajo faltan choques** —sin choques cada partícula conserva el momento angular y sólo convierte si su parámetro de impacto es b < 3r; medido con N = 1, convierten 40 de 300 realizaciones, el 13 %—, y **arriba** se achica el camino libre y el blanco queda rodeado por las demás.
- ⟨t₁₀₀⟩ tiene la misma forma pero con el mínimo más abajo (ρ = 24) y crece mucho más rápido: 135 ± 20 s en ρ = 367. El **último 10 %** es el que más castiga la densidad alta, porque las que faltan son justo las que quedaron en órbitas que no pasan por el blanco.
- Si preguntan: **no son las corridas del 2.1.b**. Ésas tienen t_f = 30 s fijo y de N = 200 para arriba no llegaba ninguna realización a F_u = 0,9; con ese corte la figura era plana y no mostraba ninguna densidad óptima, que es justo lo que el ítem pregunta.

## t₉₀ según x₀ y N (23)

- El barrido completo: **16 posiciones × 10 densidades × 20 realizaciones = 3200 corridas**. Hace falta esa resolución para contestar si el óptimo se corre con N o es siempre el mismo.
- La escala está dada vuelta a propósito: **rojo es la conversión más rápida**, porque lo que tiene que saltar a la vista es el óptimo. Está recortada en 38 s; los bordes de las densidades extremas llegan a 70 s y se llevaban media escala.
- La mancha roja **cierra por arriba y por abajo**: hay óptimo en las dos variables. La línea negra une la celda más rápida de cada fila.
- La línea **zigzaguea** porque el fondo del valle es plano y cuál celda sale la más baja es en buena parte azar. Lo que hay que leer: el óptimo cae **siempre entre 0,175 y 0,30 m**, nunca en el centro ni contra la pared. Ajustando una parábola a cada fila, de N = 20 en adelante da **x_o = 0,237 ± 0,011 m**, el mismo para todas; sólo las dos densidades más bajas se corren hacia afuera (N = 5: 0,29 m; N = 10: 0,35 m). El corrimiento global es **−1,8 ± 0,7 cm por década de N**.
- Poner mal los obstáculos **cuesta**: el peor x_o tarda de 1,9 a 4,6 veces el mínimo de su fila.

## Conclusiones (25)

1. Para que el error de la energía quede por debajo del **0,1 %** hace falta **Δt = 5·10⁻⁵ s**: da 0,04 % a N = 300 y 0,03 % en el caso más denso. Con pasos más largos el choque (3,5 ms) no se integra.
2. El paso temporal escala como **N^0,88** y los eventos como **N^3,52**: se cruzan en **N ≈ 470**, así que el paso temporal sólo conviene de ahí para arriba, y a N = 600 ya es 2,9 veces más rápido.
3. Hay **posición óptima** de los obstáculos y **densidad óptima**. El x_o óptimo está siempre entre 0,20 y 0,30 m —nunca en el centro ni contra la pared— y es el mismo para todas las densidades de N = 20 en adelante (0,24 m); poner mal los obstáculos cuesta hasta 4,6 veces más tiempo.
4. (Si se pregunta por el sistema 1) Beeman es el esquema con menor ECM en 8 de los 9 pasos; Verlet original lo iguala en pendiente y se usó en el billar porque ahí la fuerza depende sólo de las posiciones y la diferencia desaparece.

## Uso de agentes de IA — **falta en el mazo**

El ítem **2.5 del enunciado** la pide textual: *"Al finalizar las
presentaciones orales, exponer una diapositiva extra que sirva de base para
explicitar qué agente y modelo se utilizó y de qué manera"*. Va **después de
Conclusiones**, antes del "Muchas gracias". En la beamer está (página 34 de
`SdS_TP4_2026Q2G10S2_Presentación.pdf`); en este mazo hay que agregarla. El
texto, para pegar:

> **Uso de agentes de IA**
>
> - **Agente y modelo**: Claude Code (Anthropic), modelos Claude Opus 5 y Claude Fable 5.1.
> - **En qué se usó**: asistencia en la programación del motor en C++, de los scripts de post-procesamiento en Python y del código de las diapositivas, y revisión de código.
> - **En qué no se usó**: las decisiones de modelado (esquemas, elección de Δt, observables, criterios de ajuste), el análisis de los resultados y las conclusiones son del grupo, a partir de la Teórica 4 y la Teórica 0.
> - Todo lo generado se revisó y se verificó contra las figuras mostradas.

- Al decirlo, que quede claro el límite: **herramienta de programación**, no de análisis. El enunciado lo subraya ("los agentes de IA no pueden reemplazar al proceso de aprendizaje").
- Si preguntan por algo puntual que haya salido del asistente, contestarlo con el número y el `make` que lo reproduce: todo lo que está en las figuras se corrió y se verificó.

## Muchas gracias (26)

---

## Preguntas probables

- **¿Por qué Verlet en el billar si en la figura gana Beeman?** Porque el enunciado del sistema 2 lo dice textual, y porque la ventaja de Beeman se mide en el oscilador, donde la fuerza depende de la velocidad. En el billar la fuerza es el resorte de contacto y depende **sólo de las posiciones**: medido con γ = 0, las constantes de error de los dos son iguales dentro del redondeo.
- **¿Por qué la velocidad de Velocity Verlet es la de medio paso?** Ver la viñeta larga de "ECM vs dt". Consulta validada por la cátedra el 19/10.
- **¿Las barras son el error de la media?** No, son el **desvío estándar entre realizaciones** en todas las figuras del trabajo.
- **¿Por qué la gran bolsa junta cuadros de la misma corrida, que están correlacionados?** Porque lo que hace falta es la **forma** de f(v) en el estacionario, y el promedio temporal de un estado estacionario es el mismo promedio de ensamble. Para los escalares con error (t₉₀, tiempos de ejecución) el promedio es sobre realizaciones independientes.
- **¿Cuántas realizaciones hay en cada figura?** 15 en el barrido de x_o, 30 en velocidades, 20 en densidad y en el mapa, 10 en los tiempos de ejecución.
- **¿Cuánto tarda todo?** El mapa son 3200 corridas; se corrió en paralelo. El resto está en `make todo`.

---

## Revisión del mazo (lo que conviene corregir antes de exponer)

Las imágenes **están todas al día**: las 13 figuras que salen del repositorio
son idénticas a las de `slides-images/`, y los tres GIF son idénticos a
`gif/02`, `gif/05` y `gif/06` (los dos últimos, con las correcciones de hoy).

1. **Falta la diapositiva de uso de agentes de IA**, que el **ítem 2.5 del enunciado pide explícitamente** como diapositiva extra al final. Va después de Conclusiones; el texto está más arriba, en su sección del guion.
2. **Orden**: "Evolución del sistema" y "ECM vs dt" están hoy **antes de Introducción**, y las dos llevan el rótulo *Resultados* arriba a la derecha. Van después del separador **Resultados**, delante de "Conservación de la energía": así Resultados sigue el orden del enunciado (sistema 1 → paso → costo → obstáculos → velocidades → densidad).
3. **"Distribución de f(v)" (20)**: la figura es la rapidez media ⟨|v|⟩ contra el tiempo, y el ítem 2.3 pide **los histogramas de f(v) en distintos instantes, desde t = 0 hasta el estacionario**. Poner `slides-images/slide-26-f-v-vs-t.png` (f(v) en cuatro instantes) y dejar la rapidez media como diapositiva de respaldo después del "Muchas gracias", para contestar desde cuándo es estacionario.
4. **Falta la figura con la que se elige el paso**: la conclusión 1 ("hace falta Δt = 5·10⁻⁵ s") se apoya en ε_máx contra Δt, que es `slides-images/slide-17-error-maximo-vs-dt.png` y no está en el mazo. Con la de la 15 sola se puede decir igual, pero esa figura es la evidencia directa.
5. **"Animación" (17)**: dice `t_max = 100 s`, pero el GIF es de **20 s** de simulación (los 100 s son el t_max del barrido de x_o). Poner `t_f = 20 s`.
6. **"t₉₀ en función de x₀" (19)**: dice `N = 100`, pero la figura tiene **N = 20 y N = 100**.
7. **Conclusión 3**: "a mayor N, un menor x₀" está sobredicho. Lo medido es −1,8 ± 0,7 cm por década de N, y de N = 20 en adelante el óptimo es el mismo dentro del error (0,237 ± 0,011 m); sólo N = 5 y N = 10 se corren hacia afuera. Conviene la redacción de la conclusión 3 de este guion.
8. **Detalles de formato** (la cátedra los marca): coma decimal y unidades en el texto de las diapositivas — `0.1%` → `0,1 %`, `5x10-5` → `5·10⁻⁵ s`, `12.5mJ` → `12,5 mJ`; `K_bT` → `k_BT`; "Tiempo ejecución" → "Tiempo de ejecución".
9. **Opcional**: los dos GIF de la 17 tienen los ejes con distinto estilo, `x (m)` el del barrido y `posición x (m)` el del billar. Se pueden unificar regenerando las animaciones del billar (`make animations`), pero hay que volver a insertar los GIF en las diapositivas.
