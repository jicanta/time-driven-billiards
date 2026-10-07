# TP4 -- todo el flujo desde la raiz del repositorio.
#
#   make build          compila el motor (engine/build/billar)
#   make oscilador      sistema 1: integra el oscilador con los 4 esquemas y todos los dt
#   make oscilador-figuras  ECM vs dt (la unica figura del sistema 1) y la trayectoria
#   make energia        item 2.1.a: N = 300 sin obstaculos, un barrido de dt con cuadros
#   make energia-figuras    energia vs t (completa y ampliada) y deriva vs dt
#   make energia-densa  verifica el dt elegido en el caso mas denso (N = 700 con obstaculos)
#   make bench          item 2.1.b: tiempos contra N (maquina descargada)
#   make bench-tp3      los mismos tiempos con el motor del TP3 (dirigido por eventos)
#   make bench-figuras      tiempo de ejecucion vs N de los dos paradigmas
#   make obstaculos     item 2.2: barrido de xo con N = 100 y N = 20
#   make obstaculos-figuras <t90> vs xo y Fu(t) de los xo tipicos
#   make velocidades    item 2.3: N = 100 sin obstaculos, cuadros hasta el estacionario
#   make velocidades-figuras  f(v) por instante, ajuste de Maxwell-Boltzmann y E(kT)
#   make densidad-figuras   item 2.4.a: <t90> y <t100> vs densidad (usa las corridas de 2.1.b)
#   make mapa           item 2.4.b (opcional): barrido (xo, N)
#   make mapa-figuras       mapa de calor de <t90> en el plano (xo, N)
#   make check          corrida de validacion: energia, solapamientos y escapes
#   make animations     corridas caracteristicas, videos y cuadro fijo de cada una
#   make youtube        copia los videos con nombres legibles en youtube/
#   make figuras-diapositivas  todas las figuras de las diapositivas (data/figuras_diapositivas)
#   make figuras-slides     copia las figuras de la presentacion numeradas por diapositiva
#   make documentos     compila report/presentacion.tex (borrador beamer)
#   make entrega        SdS_TP4_2026Q2G10S2_Codigo.zip (< 100 KB)
#   make todo           oscilador + energia(+densa) + bench + obstaculos + velocidades + mapa
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
# Los tres xo que llevan figura de Fu(t) y animacion: el centro, el optimo y
# el borde.
# Las tres figuras de Fu(t) comparten este limite del eje de tiempos, para que
# se puedan comparar entre si (la conversion mas tardia de las tres es 96 s).
TMAX_FU     ?= 100
XO_CENTRO   ?= xo0.0175
XO_OPTIMO   ?= xo0.2000
XO_BORDE    ?= xo0.4925

# --- item 2.3 --------------------------------------------------------------
N_VEL       ?= 100
SEEDS_VEL   ?= 10
TMAX_VEL    ?= 30
DT2_VEL     ?= 0.05
ESTACIONARIO ?= 10
VELOCIDADES := data/velocidades

# --- item 2.4.b ------------------------------------------------------------
NS_MAPA     ?= 20,50,100,200,300
XOS_MAPA    ?= 0.0175,0.1000,0.2000,0.3000,0.4000,0.4925
SEEDS_MAPA  ?= 6
MAPA        := data/mapa

# --- animaciones y entrega -------------------------------------------------
RUNS        := data/runs
ANIM        := $(FIGURES)/animaciones
SLIDES_ANIM := $(SLIDES)/animaciones
YOUTUBE     := youtube
N_ANIM      ?= 100
TMAX_ANIM   ?= 20
# dt2 = 667 dt = 0,03335 s: a 30 cuadros por segundo el video corre en tiempo real.
SAVE_ANIM   ?= 667
FPS         ?= 30
CUADRO      ?= 10
TEXC        ?= tectonic -X compile
DOCS        := report/build
FIGS        := figuras-slides
GRUPO       ?= 10
COMISION    ?= S2
ENTREGA     := SdS_TP4_2026Q2G$(GRUPO)$(COMISION)
ZIP         := $(ENTREGA)_Codigo.zip

.PHONY: all todo build oscilador oscilador-figuras energia energia-figuras energia-densa \
        bench bench-tp3 \
        bench-figuras obstaculos obstaculos-figuras velocidades velocidades-figuras \
        densidad-figuras mapa mapa-figuras check animations youtube figuras-diapositivas \
        figuras-slides documentos entrega clean-figures

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

RUN_IDS := $(shell seq -s , $(SEED0) $$(( $(SEED0) + $(SEEDS) - 1 )))
obstaculos-figuras:
	$(PY) visualization/explore.py --explore $(EXPLORE)
	$(PY) visualization/explore.py --explore $(EXPLORE) --fraccion 1
	$(PY) visualization/explore.py --explore $(EXPLORE) --figures $(SLIDES) --estilo diapositiva
	@for caso in n100_$(XO_CENTRO) n100_$(XO_OPTIMO) n100_$(XO_BORDE); do \
	    runs=$$(for k in $(subst $(COMMA), ,$(RUN_IDS)); do printf "$(EXPLORE)/$$caso/s%s," $$k; done); \
	    $(PY) visualization/conversion.py --runs $${runs%,} --realizaciones \
	        --tmax $(TMAX_FU) --name Fu_vs_t_$$caso.png | tail -2; \
	    $(PY) visualization/conversion.py --runs $${runs%,} --realizaciones \
	        --tmax $(TMAX_FU) --name Fu_vs_t_$$caso.png --figures $(SLIDES) \
	        --estilo diapositiva | tail -1; \
	done

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

