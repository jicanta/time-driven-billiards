# Guion de la presentación final (`TP4SDS.pdf`)

Esta es la presentación **que se expone**: la de Google Slides exportada a
`presentacion/TP4SDS.pdf`. El guion va ordenado por **título de diapositiva**
para que siga sirviendo si se reordena el mazo (los números del PDF del 22/10
ya no coinciden con el mazo de hoy: hay una diapositiva más antes de
"Densidad óptima").

**El enunciado da 13 minutos.** Lo que está escrito para decir, leído en voz
alta a ritmo normal, son **11:50**: queda un minuto para los cambios de
expositor y para que corra la animación. Ensayar con cronómetro; si pasa de
12:30, cortar los números de respaldo (apartamientos en mm, pendientes,
porcentajes de la energía que no son el elegido). Lo que no se dice (números de
respaldo, por qué se decidió cada cosa) está al final, en "Si preguntan",
ordenado por diapositiva.

**Reparto**, tres expositores, parejo como pide la guía (§3.2):

- **Expositor 1 (4:05)**: Portada, Introducción, Implementación, Simulaciones y
  el sistema 1 (posición y ECM).
- **Expositor 2 (4:05)**: Conservación de la energía, tiempo de ejecución,
  animación, F_u(t), t₉₀ contra x_o y la distribución f(v).
- **Expositor 3 (3:40)**: ajuste de Maxwell-Boltzmann, densidad óptima, mapa,
  Conclusiones y uso de IA.

**Antes de exponer**, ver "Revisión del mazo" al final.

---

## Portada — 0:10

- Somos el grupo 10. Billar circular: dinámica molecular **regida por el paso temporal**. La diferencia con el TP3 es el paradigma: el tiempo no avanza de evento en evento sino de a un Δt fijo.

## Introducción (separador + ecuaciones) — 0:45

- Billar circular de radio R, pared fija, y **dos obstáculos fijos** de radio r en (−x_o, 0) y (+x_o, 0). N partículas del mismo radio, todas con rapidez v0 y dirección al azar.
- Interactúan **sólo por contacto**: un resorte lineal normal de constante k, activo mientras hay solapamiento ξ > 0. Sin fricción ni disipación: el sistema es **conservativo**, y con eso elegimos después el paso.
- La pared es una **partícula imagen** fija de radio r centrada en (R + r)·n̂, recalculada en cada paso: la misma fuerza, puramente normal.
- Una partícula nace **fresca** y pasa a **usada** la primera vez que toca un obstáculo; sigue moviéndose igual, N no cambia.

## Implementación (separador + UML + bucle) — 0:45

- Motor en C++: `Simulation` lleva el paso, `Forces` suma las fuerzas (pares vecinos, obstáculos e imagen de la pared) y `Grid` es la **celda de índice**. El contacto alcanza a 2r, así que cada paso cuesta **O(N)**: por eso llegamos a N = 700.
- El motor **no calcula observables**: escribe el estado cada Δt₂ y el instante de cada conversión; el resto es post-proceso.
- El bucle: correr las posiciones, rearmar la grilla, sumar fuerzas, Verlet, convertir lo que tocó un obstáculo y, cada Δt₂, escribir. El arranque necesita r(−Δt), que sale de un Euler hacia atrás.
- El paso es **fijo**: el bucle siempre avanza Δt, no decide cuándo. Por eso el costo por paso no depende de cuántos choques haya.

## Sistema de partículas (parámetros) — 0:30

- **Fijos**: R = 0,51 m, r = 0,0175 m, m = 0,025 kg, v0 = 1 m/s, k = 10⁴ N/m. El área, 0,817 m², es la de la mesa del TP3: a igual N, la misma densidad.
- **Variables**: N de 5 a 700, o sea ρ de 6 a 857 partículas por m², y x_o de r a R − r: de obstáculos en contacto entre sí a obstáculos contra la pared.
- Δt = 5·10⁻⁵ s no es del sistema sino de la integración, y **se elige en Resultados**.

## Observables (tres diapositivas) — 0:30

