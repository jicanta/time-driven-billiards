# TP4 -- todo el flujo desde la raiz del repositorio.
#
#   make build          compila el motor (engine/build/billar)
#   make oscilador      sistema 1: integra el oscilador con los 4 esquemas y todos los dt
#   make oscilador-figuras  ECM vs dt (la unica figura del sistema 1), la constante
#                           del error de los dos de cuarto orden y la trayectoria
#   make oscilador-sin-amortiguamiento  control: con gamma = 0 Beeman y Verlet dan la misma constante
#   make velocity-verlet-variantes  por que Velocity Verlet pierde un orden: las 4 maneras
#                           de evaluar a(t+dt) y el orden que da cada una
#   make energia        item 2.1.a: N = 300 sin obstaculos, un barrido de dt con cuadros
#   make energia-figuras    energia vs t (los 4 dt representativos) y deriva vs dt
#   make energia-densa  verifica el dt elegido en el caso mas denso (N = 700 con obstaculos)
#   make bench          item 2.1.b: tiempos contra N (maquina descargada)
#   make bench-tp3      los mismos tiempos con el motor del TP3 (dirigido por eventos)
#   make bench-figuras      tiempo de ejecucion vs N de los dos paradigmas
#   make obstaculos     item 2.2: barrido de xo con N = 100 y N = 20
#   make obstaculos-figuras <t90> vs xo y Fu(t) de los tres xo tipicos, en una figura
#   make velocidades    item 2.3: N = 100 sin obstaculos, cuadros hasta el estacionario
#   make velocidades-figuras  f(v) por instante, ajuste de Maxwell-Boltzmann y E(kT)
#   make densidad       item 2.4.a: barrido de N con xo = r y tmax largo, sin corte
#   make densidad-figuras   item 2.4.a: <t90> y <t100> vs densidad
#   make mapa           item 2.4.b: barrido (xo, N) (el enunciado lo da como opcional; se hace)
#                           10 densidades x 16 posiciones x 20 realizaciones, en paralelo
#   make mapa-figuras       mapa de calor de <t90> en el plano (xo, N)
#   make check          corrida de validacion: energia, solapamientos y escapes
#   make una-particula  N = 1: sin choques solo se convierte si el parametro de impacto es < 3r (item 2.4.a)
#   make animations     corridas caracteristicas, videos y cuadro fijo de cada una
#   make youtube        copia los videos con nombres legibles en youtube/
#   make gifs           los mismos cuatro videos como GIF en gif/ (para embeber en la presentacion en vivo)
#   make figuras-diapositivas  las figuras de las diapositivas (data/figuras_diapositivas);
#                           los 4 cuadros fijos de animacion salen de make animations
#   make slides-images      las 20 imagenes de la presentacion numeradas por diapositiva:
#                           copia las 15 figuras y renderiza los 5 esquemas TikZ
#   make slides-images-tikz renderiza a PNG los esquemas TikZ de las diapositivas (report/figuras)
#   make documentos     compila report/presentacion.tex (la presentación, lee slides-images/)
#   make capturas       PNG de diapositivas sueltas (la tabla de parametros) en capturas/
#   make entrega        SdS_TP4_2026Q2G10S2_Codigo.zip (< 100 KB) y ..._Presentación.pdf (la beamer)
#   make todo           oscilador + energia(+densa) + bench + obstaculos + velocidades + mapa
#   make all            alias de todo
#   make clean-figures  borra data/figures y data/figuras_diapositivas
#
# Las variables se pueden pisar: make bench NS=100,200 REPEATS=5
#                                make obstaculos XOS=0.0175,0.25 SEEDS=3

PY       ?= python3
BILLAR   := engine/build/billar

# --- parametros comunes ----------------------------------------------------
# dt sale del item 2.1.a: es el mas largo cuya deriva relativa de energia
# queda por debajo de 10^-3 (ver data/energia/resumen.csv). dt2 es el paso con
# el que se guarda el estado, siempre un numero entero de dt.
DT       ?= 5e-5
DT2      ?= 0.01
# Base de las semillas: la realizacion k usa SEED0 + k (carpetas s7, s8, ...).
# Todas las corridas con conversiones o cuadros usan la misma base, asi que la
# primera realizacion de un barrido y la de la animacion son la misma
# trayectoria.
SEED0    ?= 7
SEEDS    ?= 15
# xo = r: los dos obstaculos en contacto entre si, que es la configuracion del
# item 2.1.b y la del chequeo de energia a densidad alta.
XO_CENTRO_V ?= 0.0175
COMMA    := ,
FIGURES  := data/figures
SLIDES   := data/figuras_diapositivas

