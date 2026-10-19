# Guion de la presentación

Dos o tres puntos para decir en cada diapositiva. El número es el del pie de
la diapositiva (el mismo con el que están numeradas las figuras en
`slides-images/`). Las cifras son las de las figuras mostradas.

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
- Si preguntan por Velocity Verlet (es la pregunta más probable de esta diapositiva): la fórmula de la Teórica es v(t + Δt) = v(t) + (Δt/2m)(f(t) + f(t + Δt)), y f(t + Δt) necesita v(t + Δt), que es lo que la ecuación está calculando. Queda implícita y hay dos salidas razonables.
- Una es despejar v(t + Δt) —se puede, f es lineal en v, igual que en Verlet original—. Da segundo orden, pero el esquema que queda **es** Verlet original: sumando pasos consecutivos de las dos fórmulas se llega a la recurrencia de Verlet y a su velocidad centrada, sin usar de qué depende f. O sea que quedarían 3 esquemas distintos en vez de 4.
- La otra, la que corre, es evaluar f(t + Δt) con v(t + Δt/2), la única velocidad que aparece entre los dos pasos intermedios de la diapositiva 17. Mantiene los cuatro esquemas separados y cuesta un orden: ECM ∝ Δt^2,04 en vez de Δt⁴, porque v(t + Δt/2) se aparta de v(t + Δt) en O(Δt) y ese error entra en f(t + Δt) multiplicado por Δt/2. Beeman no lo pierde porque su predictor es de O(Δt²).
- Honestidad: ninguna de las dos es "la correcta", y está consultado a la cátedra. Si preguntan, se dice así. Las dos están medidas (`make velocity-verlet-variantes`).

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

## 9. Parámetros — `slide-09-parametros-dominio.png`

- La tabla va en tres bloques. **Fijos**, lo que no se toca en todo el trabajo: R = 0,51 m, r = 0,0175 m, m = 0,025 kg, v0 = 1 m/s y k = 10⁴ N/m.
- **Variables**, lo que se barre: N de 5 a 700, la densidad ρ = N/πR² que le corresponde (de 6 a 857 partículas por m², es el mismo barrido contado por unidad de área, y es el parámetro con el que el ítem 2.4 pide los resultados), y xo de r (obstáculos en contacto entre sí) a R − r (en contacto con la pared).
- **Simulación**, lo que fija la integración y no el sistema: Δt = 5·10⁻⁵ s, que se elige en Resultados por conservación de la energía, más Δt₂ y t_f, que van por caso y están en la diapositiva siguiente.
- πR² = 0,817 m², la misma área que la mesa del TP3: igual densidad a igual N.

## 10. Observables

- Conversión: Fu(t) = Nu/N, y t90 y t100 en el instante exacto de cada conversión.
- Energía total sobre los estados guardados (cinética más elástica) y la deriva relativa máxima D(Δt), un escalar por paso.
- f(v) en 40 intervalos con las N partículas de las M realizaciones; para el sistema 1, el ECM contra la solución analítica. Las barras de error son el desvío estándar entre realizaciones.

## 11. Casos estudiados

- Sistema 1: 4 esquemas, 9 pasos de 5·10⁻³ a 10⁻⁵ s. Paso temporal: N = 300 sin obstáculos, 7 pasos, verificado a N = 700 con obstáculos.
- Costo: xo = r, N de 50 a 700, 10 realizaciones por N, contra el motor del TP3 en la misma máquina.
- Posición de los obstáculos: 11 valores de xo con N = 100 y 20, 15 realizaciones. Velocidades: N = 100, 30 realizaciones. Densidad: las corridas del 2.1.b y un barrido (xo, N) de 16 posiciones × 10 densidades con 20 realizaciones por punto (3200 corridas).

## 12. Resultados (separador)

- Primero el oscilador, después el paso y el costo, luego obstáculos, velocidades y densidad.

## 13. Sistema 1: error cuadrático medio contra el paso — `slide-13-ECM-vs-dt.png`