- Fresca azul, usada roja. N_u(t) es la cantidad acumulada de usadas y F_u = N_u/N la fracción. **t_x es el instante en que F_u llega a x/100**: medimos t₉₀ y t₁₀₀.
- Energía total: cinética más la elástica de **todos** los contactos abiertos, y su error relativo porcentual ε(t) respecto de E₀.
- Para el sistema 1, el error cuadrático medio contra la analítica, promediado sobre todos los pasos.
- Todo promedio es sobre M realizaciones y **la barra es el desvío estándar entre ellas**.

## Evolución del sistema — sistema 1 — 0:35

- Resultados. El sistema 1 es el oscilador amortiguado con solución exacta: sirve para **medir** el error de cada esquema.
- r(t) de los cuatro esquemas con **Δt = 5·10⁻³ s**, el paso más largo del barrido, y la analítica encima.
- **Beeman, Verlet original y Velocity Verlet caen sobre la analítica**: se apartan como mucho 1, 1 y 6 mm sobre 1 m de amplitud. **Euler predictor-corrector pierde amplitud**: hasta 15 cm, y a 1 s ya está 13 cm por debajo.

## ECM vs dt — 0:50

- El ECM contra el paso, en doble logarítmica, con una ley de potencia ajustada a cada serie. **Beeman y Verlet original van como Δt⁴** (pendientes 4,00 y 4,02) y se superponen; **Velocity Verlet y Euler predictor-corrector, como Δt²** (2,04 y 1,92), un orden menos.
- Lo que los separa es **con qué velocidad evalúa cada uno a(t + Δt)**, porque acá la fuerza depende de la velocidad: Verlet la despeja, que es lineal en v; Velocity Verlet usa la de medio paso, y eso le cuesta el orden.
- **Beeman es el mejor**: menor ECM en 8 de los 9 pasos. El último punto de Verlet, en 10⁻⁵ s, ya mide el **piso de redondeo** y no entra en el ajuste.

## Conservación de la energía — 0:50

- Para el billar el enunciado fija Verlet, y el paso lo elige la energía. N = 300 sin obstáculos: E tiene que quedarse en E₀ = 3,75 J; lo que se aparta es **error del integrador**.
- En error relativo: **2·10⁻⁴ s se va al −0,6 %**, 10⁻⁴ s roza el 0,1 % y **5·10⁻⁵ s se queda en el 0,04 %**. Son tres de los siete pasos medidos: con 10⁻³ s el error es del 1100 %, porque el choque dura 3,5 ms y entran **tres pasos por choque**.
- El escalar es ε_máx, el error máximo de la corrida, y el criterio, el Δt **más largo** por debajo del 0,1 %: **5·10⁻⁵ s**. Verificado a N = 700 con obstáculos: 0,03 %.

## Tiempo de ejecución — 0:50

- Mismo problema, dos paradigmas, la misma computadora descargada: x_o = r, t_f = 30 s, 10 realizaciones por N.
- **Paso temporal: t ∝ N^0,88**, casi lineal, porque siempre son 600 000 pasos y la celda deja cada paso en O(N). **Eventos, el TP3: N^3,52**, porque cada choque rehace parte del calendario y los choques crecen con N.
- **Se cruzan cerca de N = 470**: a N = 600 los eventos cuestan **2,9 veces más**, 42 s contra 15.
- Las barras son el **desvío estándar de las 10 realizaciones**: están dibujadas, pero valen como mucho el 4 % del tiempo medio y en cuatro décadas logarítmicas quedan adentro del símbolo.

## Animación — 0:25

- A la izquierda, el barrido de x_o: los obstáculos van de tocarse en el centro a tocar la pared.
- A la derecha, N = 100 en la **posición óptima**, x_o = 0,20 m, 20 s en tiempo real: azules frescas, rojas usadas.
- A los 10 s ya hay **75 usadas**, contra 56 con los obstáculos en el centro y 51 contra la pared.

## F_u en función de t — 0:35

