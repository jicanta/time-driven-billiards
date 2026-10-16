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

## 6. Motor de simulación — `slide-06-motor-uml.png`

- C++17: Simulation lleva el paso, Forces suma las fuerzas (pares vecinos, obstáculos, imagen de la pared) y Grid es la celda de índice.
- El contacto alcanza a 2r, así que la celda deja el costo de un paso en O(N): por eso llegamos a N = 700.
- El motor no calcula observables: escribe el estado cada Δt2 y el instante de cada conversión; todo lo demás es post-proceso.

## 7. Simulaciones (separador)

- Parámetros, observables y los casos que se corrieron.

## 8. Parámetros — `slide-08-parametros-dominio.png`

- La tabla va en tres bloques. **Fijos**, lo que no se toca en todo el trabajo: R = 0,51 m, r = 0,0175 m, m = 0,025 kg, v0 = 1 m/s y k = 10⁴ N/m.
- **Variables**, lo que se barre: N de 5 a 700, y xo de r (obstáculos en contacto entre sí) a R − r (en contacto con la pared).
- **Simulación**, lo que fija la integración y no el sistema: Δt = 5·10⁻⁵ s, que se elige en Resultados por conservación de la energía, más Δt₂ y t_f, que van por caso y están en la diapositiva siguiente.
- πR² = 0,817 m², la misma área que la mesa del TP3: igual densidad a igual N.

## 9. Observables

- Conversión: Fu(t) = Nu/N, y t90 y t100 en el instante exacto de cada conversión.
- Energía total sobre los estados guardados (cinética más elástica) y la deriva relativa máxima D(Δt), un escalar por paso.
- f(v) en 40 intervalos con las N partículas de las M realizaciones; para el sistema 1, el ECM contra la solución analítica. Las barras de error son el desvío estándar entre realizaciones.

## 10. Casos estudiados

- Sistema 1: 4 esquemas, 9 pasos de 5·10⁻³ a 10⁻⁵ s. Paso temporal: N = 300 sin obstáculos, 7 pasos, verificado a N = 700 con obstáculos.
- Costo: xo = r, N de 50 a 700, 10 realizaciones por N, contra el motor del TP3 en la misma máquina.
- Posición de los obstáculos: 11 valores de xo con N = 100 y 20, 15 realizaciones. Velocidades: N = 100, 10 realizaciones. Densidad: las corridas del 2.1.b y un barrido (xo, N) con 6 realizaciones.

## 11. Resultados (separador)

- Primero el oscilador, después el paso y el costo, luego obstáculos, velocidades y densidad.

## 12. Sistema 1: error cuadrático medio contra el paso — `slide-12-ECM-vs-dt.png`

- Panel de arriba: Beeman y Verlet original van los dos como ECM ∝ Δt⁴, o sea error de segundo orden, y en diez órdenes de magnitud se superponen. Velocity Verlet y Euler p-c van como Δt², un orden menos, por cómo evalúan a(t + Δt) (ya se explicó en la diapositiva de integración).
- Panel de abajo: dividir por Δt⁴ saca la pendiente que comparten y deja la constante del error. Ahí se ve que no son iguales: Verlet queda en 380 y Beeman en 330, un 15 % más de ECM con el mismo paso.
- Esa diferencia es toda de la fuerza que depende de la velocidad. Con γ = 0 las dos constantes dan 21000 y 21019, iguales dentro del redondeo (`make oscilador-sin-amortiguamiento`).
- El punto de Verlet en Δt = 10⁻⁵ s no está: ahí su ECM es ruido de redondeo del doble y no el error del esquema. La ampliación además arranca en 5·10⁻⁵ s, porque en 2·10⁻⁵ el redondeo ya corre la medición un 20 %.
- A Δt = 10⁻⁴ s hay ocho órdenes entre Beeman y Euler p-c: Beeman es el mejor para este sistema.

## 13. Energía total contra el tiempo — `slide-13-energia-vs-t.png`

- E0 = 3,75 J y el sistema es conservativo: todo lo que se aparta es error del integrador.
- Con Δt = 10⁻³ s explota hasta 45 J: el choque dura 3,5 ms y entran sólo tres pasos.
- En la ampliación, 5·10⁻⁴ s deriva 2,6 % y 2·10⁻⁴ s un 0,6 %; de 10⁻⁴ s para abajo no se distinguen de E0.

## 14. Elección del paso: deriva relativa máxima — `slide-14-deriva-vs-dt.png`

- D(Δt) resume cada corrida en un número; sobre los pasos estables ajusta Δt^2,0, el segundo orden de Verlet.
- Criterio: el Δt más largo con D ≤ 10⁻³, el más barato con el error aceptado.
- Queda Δt = 5·10⁻⁵ s: D = 3,8·10⁻⁴, y 2,6·10⁻⁴ en el caso más exigente, N = 700 con obstáculos.

## 15. Obstáculos en el centro (animación) — `slide-15-animacion-centro.png`

- xo = r: los dos obstáculos se tocan y forman un solo blanco de 4r de ancho en el centro.
- Es la configuración del barrido de N y la de conversión más lenta de todo el trabajo.
- Cuadro congelado en t = 10 s; el video completo está en el link.

## 16. Tiempo de ejecución contra N — `slide-16-tiempo-ejecucion-vs-N.png`

- Paso temporal: t ∝ N^0,91, siempre 600 000 pasos y costo O(N) por la celda de índice.
- Eventos (TP3): t ∝ N^3,52, porque cada choque rehace parte del calendario y los choques crecen con N.
- Se cruzan cerca de N = 490; a N = 600 los eventos cuestan 2,3 veces más.