- Beeman y Verlet original van los dos como ECM ∝ Δt⁴, o sea error de segundo orden, y en diez órdenes de magnitud se superponen. Velocity Verlet y Euler p-c van como Δt², un orden menos, por cómo evalúan a(t + Δt) (ya se explicó en la diapositiva de integración).
- A Δt = 10⁻⁴ s hay ocho órdenes entre Beeman y Euler p-c. Beeman es el mejor: tiene el menor ECM en 8 de los 9 pasos del barrido.
- El último punto de Verlet, en Δt = 10⁻⁵ s, es donde se separan: ahí Verlet ya no mide el error del esquema sino el piso de redondeo del doble (su recurrencia resta dos números casi iguales) y queda 50 veces por encima de Beeman. Está dibujado como todos los demás, porque es una medición más; lo único que cambia es que queda fuera del ajuste, porque no mide el orden.
- Si preguntan por las pendientes: el ajuste de la ley de potencia ECM = c Δtᵖ da p = 4,00 (Beeman), 4,02 (Verlet original), 2,04 (Velocity Verlet) y 1,92 (Euler p-c). No están en la leyenda porque el enunciado pide esa diapositiva sin más información que la figura; los números están en `data/oscilador/ecm.csv` y en la salida de `make oscilador-figuras`.
- Si preguntan por qué Beeman y no Verlet, que en la figura se superponen: lo que los separa no es la pendiente sino la constante. Dividiendo el ECM por Δt⁴ queda 330 para Beeman y 380 para Verlet, un 15 % más de ECM con el mismo paso (la figura está en `data/figures/1_oscilador/ECM_constante_vs_dt.png`, fuera de la charla porque el enunciado pide una sola diapositiva del sistema 1).
- Esa diferencia es toda de la fuerza que depende de la velocidad. Con γ = 0 las dos constantes dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).

## 14. Energía total contra el tiempo — `slide-14-energia-vs-t.png`

- E0 = 3,75 J y el sistema es conservativo: todo lo que se aparta es error del integrador.
- 5·10⁻⁴ s deriva 2,6 % y 2·10⁻⁴ s un 0,6 % (hacia abajo); de 10⁻⁴ s para abajo no se distinguen de E0.
- Son 3 de los 7 Δt medidos, los que se leen en una misma escala: uno que deriva hacia arriba, uno hacia abajo y el que se queda sobre E0. Δt = 10⁻³ s se dispara hasta 45 J y aplastaría a todas las demás contra E0 (el choque dura 3,5 ms y entran sólo tres pasos); 10⁻⁴, 2·10⁻⁵ y 10⁻⁵ s caen encima de 5·10⁻⁵ y no se distinguen. El barrido completo está en la figura de la deriva, que es la que elige el paso.

## 15. Elección del paso: deriva relativa máxima — `slide-15-deriva-vs-dt.png`

- D(Δt) resume cada corrida en un número; sobre los pasos estables ajusta Δt^2,0, el segundo orden de Verlet.
- Criterio: el Δt más largo con D ≤ 10⁻³, el más barato con el error aceptado.
- Queda Δt = 5·10⁻⁵ s: D = 3,8·10⁻⁴, y 2,6·10⁻⁴ en el caso más exigente, N = 700 con obstáculos.

## 16. Obstáculos en el centro — `slide-16-animacion-centro.png`

- xo = r: los dos obstáculos se tocan y forman un solo blanco de 4r de ancho en el centro.
- Es la configuración del barrido de N y la de conversión más lenta de todo el trabajo.
- Cuadro congelado en t = 10 s; el video completo está en el link.

## 17. Tiempo de ejecución contra N — `slide-17-tiempo-ejecucion-vs-N.png`

- Paso temporal: siempre 600 000 pasos y costo O(N) por la celda de índice. El ajuste da t ∝ N^0,88 (la recta punteada azul).
- Eventos (TP3): t ∝ N^3,52 (la recta punteada roja), porque cada choque rehace parte del calendario y los choques crecen con N.
- Se cruzan cerca de N = 470; a N = 600 los eventos cuestan 2,9 veces más (14,8 s contra 42,3 s).
- Las barras de desvío están dibujadas pero no se ven: la figura abarca cuatro décadas y σ/⟨t⟩ es como mucho el 4 %. Cuánto vale está escrito arriba a la izquierda.
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

## 18. Obstáculos en la posición óptima — `slide-18-animacion-optimo.png`

- xo = 0,20 m: separados, cada obstáculo barre su zona y ninguno queda a la sombra del otro.
- A los 10 s ya hay 75 usadas, contra 56 con los obstáculos en el centro.

## 19. Obstáculos en el borde — `slide-19-animacion-borde.png`

- xo = R − r: pegados a la pared, quedan fuera del camino de casi todas las trayectorias.
- A los 10 s, 51 usadas: la conversión más lenta de las tres.

## 20. Fracción de usadas: los tres xo típicos — `slide-20-Fu-vs-t-xo-tipicos.png`

- Las tres curvas juntas, que es como lo pide el ítem 2.2: Fu(t) para pocos valores típicos de xo. Cada una es el promedio de las 15 realizaciones y la banda es ±1 desvío entre ellas.
- Misma forma, corrida en el tiempo: el óptimo llega a 0,9 en 14,8 s, el centro en 26,5 s y el borde en 31,2 s. El punto sobre la línea de 0,9 es ⟨t90⟩ y la barra horizontal su desvío.
- El óptimo además es el de menos dispersión (±1,7 s contra ±3,4 y ±3,1).
- La cola es larga en los tres: ⟨t100⟩ ≈ 2,3 ⟨t90⟩. Ninguna realización se queda sin convertir antes de tmax = 100 s, así que no hay que reportar Fu(tmax).

