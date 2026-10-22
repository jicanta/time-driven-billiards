# Guion de la presentación

Dos o tres puntos para decir en cada diapositiva. El número es el del pie de
la diapositiva (el mismo con el que están numeradas las figuras en
`slides-images/`). Las cifras son las de las figuras mostradas.

Éste es el guion de la **beamer** de `report/presentacion.tex`. La
presentación que se expone es `presentacion/TP4SDS.pdf` y su guion está en
`presentacion/guion.md`: tiene menos diapositivas y otro orden, con los
mismos números.

## Portada

- Billar circular: dinámica molecular regida por el paso temporal, TP4 de Simulación de Sistemas.
- Grupo 10, comisión S2.

## 1. Introducción (separador)

- Qué es el sistema y cómo se modela el contacto; después implementación, simulaciones y resultados.

## 2. Sistema — `slide-02-sistema.png`

- Billar circular de radio R con pared fija y dos obstáculos fijos de radio r en (±xo, 0); N partículas del mismo radio con rapidez v0 y dirección al azar.
- Sólo interactúan por contacto, sin fricción ni disipación: el sistema es conservativo.
- Una partícula nace fresca y pasa a usada la primera vez que toca un obstáculo; sigue moviéndose igual, N no cambia. Eso es lo que medimos.

## 3. Modelo: contacto elástico y pared como partícula imagen — `slide-03-modelo-pared-imagen.png`

- Newton con un resorte lineal normal que actúa sólo mientras hay solapamiento ξ > 0, contra las otras partículas y contra los dos obstáculos fijos.
- La pared se trata como una partícula virtual fija de radio r en (R + r) n̂, que toca la pared en el punto C: la fuerza queda puramente normal.
- La imagen se recalcula en cada paso porque durante el choque la partícula se desplaza tangencialmente.

## 4. Implementación (separador)

- Cómo se integran las ecuaciones y cómo está armado el motor.

## 5. Integración de las ecuaciones de movimiento

- Para el billar, Verlet original: paso fijo Δt, la fuerza depende sólo de las posiciones, el estado se guarda cada Δt2 = n·Δt.
- Si preguntan "¿por qué Verlet si en la figura gana Beeman?": primero, porque el enunciado del sistema 2 dice textual "utilizar el esquema de Verlet". Y además, la ventaja de Beeman se mide en el oscilador, donde la fuerza depende de la velocidad; en el billar la fuerza es el resorte de contacto y depende **sólo de las posiciones**, así que esa diferencia desaparece. Lo tenemos medido: con γ = 0 las constantes del error de los dos dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).
- Para el oscilador (sistema 1), además Velocity Verlet, Beeman y Euler predictor-corrector.
- En el oscilador la fuerza depende de la velocidad: los esquemas difieren en con qué v evalúan a(t + Δt), y de ahí sale el orden de cada uno.
- **Cada esquema lleva escrita su decisión**, media línea en gris debajo de sus ecuaciones: Verlet original la v despejada, Velocity Verlet la de medio paso v(t + Δt/2), Beeman la predicha y Euler p-c la de Euler, cada una con el orden que da. Señalar esas cuatro líneas: es lo que se compara, y lo que explica las dos figuras del sistema 1 (diapositivas 13 y 14) antes de mostrarlas. Lo que cambia de un esquema a otro no son las ecuaciones sino **esa elección**.
- Si preguntan por Velocity Verlet (es la pregunta más probable de esta diapositiva): la fórmula de la Teórica es v(t + Δt) = v(t) + (Δt/2m)(f(t) + f(t + Δt)), y f(t + Δt) necesita v(t + Δt), que es lo que la ecuación está calculando. Queda implícita y hay dos salidas razonables.
- Una es despejar v(t + Δt) —se puede, f es lineal en v, igual que en Verlet original—. Da segundo orden, pero el esquema que queda **es** Verlet original: sumando pasos consecutivos de las dos fórmulas se llega a la recurrencia de Verlet y a su velocidad centrada, sin usar de qué depende f. O sea que quedarían 3 esquemas distintos en vez de 4.
- La otra, la que corre, es evaluar f(t + Δt) con v(t + Δt/2), la única velocidad que aparece entre los dos pasos intermedios de la diapositiva 17 de la Teórica 4. Mantiene los cuatro esquemas separados y cuesta un orden: ECM ∝ Δt^2,04 en vez de Δt⁴, porque v(t + Δt/2) se aparta de v(t + Δt) en O(Δt) y ese error entra en f(t + Δt) multiplicado por Δt/2. Beeman no lo pierde porque su predictor es de O(Δt²).
- Honestidad: ninguna de las dos es "la correcta" a priori; se consultó y la cátedra validó la de medio paso el 19/10 (consulta A1). Si preguntan, se dice así. Las dos están medidas (`make velocity-verlet-variantes`).

## 6. Motor de simulación — `slide-06-motor-uml.png`

