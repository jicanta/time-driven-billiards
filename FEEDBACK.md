# Devoluciones de la cátedra que se aplican al TP4

El TP3 se entregó el 28/09/2026 y obtuvo **10 puntos**, así que lo que se
mantiene acá es lo que funcionó: el mismo esquema de presentación, las mismas
convenciones de figuras y el mismo reparto entre motor y post-procesamiento.
Las devoluciones de abajo son las del TP2 (las referencias `D<n>` son
diapositivas de ese TP) más las dos sobre el borrador de las diapositivas del
TP3, del 18/09 y del 26/09. Los errores que se repiten de un TP al siguiente
penalizan: esta lista se vuelve a revisar contra las diapositivas antes de
entregar.

## Comentarios generales (TP2)

- En las presentaciones los miembros no deben pisarse en la exposición ni
  mucho menos "aclarar" lo que creen que el compañero no dijo o dijo mal.
  Además deben distribuir de forma pareja la cantidad y calidad de lo
  expuesto.
- Salvo que el cuerpo docente lo indique, no se pueden evitar secciones de la
  presentación por más de que el contenido ya se haya escuchado en
  presentaciones previas. Sobre todo saltarse la explicación de los
  observables no debe ocurrir.
- Ser consistentes en la terminología y sostenerla, sin utilizar palabras no
  definidas previamente como parte central de lo expuesto.
- Cuidar que el tamaño de la fuente sea armonioso dentro de la diapositiva.
  Que sea más grande la leyenda que el título se ve mal; que de una
  diapositiva a la otra el tamaño cambie radicalmente, también.
- Mostrar el trabajo intermedio al cuerpo docente antes de presentarlo. La
  idea no es agarrar un trabajo y complejizarlo de más.
- Cualquier miembro del grupo debe poder explicar todo lo presentado.
- Subir todo el material al Campus.

## Presentación (TP2)

- D6: no llenar la diapositiva con detalles de implementación que se pueden
  mencionar oralmente.
- D8: las unidades van en un solo lugar de la tabla de parámetros, junto con
  el nombre de la variable o en el valor, nunca mezcladas. Sin marcas en el
  esquema del recinto que no signifiquen nada.
- D9: no saltearse los observables.
- D11: no poner carátulas intermedias.
- D12: en la presentación en vivo no deben ir los links, solo en la que se
  envía a la cátedra. La proporción entre la etiqueta de los ejes y el
  gráfico del fotograma debe ser la misma que la del video.
- D13, D16, D21, D22, D23: la leyenda debe ir **dentro** del gráfico, sin
  taparlo y sin ser más grande que el texto de la diapositiva. Los instantes
  puntuales en los que se considera alcanzado el estacionario no son
  relevantes: alcanza con marcarlos en la figura.
- D31: las conclusiones deben ser un punteo simple, sólo con cifras que
  salgan de una figura mostrada.

## Devoluciones sobre el borrador del TP3 (18/09 y 26/09)

- Sin diapositiva de contenido ni carátulas de bloque dentro de Resultados;
  sólo los separadores de sección que pide la guía.
- Poco detalle al inicio: cada concepto se explica **una vez**, donde hace
  falta.
- Lo importante ocupa la mayor parte de la pantalla: figura grande, texto
  mínimo, sin espacios en blanco. Cada diapositiva de figura es el gráfico
  grande más dos o tres viñetas con lo que se lee en él.
- Tabla de parámetros separada en **fijos y variables**, angosta para que el
  esquema del sistema sea grande.
- UML sólo del motor de simulación, sin archivos ni post-procesamiento.
- Nombres de eje en palabras, con la unidad y **en una sola línea**; coma
  decimal; el observable va al eje con su símbolo, no con la frase entera.
- Sin rectas de referencia dibujadas a mano: si se compara con una ley de
  potencia, se ajusta y se informa el exponente.
- El error de un ajuste es el **error cuadrático medio**, y se muestra la
  curva E(parámetro) con su mínimo marcado (método de la Teórica 0).
- En Resultados, un bloque por caso con el mismo esquema: animación,
  evolución temporal del observable y después la variable contra el
  observable.
- Sin la variable `M` en las figuras: se dice "promedio sobre N
  realizaciones".
- Las conclusiones son cuatro renglones.

## Cómo se aplica en el TP4

- **Secciones tal como las pide la guía** (§2): Introducción = el sistema real y
  las ecuaciones del modelo (dos diapositivas, el máximo es tres);
  Implementación = los cuatro esquemas de integración y el UML **sólo del
  motor**; Simulaciones = la tabla de parámetros con el esquema del dominio,
  los observables **definidos matemáticamente** (incluido cómo se promedia) y
  los casos con el número de realizaciones y los tiempos; Resultados;
  Conclusiones. Diapositiva de cierre "Muchas gracias" (§2.6), sin la palabra
  "preguntas".
- **Cada diapositiva de figura lleva al costado los parámetros fijos** bajo los
  que se obtuvo (§1.7), como última viñeta en gris y más chica.
- **En Resultados, por cada caso, el orden de la guía** (§2.4.1 a §2.4.3):
  primero la animación, después `Fu(t)` de ese caso y recién al final la
  variable contra el observable.
- La cátedra pidió después (21/10) que el sistema 1 lleve también la energía
  del oscilador contra el tiempo, en valor absoluto: son dos diapositivas.
- El enunciado pedía una sola diapositiva para el sistema 1, la de ECM contra
  dt de los cuatro esquemas ("no mostrar animaciones, ni introducción, ni
  ninguna otra información"): esa sigue siendo la única con el ECM, y la de
  energía es la que agregó la cátedra.
- Terminología fija y definida antes de usarse: partícula fresca/usada,
  conversión, obstáculo, partícula imagen, paso de integración `dt`, paso de
  guardado `dt2`, deriva de energía, fracción de usadas `Fu`, `t90`, `t100`,
  energía térmica `kBT`.
- Tabla de parámetros con las unidades en un solo lugar y sin semillas;
  esquema del dominio circular con `R`, `r` y `xo` marcados.
- Leyendas dentro del gráfico, más chicas que el texto de la diapositiva y
  sin tapar datos; tamaños de fuente parejos entre diapositivas.
- Cuadro fijo de cada animación con las mismas proporciones que el video; los
  links a YouTube sólo en el PDF que se entrega.
- Los dos ajustes del trabajo (`kBT` de Maxwell-Boltzmann y las leyes de
  potencia de los tiempos de ejecución) siguen el método de la Teórica 0, con
  la curva de error cuadrático medio del primero en su propia diapositiva.
- Conclusiones como punteo corto y sólo sobre lo mostrado.
- Reparto parejo de la exposición entre los tres integrantes, sin
  interrupciones ni aclaraciones sobre lo que dijo el compañero.
- Diapositiva final con la declaración de uso de agentes de IA (ítem 2.5):
  qué agente y modelo se usó y de qué manera.
- Mostrar el borrador a los docentes antes de la fecha y subir todo al
  Campus.