- Las tres configuraciones típicas: N = 100, 15 realizaciones por curva, banda de ±1 desvío.
- Misma forma, corrida en el tiempo: el **óptimo llega a 0,9 en 14,8 s**, el centro en 26,5 s y el borde en 31,2 s. El símbolo sobre la línea de 0,9 es ⟨t₉₀⟩ con su desvío.
- **Ninguna realización se quedó sin convertir** antes de t_max = 100 s, y la cola es larga: ⟨t₁₀₀⟩ es 2,3 veces ⟨t₉₀⟩.

## t₉₀ en función de x₀ — 0:40

- **Sí hay posición óptima**: ⟨t₉₀⟩ cae de 26,5 s en x_o = r a 14,8 s en 0,20 m y vuelve a 31,2 s contra la pared.
- El mínimo es un **plateau**, de 0,15 a 0,35 m: esos puntos empatan dentro del desvío.
- Con N = 20, muchos menos choques, la curva baja entera y **el mínimo cae en la misma zona**: la posición óptima no depende de la frecuencia de choques, es geométrica.

## Distribución de f(v) — 0:45

- Sistema **sin obstáculos**, N = 100, 30 realizaciones. Cada curva es **un solo histograma** con las 100 partículas de las 30 realizaciones juntas: 3000 muestras por instante.
- En **t = 0** todas tienen |v| = v0: f(v) es una **delta** que se sale de la figura. A los **0,15 s** el pico ya bajó a 2,7 veces el del estacionario y apareció la cola.
- A los **0,5 s** la curva ya cae **sobre la de 30 s**: el transitorio dura medio segundo. Y f(v) se **ensancha sin que cambie E**: lo que se redistribuye es la energía, no se pierde.

## Ajuste Maxwell-Boltzmann — 1:00

- La estacionaria es **la de t = 30 s**, el último instante: las 100 partículas de las 30 realizaciones en un solo histograma, 3000 muestras. Lo dice la leyenda.
- Encima, Maxwell-Boltzmann en 2D, f(v) = (mv/k_BT)·exp(−mv²/2k_BT), con **k_BT como único parámetro libre**.
- Ajuste a la manera de la Teórica 0: se recorre k_BT en una grilla y se toma el **mínimo del error cuadrático medio** E(k_BT), la figura de la izquierda. Da **k_BT = 12,45 mJ**; el ancho del mínimo es el error: ± 1,04 mJ, un 8 %.
- La comparación que pide el ítem: ½mv0² = **12,50 mJ**, un 0,4 % más. El ½m⟨v²⟩ medido es 12,35 mJ, un poco menos: E se conserva, pero el 1,2 % está en promedio en los resortes de los contactos abiertos. El ajuste cae entre las dos, y las dos dentro de su error.

## Densidad óptima — 0:50

- Obstáculos en el centro, x_o = r: 10 densidades, 20 realizaciones por punto y cada corrida **hasta convertirlas todas**.
- **Las dos curvas son una U: hay densidad óptima.** ⟨t₉₀⟩ baja de 66 s en ρ = 6 a **21,8 s en ρ = 86** (N = 70) y vuelve a 54 s en ρ = 367. El fondo es **ancho**: de ρ = 24 a 86 empatan dentro del desvío.
- **Abajo faltan choques**: sin choques una partícula sólo convierte si su parámetro de impacto es menor que 3r, y con N = 1 convierte el 13 %. **Arriba** se achica el camino libre y el blanco queda rodeado.
- ⟨t₁₀₀⟩ tiene la misma forma y sube mucho más rápido: 135 s en ρ = 367. El último 10 % es el que más castiga la densidad alta.

## t₉₀ según x₀ y N — 0:50

- El mapa junta las dos preguntas: ⟨t₉₀⟩ para cada posición y cada densidad, **3200 corridas**. Rojo es más rápido; la **línea negra** une la celda más rápida de cada densidad.
- La mancha roja **cierra por arriba y por abajo**: hay óptimo en las dos variables.
- La línea zigzaguea porque el fondo del valle es plano, pero el óptimo cae **siempre entre 0,175 y 0,30 m**, nunca en el centro ni contra la pared: ajustando una parábola a cada fila, de N = 20 en adelante da **x_o = 0,237 ± 0,011 m, el mismo para todas**. Sólo N = 5 y 10 se corren hacia afuera, donde manda el parámetro de impacto.
- Poner mal los obstáculos **cuesta**: el peor x_o de cada fila tarda de 1,9 a 4,6 veces el mínimo.