- C++17: Simulation lleva el paso, Forces suma las fuerzas (pares vecinos, obstáculos, imagen de la pared) y Grid es la celda de índice.
- El contacto alcanza a 2r, así que la celda deja el costo de un paso en O(N): por eso llegamos a N = 700.
- El motor no calcula observables: escribe el estado cada Δt2 y el instante de cada conversión; todo lo demás es post-proceso.

## 7. El bucle del paso temporal — `slide-07-bucle-paso-temporal.png`

- Lo que hace step() una vez, en orden: correr las posiciones, rearmar la grilla, sumar las fuerzas, aplicar Verlet, convertir y, cada Δt2, escribir el estado.
- El arranque necesita r(−Δt), que sale de un Euler en −Δt; de ahí en adelante la recurrencia es explícita porque la fuerza depende sólo de las posiciones.
- La diferencia con el TP3: ahí el bucle decidía cuándo avanzar (el próximo evento de la cola) y acá el paso es fijo, siempre Δt. Por eso el costo por paso no depende de los choques y el de eventos sí.

## 8. Simulaciones (separador)

- Parámetros, observables y los casos que se corrieron.

## 9. Parámetros — `slide-09-parametros-dominio.png` y `slide-09-parametros-tabla.png`

- La tabla va en tres bloques. **Fijos**, lo que no se toca en todo el trabajo: R = 0,51 m, r = 0,0175 m, m = 0,025 kg, v0 = 1 m/s y k = 10⁴ N/m.
- **Variables**, lo que se barre, escrito como **intervalo entre corchetes** porque es un rango recorrido y no una lista de valores sueltos: N ∈ [5, 700], la densidad ρ = N/πR² que le corresponde, ρ ∈ [6, 857] partículas/m² (el mismo barrido contado por unidad de área, y el parámetro con el que el ítem 2.4 pide los resultados), y xo ∈ [r, R − r], de obstáculos en contacto entre sí a obstáculos contra la pared.
- **Simulación**: Δt = 5·10⁻⁵ s, que no es del sistema sino de la integración, y que se elige en Resultados por conservación de la energía.
- El paso de guardado y el t_f **no están en la tabla**: van por caso, según qué mide cada figura, y están en la línea de condiciones de la figura que los usa. Si preguntan: 0,01 s para la energía, 0,05 s para f(v), 0,04 s para las animaciones, y los barridos grandes no guardan cuadros.
- πR² = 0,817 m², la misma área que la mesa del TP3: igual densidad a igual N.

## 10. Observables

- Conversión: Fu(t) = Nu/N. **t_x es el instante en que la conversión llega al x %**, el que cumple Fu(t_x) = x/100; medimos t90 y t100, que son ese t_x con x = 90 y x = 100. Decirlo así, con la definición general primero: los dos observables del trabajo son el mismo con distinto x.
- Energía total (cinética más elástica de los contactos), y su **error relativo en porcentaje** ε(t) = 100·(E(t) − E0)/E0. El escalar que resume cada corrida es ε_máx = máx|ε(t)|, un número por Δt.
- f(v) en 40 intervalos, **un solo histograma por bolsa**: todos los |v| de las N partículas de las M realizaciones juntos; la **gran bolsa** del estacionario junta además todos los cuadros con t ≥ 10 s. La rapidez media ⟨|v|⟩ de la bolsa de cada instante es el escalar que dice desde cuándo es estacionario. Para el sistema 1, el ECM contra la solución analítica.
- Promedios sobre M realizaciones, con el **desvío estándar** entre ellas como barra de error (no el error de la media σ/√M).

## 11. Casos estudiados

- Sistema 1: 4 esquemas, 9 pasos de 5·10⁻³ a 10⁻⁵ s. Paso temporal: N = 300 sin obstáculos, 7 pasos, verificado a N = 700 con obstáculos.
- Costo: xo = r, N de 50 a 700, 10 realizaciones por N, contra el motor del TP3 en la misma máquina.
- Posición de los obstáculos: 11 valores de xo con N = 100 y 20, 15 realizaciones. Velocidades: N = 100, 30 realizaciones. Densidad: barrido propio con xo = r, 10 densidades (N de 5 a 300), 20 realizaciones, cada corrida hasta convertirlas todas (tmax = 300 s, que ninguna necesita); y un barrido (xo, N) de 16 posiciones × 10 densidades con 20 realizaciones por punto (3200 corridas).

## 12. Resultados (separador)

- Primero el oscilador, después el paso y el costo, luego obstáculos, velocidades y densidad.

## 13. Sistema 1: posición contra el tiempo — `slide-13-posicion-oscilador-vs-t.png`

