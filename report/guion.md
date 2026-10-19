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
- Para el oscilador (sistema 1), además Velocity Verlet, Beeman y Euler predictor-corrector.
- En el oscilador la fuerza depende de la velocidad: los esquemas difieren en con qué v evalúan a(t + Δt), y de ahí sale el orden de cada uno.
- Si preguntan por Velocity Verlet: la Teórica (diapositiva 17) lo escribe con los dos pasos intermedios sobre la velocidad, pero no dice con qué v se evalúa a(t + Δt), porque no escribe el caso con fuerza dependiente de v. Entre los dos pasos intermedios la única velocidad que existe es la de medio paso, y es la que usamos.
- Está medido qué cuesta (`make velocity-verlet-variantes`): con la de medio paso el ECM va como Δt^2,04 (orden 1); despejando v(t + Δt) o prediciéndola con Euler, Δt^4,00 (orden 2). El error de v(t + Δt/2) respecto de v(t + Δt) es O(Δt) y entra en a(t + Δt) multiplicado por Δt/2. Beeman no lo pierde porque su predictor es de O(Δt²).
- Y despejarla no daría un esquema nuevo: la recurrencia que queda es Verlet original (coinciden dentro del 0,2 % de su propio error mientras el redondeo no mande). O sea que la variante de medio paso es la que mantiene a Velocity Verlet como uno de los cuatro esquemas distintos que pide el enunciado.

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
- Posición de los obstáculos: 11 valores de xo con N = 100 y 20, 15 realizaciones. Velocidades: N = 100, 10 realizaciones. Densidad: las corridas del 2.1.b y un barrido (xo, N) con 6 realizaciones.

## 12. Resultados (separador)

- Primero el oscilador, después el paso y el costo, luego obstáculos, velocidades y densidad.

## 13. Sistema 1: error cuadrático medio contra el paso — `slide-13-ECM-vs-dt.png`

- Beeman y Verlet original van los dos como ECM ∝ Δt⁴, o sea error de segundo orden, y en diez órdenes de magnitud se superponen. Velocity Verlet y Euler p-c van como Δt², un orden menos, por cómo evalúan a(t + Δt) (ya se explicó en la diapositiva de integración).
- A Δt = 10⁻⁴ s hay ocho órdenes entre Beeman y Euler p-c. Beeman es el mejor: tiene el menor ECM en 8 de los 9 pasos del barrido.
- Si preguntan por qué Beeman y no Verlet, que en la figura se superponen: lo que los separa no es la pendiente sino la constante. Dividiendo el ECM por Δt⁴ queda 330 para Beeman y 380 para Verlet, un 15 % más de ECM con el mismo paso (la figura está en `data/figures/1_oscilador/ECM_constante_vs_dt.png`, fuera de la charla porque el enunciado pide una sola diapositiva del sistema 1).
- Esa diferencia es toda de la fuerza que depende de la velocidad. Con γ = 0 las dos constantes dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).
- El punto de Verlet en Δt = 10⁻⁵ s no está: ahí su ECM es ruido de redondeo del doble y no el error del esquema.

## 14. Energía total contra el tiempo — `slide-14-energia-vs-t.png`

- E0 = 3,75 J y el sistema es conservativo: todo lo que se aparta es error del integrador.
- 5·10⁻⁴ s deriva 2,6 % y 2·10⁻⁴ s un 0,6 % (hacia abajo); de 10⁻⁴ s para abajo no se distinguen de E0.
- Son 4 de los 7 Δt medidos: los tres que faltan no se leerían en esta escala. Δt = 10⁻³ s se dispara hasta 45 J y aplastaría a todas las demás contra E0 (el choque dura 3,5 ms y entran sólo tres pasos); 2·10⁻⁵ y 10⁻⁵ s caen encima de 5·10⁻⁵. El barrido completo está en la figura de la deriva, que es la que elige el paso.

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
- Las barras de desvío están dibujadas pero no se ven: son como mucho el 4 % del valor y la figura abarca cuatro décadas. Dice cuánto valen arriba a la izquierda.

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
- A los 0,5 s ya es indistinguible de la estacionaria.
- f(v) se ensancha sin que cambie E: el sistema es conservativo.

## 24. Ajuste de Maxwell-Boltzmann — `slide-24-f-v-ajuste.png`

- Maxwell-Boltzmann en dos dimensiones con kBT como único parámetro libre.
- kBT = 12,42 mJ contra mv0²/2 = 12,50 mJ: −0,6 %.
- m⟨v²⟩/2 = 12,32 mJ es un poco menor: en promedio el 1,4 % de E está en los resortes.

## 25. Error cuadrático medio del ajuste — `slide-25-E-vs-kT.png`

- Método de la Teórica 0: se recorre kBT en una grilla y se toma el mínimo de E(kBT).
- El error se duplica ya en 12,2 y 12,7 mJ: el ajuste queda determinado dentro del 2 %.
- "Energía térmica" es el nombre que le da el enunciado a kBT: es el único parámetro libre del ajuste, no una temperatura medida.

## 26. Efecto de la densidad — `slide-26-t90-t100-vs-densidad.png`

- El eje de abajo es la densidad ρ = N/πR², que es como lo pide el enunciado, y el de arriba el N que le corresponde; ρ quedó definida en la diapositiva de parámetros.
- ⟨t90⟩ ≈ 21 s de N = 10 a 50 y 23,7 s en N = 100; desde N = 200 ninguna realización llega a 0,9 en 30 s.
- Sí hay densidad óptima: Fu(tf) es máxima en N = 30–50 (0,97). Sin choques cada partícula conserva su momento angular y no llega al centro (con N = 1 convierte sólo el 13 %, 40 de 300 realizaciones, exactamente las de parámetro de impacto b < 3r); con muchas, el camino libre se achica.
- A N = 700, el 82 % del área, se convierte el 1 %.
- Los símbolos huecos son los N en los que alguna realización no llegó antes de tf: el promedio se toma sobre las que sí llegaron y Fu(tf) está en el eje de la derecha, que es lo que pide el enunciado cuando no se alcanza la fracción.

## 27. Posición óptima para cada densidad — `slide-27-mapa-t90-xo-N.png`

- El círculo blanco de cada fila marca el xo que minimiza ⟨t90⟩ para ese N; está dicho arriba del mapa.
- El mínimo cae en xo = 0,2–0,3 m para las cinco densidades: no se corre con N.
- Los extremos son siempre los peores, y el castigo crece con la densidad: 1,9 veces el óptimo a N = 20 y 2,4 a N = 300.
- ⟨t90⟩ en el óptimo pasa de 11,8 s a 28,9 s entre N = 20 y 300.

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