## 17. Fracción de usadas: obstáculos en el centro — `slide-17-Fu-vs-t-centro.png`

- Las 15 realizaciones casi se superponen: la mitad se convierte en 7,6 s, pero la cola es larga.
- ⟨t90⟩ = 26,5 ± 3,4 s: los dos obstáculos se tapan entre sí y el blanco efectivo es poco más que el de uno solo.

## 18. Obstáculos en la posición óptima (animación) — `slide-18-animacion-optimo.png`

- xo = 0,20 m: separados, cada obstáculo barre su zona y ninguno queda a la sombra del otro.
- A los 10 s ya hay 75 usadas, contra 56 con los obstáculos en el centro.

## 19. Fracción de usadas: posición óptima — `slide-19-Fu-vs-t-optimo.png`

- La misma forma corrida a la izquierda: la mitad en 4,7 s y ⟨t90⟩ = 14,8 ± 1,7 s.
- Casi la mitad del tiempo que con los obstáculos juntos, y con la mitad de dispersión entre realizaciones.

## 20. Obstáculos en el borde (animación) — `slide-20-animacion-borde.png`

- xo = R − r: pegados a la pared, quedan fuera del camino de casi todas las trayectorias.
- A los 10 s, 51 usadas: la conversión más lenta de las tres.

## 21. Fracción de usadas: obstáculos en el borde — `slide-21-Fu-vs-t-borde.png`

- ⟨t90⟩ = 31,2 ± 3,1 s: la posición más lenta del barrido, 2,1 veces el óptimo.
- En las tres posiciones ⟨t100⟩ ≈ 2,3 ⟨t90⟩ y con mucho más desvío: la última partícula es la que tarda.

## 22. ⟨t90⟩ contra la posición de los obstáculos — `slide-22-t90-vs-xo.png`

- Sí hay posición óptima: ⟨t90⟩ cae de 26,5 s en xo = r a 14,8 s en 0,20 m y sube a 31,2 s contra la pared.
- El mínimo es un plateau ancho, de 0,15 a 0,35 m: esos puntos empatan dentro del desvío.
- Con N = 20 la curva baja entera pero el mínimo cae en el mismo lugar: la posición óptima no depende de la frecuencia de choques.

## 23. Sin obstáculos (animación) — `slide-23-animacion-sin-obstaculos.png`

- Sin conversión, todas quedan frescas: es el sistema con el que se eligió el paso y el de la distribución de velocidades.
- Arrancan todas con |v| = v0 y sólo los choques entre partículas reparten la energía; el choque con la pared conserva |v|.

## 24. Distribución del módulo de la velocidad — `slide-24-f-v-vs-t.png`

- En t = 0 f(v) es una delta en v0 que se sale de la figura.
- A los 0,5 s ya es indistinguible de la estacionaria.
- f(v) se ensancha sin que cambie E: el sistema es conservativo.

## 25. Ajuste de Maxwell-Boltzmann — `slide-25-f-v-ajuste.png`

- Maxwell-Boltzmann en dos dimensiones con kBT como único parámetro libre.
- kBT = 12,42 mJ contra mv0²/2 = 12,50 mJ: −0,6 %.
- m⟨v²⟩/2 = 12,32 mJ es un poco menor: en promedio el 1,4 % de E está en los resortes.

## 26. Error cuadrático medio del ajuste — `slide-26-E-vs-kT.png`

- Método de la Teórica 0: se recorre kBT en una grilla y se toma el mínimo de E(kBT).
- El error se duplica ya en 12,2 y 12,7 mJ: el ajuste queda determinado dentro del 2 %.

## 27. Efecto de la densidad — `slide-27-t90-t100-vs-densidad.png`

- ⟨t90⟩ ≈ 21 s de N = 10 a 50 y 23,7 s en N = 100; desde N = 200 ninguna realización llega a 0,9 en 30 s.
- Sí hay densidad óptima: Fu(tf) es máxima en N = 30–50 (0,97). Sin choques cada partícula conserva su momento angular y no llega al centro (con N = 1 convierte sólo el 13 %); con muchas, el camino libre se achica.
- A N = 700, el 82 % del área, se convierte el 1 %.

## 28. Posición óptima para cada densidad — `slide-28-mapa-t90-xo-N.png`

- El mínimo cae en xo = 0,2–0,3 m para las cinco densidades: no se corre con N.
- Los extremos son siempre los peores, y el castigo crece con la densidad: 1,9 veces el óptimo a N = 20 y 2,4 a N = 300.
- ⟨t90⟩ en el óptimo pasa de 11,8 s a 28,9 s entre N = 20 y 300.

## 29. Conclusiones (separador)

- Lo que queda de cada ítem.

## 30. Conclusiones

- Beeman y Verlet original son de segundo orden en el oscilador; Beeman es el mejor. Δt = 5·10⁻⁵ s por conservación de la energía.
- El paso temporal escala como N^0,91 y los eventos como N^3,52: se cruzan cerca de N = 490.
- Hay un xo óptimo en 0,2–0,3 m, el mismo de N = 20 a 300; f(v) llega a Maxwell-Boltzmann en medio segundo con kBT = mv0²/2; y con los obstáculos en el centro hay una densidad óptima en N = 30–50.

## 31. Uso de agentes de IA

- Claude Code (Anthropic), modelos Claude Opus 5 y Claude Fable 5.1, para programar el motor, los scripts y el LaTeX, y para revisar código.
- Las decisiones de modelado, el análisis y las conclusiones son del grupo; todo lo generado se verificó contra las figuras.

## Cierre

- Muchas gracias; preguntas.