- La pidió la cátedra además del ECM, y pidió **posición, no energía**: en este sistema la energía no se conserva (el amortiguamiento la disipa), y lo que se estima con cada esquema es r(t). Es r(t) de los cuatro esquemas con la solución analítica encima (punteada), r(t) = A·e^(−γt/2m)·cos(ωt), con ω = √(k/m − γ²/4m²) = 11,93 rad/s (período 0,53 s).
- Es con **un solo Δt, 5·10⁻³ s, el más largo del barrido**, y se muestran los primeros 2 s de los 5 (después las oscilaciones se amontonan y no se ve nada; la envolvente ya cayó a 0,24 m en t = 2 s). Beeman, Verlet original y Velocity Verlet caen sobre la analítica: se apartan como mucho 0,9, 1,0 y 6,4 mm sobre una amplitud de 1 m. Euler predictor-corrector se despega enseguida y **pierde amplitud**: se aparta hasta 15 cm (a 1,04 s) y a 1 s ya está 13 cm por debajo. Es el mismo error que en el ECM aparece como la curva más alta.
- **Velocity Verlet se superpone con Verlet original y es esperado**, aunque pierda un orden por evaluar a(t + Δt) con la velocidad de medio paso. Perder un orden es cómo *escala* el error con Δt, no cuánto vale: con este paso su ECM es 40 veces el de Verlet original (1,0·10⁻⁵ contra 2,4·10⁻⁷ m²), pero eso son 6 mm contra 1 mm de apartamiento máximo sobre 1 m, menos que el grosor del trazo. Euler p-c tiene 450 veces el ECM de Velocity Verlet y por eso es el único que se ve. Los órdenes (Δt² contra Δt⁴) sólo se ven en la figura siguiente, que es logarítmica. Lo imprime `make oscilador-figuras`.
- Con pasos más cortos Euler se acerca (con 2·10⁻³ s, 6,7 cm; con 10⁻³ s, 3 cm) y la figura ya no distingue nada: por eso el escalar que compara los esquemas es el ECM.
- En la versión en vivo, al lado de la figura va el GIF `gif/05-oscilador-cuatro-esquemas.gif` (`make animaciones-apoyo`): las cuatro masas oscilando a la vez, una por esquema y sin la analítica. Es lo mismo que dice la figura, pero se ve en el movimiento: tres masas van juntas y la de Euler p-c se queda corta en cada extremo. Está hecho con **el mismo Δt = 5·10⁻³ s** que la figura, así que el paso se escribe una sola vez en la diapositiva y vale para los dos: arriba del GIF va sólo el instante (y corre los 5 s completos, mientras que la figura muestra los primeros 2).

## 14. Sistema 1: error cuadrático medio contra el paso — `slide-14-ECM-vs-dt.png`

- Beeman y Verlet original van los dos como ECM ∝ Δt⁴, o sea error de segundo orden, y en diez órdenes de magnitud se superponen. Velocity Verlet y Euler p-c van como Δt², un orden menos, por cómo evalúan a(t + Δt): es la decisión que está escrita debajo de cada esquema en la diapositiva de integración, y la viñeta de acá la vuelve a nombrar.
- A Δt = 10⁻⁴ s hay ocho órdenes entre Beeman y Euler p-c (**decirlo**: no está escrito en la diapositiva, no entraba en la columna). Beeman es el mejor: tiene el menor ECM en 8 de los 9 pasos del barrido.
- El último punto de Verlet, en Δt = 10⁻⁵ s, es donde se separan: ahí Verlet ya no mide el error del esquema sino el piso de redondeo del doble (su recurrencia resta dos números casi iguales) y queda 50 veces por encima de Beeman. Está dibujado como todos los demás, porque es una medición más; lo único que cambia es que queda fuera del ajuste, porque no mide el orden.
- Si preguntan por las pendientes: el ajuste de la ley de potencia ECM = c Δtᵖ da p = 4,00 (Beeman), 4,02 (Verlet original), 2,04 (Velocity Verlet) y 1,92 (Euler p-c). No están en la leyenda porque el enunciado pide esa diapositiva sin más información que la figura; los números están en `data/oscilador/ecm.csv` y en la salida de `make oscilador-figuras`.
- Si preguntan por qué Beeman y no Verlet, que en la figura se superponen: lo que los separa no es la pendiente sino la constante. Dividiendo el ECM por Δt⁴ queda 330 para Beeman y 380 para Verlet, un 15 % más de ECM con el mismo paso (la figura está en `data/figures/1_oscilador/ECM_constante_vs_dt.png`, fuera de la charla: el enunciado pide del sistema 1 sólo la figura del ECM, y la de posición la pidió la cátedra).
- Esa diferencia es toda de la fuerza que depende de la velocidad. Con γ = 0 las dos constantes dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).

## 15. Conservación de la energía — `slide-15-energia-vs-t.png`