# Un proceso por N, en paralelo: el barrido completo tarda cerca de una hora
# en serie y los N grandes son los caros. heatmap.py junta los index.txt de
# todas las subcarpetas.
mapa: build
	rm -rf $(MAPA)
	@for n in $(subst $(COMMA), ,$(NS_MAPA)); do \
	    $(BILLAR) explore --ns $$n --xos $(XOS_MAPA) --dts $(DT) --seeds $(SEEDS_MAPA) \
	        --seed $(SEED0) --tmax $(TMAX) --until-all-used --dir $(MAPA)/n$$n & \
	done; wait

mapa-figuras:
	$(PY) visualization/heatmap.py
	$(PY) visualization/heatmap.py --figures $(SLIDES) --estilo diapositiva

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

figuras-diapositivas: oscilador-figuras energia-figuras bench-figuras obstaculos-figuras \
                      velocidades-figuras densidad-figuras mapa-figuras

clean-figures:
	rm -rf $(FIGURES) $(SLIDES)

# Copia de las figuras de la presentacion numeradas por diapositiva
# (figuras-slides/, se versiona): el numero es el del pie de la diapositiva.
figuras-slides:
	rm -rf $(FIGS) && mkdir -p $(FIGS)
	cp $(SLIDES)/1_oscilador/ECM_vs_dt.png                                          $(FIGS)/slide-12-ECM-vs-dt.png
	cp $(SLIDES)/2.1_paso_y_tiempos/energia_vs_t_N$(N_ENERGIA).png                  $(FIGS)/slide-13-energia-vs-t.png
	cp $(SLIDES)/2.1_paso_y_tiempos/energia_vs_t_N$(N_ENERGIA)_detalle.png          $(FIGS)/slide-13b-energia-vs-t-detalle.png
	cp $(SLIDES)/2.1_paso_y_tiempos/deriva_vs_dt_N$(N_ENERGIA).png                  $(FIGS)/slide-14-deriva-vs-dt.png
	cp $(SLIDES)/animaciones/cuadro_centro_t$(CUADRO).png                           $(FIGS)/slide-15-animacion-centro.png
	cp $(SLIDES)/2.1_paso_y_tiempos/tiempo_total_vs_N_paradigmas_M$(REPEATS)_log.png $(FIGS)/slide-16-tiempo-ejecucion-vs-N.png
	cp $(SLIDES)/2.2_obstaculos/Fu_vs_t_n100_$(XO_CENTRO).png                       $(FIGS)/slide-17-Fu-vs-t-centro.png
	cp $(SLIDES)/animaciones/cuadro_optimo_t$(CUADRO).png                           $(FIGS)/slide-18-animacion-optimo.png
	cp $(SLIDES)/2.2_obstaculos/Fu_vs_t_n100_$(XO_OPTIMO).png                       $(FIGS)/slide-19-Fu-vs-t-optimo.png
	cp $(SLIDES)/animaciones/cuadro_borde_t$(CUADRO).png                            $(FIGS)/slide-20-animacion-borde.png
	cp $(SLIDES)/2.2_obstaculos/Fu_vs_t_n100_$(XO_BORDE).png                        $(FIGS)/slide-21-Fu-vs-t-borde.png
	cp $(SLIDES)/2.2_obstaculos/t90_vs_xo_N20-100_M$(SEEDS).png                     $(FIGS)/slide-22-t90-vs-xo.png
	cp $(SLIDES)/animaciones/cuadro_sin_obstaculos_t$(CUADRO).png                   $(FIGS)/slide-23-animacion-sin-obstaculos.png
	cp $(SLIDES)/2.3_velocidades/f_v_vs_t_N$(N_VEL)_M$(SEEDS_VEL).png               $(FIGS)/slide-24-f-v-vs-t.png
	cp $(SLIDES)/2.3_velocidades/f_v_estacionaria_ajuste_N$(N_VEL)_M$(SEEDS_VEL).png $(FIGS)/slide-25-f-v-ajuste.png
	cp $(SLIDES)/2.3_velocidades/E_vs_kT_N$(N_VEL)_M$(SEEDS_VEL).png                $(FIGS)/slide-26-E-vs-kT.png
	cp $(SLIDES)/2.4_densidad/t90_t100_vs_densidad_M$(REPEATS).png                  $(FIGS)/slide-27-t90-t100-vs-densidad.png
	cp $(SLIDES)/2.4_densidad/mapa_t90_xo_N.png                                     $(FIGS)/slide-28-mapa-t90-xo-N.png
	@ls $(FIGS) | wc -l

# --------------------------------------------------------------------------
# Entrega
# --------------------------------------------------------------------------

# Presentacion (b): borrador beamer con un cuadro fijo por animacion y el link
# explicito debajo. tectonic baja los paquetes que falten; con otro motor:
# make documentos TEXC="latexmk -pdf -outdir"
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
	@[ -f "$(ENTREGA)_Presentación.pdf" ] || echo "  falta $(ENTREGA)_Presentación.pdf (exportar de Google Slides)"