# --- sistema 1 -------------------------------------------------------------
# dt < 10^-2 s, tres decadas con espaciado 1-2-5. Por debajo de 10^-5 el
# archivo de trayectorias de un solo dt pasa los 200 MB y los esquemas de
# segundo orden ya estan en el ruido de redondeo del doble.
DTS_OSC  ?= 5e-3,2e-3,1e-3,5e-4,2e-4,1e-4,5e-5,2e-5,1e-5
TF_OSC   ?= 5
OSC      := data/oscilador
# Control sin amortiguamiento (make oscilador-sin-amortiguamiento): cuatro dt
# alcanzan para comparar las constantes del error de los dos esquemas.
DTS_OSC0 ?= 5e-3,1e-3,2e-4,5e-5
OSC0     := data/oscilador_gamma0

# --- item 2.1 --------------------------------------------------------------
DTS_ENERGIA ?= 1e-3,5e-4,2e-4,1e-4,5e-5,2e-5,1e-5
N_ENERGIA   ?= 300
TF_ENERGIA  ?= 5
ENERGIA     := data/energia
# Verificacion del dt elegido en la condicion mas exigente del trabajo: la
# densidad maxima del barrido de N (700 particulas, 82 % del area) y con los
# obstaculos puestos.
DTS_DENSA   ?= 1e-4,5e-5,2e-5
N_DENSA     ?= 700
ENERGIA_DENSA := data/energia_densa
# La adicion secuencial al azar se traba cerca de N = 450 (fraccion de area
# 0,53, el limite del empaquetamiento al azar); la red hexagonal llega a 700
# (82 % del area ocupada), que es el tope del barrido.
NS          ?= 5,10,20,30,50,100,200,300,400,500,600,700
NS_RANDOM   ?= 5,10,20,30,50,100,200,300,400
NS_TP3      ?= 5,10,20,30,50,100,200,300,400,500,600
TF          ?= 30
REPEATS     ?= 10
WARMUP      ?= 1
BENCH       := data/bench
TP3         ?= ../tp-3

# --- item 2.2 --------------------------------------------------------------
# De xo = r (obstaculos en contacto entre si) a xo = R - r (en contacto con la
# pared), que son las dos posiciones extremas que permiten sus radios.
XOS         ?= 0.0175,0.0500,0.1000,0.1500,0.2000,0.2500,0.3000,0.3500,0.4000,0.4500,0.4925
NS_XO       ?= 100,20
TMAX        ?= 100
EXPLORE     := data/explore/2.2
# Los tres xo tipicos, los que van juntos en la figura de Fu(t) y tienen
# animacion: el centro, el optimo y el borde. El eje de tiempos de esa figura
# llega al tmax del item (la conversion mas tardia de las tres es 96 s).
TMAX_FU     ?= 100
XO_CENTRO   ?= xo0.0175
XO_OPTIMO   ?= xo0.2000
XO_BORDE    ?= xo0.4925

# --- item 2.4.a ------------------------------------------------------------
# Barrido propio del item 2.4.a, con la catedra de acuerdo (consulta A4): no se
# toman las corridas del 2.1.b. Esas tienen tf = 30 s fijo, y con los
# obstaculos en contacto casi ningun N llega a Fu = 0,9 antes de ese corte (de
# N = 200 para arriba no llega ninguna realizacion, y a N = 5 llega una sola de
# diez, asi que el promedio sale de una muestra y ni siquiera tiene desvio).
# Con tf = 30 s la figura no muestra ninguna densidad optima: es plana en 21 s
# y despues se corta.
#
# Es la MISMA configuracion (xo = r, obstaculos en contacto) y las MISMAS
# densidades que la columna xo = r del mapa del item 2.4.b, para que las dos
# figuras del item hablen de lo mismo; lo que cambia es que aca no se corta en
# Fu = 0,9, asi que la corrida sigue hasta convertirlas TODAS y se miden t90 y
# t100 de la misma corrida.
NS_DENSIDAD    ?= 5,10,20,30,50,70,100,150,200,300
TMAX_DENSIDAD  ?= 300
SEEDS_DENSIDAD ?= 20
JOBS_DENSIDAD  ?= 7
DENSIDAD       := data/densidad

# --- item 2.3 --------------------------------------------------------------
N_VEL       ?= 100
SEEDS_VEL   ?= 30
TMAX_VEL    ?= 30
DT2_VEL     ?= 0.05
ESTACIONARIO ?= 10
VELOCIDADES := data/velocidades