- La **evolución del sistema**, tal como la pide el ítem 2.1.a: la energía total en Joule contra el tiempo para distintos Δt. E0 = N·½mv0² = 3,75 J (la línea punteada) y el sistema es conservativo: todo lo que se aparta de E0 es error del integrador.
- Se ven tres Δt, los mismos de la figura siguiente y con el mismo color: 2·10⁻⁴ s **baja** hasta 3,73 J, y 10⁻⁴ y 5·10⁻⁵ s no se despegan de E0 en esta escala.
- Son 3 de los 7 Δt medidos. 5·10⁻⁴ s sube a 3,85 J (2,6 %) y Δt = 10⁻³ s llega a **45 J**: los dos aplastarían a las demás contra E0 (el choque dura τ = π√(μ/k) = 3,5 ms y con 10⁻³ s entran sólo tres pasos por choque, así que el resorte no se integra). 2·10⁻⁵ y 10⁻⁵ s caen encima de la del elegido. El barrido entero, con esos cuatro, está en la figura de ε_máx, dos diapositivas más adelante.

## 16. Error de la energía contra el tiempo — `slide-16-error-energia-vs-t.png`

- Las mismas corridas como **error relativo porcentual** ε(t) = 100·(E − E0)/E0: así el número del eje es el número de la frase con la que se elige el paso ("me quedo con éste porque el error es menor que tanto por ciento"). El cero es la conservación exacta y está en el medio.
- Los mismos tres Δt que la figura anterior. La **cota del 0,1 %** con la que se elige el paso está marcada en la escala del eje (las marcas ±0,1), no como otra línea: con tres curvas y el cero la leyenda ya está completa. 2·10⁻⁴ s se va al −0,6 %, 10⁻⁴ s roza la cota (0,1 %) y 5·10⁻⁵ s se queda en el 0,04 %, adentro.
- El error no crece sin parar: cada curva deriva en el primer segundo y después se estabiliza. Por eso el escalar que resume cada corrida es el máximo, ε_máx, y no la pendiente ni el valor final.
- Si preguntan por qué no están 5·10⁻⁴ ni 10⁻³ s: el primero sube al 2,6 % y el segundo al 1100 %, y con cualquiera de los dos adentro las tres de abajo quedaban pegadas al cero; están en la figura siguiente, que es la que tiene el barrido entero.

## 17. Elección del paso: error máximo — `slide-17-error-maximo-vs-dt.png`

- ε_máx(Δt) resume cada corrida en un número; sobre los pasos estables ajusta Δt^2,0.
- Criterio: el Δt más largo con ε_máx ≤ 0,1 %, el más barato con el error aceptado. La cota va en gris punteado porque es el criterio, no un resultado; el rojo queda para el único dato que la figura señala, el paso elegido.
- **La frase**: para que el error de la energía quede por debajo del 0,1 % hace falta Δt = 5·10⁻⁵ s. Da 0,04 %, y 0,03 % en el caso más exigente del trabajo, N = 700 con obstáculos.
- Si preguntan por el exponente 2,0: es el orden del esquema. No hace falta nombrar a Verlet acá, ya se dijo en la diapositiva de integración.

## 18. Obstáculos en el centro — `slide-18-animacion-centro.png`

- xo = r: los dos obstáculos se tocan y forman un solo blanco de 4r de ancho en el centro.
- Es la configuración del barrido de N y la de conversión más lenta de todo el trabajo.
- Cuadro congelado en t = 10 s; el video completo está en el link.
- xo es el parámetro del ítem 2.2 y va de r a R − r; en la versión en vivo, antes de las tres animaciones se puede pasar `gif/06-posicion-de-los-obstaculos.gif` (`make animaciones-apoyo`), que recorre el rango entero con los tres xo marcados: esta diapositiva es el extremo de abajo.

## 19. Tiempo de ejecución contra N — `slide-19-tiempo-ejecucion-vs-N.png`