## 21. ⟨t90⟩ contra la posición de los obstáculos — `slide-21-t90-vs-xo.png`

- Sí hay posición óptima: ⟨t90⟩ cae de 26,5 s en xo = r a 14,8 s en 0,20 m y sube a 31,2 s contra la pared.
- El mínimo es un plateau ancho, de 0,15 a 0,35 m: esos puntos empatan dentro del desvío.
- Con N = 20 la curva baja entera pero el mínimo cae en el mismo lugar: la posición óptima no depende de la frecuencia de choques.

## 22. Sin obstáculos — `slide-22-animacion-sin-obstaculos.png`

- Sin conversión, todas quedan frescas: es el sistema con el que se eligió el paso y el de la distribución de velocidades.
- Arrancan todas con |v| = v0 y sólo los choques entre partículas reparten la energía; el choque con la pared conserva |v|.

## 23. Distribución del módulo de la velocidad — `slide-23-f-v-vs-t.png`

- En t = 0 f(v) es una delta en v0 que se sale de la figura.
- A los 0,15 s el pico ya cayó a un tercio y apareció la cola de velocidades bajas; la curva de t = 30 s es el estacionario, y desde 0,5 s las curvas ya no se distinguen entre sí (por eso están éstas tres y no más).
- Las tres son instantes exactos, cada uno con su t: el estacionario se muestra como el último cuadro guardado, no como un promedio sobre cuadros. Ese promedio se usa en la figura del ajuste, que es donde hace falta la estadística.
- f(v) se ensancha sin que cambie E: el sistema es conservativo.
- Las barras son el **desvío estándar entre las 30 realizaciones**, intervalo por intervalo, la misma convención que el resto de las figuras. En un instante suelto son grandes (51 % en promedio) porque cada realización reparte sus 100 partículas en 40 intervalos; por eso están dibujadas más tenues que las curvas.

## 24. Ajuste de Maxwell-Boltzmann — `slide-24-f-v-ajuste.png`

- Maxwell-Boltzmann en dos dimensiones con kBT como único parámetro libre.
- kBT = 12,41 mJ contra mv0²/2 = 12,50 mJ: −0,7 %.
- m⟨v²⟩/2 = 12,32 mJ es un poco menor: en promedio el 1,4 % de E está en los resortes.
- Acá la estacionaria junta todos los cuadros con t ≥ 10 s de las 30 realizaciones (1,2·10⁶ muestras), así que el desvío entre realizaciones baja al 4,8 % y las barras se ven como una marca sobre cada barra.
- Si preguntan qué son las barras: el desvío estándar entre realizaciones, intervalo por intervalo, igual que en todas las demás figuras.

## 25. Error cuadrático medio del ajuste — `slide-25-E-vs-kT.png`

- Método de la Teórica 0: se recorre kBT en una grilla y se toma el mínimo de E(kBT).
- El error se duplica ya en 12,31 y 12,53 mJ: el ajuste queda determinado dentro del 1 %.
- "Energía térmica" es el nombre que le da el enunciado a kBT: es el único parámetro libre del ajuste, no una temperatura medida.

## 26. Efecto de la densidad — `slide-26-t90-t100-vs-densidad.png`

- Dos ejes y nada más, que es lo que pide el ítem: la densidad ρ = N/πR² (definida en la diapositiva de parámetros) y el tiempo de conversión. El N de cada densidad está en la tabla: ρ = 12 es N = 10, ρ = 122 es N = 100, ρ = 245 es N = 200.
- ⟨t90⟩ ≈ 21 s de N = 10 a 50 y 23,7 s en N = 100; desde N = 200 ninguna realización llega a 0,9 en 30 s, y por eso las curvas se cortan aunque el eje siga: que no haya puntos a la derecha es parte del resultado.
- Los símbolos huecos son los N en los que alguna realización no llegó antes de tf: a N = 5 llegó 1 de 10 y a N = 10, 5 de 10. Ahí el promedio es sólo de las que llegaron, o sea que está sesgado hacia abajo, y tiene que verse que lo está.
- Sí hay densidad óptima, N = 30–100: es el único tramo donde llegan las 10 realizaciones y ⟨t90⟩ es mínimo. Por debajo faltan choques (con N = 1 convierte sólo el 13 %, 40 de 300 realizaciones, exactamente las de parámetro de impacto b < 3r) y por arriba se achica el camino libre.
- Fu(tf) lo confirma: 0,58 en N = 5, máximo 0,97 en N = 30–50, 0,84 en N = 200 y 0,01 en N = 700 (el 82 % del área). Está medido y la figura está en `data/figures/2.4_densidad/Fu_tf_vs_densidad_M10.png`, fuera de la charla: ponerla como segundo eje de la figura del ítem daba cuatro escalas en un panel.
- Si preguntan por qué no está Fu(tf) en la figura: porque el ítem pide ⟨t90⟩ y ⟨t100⟩ en función de la densidad, dos ejes; la tenemos aparte y la mostramos si quieren.