# --- item 2.4.b ------------------------------------------------------------
# El item no pone techo al barrido, asi que el mapa se hace con la resolucion
# que hace falta para contestarlo: 10 densidades y 16 posiciones, mas juntas
# entre 0,05 y 0,30 m, que es donde esta el minimo y donde se decide si se
# corre con N. 20 realizaciones por punto: con 6 el error de la media era de
# hasta 3 s sobre 12 y el minimo de cada fila saltaba de columna por ruido.
# N = 5 es la fila que cierra la mancha por abajo: ahi casi no hay choques y
# la conversion se vuelve a hacer lenta.
NS_MAPA     ?= 5,10,20,30,50,70,100,150,200,300
XOS_MAPA    ?= 0.0175,0.0500,0.0750,0.1000,0.1250,0.1500,0.1750,0.2000,0.2250,0.2500,0.2750,0.3000,0.3500,0.4000,0.4500,0.4925
SEEDS_MAPA  ?= 20
# Procesos simultaneos del barrido del mapa. Son 160 celdas y 3200 corridas:
# en serie no termina mas, y aca no se cronometra nada (los tiempos de
# ejecucion son los del item 2.1.b), asi que la maquina puede estar cargada.
JOBS_MAPA   ?= 7
# El mapa usa su propio tmax, mas largo que el del item 2.2: con N = 5 hay
# realizaciones que tardan 150 s en convertir las cinco particulas, y si el
# corte quedara en 100 s esas celdas se perderian. De N = 10 para arriba no
# cambia nada: ninguna realizacion del barrido pasa de los 70 s.
TMAX_MAPA   ?= 300
MAPA        := data/mapa

# --- animaciones y entrega -------------------------------------------------
RUNS        := data/runs
ANIM        := $(FIGURES)/animaciones
SLIDES_ANIM := $(SLIDES)/animaciones
YOUTUBE     := youtube
N_ANIM      ?= 100
TMAX_ANIM   ?= 20
# dt2 = 800 dt = 0,04 s: a 25 cuadros por segundo el video corre en tiempo real y
# el cuadro fijo de t = 10 s es exactamente el cuadro 250.
SAVE_ANIM   ?= 800
FPS         ?= 25
CUADRO      ?= 10
TEXC        ?= tectonic -X compile
DOCS        := report/build
FIGS        := slides-images
GRUPO       ?= 10
COMISION    ?= S2
ENTREGA     := SdS_TP4_2026Q2G$(GRUPO)$(COMISION)
ZIP         := $(ENTREGA)_Codigo.zip

.PHONY: all todo build oscilador oscilador-figuras oscilador-sin-amortiguamiento \
        velocity-verlet-variantes \
        energia energia-figuras energia-densa \
        bench bench-tp3 \
        bench-figuras obstaculos obstaculos-figuras velocidades velocidades-figuras \
        densidad densidad-figuras mapa mapa-figuras check una-particula animations youtube gifs figuras-diapositivas \
        slides-images slides-images-tikz documentos capturas entrega clean-figures

all: todo

todo: oscilador energia energia-densa bench bench-tp3 obstaculos velocidades mapa

build:
	$(MAKE) -C engine

# --------------------------------------------------------------------------
# Sistema 1: oscilador puntual amortiguado
# --------------------------------------------------------------------------

# Una trayectoria completa por esquema y por dt (t x v en cada paso). El ECM
# contra la solucion analitica se calcula despues, en oscillator.py: el motor
# no calcula ningun observable.
oscilador: build
	$(BILLAR) oscillator --methods verlet,velocity-verlet,beeman,euler-pc \
	    --dts $(DTS_OSC) --tf $(TF_OSC) --dir $(OSC)

oscilador-figuras:
	$(PY) visualization/oscillator.py --trayectoria 1e-3
	$(PY) visualization/oscillator.py --figures $(SLIDES) --estilo diapositiva

# Por que Beeman le gana a Verlet original (diapositiva 12). Los dos son de
# cuarto orden en el ECM y en la escala completa se superponen; la ampliacion
# muestra que Verlet mide un 15 % mas de ECM con el mismo paso. Lo unico en lo
# que difieren es con que velocidad evaluan a(t+dt), y eso solo importa si la
# fuerza depende de la velocidad: con gamma = 0 la fuerza es -k r y las dos
# constantes del error ECM/dt^4 tienen que coincidir. Barrido corto, alcanza
# con comparar las dos constantes.
oscilador-sin-amortiguamiento: build
	$(BILLAR) oscillator --methods verlet,beeman --dts $(DTS_OSC0) --tf $(TF_OSC) \
	    --gamma 0 --dir $(OSC0)
	$(PY) visualization/oscillator.py --oscilador $(OSC0) --figures $(OSC0)/figuras