- Paso temporal: **t ∝ N^0,88**, casi lineal; siempre 600 000 pasos y costo O(N) por la celda de índice. La recta punteada azul es ese ajuste.
- Eventos (TP3): **t ∝ N^3,52** (la recta punteada roja), porque cada choque rehace parte del calendario y los choques crecen con N.
- Los dos exponentes están **escritos en las viñetas**: si se dibuja la recta de regresión hay que decir qué pendiente dio.
- Se cruzan cerca de N = 470; a N = 600 los eventos cuestan 2,9 veces más (14,8 s contra 42,3 s).
- Las barras de desvío están dibujadas pero no se ven: la figura abarca cuatro décadas y σ/⟨t⟩ es como mucho el 4 % (3,9 %, en los eventos a N = 400). En log, una barra del 4 % mide unos 5 píxeles contra 21 del símbolo: queda adentro del marcador. Y es el **desvío**, no el error de la media: con σ/√10 sería 3,2 veces más chica todavía. **Hay que decirlo**, porque ya no está escrito dentro de la figura: eran dos bloques de texto compitiendo con la leyenda. Lo imprime `make bench-figuras`.
- Ojo si preguntan: ese 4 % es el **desvío estándar**, no una cota de cuánto se aparta la peor corrida. El rango completo (máx − mín) llega al 7 % en el paso temporal (N = 200) y al 12 % en los eventos (N = 400). Lo imprime `make bench-figuras`.
- Si preguntan si no es poco, o si falta precisión en la medición: no falta. El cronómetro es `steady_clock` y el tiempo se escribe en milisegundos con seis decimales (resolución de nanosegundos) sobre mediciones de 1,9 a 20 s; la resolución está siete órdenes de magnitud por debajo de lo medido. Lo que hace chico al desvío es que con paso temporal fijo **todas las realizaciones de un mismo N hacen exactamente el mismo trabajo**: 600 000 pasos, el mismo barrido de 29 × 29 celdas y prácticamente los mismos contactos; lo único que cambia entre semillas son las posiciones y las direcciones iniciales. Lo que queda es ruido de la máquina, y se nota que es eso porque **baja** cuando la corrida es más larga (0,1–0,4 % de N = 400 para arriba, contra 2–3 % en las corridas de 2 s). En los eventos del TP3 el desvío es mayor (hasta 3,9 %) justamente porque ahí el trabajo sí depende de la semilla: el número de eventos cambia de una realización a otra.
- Los números, por si los piden (promedio ± desvío sobre M = 10 realizaciones, sin la de calentamiento):

  | N | paso temporal (TP4) | σ/⟨t⟩ | eventos (TP3) | σ/⟨t⟩ |
  |---:|---:|---:|---:|---:|
  | 50  | 1,8828 ± 0,0485 s | 2,6 % | 0,0061 ± 0,0002 s | 3,4 % |
  | 100 | 2,6704 ± 0,0580 s | 2,2 % | 0,0430 ± 0,0005 s | 1,1 % |
  | 200 | 4,4858 ± 0,1095 s | 2,4 % | 0,3805 ± 0,0014 s | 0,4 % |
  | 300 | 6,4343 ± 0,0391 s | 0,6 % | 1,6356 ± 0,0280 s | 1,7 % |
  | 400 | 8,7761 ± 0,0100 s | 0,1 % | 5,4333 ± 0,2116 s | 3,9 % |
  | 500 | 11,4009 ± 0,0274 s | 0,2 % | 16,4279 ± 0,5369 s | 3,3 % |
  | 600 | 14,7894 ± 0,0350 s | 0,2 % | 42,3285 ± 1,0298 s | 2,4 % |
  | 700 | 19,9085 ± 0,0886 s | 0,4 % | — | — |

  (La medición de calentamiento, la que se descarta, queda dentro del ±4,5 % del promedio en todos los N: el arranque en frío tampoco es lo que domina.)

## 20. Obstáculos en la posición óptima — `slide-20-animacion-optimo.png`

- xo = 0,20 m: separados, cada obstáculo barre su zona y ninguno queda a la sombra del otro.
- A los 10 s ya hay 75 usadas, contra 56 con los obstáculos en el centro.

## 21. Obstáculos en el borde — `slide-21-animacion-borde.png`

- xo = R − r: pegados a la pared, quedan fuera del camino de casi todas las trayectorias.
- A los 10 s, 51 usadas: la conversión más lenta de las tres.

## 22. Fracción de usadas: los tres xo típicos — `slide-22-Fu-vs-t-xo-tipicos.png`

- Las tres curvas juntas, que es como lo pide el ítem 2.2: Fu(t) para pocos valores típicos de xo. Cada una es el promedio de las 15 realizaciones y la banda es ±1 desvío entre ellas.
- Misma forma, corrida en el tiempo: el óptimo llega a 0,9 en 14,8 s, el centro en 26,5 s y el borde en 31,2 s. La línea punteada de 0,9 está en la leyenda porque es la definición de t90: el símbolo de cada curva sobre ella es ⟨t90⟩ y la barra horizontal su desvío, con el mismo estilo de barra que el resto de las figuras.
- El óptimo además es el de menos dispersión (±1,7 s contra ±3,4 y ±3,1).
- La cola es larga en los tres: ⟨t100⟩ ≈ 2,3 ⟨t90⟩. Ninguna realización se queda sin convertir antes de tmax = 100 s, así que no hay que reportar Fu(tmax).

## 23. ⟨t90⟩ contra la posición de los obstáculos — `slide-23-t90-vs-xo.png`

- Sí hay posición óptima: ⟨t90⟩ cae de 26,5 s en xo = r a 14,8 s en 0,20 m y sube a 31,2 s contra la pared.
- El mínimo es un plateau ancho, de 0,15 a 0,35 m: esos puntos empatan dentro del desvío.
- Con N = 20 la curva baja entera pero el mínimo cae en el mismo lugar: la posición óptima no depende de la frecuencia de choques.

## 24. Sin obstáculos — `slide-24-animacion-sin-obstaculos.png`

- Sin conversión, todas quedan frescas: es el sistema con el que se eligió el paso y el de la distribución de velocidades.
- Arrancan todas con |v| = v0 y sólo los choques entre partículas reparten la energía; el choque con la pared conserva |v|.