## 27. Posición óptima para cada densidad — `slide-27-mapa-t90-xo-N.png`

- El barrido es de 16 posiciones × 10 densidades × 20 realizaciones (3200 corridas): hace falta esa resolución para distinguir si el óptimo se corre con N o si es siempre el mismo.
- La escala de colores está dada vuelta a propósito: el rojo es la conversión **más rápida**, porque lo que tiene que saltar a la vista es el óptimo y no el peor caso. Y está recortada en 38 s (1,3 veces el más alto de los mínimos de cada fila, la flecha de la barra lo marca): los bordes de las densidades extremas llegan a 70 s y se llevaban media escala ellos solos.
- La mancha roja **cierra por arriba y por abajo**: hay óptimo en las dos variables. Por eso está la fila de N = 5, que es la que la cierra por abajo.
- A propósito no marcamos ninguna celda: cuál de las del fondo sale la más baja es en buena parte azar (a N = 50 cae en 0,175 m y a N = 150 en 0,275 m, y las dos tienen el mismo óptimo dentro del error). El número sale de ajustar una parábola a cada fila sobre el mismo tramo, xo = 0,10–0,40 m, y quedarse con el vértice.
- De N = 20 en adelante (ocho densidades) los vértices dan **0,237 ± 0,011 m**: el óptimo no se corre con la densidad en todo ese rango, y no es exactamente 0,2 sino 0,24 m (0,46 R).
- Las dos densidades más bajas sí se corren hacia afuera: 0,287 ± 0,020 m en N = 5 y 0,350 ± 0,031 m en N = 10 (a 2,5 y 3,7 σ del promedio). Con tan pocas partículas casi no hay choques y la conversión la decide el parámetro de impacto de cada trayectoria, así que separar los obstáculos cubre más parámetros de impacto. Es el mismo argumento del ítem 2.4.a (con N = 1 sólo convierte si b < 3r). Sobre las diez densidades el ajuste da −0,018 ± 0,007 m por década de N, y ese corrimiento lo aportan enteramente esas dos filas.
- Los extremos son siempre los peores, y cuál de los dos es peor cambia con la densidad: a N = 5 el centro es cuatro veces y media el mínimo, a N = 10 centro y pared cuestan lo mismo (30,1 y 29,5 s), y a N = 300 la pared es claramente peor (69,8 contra 54,3 s). El castigo de la pared crece con N: 1,9 veces el mínimo a N = 20 y 2,4 a N = 300.
- ⟨t90⟩ en el óptimo pasa de 11,0 s (N = 10) a 29,5 s (N = 300), y vuelve a subir a 14,3 s en N = 5.
- El barrido del mapa corre con tmax = 300 s, no 100: a N = 5 hay realizaciones que tardan 150 s en convertir las cinco partículas. De N = 10 para arriba no cambia nada, ninguna pasa de 70 s.
- Si preguntan por qué el barrido corta en Fu = 0,9: el mapa sólo mide t90, y seguir hasta que se convierten todas cuesta el triple de cómputo (a N = 300, t90 ≈ 29 s contra t100 ≈ 98 s de tiempo simulado). Está verificado contra una corrida completa: la conversión número 90 de la misma semilla cae exactamente en el mismo instante.

## 28. Conclusiones (separador)

- Lo que queda de cada ítem.

## 29. Conclusiones

- Beeman y Verlet original son de segundo orden en el oscilador; Beeman es el mejor. Δt = 5·10⁻⁵ s por conservación de la energía.
- El costo del paso temporal crece casi lineal con N y el de los eventos mucho más rápido: se cruzan cerca de N = 470. Los exponentes ajustados, si los piden: 0,88 y 3,52.
- Hay un xo óptimo en 0,2–0,3 m, el mismo de N = 20 a 300; f(v) llega a Maxwell-Boltzmann en medio segundo con kBT = mv0²/2; y con los obstáculos en el centro hay una densidad óptima en N = 30–50.

## 30. Uso de agentes de IA

- Claude Code (Anthropic), modelos Claude Opus 5 y Claude Fable 5.1, para programar el motor, los scripts y el LaTeX, y para revisar código.
- Las decisiones de modelado, el análisis y las conclusiones son del grupo; todo lo generado se verificó contra las figuras.

## Cierre

- Muchas gracias; preguntas.