# Por que Velocity Verlet pierde un orden (diapositiva 5). La Teorica escribe
# sus dos pasos intermedios sobre la velocidad pero no dice con que v se
# evalua a(t+dt) cuando la fuerza depende de v: entre los dos pasos la unica
# que hay es la de medio paso, y esa usa el motor. Esto mide que cuesta: corre
# el mismo barrido con las cuatro maneras posibles de evaluarla y ajusta el
# orden de cada una. Necesita data/oscilador (make oscilador) para verificar
# antes que la variante de medio paso reproduce lo que corrio en C++.
velocity-verlet-variantes:
	$(PY) visualization/halfstep.py --figura

# --------------------------------------------------------------------------
# Item 2.1.a: eleccion del paso temporal
# --------------------------------------------------------------------------

# Sistema sin obstaculos y N = 300, un barrido de dt con el MISMO dt2 para
# todos (--dt2 en segundos: cada dt usa el numero entero de pasos que lo da),
# para que las curvas de energia se comparen sobre el mismo eje.
energia: build
	$(BILLAR) explore --ns $(N_ENERGIA) --xos sin --dts $(DTS_ENERGIA) --seeds 1 \
	    --seed $(SEED0) --tmax $(TF_ENERGIA) --dt2 $(DT2) --dir $(ENERGIA)

energia-figuras:
	$(PY) visualization/energy.py
	$(PY) visualization/energy.py --figures $(SLIDES) --estilo diapositiva

# El dt elegido con N = 300 y sin obstaculos tiene que seguir cumpliendo la
# cota en el caso mas denso del trabajo: N = 700 con los obstaculos en
# contacto. Solo imprime el resumen (no lleva figura propia a la presentacion).
energia-densa: build
	$(BILLAR) explore --ns $(N_DENSA) --xos $(XO_CENTRO_V) --dts $(DTS_DENSA) --seeds 1 \
	    --seed $(SEED0) --tmax $(TF_ENERGIA) --dt2 $(DT2) --placement hexagonal \
	    --dir $(ENERGIA_DENSA)
	$(PY) visualization/energy.py --energia $(ENERGIA_DENSA) --figures $(ENERGIA_DENSA)

# --------------------------------------------------------------------------
# Item 2.1.b: tiempo de ejecucion contra N
# --------------------------------------------------------------------------

# Obstaculos en contacto (xo = r) y tiempo absoluto fijo tf, sin escribir
# cuadros: se cronometran la generacion de la condicion inicial y el bucle de
# integracion por separado, y por cada N se corren REPEATS + WARMUP
# realizaciones (la primera queda marcada como descartada: arranque en frio).
# Correr con la maquina descargada. La condicion inicial al azar es la del
# enunciado; la hexagonal es la unica que entra por encima de N = 450.
bench: build
	$(BILLAR) bench --ns $(NS) --tf $(TF) --dt $(DT) --repeats $(REPEATS) \
	    --warmup $(WARMUP) --seed 1 --placement hexagonal --dir $(BENCH)/hexagonal
	$(BILLAR) bench --ns $(NS_RANDOM) --tf $(TF) --dt $(DT) --repeats $(REPEATS) \
	    --warmup $(WARMUP) --seed 1 --placement random --dir $(BENCH)/random

# Los tiempos del item 1.1 del TP3 (dinamica molecular dirigida por eventos),
# recorridos en ESTA computadora para que la comparacion sea valida.
bench-tp3:
	$(MAKE) -C $(TP3)/engine
	cd $(TP3)/engine && ./build/metegol bench --ns $(NS_TP3) --tf $(TF) \
	    --repeats $(REPEATS) --warmup $(WARMUP) --placement hexagonal --seed 1 \
	    --out $(CURDIR)/$(BENCH)/tp3_hexagonal.txt
	cd $(TP3)/engine && ./build/metegol bench --ns $(NS_RANDOM) --tf $(TF) \
	    --repeats $(REPEATS) --warmup $(WARMUP) --placement random --seed 1 \
	    --out $(CURDIR)/$(BENCH)/tp3_random.txt