## 25. Rapidez media contra el tiempo — `slide-25-v-medio-vs-t.png`

- Un escalar por instante: la rapidez media ⟨|v|⟩ de las 100 partículas de las 30 realizaciones (la bolsa de ese instante), con el desvío entre realizaciones como banda: ⟨|v|⟩ se calcula por realización y se promedia. Es la misma dispersión que dibuja la barra de error de la gran bolsa, dos diapositivas más adelante.
- Arranca **exactamente en v0** en t = 0 (todas nacen con |v| = v0) y baja mientras f(v) se ensancha: la energía no cambia (E se conserva), pero la media de |v| no es la raíz de la media de v², y cuanto más ancha es f(v) más chica queda ⟨|v|⟩. En el primer cuadro guardado, 0,05 s, ya hubo choques y la media ya bajó a 0,97. Desde 0,4 s está dentro de la banda del estacionario y sigue plana hasta los 30 s (la figura muestra los primeros 2 s, que es donde pasa algo).
- La gran bolsa del ajuste toma t ≥ 10 s: es estacionario desde mucho antes, el margen es gratis porque la corrida llega a 30 s. Va en la línea de condiciones de la diapositiva del ajuste, no dibujado acá.
- La línea roja punteada es la verificación: Maxwell-Boltzmann en 2D con el kBT ajustado en la diapositiva 27 predice ⟨|v|⟩ = √(πkBT/2m) = 0,883 m/s, y la medida en el estacionario es 0,881 m/s (0,2 %). El ajuste usa la forma entera de f(v); esto usa un solo momento, por eso es independiente.
- Si preguntan por qué la banda es tan ancha (±0,014 m/s) frente a lo chica que es la diferencia entre instantes: es el desvío entre realizaciones de un promedio de 100 partículas, no el error de la media.

## 26. Distribución del módulo de la velocidad — `slide-26-f-v-vs-t.png`

- En t = 0 f(v) es una delta en v0 que se sale de la figura.
- A los 0,15 s el pico ya bajó a 2,45 s/m, 2,7 veces el del estacionario (0,90 s/m; la delta de t = 0 mide 11,3 s/m, que es 1 sobre el ancho del intervalo), y apareció la cola de velocidades bajas; la curva de t = 30 s es el estacionario, y desde 0,5 s las curvas ya no se distinguen entre sí (por eso están éstas tres y no más).
- Las tres son instantes exactos, cada uno con su t: el estacionario se muestra como el último cuadro guardado, no como un promedio sobre cuadros. Ese promedio se usa en la figura del ajuste, que es donde hace falta la estadística.
- f(v) se ensancha sin que cambie E: el sistema es conservativo.
- Cada curva es **un solo histograma de una bolsa**: los |v| de las 100 partículas de las 30 realizaciones de ese instante, todos juntos, 3000 muestras (la bolsa de un instante; la **gran bolsa** de la diapositiva siguiente junta además todos los cuadros del estacionario). No es el promedio de 30 histogramas con su desvío como barra: el histograma de una realización sola (100 partículas en 40 intervalos) es ruido, y promediarlos con barras del 51 % tapaba la forma de f(v), que es lo que la figura muestra. Decir cuántas realizaciones y cuántas muestras entran en la bolsa: está en la línea de condiciones.
- Si preguntan por el desvío entre realizaciones en esta figura: se mide y lo imprime `make velocidades-figuras` (51 % en un instante suelto), pero acá no se dibuja porque taparía la curva; en la gran bolsa baja al 4,8 % y ahí sí va como barra.

## 27. La gran bolsa: ajuste de Maxwell-Boltzmann — `slide-27-f-v-gran-bolsa-ajuste.png`

- **Ésta es la figura de la gran bolsa**: un solo histograma con todos los |v| del estacionario (t ≥ 10 s) de todas las realizaciones, 1,2·10⁶ muestras. La barra de error de cada intervalo es el desvío estándar entre las 30 realizaciones (el histograma de cada una por separado): 4,8 % en promedio, la misma dispersión que la banda de la rapidez media. Es chica porque cada realización aporta 40 000 muestras, y se ve que es chica. Encima, Maxwell-Boltzmann en dos dimensiones con kBT como único parámetro libre.
- Las tres energías del análisis que pide el ítem (las imprime `make velocidades-figuras`): la inicial **½ m v0² = 12,50 mJ** (exacta: todas arrancan con |v| = v0), la del estacionario **½ m ⟨v²⟩ = 12,32 mJ** y el ajuste **kBT = 12,41 mJ**.
- kBT contra ½ m v0²: −0,7 %. Contra ½ m ⟨v²⟩: +0,7 %. El ajuste cae entre las dos.
- ½ m ⟨v²⟩ es 1,4 % menor que ½ m v0² porque E se conserva pero no toda es cinética: en promedio ese 1,4 % está en los resortes de los contactos. Por eso kBT, que ajusta la forma de f(v), no tiene por qué dar exactamente ninguna de las dos.
- La bolsa del estacionario: **30 realizaciones × 401 cuadros (t ≥ 10 s) × 100 partículas = 1,2·10⁶ muestras**, un solo histograma de 40 intervalos y área 1. Decir los tres factores: es de donde sale que la curva se superponga tan bien con Maxwell-Boltzmann.
- Los cuadros de una misma realización están correlacionados entre sí; igual se juntan, porque lo que hace falta acá es la forma de f(v) en el estacionario y el promedio temporal de un estado estacionario es el mismo promedio de ensamble.