## Conclusiones — 0:45

1. Beeman y Verlet original van como Δt⁴, Velocity Verlet y Euler predictor-corrector como Δt²: **Beeman es el mejor** para el oscilador.
2. Por conservación de la energía, **Δt = 5·10⁻⁵ s**: error del 0,04 % a N = 300 y 0,03 % a N = 700.
3. El paso temporal escala como **N^0,88** y los eventos como **N^3,52**: se cruzan en N ≈ 470, y a N = 600 el paso temporal es 2,9 veces más rápido.
4. Hay **posición óptima**, entre 0,2 y 0,3 m, la misma de N = 20 a 300; con los obstáculos en el centro hay **densidad óptima**, ρ = 86 con ⟨t₉₀⟩ = 21,8 s.
5. f(v) llega a Maxwell-Boltzmann en medio segundo, con **k_BT = 12,45 ± 1,04 mJ**, a 0,4 % de ½mv0².

## Uso de agentes de IA — 0:15

- Usamos **Claude Code (Anthropic), modelos Claude Opus 5 y Claude Fable 5.1**, como asistente de programación: el motor en C++, los scripts de post-proceso y el código de las diapositivas, y revisión de código.
- Las decisiones de modelado, el análisis y las conclusiones son del grupo, a partir de la Teórica 4 y la Teórica 0.

## Muchas gracias

---

## Si preguntan (no se dice; por diapositiva)

### Sistema 1