# El barrido de N llega hasta 5 porque el item 2.4.a usa estas mismas corridas;
# la figura del item 2.1.b arranca en N = 50 (ver PLAN.md, decision 9).
N_BENCH_MIN ?= 50
bench-figuras:
	$(PY) visualization/bench.py --desde $(N_BENCH_MIN) \
	    --bench $(BENCH)/hexagonal/tiempos.txt,$(BENCH)/tp3_hexagonal.txt \
	    --labels "paso temporal (TP4),eventos (TP3)" --name paradigmas
	$(PY) visualization/bench.py --desde $(N_BENCH_MIN) \
	    --bench $(BENCH)/hexagonal/tiempos.txt,$(BENCH)/tp3_hexagonal.txt \
	    --labels "paso temporal (TP4),eventos (TP3)" --name paradigmas \
	    --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/bench.py --desde $(N_BENCH_MIN) \
	    --bench $(BENCH)/hexagonal/tiempos.txt,$(BENCH)/random/tiempos.txt,$(BENCH)/tp3_hexagonal.txt,$(BENCH)/tp3_random.txt \
	    --labels "paso temporal (red hexagonal),paso temporal (al azar),eventos (red hexagonal),eventos (al azar)" \
	    --name condiciones-iniciales

# --------------------------------------------------------------------------
# Item 2.2: posicion de los obstaculos
# --------------------------------------------------------------------------

# N = 100 (la densidad del enunciado) y N = 20 (densidad menor, para ver si la
# respuesta depende de la frecuencia de choques entre particulas). Las
# corridas terminan apenas se convierten todas las particulas: despues de eso
# no cambia ningun observable.
obstaculos: build
	$(BILLAR) explore --ns $(NS_XO) --xos $(XOS) --dts $(DT) --seeds $(SEEDS) \
	    --seed $(SEED0) --tmax $(TMAX) --until-all-used --dir $(EXPLORE)

# Fu(t) de los xo tipicos va en UNA sola figura, con las tres curvas juntas:
# es lo que pide el enunciado del item 2.2 ("graficar Fu(t) para pocos valores
# tipicos de xo"), y es la unica forma de leer como se corre la curva al mover
# los obstaculos. Cada curva es el promedio de las SEEDS realizaciones del
# caso, con su banda de +-1 desvio.
CASOS_FU := $(EXPLORE)/n100_$(XO_CENTRO),$(EXPLORE)/n100_$(XO_OPTIMO),$(EXPLORE)/n100_$(XO_BORDE)
obstaculos-figuras:
	$(PY) visualization/explore.py --explore $(EXPLORE)
	$(PY) visualization/explore.py --explore $(EXPLORE) --fraccion 1
	$(PY) visualization/explore.py --explore $(EXPLORE) --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/conversion.py --casos $(CASOS_FU) --tmax $(TMAX_FU) \
	    --name Fu_vs_t_n100_xo_tipicos.png
	$(PY) visualization/conversion.py --casos $(CASOS_FU) --tmax $(TMAX_FU) \
	    --name Fu_vs_t_n100_xo_tipicos.png --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Item 2.3: distribucion de velocidades
# --------------------------------------------------------------------------

velocidades: build
	$(BILLAR) explore --ns $(N_VEL) --xos sin --dts $(DT) --seeds $(SEEDS_VEL) \
	    --seed $(SEED0) --tmax $(TMAX_VEL) --dt2 $(DT2_VEL) --dir $(VELOCIDADES)

velocidades-figuras:
	$(PY) visualization/speeds.py --estacionario $(ESTACIONARIO)
	$(PY) visualization/speeds.py --estacionario $(ESTACIONARIO) \
	    --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Item 2.4: efecto de la densidad
# --------------------------------------------------------------------------

densidad-figuras:
	$(PY) visualization/density.py
	$(PY) visualization/density.py --figures $(SLIDES) --estilo diapositiva

# Un proceso por celda (N, xo) y los N grandes primero, que son los caros: el
# barrido son 3200 corridas y en serie no termina mas. heatmap.py junta los
# index.txt de todas las subcarpetas, asi que partirlo asi se lee igual que si
# hubiera salido de una sola corrida.
#
# --until-fraction 0.9 corta cada corrida apenas Fu llega a 0,9, que es lo
# unico que mide el mapa: esperar de t90 a t100 cuesta el triple de computo (a
# N = 300, 29 s contra 98 s de tiempo simulado) y no cambia la figura. Por eso
# este barrido NO sirve para el mapa de <t100>: para ese hay que correrlo sin
# --until-fraction (make mapa SEEDS_MAPA=6, o va a tardar horas).
mapa: build
	rm -rf $(MAPA)
	@mkdir -p $(MAPA)
	@for n in $(subst $(COMMA), ,$(NS_MAPA)); do \
	    for x in $(subst $(COMMA), ,$(XOS_MAPA)); do printf '%s %s\n' "$$n" "$$x"; done; \
	done | sort -k1,1nr | xargs -P $(JOBS_MAPA) -n 2 sh -c \
	    '$(BILLAR) explore --ns $$0 --xos $$1 --dts $(DT) --seeds $(SEEDS_MAPA) \
	        --seed $(SEED0) --tmax $(TMAX_MAPA) --until-all-used --until-fraction 0.9 \
	        --dir $(MAPA)/n$$0_xo$$1 > /dev/null'