## 28. Error cuadrático medio del ajuste — `slide-28-E-vs-kT.png`

- Método de la Teórica 0: se recorre kBT en una grilla y se toma el mínimo de E(kBT). Los ejes son el símbolo con la unidad, como en el resto: E(kBT) es el error cuadrático medio del ajuste (el argumento lo distingue de la energía total E(t)) y kBT la energía térmica, los dos nombrados en la viñeta.
- **El ancho del mínimo es el error del ajuste**, que es lo que esta figura agrega: E se duplica ya en 12,31 y 12,53 mJ, o sea kBT = 12,41 ± 0,11 mJ, un 0,9 %. Es la forma de ponerle error a un ajuste de un parámetro sin más que la curva E(parámetro).
- "Energía térmica" es el nombre que le da el enunciado a kBT: es el único parámetro libre del ajuste, no una temperatura medida.

## 29. Efecto de la densidad — `slide-29-t90-t100-vs-densidad.png`

- Dos ejes y nada más, que es lo que pide el ítem: la densidad ρ = N/πR² en partículas/m² (definida en la diapositiva de parámetros, con la misma unidad) y el tiempo de conversión. El N de cada densidad, por si lo piden: ρ = 6 es N = 5, ρ = 24 es N = 20, ρ = 86 es N = 70, ρ = 367 es N = 300.
- **Las dos curvas son una U y hay densidad óptima.** ⟨t90⟩ baja de 66,3 ± 40,3 s en ρ = 6 hasta 21,8 ± 3,0 s en ρ = 86 (N = 70) y vuelve a subir a 54,3 ± 3,7 s en ρ = 367 (N = 300).
- El fondo es **ancho**: de ρ = 24 a 86 (N = 20 a 70) las cuatro densidades dan 22,0, 22,6, 22,3 y 21,8 s, todas iguales dentro del desvío. El óptimo es ese tramo, no un punto.
- Por qué sube de los dos lados. **Abajo** faltan choques: sin choques cada partícula conserva el momento angular respecto del centro y sólo convierte si su parámetro de impacto es b < 3r (medido: con N = 1 convierten 40 de 300 realizaciones, el 13 %). **Arriba** se achica el camino libre y el blanco queda rodeado por las demás partículas.
- ⟨t100⟩ tiene la misma forma pero el mínimo más abajo, en ρ = 24 (36,3 ± 9,6 s), y crece mucho más rápido: 135,0 ± 19,7 s en ρ = 367. El **último 10 %** es el que más castiga la densidad alta, porque las que faltan son justamente las que quedaron en las órbitas que no pasan por el blanco.
- **Este barrido es propio del ítem, no son las corridas del 2.1.b**, y lo consultamos. Las del 2.1.b tienen tf = 30 s fijo: con los obstáculos en contacto, de N = 200 para arriba no llegaba ninguna realización a Fu = 0,9 y a N = 5 llegaba una sola de diez (promedio de una muestra, sin desvío). Con ese corte la figura era plana en 21 s y después se cortaba: no mostraba ninguna densidad óptima, que es justo lo que el ítem pregunta. Lo que cambia es sólo el tf; la configuración es la misma (xo = r) y las densidades son las mismas que la columna xo = r del mapa de la diapositiva siguiente.
- Las condiciones, por si las piden: xo = r, 20 realizaciones por densidad, cada corrida hasta convertirlas **todas** (tmax = 300 s, que ninguna necesita). Las 20 llegan en todas las densidades y en los dos observables: **todos los puntos tienen desvío**, que es lo que antes no pasaba.
- Si preguntan por qué el eje llega a ρ = 367 y no a 857: porque el barrido de esta figura es el de las diez densidades del mapa, para que las dos figuras del ítem 2.4 hablen de lo mismo. De N = 300 para arriba la fracción de área pasa el 35 % y la conversión se vuelve muy lenta; el comportamiento ya se ve.

## 30. Posición óptima para cada densidad — `slide-30-mapa-t90-xo-N.png`