- **¿Por qué Verlet en el billar si en la figura gana Beeman?** Porque el enunciado del sistema 2 lo pide, y porque la ventaja de Beeman se mide en el oscilador, donde la fuerza depende de la velocidad. En el billar la fuerza es el resorte de contacto y depende **sólo de las posiciones**: medido con γ = 0, las constantes del error de los dos (ECM/Δt⁴) dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`). Con γ = 100 dan 330 contra 380: Verlet mide un 15 % más de ECM con el mismo paso, y toda la diferencia es de la fuerza que depende de v.
- **¿Por qué Velocity Verlet usa la velocidad de medio paso?** La fórmula de la Teórica necesita f(t + Δt), que necesita v(t + Δt), que es lo que se está calculando. Se puede despejar, pero entonces el esquema **es** Verlet original; o evaluar con v(t + Δt/2), la única velocidad que hay entre los dos pasos intermedios. Se eligió la segunda para mantener los cuatro esquemas separados; **la cátedra la validó el 19/10**. Las dos están medidas (`make velocity-verlet-variantes`).
- **¿Por qué Velocity Verlet se superpone en r(t) si pierde un orden?** Perder un orden es cómo *escala* el error con Δt, no cuánto vale. Con Δt = 5·10⁻³ s su ECM es 40 veces el de Verlet, y eso son 6 mm contra 1 mm: menos que el grosor del trazo.
- **¿Por qué el último punto de Verlet se separa?** Su recurrencia resta dos números casi iguales: en 10⁻⁵ s mide el piso de redondeo del doble y queda 50 veces por encima de Beeman. Está dibujado como los demás; sólo no entra en el ajuste.
- La figura de r(t) muestra los **primeros 2 s** de t_f = 5 s; ω = 11,93 rad/s, período 0,53 s.

### Energía

- El error **no crece sin parar**: cada curva deriva en el primer segundo y se estabiliza. Por eso el escalar es el máximo, ε_máx, y ajusta ε_máx ∝ Δt^2,0.
- τ = π·√(μ/k) = 3,5 ms es la duración de un choque con la masa reducida μ = m/2.

### Tiempo de ejecución

- **¿Las barras son el error de la media?** No: son el desvío estándar muestral entre las 10 realizaciones (varianza con M − 1), **sin dividir por √M**. Es lo que la cátedra pidió el 19/10 (B7b): el error de la media tiende a cero con M. Vale como mucho el 4 % del tiempo medio en paso temporal; el rango completo (máx − mín) llega al 7 % en paso temporal y al 12 % en eventos.
- **¿Por qué el desvío es tan chico?** Con paso fijo todas las realizaciones de un mismo N hacen **exactamente el mismo trabajo** (600 000 pasos, el mismo barrido de celdas); sólo cambia la condición inicial. En eventos el trabajo sí depende de la semilla, y por eso ahí el desvío es mayor.
- Más una medición de calentamiento por N, descartada: paga el arranque en frío del proceso.

### Obstáculos

- El óptimo es además el de **menos dispersión**: ±1,7 s contra ±3,4 (centro) y ±3,1 (borde).
- Con N = 20 el mínimo medido cae en 0,25 m (11,7 s), empatado con 0,20 m (11,7 s); con N = 100, en 0,20 m (14,8 s). El plateau de N = 100 va de 0,15 a 0,35 m.
- La animación de la derecha es de **20 s** de simulación (un cuadro por estado guardado, cada 0,04 s, a 25 cuadros por segundo); los 100 s son el t_max del barrido.

### Velocidades

- **¿Por qué un solo histograma y no el promedio de 30 con su desvío?** Porque el histograma de una realización sola (100 partículas en 40 intervalos) es ruido: el desvío entre realizaciones en un instante es del **51 %** por intervalo y taparía la forma. Juntar las 30 en una bolsa reemplaza al promedio de 30 histogramas con su dispersión (es lo que pidió la cátedra el 19/10, B7), y por eso no lleva barra.
- **¿Por qué el ajuste es sobre un solo instante, t = 30 s?** Porque es lo que pide el ítem: f(v) en instantes, promediando sobre realizaciones, y "la distribución estacionaria obtenida" es la del último. Un promedio sobre cuadros de la misma corrida no es un instante y el enunciado no lo pide. **Si preguntan cuánto cambia con más estadística** (sólo si preguntan): juntando todos los cuadros de t = 10 a 30 s, 1,2·10⁶ muestras, el ajuste da 12,41 ± 0,11 mJ y el desvío entre realizaciones baja al 4,8 %; el valor es el mismo dentro del error del instante. Lo imprime `make velocidades-figuras`.
- **¿Por qué 30 s de simulación si el estacionario llega en medio segundo?** Porque que f(v) a los 30 s sea la misma que a los 0,5 s es la prueba de que es estacionario y no una deriva lenta; con N = 100 son segundos de cómputo.
- **Desde cuándo es estacionario** (figura de respaldo, rapidez media contra t): arranca exactamente en v0 = 1 m/s y baja hasta 0,88 m/s, estacionaria desde 0,4 s y plana hasta los 30 s. Verificación independiente: Maxwell-Boltzmann con el k_BT ajustado predice ⟨|v|⟩ = √(πk_BT/2m) = 0,884 m/s; medido, 0,881 (0,4 %).
- La grilla del ajuste son 4001 valores de k_BT entre 2,5 y 30,8 mJ, uno cada 7 µJ; en la figura va uno de cada 66 para que se lea como el barrido que es. El error "se duplica" en 11,46 y 13,54 mJ.
- El pico de la delta en t = 0 mide 11,3 s/m (1 sobre el ancho del intervalo); a 0,15 s, 2,45 s/m.

### Densidad y mapa

- **¿No había que usar las corridas del 2.1.b?** Ésas tienen t_f = 30 s fijo y de N = 200 para arriba no llegaba ninguna realización a F_u = 0,9; con ese corte la figura era plana y no mostraba ninguna densidad óptima. La cátedra aceptó el barrido propio (consulta A4, 19/10): misma configuración (x_o = r) y mismas densidades que la columna x_o = r del mapa.
- Valores: 66,3 ± 40,3 s (ρ = 6), 22,0 / 22,6 / 22,3 / 21,8 s de ρ = 24 a 86, 54,3 ± 3,7 s (ρ = 367). ⟨t₁₀₀⟩: mínimo 36,3 s en ρ = 24, 135 ± 20 s en ρ = 367.
- La prueba de "abajo faltan choques": N = 1 conserva el momento angular respecto del centro y sólo convierte si b < 3r; en 300 realizaciones convierten 40 (13 %).
- El mapa tiene la escala cortada en 38 s; los bordes de las densidades extremas llegan a 70 s. t_max = 300 s, porque con N = 5 hay realizaciones que tardan 150 s en convertir las cinco.
- El corrimiento del óptimo con la densidad es **−1,8 ± 0,7 cm por década de N**: de N = 20 en adelante es el mismo dentro del error; N = 5 da 0,29 m y N = 10, 0,35 m (vértices de las parábolas).
- **¿Cuántas realizaciones hay en cada figura?** 15 en el barrido de x_o, 30 en velocidades, 20 en densidad y en el mapa, 10 en los tiempos de ejecución.

---

## Revisión del mazo (contra el PDF exportado el 22/10)

Las imágenes estaban todas al día en esa exportación, salvo las dos del
ajuste, que **hoy cambiaron**: el ajuste es ahora sobre el instante t = 30 s
(leyenda "simulación, t = 30 s, 30 realizaciones") y E(k_BT) con él. Volver a
pegar `slides-images/slide-27-f-v-gran-bolsa-ajuste.png` y
`slides-images/slide-28-E-vs-kT.png`, y los números: k_BT = 12,45 ± 1,04 mJ.

1. **Falta la diapositiva de uso de agentes de IA**, que el ítem 2.5 del enunciado pide como diapositiva extra al final. Va después de Conclusiones; el texto está en su sección del guion.
2. **Orden**: "Evolución del sistema" y "ECM vs dt" estaban **antes de Introducción**, con el rótulo *Resultados*. Van después del separador Resultados, delante de "Conservación de la energía".
3. **Sistema 1 sin animación**: el enunciado dice textual "no mostrar animaciones, ni introducción, ni ninguna otra información" para el sistema 1. La cátedra pidió después (21/10 y 22/10) agregar r(t) contra el tiempo, pero no una animación: el GIF de los cuatro resortes en "Evolución del sistema" conviene sacarlo y dejar la figura de r(t) sola, como en la beamer.
4. **"Distribución de f(v)"**: el ítem 2.3 pide los **histogramas de f(v) en distintos instantes**. Si la diapositiva todavía muestra la rapidez media contra t, poner `slides-images/slide-26-f-v-vs-t.png` (o `slide-26b-f-v-paneles.png`) y dejar la rapidez media como respaldo después del "Muchas gracias".
5. **Falta la figura con la que se elige el paso**: la conclusión 2 se apoya en ε_máx contra Δt (`slides-images/slide-17-error-maximo-vs-dt.png`). Con la de energía sola se puede decir igual, pero esa es la evidencia directa.
6. **"Animación"**: decía `t_max = 100 s`; el GIF es de **20 s** de simulación. Poner `t_f = 20 s`.
7. **"t₉₀ en función de x₀"**: decía `N = 100`; la figura tiene **N = 20 y N = 100**.
8. **Conclusiones**: "a mayor N, un menor x₀" está sobredicho (lo medido es −1,8 ± 0,7 cm por década, el mismo óptimo de N = 20 en adelante). Usar las cinco de este guion: incluyen la del sistema 1 y la de Maxwell-Boltzmann, que faltaban.
9. **"Muchas gracias"**: la guía (§2.6) dice que no se escribe "¿Preguntas?" en la diapositiva de cierre. Sacarlo.
10. **Formato** (la cátedra lo marca): coma decimal y unidades, `0.1%` → `0,1 %`, `5x10-5` → `5·10⁻⁵ s`, `12.5mJ` → `12,5 mJ`; `K_bT` → `k_BT`; "Tiempo ejecución" → "Tiempo de ejecución"; "t90 Según x0 y N" → "t₉₀ según x₀ y N".
11. **Cada figura con sus condiciones al costado** (guía §1.7): tiempo de ejecución (x_o = r, t_f = 30 s, 10 realizaciones por N), densidad óptima (x_o = r, 20 realizaciones, hasta convertirlas todas), mapa (3200 corridas, t_max = 300 s), Maxwell-Boltzmann (N = 100, sin obstáculos, t = 30 s, 30 realizaciones, 3000 muestras).