# Un proceso por N y los grandes primero, que son los caros. Sin cuadros: de
# estas corridas solo se leen los events.txt (el instante de cada conversion).
densidad: build
	rm -rf $(DENSIDAD)
	@mkdir -p $(DENSIDAD)
	@for n in $(subst $(COMMA), ,$(NS_DENSIDAD)); do printf '%s\n' "$$n"; done \
	    | sort -k1,1nr | xargs -P $(JOBS_DENSIDAD) -n 1 sh -c \
	    '$(BILLAR) explore --ns $$0 --xos $(XO_CENTRO_V) --dts $(DT) \
	        --seeds $(SEEDS_DENSIDAD) --seed $(SEED0) --tmax $(TMAX_DENSIDAD) \
	        --until-all-used --dir $(DENSIDAD)/n$$0 > /dev/null'

mapa-figuras:
	$(PY) visualization/heatmap.py
	$(PY) visualization/heatmap.py --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Una sola particula (prueba de la explicacion del item 2.4.a)
# --------------------------------------------------------------------------

# Sin choques, la particula conserva el momento angular respecto del centro
# (la fuerza de la pared es radial) y solo se convierte si su parametro de
# impacto es menor que 3r. Se guarda un solo cuadro (el de t = 0) por corrida.
SEEDS_UNA   ?= 300
TMAX_UNA    ?= 60
UNA         := data/una_particula
una-particula: build
	$(BILLAR) explore --ns 1 --xos $(XO_CENTRO_V) --dts $(DT) --seeds $(SEEDS_UNA) \
	    --seed 1000 --tmax $(TMAX_UNA) --save-every 100000000 --until-all-used --dir $(UNA)
	$(PY) visualization/single.py --una $(UNA)

# --------------------------------------------------------------------------
# Validacion
# --------------------------------------------------------------------------

check: build
	$(BILLAR) simulate --n $(N_ANIM) --xo 0.0175 --dt $(DT) --tmax 10 \
	    --save-every 200 --seed $(SEED0) --dir $(RUNS)/validacion > /dev/null
	$(PY) visualization/check.py --run $(RUNS)/validacion

# --------------------------------------------------------------------------
# Animaciones y figuras de las diapositivas
# --------------------------------------------------------------------------

# Una corrida por animacion, con la misma semilla que la primera realizacion
# del barrido (misma trayectoria que el Fu(t) que se muestra). El estado se
# guarda cada SAVE_ANIM pasos para que el video corra en tiempo real a FPS
# cuadros por segundo. El cuadro fijo del PDF tiene el mismo lienzo y
# tipografia que el video.
define ANIMAR
	$(BILLAR) simulate --n $(N_ANIM) --xo $(2) --dt $(DT) --tmax $(TMAX_ANIM) \
	    --save-every $(SAVE_ANIM) --seed $(SEED0) --dir $(RUNS)/$(1) > /dev/null
	$(PY) visualization/animate.py --run $(RUNS)/$(1) --fps $(FPS) --estilo diapositiva
	$(PY) visualization/animate.py --run $(RUNS)/$(1) --cuadro $(CUADRO) --estilo diapositiva \
	    --figures $(SLIDES)

endef

animations: build
	$(call ANIMAR,centro,0.0175)
	$(call ANIMAR,optimo,0.20)
	$(call ANIMAR,borde,0.4925)
	$(call ANIMAR,sin_obstaculos,sin)