- El barrido es de 16 posiciones × 10 densidades × 20 realizaciones (3200 corridas): hace falta esa resolución para distinguir si el óptimo se corre con N o si es siempre el mismo.
- La escala de colores está dada vuelta a propósito: el rojo es la conversión **más rápida**, porque lo que tiene que saltar a la vista es el óptimo y no el peor caso. Y está recortada en 38 s (1,3 veces el más alto de los mínimos de cada fila, la flecha de la barra lo marca): los bordes de las densidades extremas llegan a 70 s y se llevaban media escala ellos solos.
- La mancha roja **cierra por arriba y por abajo**: hay óptimo en las dos variables. Por eso está la fila de N = 5, que es la que la cierra por abajo.
- La **línea negra** une la celda más rápida de cada densidad (el cuadrado más rojo de cada fila, calculado de los datos: el argmin de ⟨t90⟩ sobre xo): el color contesta “cuánto tarda” y la línea contesta “dónde está el mínimo de esta fila”.
- La línea **zigzaguea** de N = 20 para arriba porque el fondo del valle es ancho y plano: cuál de las celdas del fondo sale la más baja es en buena parte azar (a N = 50 cae en 0,175 m y a N = 150 en 0,275 m, y las dos filas son iguales dentro del desvío). Lo que hay que leer es que **siempre cae entre 0,175 y 0,30 m**, nunca en el centro ni en la pared.
- El número fino sale de ajustar una **parábola a cada fila** sobre el mismo tramo (xo = 0,10–0,40 m) y tomar el vértice: de N = 20 en adelante (ocho densidades) da **0,237 ± 0,011 m**. El óptimo no se corre con la densidad en todo ese rango, y no es exactamente 0,2 sino 0,24 m (0,46 R). Lo imprime `make mapa-figuras` fila por fila; no está dibujado porque la línea es la medición y el vértice es un ajuste.
- Las dos densidades más bajas sí se corren hacia afuera: la celda más baja está en 0,35 m en N = 5 y en 0,40 m en N = 10 (los vértices, 0,287 ± 0,020 y 0,350 ± 0,031 m, a 2,5 y 3,7 σ del promedio). Con tan pocas partículas casi no hay choques y la conversión la decide el parámetro de impacto de cada trayectoria, así que separar los obstáculos cubre más parámetros de impacto. Es el mismo argumento del ítem 2.4.a (con N = 1 sólo convierte si b < 3r). Sobre las diez densidades el ajuste da −0,018 ± 0,007 m por década de N, y ese corrimiento lo aportan enteramente esas dos filas.
- Los extremos son siempre los peores, y cuál de los dos es peor cambia con la densidad: a N = 5 el centro es cuatro veces y media el mínimo, a N = 10 centro y pared cuestan lo mismo (30,1 y 29,5 s), y a N = 300 la pared es claramente peor (69,8 contra 54,3 s). El castigo de la pared crece con N: 1,9 veces el mínimo a N = 20 y 2,4 a N = 300.
- ⟨t90⟩ en el óptimo pasa de 11,0 s (N = 10) a 29,5 s (N = 300), y vuelve a subir a 14,3 s en N = 5.
- El barrido del mapa corre con tmax = 300 s, no 100: a N = 5 hay realizaciones que tardan 150 s en convertir las cinco partículas. De N = 10 para arriba no cambia nada, ninguna pasa de 70 s.
- Si preguntan por qué el barrido corta en Fu = 0,9: el mapa sólo mide t90, y seguir hasta que se convierten todas cuesta el triple de cómputo (a N = 300, t90 ≈ 29 s contra t100 ≈ 98 s de tiempo simulado). Está verificado contra una corrida completa: la conversión número 90 de la misma semilla cae exactamente en el mismo instante.

## 31. Conclusiones (separador)

- Lo que queda de cada ítem.

## 32. Conclusiones

- Beeman y Verlet original son de segundo orden en el oscilador; Beeman es el mejor. Δt = 5·10⁻⁵ s por conservación de la energía: deja el error de E en 0,04 % a N = 300 y 0,03 % a N = 700.
- El costo del paso temporal crece casi lineal con N (t ∝ N^0,88) y el de los eventos mucho más rápido (N^3,52): se cruzan cerca de N = 470.
- Hay un xo óptimo, 0,237 ± 0,011 m, el mismo de N = 20 a 300; f(v) llega a Maxwell-Boltzmann en medio segundo con kBT = 12,41 ± 0,11 mJ ≈ mv0²/2 (y la rapidez media medida, 0,881 m/s, está a 0,2 % de la que predice con ese kBT); y con los obstáculos en el centro hay una densidad óptima en ρ = 86 partículas/m² (N = 70), donde ⟨t90⟩ = 21,8 s contra 66 s a ρ = 6 y 54 s a ρ = 367.

## 33. Uso de agentes de IA

- Claude Code (Anthropic), modelos Claude Opus 5 y Claude Fable 5.1, para programar el motor, los scripts y el LaTeX, y para revisar código.
- Las decisiones de modelado, el análisis y las conclusiones son del grupo; todo lo generado se verificó contra las figuras.

## Cierre

- Muchas gracias.