youtube:
	mkdir -p $(YOUTUBE)
	rm -f $(YOUTUBE)/*.mp4
	cp $(ANIM)/centro.mp4          "$(YOUTUBE)/01 - SdS TP4 G10 - Obstaculos en el centro - N 100.mp4"
	cp $(ANIM)/optimo.mp4          "$(YOUTUBE)/02 - SdS TP4 G10 - Obstaculos en la posicion optima - N 100.mp4"
	cp $(ANIM)/borde.mp4           "$(YOUTUBE)/03 - SdS TP4 G10 - Obstaculos en el borde - N 100.mp4"
	cp $(ANIM)/sin_obstaculos.mp4  "$(YOUTUBE)/04 - SdS TP4 G10 - Sin obstaculos - N 100.mp4"
	@ls -l $(YOUTUBE)/*.mp4 | awk '{printf "  %5.1f MB  ", $$5/1e6; for (i=9;i<=NF;i++) printf "%s ", $$i; print ""}'

# Los mismos cuatro videos como GIF, para embeberlos en la presentacion en
# vivo (la que se proyecta sin links, D12 del TP2) y para quien no abra el
# mp4. Uno de cada dos cuadros guardados a la mitad de los cuadros por segundo,
# asi el GIF corre en tiempo real igual que el video, y GIF_WIDTH px de ancho
# con una paleta propia por video (dos pasadas de ffmpeg): unos 8 MB cada uno.
# Se versionan, como los del TP3. Mismo numero y nombre que el video de
# youtube/titulos.md.
GIF       := gif
GIF_WIDTH ?= 560
gifs:
	mkdir -p $(GIF)
	@for par in centro:01-obstaculos-en-el-centro optimo:02-obstaculos-en-la-posicion-optima \
	           borde:03-obstaculos-en-el-borde sin_obstaculos:04-sin-obstaculos; do \
	    caso=$${par%%:*}; nombre=$${par##*:}; \
	    ffmpeg -v error -y -i $(ANIM)/$$caso.mp4 -filter_complex \
	        "[0:v]fps=$$(echo "$(FPS)/2" | bc -l),scale=$(GIF_WIDTH):-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
	        $(GIF)/$$nombre.gif; \
	    echo "  $(GIF)/$$nombre.gif"; \
	done
	@ls -l $(GIF)/*.gif | awk '{printf "  %5.1f MB  ", $$5/1e6; for (i=9;i<=NF;i++) printf "%s ", $$i; print ""}'

figuras-diapositivas: oscilador-figuras energia-figuras bench-figuras obstaculos-figuras \
                      velocidades-figuras densidad-figuras mapa-figuras

clean-figures:
	rm -rf $(FIGURES) $(SLIDES)

# Copia de las figuras de la presentacion numeradas por diapositiva
# (slides-images/, se versiona y es de donde las lee report/presentacion.tex):
# el numero es el del pie de la diapositiva.
slides-images:
	rm -rf $(FIGS) && mkdir -p $(FIGS)
	cp $(SLIDES)/1_oscilador/ECM_vs_dt.png                                          $(FIGS)/slide-13-ECM-vs-dt.png
	cp $(SLIDES)/2.1_paso_y_tiempos/error_energia_vs_t_N$(N_ENERGIA).png            $(FIGS)/slide-14-error-energia-vs-t.png
	cp $(SLIDES)/2.1_paso_y_tiempos/error_maximo_vs_dt_N$(N_ENERGIA).png            $(FIGS)/slide-15-error-maximo-vs-dt.png
	cp $(SLIDES)/animaciones/cuadro_centro_t$(CUADRO).png                           $(FIGS)/slide-16-animacion-centro.png
	cp $(SLIDES)/2.1_paso_y_tiempos/tiempo_total_vs_N_paradigmas_M$(REPEATS)_log.png $(FIGS)/slide-17-tiempo-ejecucion-vs-N.png
	cp $(SLIDES)/animaciones/cuadro_optimo_t$(CUADRO).png                           $(FIGS)/slide-18-animacion-optimo.png
	cp $(SLIDES)/animaciones/cuadro_borde_t$(CUADRO).png                            $(FIGS)/slide-19-animacion-borde.png
	cp $(SLIDES)/2.2_obstaculos/Fu_vs_t_n100_xo_tipicos.png                         $(FIGS)/slide-20-Fu-vs-t-xo-tipicos.png
	cp $(SLIDES)/2.2_obstaculos/t90_vs_xo_N20-100_M$(SEEDS).png                     $(FIGS)/slide-21-t90-vs-xo.png
	cp $(SLIDES)/animaciones/cuadro_sin_obstaculos_t$(CUADRO).png                   $(FIGS)/slide-22-animacion-sin-obstaculos.png
	cp $(SLIDES)/2.3_velocidades/f_v_vs_t_N$(N_VEL)_M$(SEEDS_VEL).png               $(FIGS)/slide-23-f-v-vs-t.png
	cp $(SLIDES)/2.3_velocidades/f_v_estacionaria_ajuste_N$(N_VEL)_M$(SEEDS_VEL).png $(FIGS)/slide-24-f-v-ajuste.png
	cp $(SLIDES)/2.3_velocidades/E_vs_kT_N$(N_VEL)_M$(SEEDS_VEL).png                $(FIGS)/slide-25-E-vs-kT.png
	cp $(SLIDES)/2.4_densidad/t90_t100_vs_densidad_M$(SEEDS_DENSIDAD).png           $(FIGS)/slide-26-t90-t100-vs-densidad.png
	cp $(SLIDES)/2.4_densidad/mapa_t90_xo_N.png                                     $(FIGS)/slide-27-mapa-t90-xo-N.png
	$(MAKE) slides-images-tikz
	@ls $(FIGS) | wc -l

# Los fragmentos de las diapositivas escritos en LaTeX (report/figuras/*.tikz,
# los mismos que \input presentacion.tex: los esquemas TikZ de introduccion e
# implementacion y la tabla de parametros) renderizados sueltos a PNG con la
# misma tipografia y colores, numerados por diapositiva.
TIKZ_FIGS := 02-sistema 03-modelo-pared-imagen 06-motor-uml 07-bucle-paso-temporal \
             09-parametros-tabla 09-parametros-dominio
slides-images-tikz:
	mkdir -p $(DOCS)/figuras $(FIGS)
	for f in $(TIKZ_FIGS); do \
	    n=$${f#*-}; \
	    printf '\\def\\figura{%s}\\input{render.tex}\n' "$$n" > report/figuras/_$$n.tex; \
	    $(TEXC) report/figuras/_$$n.tex --outdir $(DOCS)/figuras; \
	    pdftoppm -r 600 -png -singlefile $(DOCS)/figuras/_$$n.pdf $(FIGS)/slide-$$f; \
	    rm -f report/figuras/_$$n.tex; \
	done

# Capturas de diapositivas sueltas, en PNG, para pasarlas a otro lado: la
# tabla de parametros esta escrita en LaTeX dentro de la diapositiva (no es
# una figura aparte), asi que la unica forma de tenerla como imagen es
# recortar la pagina del PDF ya compilado. PAGINAS son pares pagina:nombre,
# con la pagina del PDF (que es el numero del pie mas uno, porque la portada
# no se numera).
CAPTURAS ?= capturas
PAGINAS  ?= 10:slide-09-parametros
capturas: documentos
	mkdir -p $(CAPTURAS)
	@for par in $(PAGINAS); do \
	    pagina=$${par%%:*}; nombre=$${par##*:}; \
	    pdftoppm -f $$pagina -l $$pagina -r 200 -png -singlefile \
	        $(DOCS)/presentacion.pdf $(CAPTURAS)/$$nombre; \
	    echo "  $(CAPTURAS)/$$nombre.png (página $$pagina)"; \
	done

# --------------------------------------------------------------------------
# Entrega
# --------------------------------------------------------------------------

# Presentacion (b), la que se entrega: beamer con un cuadro fijo por animacion y el link explicito
# debajo; las figuras las lee de slides-images/ (make slides-images). tectonic
# baja los paquetes que falten; con otro motor: make documentos TEXC="latexmk -pdf -outdir"
documentos:
	mkdir -p $(DOCS)
	$(TEXC) report/presentacion.tex --outdir $(DOCS)
	@echo "  $(DOCS)/presentacion.pdf"

# El motor, como pide la consigna (c), mas el codigo con el que se hacen las
# animaciones a partir de las salidas primarias (pedido de la catedra sobre el
# TP3: animate.py y common.py, del que depende); sin datos ni documentacion
# extra. Debe quedar por debajo de 100 KB.
entrega:
	rm -f $(ZIP)
	zip -q -r $(ZIP) engine/Makefile engine/include engine/src \
	    visualization/animate.py visualization/common.py
	@echo "$(ZIP)  ($$(du -h $(ZIP) | cut -f1))"
	@[ $$(stat -c%s $(ZIP)) -lt 102400 ] || echo "  ATENCIÓN: el zip supera los 100 KB"
	@if [ -f $(DOCS)/presentacion.pdf ]; then \
	    cp $(DOCS)/presentacion.pdf "$(ENTREGA)_Presentación.pdf"; \
	    echo "$(ENTREGA)_Presentación.pdf  ($$(du -h "$(ENTREGA)_Presentación.pdf" | cut -f1))"; \
	    grep -q PENDIENTE report/presentacion.tex && echo "  ATENCIÓN: quedan links PENDIENTE a YouTube en report/presentacion.tex" || true; \
	else echo "  falta $(DOCS)/presentacion.pdf (make documentos)"; fi
