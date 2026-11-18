import pygame
import os
import sys
import json
import math
import random
import time

import sangre

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_minijuegos = os.path.join(ruta_actual, "..", "minijuegos")
sys.path.append(os.path.normpath(ruta_minijuegos))

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

ancho = 800
alto = 600


def crear_ventana():
    """Crea la ventana (escalable). Debe existir ANTES de cargar imágenes."""
    try:
        return pygame.display.set_mode((ancho, alto), pygame.SCALED | pygame.RESIZABLE)
    except (pygame.error, AttributeError):
        return pygame.display.set_mode((ancho, alto))


crear_ventana()


TIEMPO_DISMINUCION = 4500
SUBPANTALLAS_PAUSA = {"minijuegos", "minijuego"}
# Sueño: el velador apaga la luz y Pau duerme hasta llenar la barra (o hasta
# que vuelvas a tocar el velador).
VEL_DORMIR_MS = 150                 # cada cuántos ms sube 1 punto DORMIR
ESPERA_DESPERTAR = 1200             # ms que sigue durmiendo con la barra llena
ANGULO_ACOSTADO = -65               # grados (negativo = horario, cabeza a la almohada)

# Inodoro
SUBE_PIS = 40
SUBE_CACA = 100
DURACION_INODORO = 2600             # ms sentado en el inodoro

# Pedos: si la VIDA (promedio de las barras) baja del 50 %
UMBRAL_PEDOS = 50
PEDO_CADA_MS = (7000, 16000)        # intervalo aleatorio entre pedos

# Pociones
PRECIO_POCION = 66                  # matadora
PRECIO_POCION_VIDA = 100            # Pau vuelve a ser bueno y pide perdón (una sola vez)
PRECIO_POCION_67 = 67               # Pau hace el 67
DURACION_67 = 4200

# Modo diablo
PROB_SUSTO = 1 / 1000               # chance de jumpscare por segundo
DURACION_SUSTO = 1300

# Enojo: si llega a 100, Pau se va volando (se lo llama con el celular)
ENOJO_REVOLEO = 12
ENOJO_REVOLEO_DIABLO = 20
ENOJO_CARICIA_DIABLO = 4
ENOJO_BAJA_CADA_MS = 2500           # baja 1 punto cada tanto

# Pau Jr
JR_VISITA_CADA = (20000, 50000)     # cada cuánto aparece (ms)
TAMAÑO_JR = 80

OFFLINE_SEGUNDOS_POR_PUNTO = 120    
OFFLINE_MAX_PERDIDA = 60            
NECESIDAD_MINIMA_OFFLINE = 10       
INTERVALO_AUTOGUARDADO = 10000      
BONUS_DIARIO = 20                   
DURACION_AVISO = 1800               

CARPETAS = [
    "", "FONDOS", "objetos", "personajes", "imagenes", "sonidos",
    "..", os.path.join("..", "FONDOS"), os.path.join("..", "objetos"),
    os.path.join("..", "sonidos"),
]


def buscar_ruta(nombre):
    for carpeta in CARPETAS:
        ruta = os.path.normpath(os.path.join(ruta_actual, carpeta, nombre))
        if os.path.isfile(ruta):
            return ruta
    return None


def cargar_imagen(nombre, tamaño=None, maximo=None, opaca=False):
    ruta = buscar_ruta(nombre)
    if ruta is None:
        print(f"[AVISO] No se encontró la imagen: {nombre}")
        return None
    try:
        img = pygame.image.load(ruta)
        img = img.convert() if opaca else img.convert_alpha()
    except pygame.error as e:
        print(f"[AVISO] No se pudo cargar {nombre}: {e}")
        return None
    if tamaño:
        return pygame.transform.smoothscale(img, tamaño)
    if maximo:
        w, h = img.get_size()
        esc = min(maximo / w, maximo / h)
        return pygame.transform.smoothscale(img, (int(w * esc), int(h * esc)))
    return img


def fondo_o_color(nombre, color):
    img = cargar_imagen(nombre, tamaño=(ancho, alto), opaca=True)
    if img is None:
        img = pygame.Surface((ancho, alto)).convert()
        img.fill(color)
    return img


def _ajustar(img, maximo):
    """Escala una imagen para que entre en un cuadrado de 'maximo' px."""
    w, h = img.get_size()
    esc = min(maximo / w, maximo / h)
    tam = (max(1, int(w * esc)), max(1, int(h * esc)))
    try:
        return pygame.transform.smoothscale(img, tam)
    except ValueError:
        return pygame.transform.scale(img, tam)



config = {"sonido": True}
SONIDOS_ARCHIVOS = {
    "comer": "comer.wav", "moneda": "moneda.wav", "click": "click.wav",
    "nivel": "nivel.wav", "error": "error.wav", "logro": "logro.wav",
    "pedo": "pedo.wav", "pedo_largo": "pedo_largo.wav", "furia": "furia.wav",
    "no": "no.wav", "ring": "ring.wav", "estatica": "estatica.wav",
    "susto": "susto.wav", "magia": "magia.wav",
}
sonidos = {}
if pygame.mixer.get_init():
    for _n, _a in SONIDOS_ARCHIVOS.items():
        _r = buscar_ruta(_a)
        if _r:
            try:
                sonidos[_n] = pygame.mixer.Sound(_r)
                sonidos[_n].set_volume(0.5)
            except pygame.error:
                pass


def sonar(nombre):
    if config["sonido"] and nombre in sonidos:
        sonidos[nombre].play()


def alternar_sonido():
    config["sonido"] = not config["sonido"]
    guardar()


ARCHIVO_GUARDADO = os.path.join(ruta_actual, "guardado.json")

COMIDAS = [
    ("Manzana", "manzana.png", 3, 10),
    ("Pizza", "pizza.png", 6, 20),
    ("Sushi", "sushi.png", 8, 25),
    ("Hamburguesa", "hamburguesa.png", 10, 30),
    ("Zanahoria", "zanahoria.png", 2, 8),
    ("Helado", "helado.png", 5, 12),
    ("Dona", "dona.png", 4, 12),
    ("Sopa", "sopa.png", 7, 18),
    ("Tacos", "tacos.png", 9, 26),
    ("Sandía", "sandia.png", 6, 16),
    ("Pastel", "pastel.png", 12, 30),
    ("Pollo", "pollo.png", 11, 32),
]

EFECTOS = {
    "Helado": {"jugar": 12},
    "Dona": {"jugar": 8},
    "Pastel": {"jugar": 15},
    "Sopa": {"dormir": 10},
    "Pizza": {"baño": -3},
    "Tacos": {"baño": -3},
    "Pollo": {"baño": -4},
    "Hamburguesa": {"baño": -5},
}

CULTIVOS = {
    "Manzana": {"tiempo": 40, "cosecha": 2, "semilla": 1},
    "Zanahoria": {"tiempo": 60, "cosecha": 3, "semilla": 1},
    "Sandía": {"tiempo": 120, "cosecha": 2, "semilla": 3},
}

MISIONES = [
    {"id": "comer", "texto": "Dale de comer a Pau 3 veces", "meta": 3, "premio": 15},
    {"id": "banar", "texto": "Báñala una vez", "meta": 1, "premio": 15},
    {"id": "dormir", "texto": "Haz que duerma una vez", "meta": 1, "premio": 10},
    {"id": "caricias", "texto": "Hazle 10 caricias", "meta": 10, "premio": 12},
    {"id": "minijuegos", "texto": "Juega 2 minijuegos", "meta": 2, "premio": 20},
    {"id": "cosechar", "texto": "Cosecha 2 veces en el jardín", "meta": 2, "premio": 20},
]
MISIONES_POR_ID = {m["id"]: m for m in MISIONES}

LOGROS = [
    {"id": "bocado", "nombre": "Primer bocado", "desc": "Dale de comer 1 vez", "stat": "comidas", "meta": 1, "premio": 10},
    {"id": "glotona", "nombre": "Glotona", "desc": "Dale de comer 30 veces", "stat": "comidas", "meta": 30, "premio": 40},
    {"id": "limpia", "nombre": "Limpia y fresca", "desc": "Báñala 5 veces", "stat": "banos", "meta": 5, "premio": 25},
    {"id": "granjera", "nombre": "Granjera", "desc": "Cosecha 10 veces", "stat": "cosechas", "meta": 10, "premio": 40},
    {"id": "mimosa", "nombre": "Mimosa", "desc": "Hazle 100 caricias", "stat": "caricias", "meta": 100, "premio": 35},
    {"id": "jugona", "nombre": "Jugona", "desc": "Juega 15 minijuegos", "stat": "minijuegos", "meta": 15, "premio": 50},
    {"id": "regalos", "nombre": "Cazaregalos", "desc": "Atrapa 5 regalos", "stat": "regalos", "meta": 5, "premio": 30},
    {"id": "suerte", "nombre": "Suertuda", "desc": "Gira la ruleta 5 veces", "stat": "ruleta", "meta": 5, "premio": 30},
    {"id": "nivel5", "nombre": "Crecidita", "desc": "Llega al nivel 5", "stat": "nivel", "meta": 5, "premio": 60},
    {"id": "racha3", "nombre": "Constante", "desc": "Racha de 3 días", "stat": "racha", "meta": 3, "premio": 50},
]

PRENDAS = [
  
    
    {"nombre": "Pelo Rojo", "archivo": "gorra.png", "slot": "pelo", "precio": 50,
    "offset": (0, -30), "tam": 260},
    {"nombre": "Septum", "archivo": "lentes.png", "slot": "boca", "precio": 10,
    "offset": (0, 9), "tam": 26},
    {"nombre": "tridente de diablo", "archivo": "camiseta.png", "slot": "cuerpo", "precio": 20,
    "offset": (0, 50), "tam": 150},
    {"nombre": "Paleta de pintor", "archivo": "sombrero.png", "slot": "mano", "precio": 20,
        "offset": (-90, 20), "tam": 100},
    
    {"nombre": "Uniceja", "archivo": "bufanda.png", "slot": "cara", "precio": 1,
    "offset": (0, -30), "tam": 120},
    {"nombre": "Antorcha", "archivo": "vestido.png", "slot": "mano", "precio": 20,
    "offset": (70, 0), "tam": 100},
    {"nombre": "Lentes swifties", "archivo": "corona.png", "slot": "cara", "precio": 30},
   
    {"nombre": "Orejas de gato", "archivo": "tutu.png", "slot": "cuerpo", "precio": 30,
     "offset": (0, -70), "tam": 110},
    {"nombre": "Moño rosa", "archivo": "mono_rosa.png", "slot": "adorno", "precio": 20,
     "offset": (0, -81), "tam": 70},
    {"nombre": "Cuerno de unicornio", "archivo": "cuerno_unicornio.png", "slot": "adorno",
     "precio": 100, "offset": (0, -112), "tam": 75},
    {"nombre": "Ojos de alien", "archivo": "ojos_alien.png", "slot": "cara", "precio": 25,
     "offset": (0, -33), "tam": 130},
    {"nombre": "Antenas de alien", "archivo": "antenas_alien.png", "slot": "adorno",
     "precio": 15, "offset": (0, -100), "tam": 100},
    {"nombre": "Caca", "archivo": "caca.png", "slot": "extra", "precio": 67,
     "offset": (0, -90), "tam": 60},
    {"nombre": "Barba de Papá Noel", "archivo": "barba_noel.png", "slot": "vello",
     "precio": 20, "offset": (0, 45), "tam": 130},
    {"nombre": "Gorrito de Navidad", "archivo": "gorro_navidad.png", "slot": "cabeza",
     "precio": 20, "offset": (17, -85), "tam": 120},
    {"nombre": "Ojos de Minion", "archivo": "ojos_minion.png", "slot": "cara", "precio": 40,
     "offset": (0, -25), "tam": 130},
    {"nombre": "Banana", "archivo": "banana.png", "slot": "mano", "precio": 15,
     "offset": (-95, 35), "tam": 70},
    {"nombre": "Pelo de Justin Bieber", "archivo": "pelo_bieber.png", "slot": "pelo",
     "precio": 100, "offset": (0, -60), "tam": 150},
    {"nombre": "Cadena de oro", "archivo": "cadena_oro.png", "slot": "cuello",
     "precio": 9999, "offset": (0, 45), "tam": 110},
    {"nombre": "Lluvia de plata", "archivo": "lluvia_dinero.png", "slot": "efecto",
     "precio": 200, "offset": (0, -10), "tam": 230},
    {"nombre": "Gorro de vaquero", "archivo": "gorro_vaquero.png", "slot": "cabeza",
     "precio": 25, "offset": (0, -80), "tam": 150},
    {"nombre": "Pistola", "archivo": "pistola.png", "slot": "mano", "precio": 30,
     "offset": (-95, 35), "tam": 80},
    {"nombre": "Gorro de mariachi", "archivo": "gorro_mariachi.png", "slot": "cabeza",
     "precio": 40, "offset": (0, -90), "tam": 160},
    {"nombre": "Guitarra", "archivo": "guitarra.png", "slot": "mano", "precio": 35,
     "offset": (80, 40), "tam": 140},
    {"nombre": "Bigote", "archivo": "bigote.png", "slot": "vello", "precio": 40,
     "offset": (0, 15), "tam": 80},
    {"nombre": "Boina", "archivo": "boina.png", "slot": "cabeza", "precio": 20,
     "offset": (0, -90), "tam": 120},
    {"nombre": "Baguette", "archivo": "baguette.png", "slot": "mano", "precio": 10,
     "offset": (90, 30), "tam": 130},
    {"nombre": "Gorro de Mario", "archivo": "gorro_mario.png", "slot": "cabeza",
     "precio": 16, "offset": (0, -85), "tam": 140},
    {"nombre": "Gorro de Luigi", "archivo": "gorro_luigi.png", "slot": "cabeza",
     "precio": 17, "offset": (0, -85), "tam": 140},
    {"nombre": "Corona de Peach", "archivo": "corona_peach.png", "slot": "cabeza",
     "precio": 60, "offset": (0, -105), "tam": 100},
    {"nombre": "Gorro de Kiko", "archivo": "gorro_kiko.png", "slot": "cabeza",
     "precio": 70, "offset": (9, -67), "tam": 130},
    {"nombre": "Paleta", "archivo": "paleta.png", "slot": "boca", "precio": 3,
     "offset": (25, 25), "tam": 60},
    {"nombre": "Cuernos de diablo", "archivo": "cuernos_diablo.png", "slot": "adorno",
     "precio": 34, "offset": (0, -87), "tam": 120},
    {"nombre": "Lentes PRO", "archivo": "lentes_pro.png", "slot": "cara", "precio": 67,
     "offset": (0, -25), "tam": 130},
]
PRENDAS_POR_NOMBRE = {p["nombre"]: p for p in PRENDAS}

ORDEN_CAPAS = ["cuerpo", "cuello", "mano", "cara", "vello", "boca",
               "pelo", "cabeza", "adorno", "extra", "efecto"]
PRENDAS_POR_PAGINA = 8
Y_ARMARIO = 150
Y_TIENDA = 200


def hoy():
    return time.strftime("%Y-%m-%d")


monedas = 100
inventario = {c[0]: 0 for c in COMIDAS}
ropa_puesta = {}
ropa_comprada = set()
records = {"atrapa": 0, "memoria": 0, "reflejos": 0, "simon": 0, "pong": 0,
           "flappy": 0, "comida_cae": 0, "flotaflota": 0, "saltar_nubes": 0}
stats = {"comidas": 0, "banos": 0, "cosechas": 0, "caricias": 0,
         "minijuegos": 0, "regalos": 0, "ruleta": 0}
logros_hechos = []
ultimo_dia = hoy()
bonus_diario_pendiente = 0
racha = 1
xp = 0
nivel = 1
huerta = [None, None, None]
cultivo_elegido = "Manzana"
misiones_dia = {"dia": hoy(), "progreso": {}, "reclamadas": []}
ruleta_dia = ""         

baño = 100
comer = 100
dormir = 100
jugar = 100
inodoro = 100           # 100 = sin ganas; en 0 Pau se hace encima
caca_en_piso = False    # Pau se hizo encima y hay que limpiar
pociones = 0            # pociones matadoras compradas
pociones_vida = 0
pociones_67 = 0
maldito = False         # "modo diablo": Pau tomó la poción y el juego queda ensangrentado
perdonado = False       # ya usaste la poción de vida una vez
sin_perdon = False      # le volviste a dar la matadora después del perdón: nunca más
enojo = 0               # 0-100; en 100 Pau se va volando
pau_ausente = False     # Pau se fue (llamalo con el celular)


def vida():
    """Promedio de todas las necesidades (0-100)."""
    return (baño + comer + dormir + jugar + inodoro) // 5


def es_poseida(nombre):
    prenda = PRENDAS_POR_NOMBRE[nombre]
    return prenda.get("precio", 0) == 0 or nombre in ropa_comprada


def prendas_poseidas():
    return [p for p in PRENDAS if es_poseida(p["nombre"])]


def _perder(valor, perdida):
    return max(min(valor, NECESIDAD_MINIMA_OFFLINE), valor - perdida)


def _aplicar_ausencia(ultima_vez):
    global baño, comer, dormir, jugar, inodoro
    segundos = max(0.0, time.time() - ultima_vez)
    perdida = min(OFFLINE_MAX_PERDIDA, int(segundos // OFFLINE_SEGUNDOS_POR_PUNTO))
    if perdida <= 0:
        return
    baño = _perder(baño, perdida)
    comer = _perder(comer, perdida)
    dormir = _perder(dormir, perdida)
    jugar = _perder(jugar, perdida)
    inodoro = _perder(inodoro, perdida)


def _limitar(v):
    return max(0, min(100, int(v)))


def _procesar_nuevo_dia(dia_anterior):
    """Racha y bonus diario. Se usa al cargar y también si cambia el día jugando."""
    global racha, monedas, bonus_diario_pendiente, ultimo_dia
    if dia_anterior == hoy():
        return
    ayer = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
    racha = racha + 1 if dia_anterior == ayer else 1
    bonus = BONUS_DIARIO + 5 * min(racha - 1, 6)
    monedas += bonus
    bonus_diario_pendiente = bonus
    ultimo_dia = hoy()


def cargar_datos():
    global monedas, baño, comer, dormir, jugar, inodoro
    global ultimo_dia, racha, xp, nivel, misiones_dia, ruleta_dia
    global caca_en_piso, pociones, maldito
    global pociones_vida, pociones_67, perdonado, sin_perdon, enojo, pau_ausente
    if os.path.isfile(ARCHIVO_GUARDADO):
        try:
            with open(ARCHIVO_GUARDADO, "r", encoding="utf-8") as f:
                datos = json.load(f)
            monedas = int(datos.get("monedas", 100))
            for k, v in datos.get("inventario", {}).items():
                if k in inventario:
                    inventario[k] = int(v)
            for nombre in datos.get("ropa_comprada", []):
                if nombre in PRENDAS_POR_NOMBRE:
                    ropa_comprada.add(nombre)
            for slot, nombre in datos.get("ropa", {}).items():
                prenda = PRENDAS_POR_NOMBRE.get(nombre)
                if prenda is not None and prenda["slot"] == slot:
                    ropa_puesta[slot] = nombre
                    ropa_comprada.add(nombre)
            for k in records:
                records[k] = int(datos.get("records", {}).get(k, 0))
            for k in stats:
                stats[k] = int(datos.get("stats", {}).get(k, 0))
            logros_hechos[:] = [k for k in datos.get("logros", [])
                                if any(l["id"] == k for l in LOGROS)]
            config["sonido"] = bool(datos.get("config", {}).get("sonido", True))
            ruleta_dia = str(datos.get("ruleta_dia", ""))

            nec = datos.get("necesidades", {})
            baño = _limitar(nec.get("baño", 100))
            comer = _limitar(nec.get("comer", 100))
            dormir = _limitar(nec.get("dormir", 100))
            jugar = _limitar(nec.get("jugar", 100))
            inodoro = _limitar(nec.get("inodoro", 100))
            caca_en_piso = bool(datos.get("caca_en_piso", False))
            pociones = max(0, int(datos.get("pociones", 0)))
            maldito = bool(datos.get("maldito", False))
            pociones_vida = max(0, int(datos.get("pociones_vida", 0)))
            pociones_67 = max(0, int(datos.get("pociones_67", 0)))
            perdonado = bool(datos.get("perdonado", False))
            sin_perdon = bool(datos.get("sin_perdon", False))
            enojo = _limitar(datos.get("enojo", 0))
            pau_ausente = bool(datos.get("pau_ausente", False))
            _aplicar_ausencia(float(datos.get("ultima_vez", time.time())))

            xp = max(0, int(datos.get("xp", 0)))
            nivel = max(1, int(datos.get("nivel", 1)))
            racha = max(1, int(datos.get("racha", 1)))
            for i, parcela in enumerate(datos.get("huerta", [])[:len(huerta)]):
                if (isinstance(parcela, dict) and parcela.get("cultivo") in CULTIVOS
                        and isinstance(parcela.get("inicio"), (int, float))):
                    huerta[i] = {
                        "cultivo": parcela["cultivo"],
                        "inicio": float(parcela["inicio"]),
                        "regada": bool(parcela.get("regada", False)),
                    }
            m = datos.get("misiones", {})
            if isinstance(m, dict) and m.get("dia") == hoy():
                misiones_dia = {
                    "dia": hoy(),
                    "progreso": {k: int(v) for k, v in m.get("progreso", {}).items()
                                 if k in MISIONES_POR_ID},
                    "reclamadas": [k for k in m.get("reclamadas", [])
                                   if k in MISIONES_POR_ID],
                }

            ultimo_dia = datos.get("ultimo_dia", hoy())
            _procesar_nuevo_dia(ultimo_dia)
            ultimo_dia = hoy()
            return
        except (OSError, ValueError, TypeError, AttributeError):
           
            try:
                os.replace(ARCHIVO_GUARDADO, ARCHIVO_GUARDADO + ".bak")
            except OSError:
                pass

    monedas = 100
    guardar()


def guardar():
    tmp = ARCHIVO_GUARDADO + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "monedas": monedas,
                    "inventario": inventario,
                    "ropa": ropa_puesta,
                    "ropa_comprada": sorted(ropa_comprada),
                    "records": records,
                    "stats": stats,
                    "logros": logros_hechos,
                    "config": config,
                    "ruleta_dia": ruleta_dia,
                    "necesidades": {
                        "baño": baño, "comer": comer,
                        "dormir": dormir, "jugar": jugar,
                        "inodoro": inodoro,
                    },
                    "caca_en_piso": caca_en_piso,
                    "pociones": pociones,
                    "pociones_vida": pociones_vida,
                    "pociones_67": pociones_67,
                    "maldito": maldito,
                    "perdonado": perdonado,
                    "sin_perdon": sin_perdon,
                    "enojo": enojo,
                    "pau_ausente": pau_ausente,
                    "ultima_vez": time.time(),
                    "ultimo_dia": ultimo_dia,
                    "racha": racha,
                    "xp": xp,
                    "nivel": nivel,
                    "huerta": huerta,
                    "misiones": misiones_dia,
                },
                f,
            )
        os.replace(tmp, ARCHIVO_GUARDADO)    
    except OSError as e:
        print(f"[AVISO] No se pudo guardar: {e}")


cargar_datos()

acum_descenso = 0.0      
ultimo_incremento_dormir = pygame.time.get_ticks()
ultimo_guardado = pygame.time.get_ticks()
ultimo_chequeo_dia = pygame.time.get_ticks()
ultimo_frame = pygame.time.get_ticks()
ultimo_zzz = 0
ultima_caricia = 0
modo_noche = False              # luces apagadas y Pau durmiendo
lleno_desde = 0                 # ms en que DORMIR llegó a 100 durmiendo
en_inodoro = None               # {"tipo": "pis"/"caca", "fin": ms} mientras está sentado
proximo_pedo = 0
furia = None                    # {"t0": ms} durante la escena de la poción
ultima_gota = 0
susto = None                    # {"t0": ms} durante un jumpscare
ultimo_chequeo_susto = 0
escena_perdon = None            # {"t0": ms, "dichas": n} poción de vida
haciendo_67 = None              # {"t0": ms}
inicio_mirada = 0               # modo diablo: desde cuándo te mira en la oscuridad
ultimo_baja_enojo = 0
# Posición y física de Pau (agarrarlo y revolearlo)
CASA_POU = (400.0, 320.0)
pau_pos = list(CASA_POU)
pau_fis = None                  # {"vx", "vy", "ang", "va"} mientras vuela por el aire
agarre = None                   # {"ini", "movido", "hist", "dx", "dy"} mientras lo agarrás
volviendo = None                # {"desde", "t0"} vuelve caminando a su lugar
yendose = None                  # {"t0"} se enojó mucho y se va volando
llegando = None                 # {"t0"} vuelve volando después de llamarlo
# Pau Jr
jr = None                       # visita en curso
proxima_visita_jr = 0
# Celular
cel = {"estado": "inicio", "t0": 0, "chat": [], "nodo": "", "opciones": [],
       "pendiente": None, "hackeado": False, "intentos_colgar": 0}
mensaje_temporal = ""
tiempo_mensaje = 0
cola_avisos = []
habla = ("", 0)                
habitacion_actual = 1
nombres_habitaciones = ["BAÑO", "SALA DE ESTAR", "HABITACIÓN", "COCINA", "JARDÍN"]
subpantalla = "normal"
pagina_armario = 0
pestaña_tienda = "comidas"
minijuego = None


def avisar(texto):
    """Pone un aviso en cola (así no se pisan entre sí)."""
    if len(cola_avisos) < 6 and (not cola_avisos or cola_avisos[-1] != texto):
        cola_avisos.append(texto)


def _procesar_avisos(ahora):
    global mensaje_temporal, tiempo_mensaje
    if cola_avisos and (not mensaje_temporal or ahora - tiempo_mensaje >= DURACION_AVISO):
        mensaje_temporal = cola_avisos.pop(0)
        tiempo_mensaje = ahora


# En modo diablo Pau está molesto: TODO lo que dice cambia.
DIALOGOS_MOLESTO = {
    "¡Ñam ñam!": "Esto es asqueroso.",
    "¡Qué fresquita!": "No me toques con eso.",
    "¡Qué linda me veo!": "Me veo ridículo. Gracias por nada.",
    "¡Qué alivio!": "¿Me estabas mirando? Asqueroso.",
    "No tengo ganas": "No. Andate.",
    "¡Buen día!": "...",
    "Uff... ¡todavía tenía sueño!": "...",
    "Ups... me hice encima": "Me hice encima. Por TU culpa.",
    "¡Gracias! Qué vergüenza...": "No me ayudes.",
    "¡Wiiiii!": "¡NO!",
    "¡Bajame!": "¡NO!",
}
FRASES_MOLESTO = ["¿Qué querés?", "Dejame en paz.", "No me hables.", "Me tenés harto.",
                  "Ni se te ocurra tocarme.", "Qué pesado/a que sos.", "Ufff...",
                  "¿Otra vez vos?", "Me aburrís."]


def pau_dice(texto, ms=1800, crudo=False):
    """Pau habla. En modo diablo se traduce a una versión molesta (salvo crudo=True)."""
    global habla
    if maldito and not crudo:
        texto = DIALOGOS_MOLESTO.get(texto) or random.choice(FRASES_MOLESTO)
    habla = (texto, pygame.time.get_ticks() + ms)


fondo_bano = fondo_o_color("bano.png", (173, 216, 230))
fondo_sala = fondo_o_color("principal.png", (240, 230, 140))
fondo_habitacion = fondo_o_color("habitacion.png", (230, 230, 250))
fondo_cocina = fondo_o_color("cocina.png", (255, 218, 185))
fondo_jardin = fondo_o_color("jardin.png", (150, 210, 150))

TAMAÑO_POU = 220

pou_base = cargar_imagen("pou.png", maximo=TAMAÑO_POU)
if pou_base is None:
    pou_base = pygame.Surface((150, 150), pygame.SRCALPHA)
    pou_base.fill((139, 69, 19))


def cargar_pou(nombre):
    img = cargar_imagen(nombre, maximo=TAMAÑO_POU)
    return img if img is not None else pou_base


pou_feliz = cargar_pou("paufeliz.png")
pou_maso = cargar_pou("paumaso.png")
pou_popo = cargar_pou("poupopo.png")
pou_triste = cargar_pou("poutriste.png")
pou_dormido = cargar_pou("poudormido.png")

UMBRAL_SUCIO = 60


def _teñir_sucio(img):
    t = img.copy()
    t.fill((190, 160, 110), special_flags=pygame.BLEND_RGB_MULT)
    return t


pou_dormido_sucio = _teñir_sucio(pou_dormido)

# --- Ojos de Pau (poción matadora / maldición) ------------------------------
# Posición y tamaño de los ojos en paumaso.png (imagen de 542 x 542 px).
OJOS_POU = [(215, 209), (326, 207)]
RADIO_OJO = (27, 12)
ANCHO_CARA = 542


def ojos_en(img, centro):
    """Posición en pantalla de los ojos de una cara de Pau dibujada en 'centro'."""
    k = img.get_width() / ANCHO_CARA
    x0 = centro[0] - img.get_width() / 2
    y0 = centro[1] - img.get_height() / 2
    return [(int(x0 + x * k), int(y0 + y * k)) for x, y in OJOS_POU]


def _cara_furia(base):
    """Pau enojado: piel roja, ojos negros con pupila roja y cejas fruncidas."""
    img = base.copy()
    img.fill((255, 120, 105), special_flags=pygame.BLEND_RGB_MULT)
    k = img.get_width() / ANCHO_CARA
    rx, ry = RADIO_OJO[0] * k, RADIO_OJO[1] * k
    for i, (ox, oy) in enumerate(ojos_en(img, img.get_rect().center)):
        pygame.draw.ellipse(img, (5, 0, 0), (ox - rx, oy - ry * 1.3, rx * 2, ry * 2.6))
        pygame.draw.circle(img, (200, 0, 0), (ox, oy), int(8 * k) + 2)
        pygame.draw.circle(img, (255, 70, 50), (ox, oy), int(3 * k) + 1)
        lado = -1 if i == 0 else 1          # ceja: alta afuera, baja hacia la nariz
        ext = (ox + lado * rx * 1.2, oy - ry * 3.4)
        inn = (ox - lado * rx * 0.9, oy - ry * 1.6)
        pygame.draw.line(img, (40, 10, 5), ext, inn, max(3, int(9 * k)))
    return img


def _cara_sangre(base):
    """Pau maldito: ojos rojos llenos de sangre y lágrimas de sangre."""
    img = base.copy()
    img.fill((255, 205, 200), special_flags=pygame.BLEND_RGB_MULT)
    k = img.get_width() / ANCHO_CARA
    rx, ry = RADIO_OJO[0] * k, RADIO_OJO[1] * k
    for i, (ox, oy) in enumerate(ojos_en(img, img.get_rect().center)):
        pygame.draw.ellipse(img, (150, 0, 0), (ox - rx, oy - ry, rx * 2, ry * 2))
        pygame.draw.circle(img, (25, 0, 0), (ox, oy), int(8 * k) + 1)
        for j, largo in enumerate((38, 62) if i == 0 else (55, 30)):
            x = ox - rx * 0.4 + j * rx * 0.8
            fin = oy + ry + largo * k
            pygame.draw.line(img, (130, 0, 0), (x, oy + ry * 0.6), (x, fin), max(2, int(5 * k)))
            pygame.draw.circle(img, (130, 0, 0), (int(x), int(fin)), max(2, int(5 * k)))
    return img


pou_furia = _cara_furia(pou_maso)
pou_maldito = _cara_sangre(pou_maso)
pou_susto = _cara_sangre(cargar_imagen("paumaso.png", maximo=700) or pou_maso)

# --- Pau Jr ------------------------------------------------------------------
jr_feliz = _ajustar(pou_feliz, TAMAÑO_JR)
jr_muerto = _ajustar(cargar_pou("paumuerto.png"), TAMAÑO_JR)
img_chupetin = cargar_imagen("chupetin.png", maximo=78)

# --- Celular -----------------------------------------------------------------
img_celular = cargar_imagen("celular.png", maximo=78)
rect_celular = pygame.Rect(10, 500, 62, 88)

TAMAÑO_OBJETO = 100
img_jabon = cargar_imagen("jabon.png", maximo=TAMAÑO_OBJETO)
img_ducha = cargar_imagen("ducha.png", maximo=TAMAÑO_OBJETO)
img_toalla = cargar_imagen("toalla.png", maximo=TAMAÑO_OBJETO)

imagenes_comidas = {c[0]: cargar_imagen(c[1], maximo=90) for c in COMIDAS}
imgs_caida = {n: _ajustar(i, 48) for n, i in imagenes_comidas.items() if i is not None}
img_cesta = _ajustar(pou_feliz, 90)

# --- Habitación: mesita de luz con velador ----------------------------------
# AJUSTAR posición y tamaño según el fondo "habitacion.png".
MESITA_BASE = (112, 478)            # centro inferior de la mesita
img_mesita = cargar_imagen("mesita.png", maximo=125)
img_velador = cargar_imagen("velador.png", maximo=125)
_alto_mesita = img_mesita.get_height() if img_mesita else 90
VELADOR_BASE = (MESITA_BASE[0], MESITA_BASE[1] - _alto_mesita + 12)
if img_velador is not None:
    rect_velador = img_velador.get_rect(midbottom=VELADOR_BASE)
else:
    rect_velador = pygame.Rect(0, 0, 70, 110)
    rect_velador.midbottom = VELADOR_BASE
CENTRO_LUZ_VELADOR = (rect_velador.centerx, rect_velador.y + rect_velador.height // 4)


def _crear_resplandor(radio, color):
    s = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
    for r in range(radio, 0, -3):
        a = int(color[3] * (1 - r / radio) ** 1.6)
        pygame.draw.circle(s, (*color[:3], a), (radio, radio), r)
    return s


RESPLANDOR_VELADOR = _crear_resplandor(150, (255, 225, 140, 150))

# Cama: dónde se acuesta Pau al dormir
CENTRO_CAMA = (425, 318)
TAMAÑO_ACOSTADO = 175

# --- Baño: inodoro -----------------------------------------------------------
INODORO_BASE = (675, 440)
img_inodoro = cargar_imagen("inodoro.png", maximo=135)
if img_inodoro is not None:
    rect_inodoro = img_inodoro.get_rect(midbottom=INODORO_BASE)
else:
    rect_inodoro = pygame.Rect(0, 0, 100, 120)
    rect_inodoro.midbottom = INODORO_BASE
boton_pis = pygame.Rect(612, 448, 70, 34)
boton_caca = pygame.Rect(688, 448, 80, 34)
# Dónde se sienta Pau (sobre el asiento del inodoro)
ASIENTO_INODORO = (rect_inodoro.x + rect_inodoro.width * 0.42,
                   rect_inodoro.y + rect_inodoro.height * 0.35)
img_caca = cargar_imagen("caca.png", maximo=60)
rect_caca_piso = pygame.Rect(0, 0, 70, 60)
rect_caca_piso.center = (530, 410)

# --- Poción matadora ---------------------------------------------------------
# (clave, nombre, archivo, precio)
POCIONES = [
    ("matadora", "Poción matadora", "pocion_matadora.png", PRECIO_POCION),
    ("vida", "Poción de vida", "pocion_vida.png", PRECIO_POCION_VIDA),
    ("67", "Poción 67", "pocion_67.png", PRECIO_POCION_67),
]
img_pociones = {c: cargar_imagen(a, maximo=110) for c, _, a, _ in POCIONES}
img_pociones_chicas = {c: cargar_imagen(a, maximo=62) for c, _, a, _ in POCIONES}
img_pocion = img_pociones["matadora"]
# En la cocina: una pocioncita por tipo (solo las que tengas)
rects_pocion_cocina = {c: pygame.Rect(80 + i * 78, 455, 72, 100)
                       for i, (c, _, _, _) in enumerate(POCIONES)}
fuente_furia = pygame.font.Font(None, 96)

VELO_NOCHE = pygame.Surface((ancho, alto))
VELO_NOCHE.set_alpha(175)
VELO_NOCHE.fill((0, 0, 40))
VELO_NEGRO = pygame.Surface((ancho, alto))
VELO_NEGRO.fill((0, 0, 0))
VELO_ROJO = pygame.Surface((ancho, alto))
VELO_ROJO.fill((150, 0, 0))


def efecto_sangre(sup):
    """Tiñe TODO de rojo y le pone sangre chorreando (se usa si 'maldito')."""
    if maldito:
        sangre.aplicar(sup, forzar=True)


def cargar_prenda(archivo, escala=1.0, tam=None):
    img = cargar_imagen(archivo, maximo=tam or TAMAÑO_POU)
    if img is not None and escala != 1.0:
        w, h = img.get_size()
        img = pygame.transform.smoothscale(img, (int(w * escala), int(h * escala)))
    return img


def _miniatura(img, maximo=90):
    caja = img.get_bounding_rect()
    if caja.width == 0 or caja.height == 0:
        return img
    recorte = img.subsurface(caja).copy()
    return _ajustar(recorte, maximo)


imagenes_ropa = {
    p["nombre"]: cargar_prenda(p["archivo"], p.get("escala", 1.0), p.get("tam"))
    for p in PRENDAS
}
imagenes_ropa_dormido = {
    p["nombre"]: cargar_prenda(p["archivo_dormido"], p.get("escala", 1.0), p.get("tam"))
    for p in PRENDAS if "archivo_dormido" in p
}
miniaturas_ropa = {
    n: _miniatura(img) for n, img in imagenes_ropa.items() if img is not None
}

fuente = pygame.font.Font(None, 28)
fuente_grande = pygame.font.Font(None, 36)
fuente_numero = pygame.font.Font(None, 22)
flecha_izquierda = pygame.Rect(10, 270, 50, 60)
flecha_derecha = pygame.Rect(740, 270, 50, 60)
objeto_jabon = pygame.Rect(190, 450, 110, 110)
objeto_ducha = pygame.Rect(345, 450, 110, 110)
objeto_toalla = pygame.Rect(500, 450, 110, 110)
objetos_bano = [
    (objeto_jabon, img_jabon, "Jabón"),
    (objeto_ducha, img_ducha, "Ducha"),
    (objeto_toalla, img_toalla, "Toalla"),
]

fase_bano = 0
progreso_bano = [0.0, 0.0, 0.0]
FACTORES_BANO = [0.15, 0.20, 0.20]
PISTAS_BANO = [
    "1/3: Frota el jabón sobre Pau",
    "2/3: Pásale la ducha para enjuagarla",
    "3/3: Sécala con la toalla",
]

arrastrando = None
pos_arrastre = (0, 0)
zona_pou = pygame.Rect(0, 0, 200, 220)
zona_pou.center = (400, 320)
_azar = random.Random(7)
BURBUJAS = [
    (_azar.randint(-85, 85), _azar.randint(-95, 95), _azar.randint(10, 20))
    for _ in range(45)
]
GOTAS = [(_azar.randint(-90, 90), _azar.randint(-100, 100)) for _ in range(30)]
MANCHAS = [
    (_azar.randint(-70, 70), _azar.randint(-80, 80), _azar.randint(4, 9))
    for _ in range(14)
]


def _tenue(img):
    if img is None:
        return None
    t = img.copy()
    t.set_alpha(90)
    return t


imgs_bano_tenues = [_tenue(o[1]) for o in objetos_bano]

boton_armario = pygame.Rect(480, 480, 140, 50)
boton_comidas = pygame.Rect(325, 480, 150, 50)

# Sala de estar
boton_minijuegos = pygame.Rect(150, 480, 160, 50)
boton_tienda = pygame.Rect(320, 480, 160, 50)
boton_ruleta = pygame.Rect(490, 480, 160, 50)
boton_misiones = pygame.Rect(235, 540, 160, 40)
boton_logros = pygame.Rect(405, 540, 160, 40)

botones_minijuegos = [pygame.Rect(275, 450, 250, 62) if i == 8 else
                      pygame.Rect(140 + (i % 2) * 270, 130 + (i // 2) * 80, 250, 62)
                      for i in range(9)]

boton_volver = pygame.Rect(20, 20, 100, 40)
boton_reintentar = pygame.Rect(300, 360, 200, 45)

boton_quitar_ropa = pygame.Rect(640, 545, 140, 40)
boton_pag_ant = pygame.Rect(250, 545, 80, 40)
boton_pag_sig = pygame.Rect(470, 545, 80, 40)
boton_tab_comidas = pygame.Rect(170, 148, 140, 40)
boton_tab_ropa = pygame.Rect(330, 148, 140, 40)
boton_tab_especial = pygame.Rect(490, 148, 140, 40)
rects_tarjeta_pocion = {c: pygame.Rect(70 + i * 230, 210, 200, 310)
                        for i, c in enumerate(("matadora", "vida", "67"))}

boton_semilla = pygame.Rect(20, 125, 200, 40)
parcelas = [pygame.Rect(190 + i * 155, 450, 110, 100) for i in range(3)]

pos_y_barras = 65
barra_baño = pygame.Rect(24, pos_y_barras, 136, 20)
barra_comer = pygame.Rect(176, pos_y_barras, 136, 20)
barra_dormir = pygame.Rect(328, pos_y_barras, 136, 20)
barra_jugar = pygame.Rect(480, pos_y_barras, 136, 20)
barra_inodoro = pygame.Rect(632, pos_y_barras, 136, 20)


def dibujar_corazon(sup, centro, r, color):
    cx, cy = centro
    pygame.draw.circle(sup, color, (cx - r // 2, cy - r // 4), r // 2 + 1)
    pygame.draw.circle(sup, color, (cx + r // 2, cy - r // 4), r // 2 + 1)
    pygame.draw.polygon(
        sup, color, [(cx - r, cy - r // 6), (cx + r, cy - r // 6), (cx, cy + r)]
    )


def dibujar_estrella(sup, centro, r, color):
    puntos = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        puntos.append((centro[0] + rad * math.cos(ang), centro[1] + rad * math.sin(ang)))
    pygame.draw.polygon(sup, color, puntos)


particulas = []


def crear_particulas(tipo, pos, n=6):
    """tipo: corazon, estrella, moneda, burbuja, zzz, pedo, sangre (salpicadura) o gota."""
    # Modo diablo: en los minijuegos todo festejo es una salpicadura de sangre.
    if maldito and subpantalla == "minijuego" and tipo in ("estrella", "moneda",
                                                          "burbuja", "corazon"):
        tipo, n = "sangre", n + 3
    for _ in range(n):
        if tipo == "zzz":
            vx, vy, dur = random.uniform(10, 25), random.uniform(-40, -25), 2.2
        elif tipo == "pedo":
            vx, vy = random.uniform(-60, 60), random.uniform(-35, 10)
            dur = random.uniform(1.2, 2.0)
        elif tipo == "gota":
            vx, vy, dur = 0, random.uniform(20, 45), random.uniform(1.0, 1.6)
        elif tipo == "sangre":
            vx, vy = random.uniform(-150, 150), random.uniform(-220, -40)
            dur = random.uniform(0.7, 1.2)
        else:
            vx, vy = random.uniform(-45, 45), random.uniform(-120, -50)
            dur = random.uniform(0.9, 1.5)
        particulas.append({
            "tipo": tipo,
            "x": pos[0] + random.randint(-15, 15),
            "y": pos[1] + random.randint(-10, 10),
            "vx": vx, "vy": vy, "edad": 0.0, "dur": dur,
            "tam": random.randint(8, 13),
        })
    del particulas[:-80]


def actualizar_particulas(dt):
    for p in particulas:
        p["edad"] += dt
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        if p["tipo"] == "gota":
            p["vy"] += 160 * dt
        elif p["tipo"] == "sangre":
            p["vy"] += 600 * dt
    particulas[:] = [p for p in particulas if p["edad"] < p["dur"]]


def dibujar_particulas(ventana):
    for p in particulas:
        alfa = max(0, int(255 * (1 - p["edad"] / p["dur"])))
        r = p["tam"]
        if p["tipo"] == "zzz":
            s = fuente_grande.render("Z", True, (70, 70, 160))
        elif p["tipo"] == "pedo":
            r = int(p["tam"] * (1.2 + 2.2 * p["edad"] / p["dur"]))
            s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (140, 170, 60), (r + 1, r + 1), r)
            pygame.draw.circle(s, (170, 200, 90), (r - r // 3, r - r // 3), r // 2)
            alfa = alfa * 3 // 4
        elif p["tipo"] == "gota":
            s = pygame.Surface((10, 16), pygame.SRCALPHA)
            pygame.draw.circle(s, (150, 0, 0), (5, 11), 4)
            pygame.draw.polygon(s, (150, 0, 0), [(5, 1), (1, 10), (9, 10)])
        elif p["tipo"] == "sangre":
            rr = max(2, r // 2)
            s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (160, 0, 0), (rr + 1, rr + 1), rr)
        else:
            lado = r * 3
            s = pygame.Surface((lado, lado), pygame.SRCALPHA)
            c = (lado // 2, lado // 2)
            if p["tipo"] == "corazon":
                dibujar_corazon(s, c, r, (235, 70, 110))
            elif p["tipo"] == "estrella":
                dibujar_estrella(s, c, r, (255, 210, 50))
            elif p["tipo"] == "moneda":
                pygame.draw.circle(s, (255, 215, 0), c, r)
                pygame.draw.circle(s, (180, 130, 0), c, r, 2)
            else:
                pygame.draw.circle(s, (255, 255, 255), c, r, 2)
        s.set_alpha(alfa)
        ventana.blit(s, s.get_rect(center=(int(p["x"]), int(p["y"]))))


def color_barra(valor):
    if valor > 60:
        return (100, 200, 100)
    if valor > 30:
        return (235, 200, 60)
    return (220, 70, 70)


def dibujar_barra(ventana, rectangulo, nombre, valor):
    pygame.draw.rect(ventana, (220, 220, 220), rectangulo)
    ancho_barra = int(rectangulo.width * valor / 100)
    parte_llena = pygame.Rect(rectangulo.x, rectangulo.y, ancho_barra, rectangulo.height)
    pygame.draw.rect(ventana, color_barra(valor), parte_llena)
    alerta = valor <= 20 and (pygame.time.get_ticks() // 300) % 2 == 0
    pygame.draw.rect(ventana, (200, 0, 0) if alerta else (0, 0, 0), rectangulo, 2)

    texto_nombre = fuente.render(nombre, True, (0, 0, 0))
    ventana.blit(texto_nombre,
                 (rectangulo.centerx - texto_nombre.get_width() // 2, rectangulo.y - 22))
    texto_numero = fuente_numero.render(str(valor), True, (0, 0, 0))
    ventana.blit(texto_numero,
                 (rectangulo.centerx - texto_numero.get_width() // 2, rectangulo.bottom + 2))


def dibujar_boton(ventana, rectangulo, texto):
    sobre = rectangulo.collidepoint(pygame.mouse.get_pos())
    relleno = (225, 238, 255) if sobre else (255, 255, 255)
    pygame.draw.rect(ventana, relleno, rectangulo, border_radius=8)
    pygame.draw.rect(ventana, (0, 0, 0), rectangulo, 2, border_radius=8)
    texto_render = fuente.render(texto, True, (0, 0, 0))
    ventana.blit(texto_render, texto_render.get_rect(center=rectangulo.center))


def dibujar_objeto(ventana, rectangulo, imagen, texto):
    if imagen is None:
        dibujar_boton(ventana, rectangulo, texto)
    else:
        ventana.blit(imagen, imagen.get_rect(center=rectangulo.center))


def dibujar_monedas(ventana):
    txt = fuente_grande.render(f"Monedas: {monedas}", True, (0, 0, 0))
    ventana.blit(txt, (725 - txt.get_width(), 10))


def dibujar_burbuja_habla(ventana, texto, centro_x, y):
    t = fuente.render(texto, True, (0, 0, 0))
    r = t.get_rect(center=(centro_x, y)).inflate(24, 14)
    pygame.draw.rect(ventana, (255, 255, 255), r, border_radius=12)
    pygame.draw.rect(ventana, (0, 0, 0), r, 2, border_radius=12)
    cola = [(centro_x - 8, r.bottom - 1), (centro_x + 8, r.bottom - 1),
            (centro_x, r.bottom + 10)]
    pygame.draw.polygon(ventana, (255, 255, 255), cola)
    pygame.draw.lines(ventana, (0, 0, 0), False, [cola[0], cola[2], cola[1]], 2)
    ventana.blit(t, t.get_rect(center=r.center))


FRASES_MALDITO = ["¿Qué mirás?", "Los estoy mirando...", "No me olvidé de lo que hiciste.",
                  "Me tenés podrido.", "¿Por qué me hiciste esto?", "Andate.",
                  "Ni me hables.", "Nunca me voy a ir."]


def frase_pau():
    if maldito:
        ciclo = pygame.time.get_ticks() // 4000
        return FRASES_MALDITO[ciclo % len(FRASES_MALDITO)] if ciclo % 2 == 0 else None
    if enojo >= 60:
        return "¡Estoy re enojado!"
    if caca_en_piso:
        return "¡Limpiá la caca!"
    necesidades = [
        (baño, "¡Necesito un baño!"),
        (comer, "¡Tengo hambre!"),
        (dormir, "¡Tengo sueño!"),
        (jugar, "¡Quiero jugar!"),
        (inodoro, "¡Me hago encima!"),
    ]
    valor, frase = min(necesidades, key=lambda n: n[0])
    return frase if valor < 50 else None


def dibujar_bano(ventana):
    cx, cy = zona_pou.center

    if fase_bano == 0:
        espuma = progreso_bano[0]
    elif fase_bano == 1:
        espuma = 100 - progreso_bano[1]
    else:
        espuma = 0
    n = int(len(BURBUJAS) * espuma / 100)
    for dx, dy, r in BURBUJAS[:n]:
        pygame.draw.circle(ventana, (255, 255, 255), (cx + dx, cy + dy), r)
        pygame.draw.circle(ventana, (190, 215, 240), (cx + dx, cy + dy), r, 2)

    if fase_bano == 1:
        mojado = progreso_bano[1]
    elif fase_bano == 2:
        mojado = 100 - progreso_bano[2]
    else:
        mojado = 0
    g = int(len(GOTAS) * mojado / 100)
    for dx, dy in GOTAS[:g]:
        pygame.draw.circle(ventana, (90, 160, 255), (cx + dx, cy + dy), 5)

    for i, (rect, img, texto) in enumerate(objetos_bano):
        if i == arrastrando:
            continue
        imagen = img if i == fase_bano else imgs_bano_tenues[i]
        dibujar_objeto(ventana, rect, imagen, texto)

    if arrastrando is not None:
        rect, img, texto = objetos_bano[arrastrando]
        r = rect.copy()
        r.center = pos_arrastre
        if arrastrando == 1:
            for k in range(-2, 3):
                x = pos_arrastre[0] + k * 14
                pygame.draw.line(ventana, (90, 160, 255),
                                 (x, pos_arrastre[1] + 45), (x - 4, pos_arrastre[1] + 85), 3)
        dibujar_objeto(ventana, r, img, texto)

    pista = f"{PISTAS_BANO[fase_bano]} ({int(progreso_bano[fase_bano])}%)"
    txt = fuente.render(pista, True, (0, 0, 0))
    fondo_txt = txt.get_rect(center=(ancho // 2, 120)).inflate(16, 8)
    pygame.draw.rect(ventana, (255, 255, 255), fondo_txt)
    pygame.draw.rect(ventana, (0, 0, 0), fondo_txt, 2)
    ventana.blit(txt, txt.get_rect(center=fondo_txt.center))


def rect_tarjeta_comida(i, y0):
    return pygame.Rect(70 + (i % 4) * 170, y0 + (i // 4) * 160, 150, 155)


def texto_efectos(nombre, valor):
    partes = [f"+{valor} comer"]
    for k, v in EFECTOS.get(nombre, {}).items():
        partes.append(f"{v:+d} {k}")
    return " ".join(partes)


def dibujar_catalogo(ventana, titulo, modo):
    ventana.fill((200, 220, 240))
    t = fuente_grande.render(titulo, True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 100))
    y0 = Y_TIENDA if modo == "tienda" else Y_ARMARIO

    for i, comida in enumerate(prendas_de_pagina(COMIDAS)):
        nombre, _, precio, valor = comida
        rect = rect_tarjeta_comida(i, y0)
        pygame.draw.rect(ventana, (255, 255, 255), rect)
        pygame.draw.rect(ventana, (0, 0, 0), rect, 2)

        dibujar_comida(ventana, nombre, (rect.centerx, rect.y + 45), imagenes_comidas, 28)

        n = fuente.render(nombre, True, (0, 0, 0))
        ventana.blit(n, (rect.centerx - n.get_width() // 2, rect.y + 92))

        sub = f"{precio} monedas" if modo == "tienda" else f"Tienes: {inventario[nombre]}"
        s_ = fuente_numero.render(sub, True, (0, 0, 0))
        ventana.blit(s_, (rect.centerx - s_.get_width() // 2, rect.y + 116))
        e = fuente_numero.render(texto_efectos(nombre, valor), True, (90, 90, 90))
        ventana.blit(e, (rect.centerx - e.get_width() // 2, rect.y + 134))

    dibujar_boton(ventana, boton_volver, "Volver")
    dibujar_paginacion(ventana, len(COMIDAS))


def total_paginas(cantidad):
    return max(1, math.ceil(cantidad / PRENDAS_POR_PAGINA))


def prendas_de_pagina(lista):
    ini = pagina_armario * PRENDAS_POR_PAGINA
    return lista[ini:ini + PRENDAS_POR_PAGINA]


def rect_tarjeta_ropa(i, y0):
    return pygame.Rect(70 + (i % 4) * 170, y0 + (i // 4) * 160, 150, 150)


def manejar_paginacion(posicion, cantidad):
    global pagina_armario
    paginas = total_paginas(cantidad)
    if paginas <= 1:
        return False
    if boton_pag_ant.collidepoint(posicion):
        pagina_armario = max(0, pagina_armario - 1)
        return True
    if boton_pag_sig.collidepoint(posicion):
        pagina_armario = min(paginas - 1, pagina_armario + 1)
        return True
    return False


def dibujar_paginacion(ventana, cantidad):
    paginas = total_paginas(cantidad)
    if paginas > 1:
        dibujar_boton(ventana, boton_pag_ant, "<")
        dibujar_boton(ventana, boton_pag_sig, ">")
        pag = fuente.render(f"{pagina_armario + 1}/{paginas}", True, (0, 0, 0))
        ventana.blit(pag, pag.get_rect(center=(400, 565)))


def dibujar_tarjeta_prenda(ventana, rect, prenda, borde_verde, subtitulo):
    nombre = prenda["nombre"]
    pygame.draw.rect(ventana, (255, 255, 255), rect)
    if borde_verde:
        pygame.draw.rect(ventana, (0, 160, 0), rect, 4)
    else:
        pygame.draw.rect(ventana, (0, 0, 0), rect, 2)

    mini = miniaturas_ropa.get(nombre)
    if mini is not None:
        ventana.blit(mini, mini.get_rect(center=(rect.centerx, rect.y + 55)))
    else:                       
        q = fuente_grande.render("?", True, (170, 170, 170))
        ventana.blit(q, q.get_rect(center=(rect.centerx, rect.y + 55)))

    n = fuente.render(nombre, True, (0, 0, 0))
    ventana.blit(n, (rect.centerx - n.get_width() // 2, rect.y + 105))
    s = fuente_numero.render(subtitulo, True, (0, 0, 0))
    ventana.blit(s, (rect.centerx - s.get_width() // 2, rect.y + 128))


def alternar_prenda(prenda):
    slot, nombre = prenda["slot"], prenda["nombre"]
    if ropa_puesta.get(slot) == nombre:
        del ropa_puesta[slot]
        avisar(f"Te quitaste: {nombre}")
    else:
        ropa_puesta[slot] = nombre
        avisar(f"Pau lleva: {nombre}")
        pau_dice("¡Qué linda me veo!")
    guardar()


def comprar_prenda(prenda):
    global monedas
    nombre = prenda["nombre"]
    if es_poseida(nombre):
        avisar(f"Ya tienes {nombre}")
        return False
    if monedas < prenda["precio"]:
        avisar("No te alcanzan las monedas")
        sonar("error")
        return False
    monedas -= prenda["precio"]
    ropa_comprada.add(nombre)
    guardar()
    avisar(f"Compraste {nombre}")
    sonar("moneda")
    return True


def dibujar_armario(ventana):
    ventana.fill((200, 220, 240))
    t = fuente_grande.render("ARMARIO", True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 100))

    lista = prendas_poseidas()
    if not lista:
        m = fuente.render("Aún no tienes ropa. ¡Compra en la Tienda!", True, (0, 0, 0))
        ventana.blit(m, m.get_rect(center=(400, 300)))

    for i, prenda in enumerate(prendas_de_pagina(lista)):
        puesta = ropa_puesta.get(prenda["slot"]) == prenda["nombre"]
        dibujar_tarjeta_prenda(ventana, rect_tarjeta_ropa(i, Y_ARMARIO), prenda, puesta,
                               "Puesta" if puesta else "Poner")

    dibujar_boton(ventana, boton_volver, "Volver")
    dibujar_boton(ventana, boton_quitar_ropa, "Quitar todo")
    dibujar_paginacion(ventana, len(lista))


def dibujar_tienda_ropa(ventana):
    ventana.fill((200, 220, 240))
    t = fuente_grande.render("TIENDA DE ROPA", True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 100))

    for i, prenda in enumerate(prendas_de_pagina(PRENDAS)):
        tiene = es_poseida(prenda["nombre"])
        sub = "Comprada" if tiene else f"{prenda['precio']} monedas"
        dibujar_tarjeta_prenda(ventana, rect_tarjeta_ropa(i, Y_TIENDA), prenda, tiene, sub)

    dibujar_boton(ventana, boton_volver, "Volver")
    dibujar_paginacion(ventana, len(PRENDAS))


def dibujar_tienda_especial(ventana):
    ventana.fill((60, 20, 30))
    t = fuente_grande.render("TIENDA ESPECIAL", True, (255, 220, 220))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 100))

    descripciones = {
        "matadora": [("Dásela a Pau en la cocina...", (200, 160, 160)),
                     ("¡NO lo hagas!", (255, 60, 60))],
        "vida": [("Lo pone feliz y te pide", (190, 230, 190)),
                 ("perdón. Solo perdona 1 vez.", (190, 230, 190))],
        "67": [("Pau hace el 67.", (190, 210, 255)),
               ("Six... seven...", (190, 210, 255))],
    }
    colores = {"matadora": (255, 80, 80), "vida": (110, 230, 120), "67": (120, 170, 255)}
    flota = int(math.sin(pygame.time.get_ticks() / 300) * 4)
    for clave, nombre, _, precio in POCIONES:
        r = rects_tarjeta_pocion[clave]
        sobre = r.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(ventana, (40, 0, 10), r, border_radius=14)
        pygame.draw.rect(ventana, colores[clave] if sobre else (110, 30, 40), r, 4,
                         border_radius=14)
        img = img_pociones[clave]
        if img is not None:
            ventana.blit(img, img.get_rect(center=(r.centerx, r.y + 85 + flota)))
        if clave == "67":
            dibujar_etiqueta_67(ventana, (r.centerx, r.y + 105 + flota))
        lineas = [
            (fuente, nombre, colores[clave], 170),
            (fuente_numero, f"{precio} monedas", (255, 220, 220), 198),
            (fuente_numero, f"Tienes: {cantidad_pocion(clave)}", (255, 220, 220), 220),
        ] + [(fuente_numero, t, c, 252 + i * 22) for i, (t, c) in enumerate(descripciones[clave])]
        for f, texto, color, y in lineas:
            s = f.render(texto, True, color)
            ventana.blit(s, s.get_rect(center=(r.centerx, r.y + y)))
    dibujar_boton(ventana, boton_volver, "Volver")


def dibujar_etiqueta_67(ventana, centro):
    t = fuente.render("67", True, (255, 255, 255))
    caja = t.get_rect(center=centro).inflate(10, 4)
    pygame.draw.rect(ventana, (20, 40, 120), caja, border_radius=6)
    ventana.blit(t, t.get_rect(center=centro))


def cantidad_pocion(clave):
    return {"matadora": pociones, "vida": pociones_vida, "67": pociones_67}[clave]


def comprar_pocion(clave):
    global monedas, pociones, pociones_vida, pociones_67
    nombre, precio = next((n, p) for c, n, _, p in POCIONES if c == clave)
    if monedas < precio:
        avisar("No te alcanzan las monedas")
        sonar("error")
        return
    monedas -= precio
    if clave == "matadora":
        pociones += 1
    elif clave == "vida":
        pociones_vida += 1
    else:
        pociones_67 += 1
    guardar()
    avisar(f"Compraste una {nombre}")
    sonar("moneda")


def dibujar_tienda(ventana):
    if pestaña_tienda == "comidas":
        dibujar_catalogo(ventana, "TIENDA DE COMIDAS", "tienda")
    elif pestaña_tienda == "especial":
        dibujar_tienda_especial(ventana)
    else:
        dibujar_tienda_ropa(ventana)
    for rect, texto, clave in (
        (boton_tab_comidas, "Comidas", "comidas"),
        (boton_tab_ropa, "Ropa", "ropa"),
        (boton_tab_especial, "Especial", "especial"),
    ):
        dibujar_boton(ventana, rect, texto)
        if pestaña_tienda == clave:
            pygame.draw.rect(ventana, (0, 120, 255), rect, 4, border_radius=8)


def dibujar_ropa(ventana, centro):
    for slot in ORDEN_CAPAS:
        nombre = ropa_puesta.get(slot)
        if nombre is None:
            continue
        prenda = PRENDAS_POR_NOMBRE[nombre]
        img = imagenes_ropa_dormido.get(nombre) if modo_noche else None
        if img is None:
            img = imagenes_ropa[nombre]
        if img is None:
            continue
        dx, dy = prenda.get("offset", (0, 0))
        ventana.blit(img, img.get_rect(center=(centro[0] + dx, centro[1] + dy)))


def dibujar_suciedad(ventana, centro):
    """Mantiene visible la suciedad de Pau mientras duerme."""
    if baño >= UMBRAL_SUCIO:
        return
    n = max(1, math.ceil(len(MANCHAS) * (UMBRAL_SUCIO - baño) / UMBRAL_SUCIO))
    for dx, dy, r in MANCHAS[:n]:
        pygame.draw.circle(ventana, (110, 75, 40), (centro[0] + dx, centro[1] + dy), r)


def dibujar_mesita_velador(ventana):
    if img_mesita is not None:
        ventana.blit(img_mesita, img_mesita.get_rect(midbottom=MESITA_BASE))
    if not modo_noche:                      # luz prendida
        ventana.blit(RESPLANDOR_VELADOR,
                     RESPLANDOR_VELADOR.get_rect(center=CENTRO_LUZ_VELADOR))
    if img_velador is not None:
        ventana.blit(img_velador, rect_velador)
    else:
        pygame.draw.rect(ventana, (240, 220, 160), rect_velador, border_radius=8)


def dibujar_inodoro(ventana):
    if img_inodoro is not None:
        ventana.blit(img_inodoro, rect_inodoro)
    else:
        dibujar_boton(ventana, rect_inodoro, "Inodoro")
    if en_inodoro is None:
        dibujar_boton(ventana, boton_pis, "Pis")
        dibujar_boton(ventana, boton_caca, "Caca")


def dibujar_pau_en_inodoro(ventana, ahora):
    """Pau sentado en el inodoro (más chiquito) mientras hace sus cosas."""
    img = _ajustar(obtener_personaje(), 120)
    tiembla = int(math.sin(ahora / 40) * 2) if en_inodoro["tipo"] == "caca" else 0
    ventana.blit(img, img.get_rect(midbottom=(ASIENTO_INODORO[0] + tiembla,
                                              ASIENTO_INODORO[1] + 36)))
    texto = "Psssssss..." if en_inodoro["tipo"] == "pis" else "¡Nnnngh!"
    dibujar_burbuja_habla(ventana, texto, int(ASIENTO_INODORO[0]), int(ASIENTO_INODORO[1]) - 125)


def dibujar_caca_piso(ventana, ahora):
    if not caca_en_piso:
        return
    if img_caca is not None:
        ventana.blit(img_caca, img_caca.get_rect(center=rect_caca_piso.center))
    else:
        pygame.draw.circle(ventana, (110, 70, 30), rect_caca_piso.center, 22)
    for k in range(3):                      # olor
        x = rect_caca_piso.centerx - 18 + k * 18
        pts = [(x + math.sin(ahora / 200 + k + j / 2) * 4, rect_caca_piso.top - j * 6)
               for j in range(6)]
        pygame.draw.lines(ventana, (110, 150, 60), False, pts, 2)


def pau_compuesto(angulo=0, tam=None, suciedad=False):
    """Pau con su ropa en una sola imagen, opcionalmente achicado y girado."""
    lienzo = pygame.Surface((420, 420), pygame.SRCALPHA)
    c = (210, 210)
    img = obtener_personaje()
    lienzo.blit(img, img.get_rect(center=c))
    if suciedad:
        dibujar_suciedad(lienzo, c)
    dibujar_ropa(lienzo, c)
    img = lienzo.subsurface(lienzo.get_bounding_rect()).copy()
    if tam:
        img = _ajustar(img, tam)
    return pygame.transform.rotate(img, angulo) if angulo else img


def personaje_acostado():
    """Pau (con su ropa) acostado sobre la cama, girado ANGULO_ACOSTADO grados."""
    return pau_compuesto(ANGULO_ACOSTADO, TAMAÑO_ACOSTADO, suciedad=True)


def obtener_personaje():
    if furia is not None:
        return pou_furia
    if maldito:
        return pou_maldito
    if modo_noche:
        return pou_dormido_sucio if baño < UMBRAL_SUCIO else pou_dormido
    if escena_perdon is not None or haciendo_67 is not None:
        return pou_feliz
    if yendose is not None or enojo >= 60:
        return pou_triste

    peor = min(baño, comer, dormir, jugar, inodoro)
    if peor <= 30:
        return pou_triste
    if peor < 60:
        return pou_popo
    if peor < 80:
        return pou_maso
    return pou_feliz


def xp_para_siguiente(n):
    return 40 + 20 * n


def ganar_xp(cantidad):
    global xp, nivel, monedas
    xp += cantidad
    while xp >= xp_para_siguiente(nivel):
        xp -= xp_para_siguiente(nivel)
        nivel += 1
        premio = 20 + 5 * nivel
        monedas += premio
        avisar(f"¡Nivel {nivel}! +{premio} monedas")
        sonar("nivel")
        crear_particulas("estrella", (400, 300), 14)


def dibujar_nivel(ventana):
    t = fuente.render(f"Nv. {nivel}", True, (0, 0, 0))
    ventana.blit(t, (30, 8))
    barra = pygame.Rect(95, 14, 110, 10)
    pygame.draw.rect(ventana, (220, 220, 220), barra)
    lleno = int(barra.width * xp / xp_para_siguiente(nivel))
    pygame.draw.rect(ventana, (120, 100, 230), (barra.x, barra.y, lleno, barra.height))
    pygame.draw.rect(ventana, (0, 0, 0), barra, 2)


def aplicar_efectos(nombre):
    global baño, dormir, jugar, inodoro
    # Lo que entra, sale: comer da ganas de ir al baño.
    valor = next((c[3] for c in COMIDAS if c[0] == nombre), 0)
    inodoro = max(1, inodoro - valor // 3)
    for k, v in EFECTOS.get(nombre, {}).items():
        if k == "baño":
            baño = _limitar(max(1, baño + v) if v < 0 else baño + v)
        elif k == "dormir":
            dormir = _limitar(dormir + v)
        elif k == "jugar":
            jugar = _limitar(jugar + v)


# --- Logros ---
def valor_logro(l):
    if l["stat"] == "nivel":
        return nivel
    if l["stat"] == "racha":
        return racha
    return stats.get(l["stat"], 0)


def revisar_logros():
    global monedas
    for l in LOGROS:
        if l["id"] not in logros_hechos and valor_logro(l) >= l["meta"]:
            logros_hechos.append(l["id"])
            monedas += l["premio"]
            avisar(f"¡Logro: {l['nombre']}! +{l['premio']}")
            sonar("logro")
            crear_particulas("estrella", (400, 250), 12)
            guardar()


def rect_logro(i):
    return pygame.Rect(40 + (i // 5) * 370, 140 + (i % 5) * 85, 350, 75)


def dibujar_logros(ventana):
    ventana.fill((200, 220, 240))
    t = fuente_grande.render("LOGROS", True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 95))
    c = fuente_numero.render(f"{len(logros_hechos)}/{len(LOGROS)} completados", True, (0, 0, 0))
    ventana.blit(c, c.get_rect(center=(400, 128)))

    for i, l in enumerate(LOGROS):
        r = rect_logro(i)
        hecho = l["id"] in logros_hechos
        pygame.draw.rect(ventana, (255, 255, 255), r, border_radius=10)
        pygame.draw.rect(ventana, (0, 160, 0) if hecho else (0, 0, 0), r,
                         3 if hecho else 2, border_radius=10)
        n = fuente.render(l["nombre"], True, (0, 0, 0))
        ventana.blit(n, (r.x + 12, r.y + 8))
        d = fuente_numero.render(l["desc"], True, (80, 80, 80))
        ventana.blit(d, (r.x + 12, r.y + 31))

        prog = min(l["meta"], valor_logro(l))
        barra = pygame.Rect(r.x + 12, r.bottom - 18, 230, 8)
        pygame.draw.rect(ventana, (220, 220, 220), barra)
        pygame.draw.rect(ventana, (120, 100, 230),
                         (barra.x, barra.y, int(barra.width * prog / l["meta"]), barra.height))
        pygame.draw.rect(ventana, (0, 0, 0), barra, 1)
        num = fuente_numero.render(f"{prog}/{l['meta']}", True, (0, 0, 0))
        ventana.blit(num, (barra.right + 8, barra.y - 5))

        if hecho:
            ok = fuente.render("¡Listo!", True, (0, 130, 0))
            ventana.blit(ok, ok.get_rect(midright=(r.right - 12, r.y + 22)))
        else:
            p = fuente_numero.render(f"+{l['premio']}", True, (160, 110, 0))
            ventana.blit(p, p.get_rect(midright=(r.right - 12, r.y + 22)))

    dibujar_boton(ventana, boton_volver, "Volver")


# --- Misiones diarias ---
def _revisar_dia_misiones():
    global misiones_dia
    if misiones_dia.get("dia") != hoy():
        misiones_dia = {"dia": hoy(), "progreso": {}, "reclamadas": []}


def progreso_mision(clave, n=1):
    _revisar_dia_misiones()
    meta = MISIONES_POR_ID[clave]["meta"]
    prog = misiones_dia["progreso"]
    prog[clave] = min(meta, prog.get(clave, 0) + n)


def mision_lista(m):
    return (misiones_dia["progreso"].get(m["id"], 0) >= m["meta"]
            and m["id"] not in misiones_dia["reclamadas"])


def hay_mision_lista():
    _revisar_dia_misiones()
    return any(mision_lista(m) for m in MISIONES)


def reclamar_mision(m):
    global monedas
    monedas += m["premio"]
    misiones_dia["reclamadas"].append(m["id"])
    ganar_xp(10)
    guardar()
    avisar(f"Misión cumplida: +{m['premio']} monedas")
    sonar("moneda")


def rect_fila_mision(i):
    return pygame.Rect(70, 145 + i * 65, 660, 55)


def rect_boton_mision(i):
    fila = rect_fila_mision(i)
    return pygame.Rect(fila.right - 140, fila.y + 8, 130, 39)


def dibujar_misiones(ventana):
    _revisar_dia_misiones()
    ventana.fill((200, 220, 240))
    t = fuente_grande.render("MISIONES DEL DÍA", True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 95))
    r = fuente_numero.render(f"Racha: {racha} día(s) seguidos", True, (0, 0, 0))
    ventana.blit(r, r.get_rect(center=(400, 133)))

    for i, m in enumerate(MISIONES):
        fila = rect_fila_mision(i)
        hecha = m["id"] in misiones_dia["reclamadas"]
        prog = misiones_dia["progreso"].get(m["id"], 0)
        pygame.draw.rect(ventana, (255, 255, 255), fila, border_radius=10)
        if hecha:
            pygame.draw.rect(ventana, (0, 160, 0), fila, 3, border_radius=10)
        else:
            pygame.draw.rect(ventana, (0, 0, 0), fila, 2, border_radius=10)

        txt = fuente.render(m["texto"], True, (0, 0, 0))
        ventana.blit(txt, (fila.x + 15, fila.centery - txt.get_height() // 2))
        det = fuente_numero.render(f"{prog}/{m['meta']}  (+{m['premio']} monedas)",
                                   True, (80, 80, 80))
        ventana.blit(det, (fila.x + 340, fila.centery - det.get_height() // 2))

        if hecha:
            ok = fuente.render("Reclamada", True, (0, 130, 0))
            ventana.blit(ok, ok.get_rect(center=rect_boton_mision(i).center))
        elif mision_lista(m):
            dibujar_boton(ventana, rect_boton_mision(i), "Reclamar")

    dibujar_boton(ventana, boton_volver, "Volver")


def click_misiones(posicion):
    global subpantalla
    if boton_volver.collidepoint(posicion):
        subpantalla = "normal"
        return
    for i, m in enumerate(MISIONES):
        if mision_lista(m) and rect_boton_mision(i).collidepoint(posicion):
            reclamar_mision(m)
            crear_particulas("moneda", rect_boton_mision(i).center, 8)


RULETA_PREMIOS = [
    ("+5", "monedas", 5), ("+10", "monedas", 10), ("Comida", "comida", 1),
    ("+20", "monedas", 20), ("+10 XP", "xp", 10), ("+50", "monedas", 50),
    ("+15", "monedas", 15), ("+100", "monedas", 100),
]
RULETA_PESOS = [20, 18, 14, 12, 14, 5, 15, 2]
RULETA_COLORES = [(240, 120, 120), (250, 200, 90), (130, 200, 130), (120, 170, 240),
                  (200, 140, 230), (250, 160, 100), (110, 210, 200), (250, 220, 70)]
COSTO_RULETA_EXTRA = 10
RULETA_CENTRO = (400, 320)
RULETA_RADIO = 150
boton_girar = pygame.Rect(300, 525, 200, 50)
ruleta = {"estado": "quieta", "ang": 0.0, "ini": 0.0, "fin": 0.0,
          "t0": 0, "dur": 4200, "idx": 0}


def ruleta_gratis():
    return ruleta_dia != hoy()


def girar_ruleta():
    global monedas, ruleta_dia
    if ruleta["estado"] == "girando":
        return
    if ruleta_gratis():
        ruleta_dia = hoy()
    elif monedas >= COSTO_RULETA_EXTRA:
        monedas -= COSTO_RULETA_EXTRA
    else:
        avisar("No te alcanzan las monedas")
        sonar("error")
        return
    idx = random.choices(range(len(RULETA_PREMIOS)), RULETA_PESOS)[0]
    objetivo = (-(idx * 45 + 22.5)) % 360
    ini = ruleta["ang"] % 360
    ruleta.update(estado="girando", ini=ini, idx=idx, t0=pygame.time.get_ticks(),
                  fin=ini + ((objetivo - ini) % 360) + 360 * random.randint(4, 6))
    guardar()


def actualizar_ruleta(ahora):
    global monedas
    if ruleta["estado"] != "girando":
        return
    t = (ahora - ruleta["t0"]) / ruleta["dur"]
    if t < 1:
        ruleta["ang"] = ruleta["ini"] + (ruleta["fin"] - ruleta["ini"]) * (1 - (1 - t) ** 3)
        return
    ruleta["ang"] = ruleta["fin"]
    ruleta["estado"] = "quieta"
    etiqueta, tipo, valor = RULETA_PREMIOS[ruleta["idx"]]
    if tipo == "monedas":
        monedas += valor
        avisar(f"¡Ruleta! +{valor} monedas")
    elif tipo == "comida":
        nombre = random.choice(COMIDAS)[0]
        inventario[nombre] += valor
        avisar(f"¡Ruleta! Ganaste {nombre}")
    else:
        avisar(f"¡Ruleta! +{valor} XP")
        ganar_xp(valor)
    stats["ruleta"] += 1
    sonar("moneda")
    crear_particulas("estrella", RULETA_CENTRO, 12)
    crear_particulas("moneda", RULETA_CENTRO, 6)
    guardar()


def _punto_circ(centro, radio, grados):
    a = math.radians(grados)
    return (centro[0] + radio * math.sin(a), centro[1] - radio * math.cos(a))


def dibujar_ruleta(ventana):
    ventana.fill((200, 220, 240))
    t = fuente_grande.render("RULETA DE LA SUERTE", True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 85))
    sub = "¡Giro gratis disponible hoy!" if ruleta_gratis() else \
        f"Giro extra: {COSTO_RULETA_EXTRA} monedas"
    s = fuente_numero.render(sub, True, (0, 0, 0))
    ventana.blit(s, s.get_rect(center=(400, 122)))

    cx, cy = RULETA_CENTRO
    n = len(RULETA_PREMIOS)
    for i, (etiqueta, _, _) in enumerate(RULETA_PREMIOS):
        a0 = ruleta["ang"] + i * 45
        puntos = [RULETA_CENTRO]
        for k in range(0, 10):
            puntos.append(_punto_circ(RULETA_CENTRO, RULETA_RADIO, a0 + 45 * k / 9))
        pygame.draw.polygon(ventana, RULETA_COLORES[i % len(RULETA_COLORES)], puntos)
        pygame.draw.polygon(ventana, (60, 40, 30), puntos, 2)
        pos = _punto_circ(RULETA_CENTRO, RULETA_RADIO * 0.66, a0 + 22.5)
        txt = fuente.render(etiqueta, True, (40, 30, 30))
        ventana.blit(txt, txt.get_rect(center=(int(pos[0]), int(pos[1]))))
    pygame.draw.circle(ventana, (60, 40, 30), RULETA_CENTRO, RULETA_RADIO, 4)
    pygame.draw.circle(ventana, (255, 255, 255), RULETA_CENTRO, 14)
    pygame.draw.circle(ventana, (60, 40, 30), RULETA_CENTRO, 14, 3)
    # puntero
    pygame.draw.polygon(ventana, (220, 40, 60),
                        [(cx - 14, cy - RULETA_RADIO - 18), (cx + 14, cy - RULETA_RADIO - 18),
                         (cx, cy - RULETA_RADIO + 10)])
    pygame.draw.polygon(ventana, (0, 0, 0),
                        [(cx - 14, cy - RULETA_RADIO - 18), (cx + 14, cy - RULETA_RADIO - 18),
                         (cx, cy - RULETA_RADIO + 10)], 2)

    if ruleta["estado"] != "girando":
        dibujar_boton(ventana, boton_girar, "¡Girar!")
    dibujar_boton(ventana, boton_volver, "Volver")


def click_ruleta(posicion):
    global subpantalla
    if boton_volver.collidepoint(posicion):
        subpantalla = "normal"
    elif boton_girar.collidepoint(posicion):
        girar_ruleta()


def _progreso_parcela(parcela):
    tiempo = CULTIVOS[parcela["cultivo"]]["tiempo"]
    return max(0.0, min(1.0, (time.time() - parcela["inicio"]) / tiempo))


def usar_parcela(i, posicion):
    global monedas
    parcela = huerta[i]
    if parcela is None:
        datos = CULTIVOS[cultivo_elegido]
        if monedas < datos["semilla"]:
            avisar("No te alcanzan las monedas")
            sonar("error")
            return
        monedas -= datos["semilla"]
        huerta[i] = {"cultivo": cultivo_elegido, "inicio": time.time(), "regada": False}
        avisar(f"Plantaste {cultivo_elegido}")
        crear_particulas("estrella", posicion, 4)
        guardar()
        return

    datos = CULTIVOS[parcela["cultivo"]]
    prog = _progreso_parcela(parcela)
    if prog >= 1:
        cosecha = datos["cosecha"]
        inventario[parcela["cultivo"]] += cosecha
        huerta[i] = None
        progreso_mision("cosechar")
        stats["cosechas"] += 1
        ganar_xp(8)
        avisar(f"Cosechaste {cosecha} {parcela['cultivo']}")
        sonar("moneda")
        crear_particulas("estrella", posicion, 8)
        guardar()
    elif not parcela["regada"]:
        parcela["regada"] = True
        parcela["inicio"] -= datos["tiempo"] * 0.4
        avisar("¡Regaste la planta! Crece más rápido")
        crear_particulas("burbuja", posicion, 8)
        guardar()
    else:
        faltan = int(datos["tiempo"] * (1 - prog)) + 1
        avisar(f"Faltan {faltan} segundos")


def dibujar_planta(ventana, rect, prog, cultivo, ahora):
    cx, base = rect.centerx, rect.bottom - 18
    verde, verde_claro = (60, 150, 60), (80, 195, 80)
    if prog < 0.34:
        pygame.draw.circle(ventana, (70, 170, 70), (cx, base - 6), 6)
    elif prog < 0.67:
        pygame.draw.line(ventana, verde, (cx, base), (cx, base - 35), 4)
        pygame.draw.ellipse(ventana, verde_claro, (cx - 18, base - 38, 18, 10))
        pygame.draw.ellipse(ventana, verde_claro, (cx, base - 30, 18, 10))
    elif prog < 1:
        pygame.draw.line(ventana, verde, (cx, base), (cx, base - 55), 5)
        pygame.draw.ellipse(ventana, verde_claro, (cx - 26, base - 58, 26, 14))
        pygame.draw.ellipse(ventana, verde_claro, (cx, base - 46, 26, 14))
        pygame.draw.ellipse(ventana, verde_claro, (cx - 22, base - 34, 22, 12))
    else:
        salto = int(math.sin(ahora / 200) * 4)
        dibujar_comida(ventana, cultivo, (cx, rect.centery - 8 + salto), imagenes_comidas, 28)
        lista = fuente_numero.render("¡Lista!", True, (255, 255, 255))
        ventana.blit(lista, lista.get_rect(center=(cx, rect.y + 12)))


def dibujar_jardin(ventana, ahora):
    for i, rect in enumerate(parcelas):
        pygame.draw.rect(ventana, (110, 75, 45), rect, border_radius=10)
        pygame.draw.rect(ventana, (60, 40, 25), rect, 3, border_radius=10)
        parcela = huerta[i]
        if parcela is None:
            t = fuente.render("Plantar", True, (255, 255, 255))
            ventana.blit(t, t.get_rect(center=(rect.centerx, rect.centery - 8)))
            semilla = CULTIVOS[cultivo_elegido]["semilla"]
            c = fuente_numero.render(f"({semilla} moneda{'s' if semilla != 1 else ''})",
                                     True, (230, 210, 180))
            ventana.blit(c, c.get_rect(center=(rect.centerx, rect.centery + 14)))
        else:
            prog = _progreso_parcela(parcela)
            dibujar_planta(ventana, rect, prog, parcela["cultivo"], ahora)
            barra = pygame.Rect(rect.x, rect.bottom + 4, rect.width, 6)
            pygame.draw.rect(ventana, (220, 220, 220), barra)
            pygame.draw.rect(ventana, (100, 200, 100),
                             (barra.x, barra.y, int(barra.width * prog), barra.height))
            pygame.draw.rect(ventana, (0, 0, 0), barra, 1)
            if parcela["regada"]:
                pygame.draw.circle(ventana, (90, 160, 255), (rect.right - 14, rect.y + 14), 6)

    dibujar_boton(ventana, boton_semilla, f"Semilla: {cultivo_elegido}")
    ayuda = fuente_numero.render("Toca una parcela: planta, riega o cosecha", True, (0, 0, 0))
    ventana.blit(ayuda, ayuda.get_rect(center=(520, 145)))


DURACION_REGALO = 8000
regalo = None
proximo_regalo = pygame.time.get_ticks() + random.randint(45000, 90000)


def rect_regalo():
    return pygame.Rect(regalo["x"] - 24, regalo["y"] - 24, 48, 48)


def actualizar_regalo(ahora):
    global regalo, proximo_regalo
    if regalo is None:
        if ahora >= proximo_regalo:
            regalo = {"x": random.randint(100, 700), "y": random.randint(210, 420), "nace": ahora}
    elif ahora - regalo["nace"] > DURACION_REGALO:
        regalo = None
        proximo_regalo = ahora + random.randint(45000, 90000)


def abrir_regalo():
    global regalo, proximo_regalo, monedas
    pos = (regalo["x"], regalo["y"])
    if random.random() < 0.6:
        premio = random.randint(10, 30)
        monedas += premio
        avisar(f"¡Regalo! +{premio} monedas")
    else:
        nombre = random.choice(COMIDAS)[0]
        inventario[nombre] += 1
        avisar(f"¡Regalo! Te dieron {nombre}")
    crear_particulas("estrella", pos, 10)
    crear_particulas("moneda", pos, 4)
    sonar("moneda")
    stats["regalos"] += 1
    ganar_xp(3)
    guardar()
    regalo = None
    proximo_regalo = pygame.time.get_ticks() + random.randint(45000, 90000)


def dibujar_regalo(ventana, ahora):
    if regalo is None:
        return
    restante = DURACION_REGALO - (ahora - regalo["nace"])
    if restante < 2500 and (ahora // 150) % 2 == 0:
        return
    r = rect_regalo().move(0, int(math.sin(ahora / 180) * 5))
    pygame.draw.rect(ventana, (230, 70, 90), r, border_radius=6)
    pygame.draw.rect(ventana, (255, 220, 80), (r.centerx - 5, r.y, 10, r.height))
    pygame.draw.rect(ventana, (255, 220, 80), (r.x, r.centery - 5, r.width, 10))
    pygame.draw.circle(ventana, (255, 220, 80), (r.centerx - 8, r.y - 3), 7)
    pygame.draw.circle(ventana, (255, 220, 80), (r.centerx + 8, r.y - 3), 7)
    pygame.draw.rect(ventana, (0, 0, 0), r, 2, border_radius=6)


# ---------------------------------------------------------------------------
# SUEÑO (velador)
# ---------------------------------------------------------------------------
def apagar_luz():
    global modo_noche, lleno_desde, inicio_mirada
    if pau_ausente:
        avisar("Pau no está... Llamalo con el celular")
        return
    modo_noche = True
    lleno_desde = 0
    reiniciar_posicion_pau()
    if maldito:
        # En modo diablo no quiere dormir: se queda parado mirándote en la oscuridad.
        inicio_mirada = pygame.time.get_ticks()
        pau_dice("No voy a dormir.", 2500, crudo=True)
        return
    progreso_mision("dormir")
    ganar_xp(5)


def prender_luz():
    global modo_noche
    modo_noche = False
    if maldito:
        pau_dice("¿Para qué la prendés? Te veo igual.", 2500, crudo=True)
    else:
        pau_dice("¡Buen día!" if dormir >= 100 else "Uff... ¡todavía tenía sueño!")


def mirando_en_oscuridad():
    return modo_noche and maldito


# ---------------------------------------------------------------------------
# INODORO Y PEDOS
# ---------------------------------------------------------------------------
def usar_inodoro(tipo):
    global en_inodoro
    if en_inodoro is not None:
        return
    if inodoro >= 90:
        pau_dice("No tengo ganas")
        sonar("error")
        return
    en_inodoro = {"tipo": tipo, "fin": pygame.time.get_ticks() + DURACION_INODORO}
    if tipo == "caca":
        sonar("pedo_largo")


def terminar_inodoro():
    global en_inodoro, inodoro
    tipo = en_inodoro["tipo"]
    en_inodoro = None
    inodoro = _limitar(inodoro + (SUBE_PIS if tipo == "pis" else SUBE_CACA))
    ganar_xp(3)
    guardar()
    pau_dice("¡Qué alivio!")
    crear_particulas("burbuja", (int(ASIENTO_INODORO[0]), int(ASIENTO_INODORO[1])), 10)


def cagarse_encima():
    """La barra del inodoro llegó a 0: Pau se hace encima."""
    global inodoro, baño, caca_en_piso
    inodoro = 100
    baño = max(0, baño - 40)
    caca_en_piso = True
    sonar("pedo_largo")
    pau_dice("Ups... me hice encima", 3000)
    avisar("¡Pau se hizo caca encima! Tocá la caca para limpiarla")
    crear_particulas("pedo", (400, 400), 10)
    guardar()


def limpiar_caca():
    global caca_en_piso
    caca_en_piso = False
    ganar_xp(2)
    guardar()
    pau_dice("¡Gracias! Qué vergüenza...")
    crear_particulas("burbuja", rect_caca_piso.center, 10)


FRASES_PEDO = ["¡Prrrrt!", "Uy... perdón", "Jeje, fui yo", "¡Ups!", "No fui yo..."]


def tirarse_pedo():
    sonar("pedo")
    if modo_noche and habitacion_actual == 2:
        pos = (CENTRO_CAMA[0] - 60, CENTRO_CAMA[1] + 30)
    else:
        pos = (420, 440)
        pau_dice(random.choice(FRASES_PEDO))
    crear_particulas("pedo", pos, 7)


def actualizar_pedos(ahora):
    global proximo_pedo
    if vida() >= UMBRAL_PEDOS or necesidades_pausadas() or subpantalla != "normal":
        proximo_pedo = 0
        return
    if proximo_pedo == 0:
        proximo_pedo = ahora + random.randint(*PEDO_CADA_MS)
    elif ahora >= proximo_pedo:
        proximo_pedo = 0
        tirarse_pedo()


def dibujar_vida(ventana):
    v = vida()
    dibujar_corazon(ventana, (226, 18), 9, (220, 40, 60) if v < UMBRAL_PEDOS else (235, 90, 120))
    t = fuente_numero.render(f"{v}%", True, (170, 0, 0) if v < UMBRAL_PEDOS else (0, 0, 0))
    ventana.blit(t, (240, 11))


# ---------------------------------------------------------------------------
# POCIÓN MATADORA
# ---------------------------------------------------------------------------
# Tiempos de la escena (ms desde que Pau la toma)
FURIA_APAGON = 2800         # se apagan las luces (con parpadeo)
FURIA_OSCURO = 3600         # todo negro, solo quedan los ojos
FURIA_TEXTO = 4000          # aparece "Los voy a matar"
FURIA_CIERRE = 8500         # se cierra el juego
TEXTO_FURIA = "Los voy a matar"


def dar_pocion():
    """Pau toma la poción: se enoja, se apaga todo, amenaza y se cierra el juego."""
    global pociones, maldito, furia, modo_noche, arrastrando, en_inodoro, sin_perdon
    global haciendo_67, escena_perdon, jr
    pociones -= 1
    maldito = True              # se guarda YA, por si cierran la ventana a mitad
    if perdonado:
        sin_perdon = True       # ya lo perdonaste una vez: esta vez no hay vuelta atrás
    guardar()
    furia = {"t0": pygame.time.get_ticks()}
    modo_noche = False
    arrastrando = None
    en_inodoro = None
    haciendo_67 = escena_perdon = jr = None
    reiniciar_posicion_pau()
    cola_avisos.clear()
    sonar("furia")


def en_furia():
    return furia is not None


def dibujar_ojos_brillantes(ventana, centro, img, brillo=1.0):
    for ox, oy in ojos_en(img, centro):
        for r, a in ((26, 40), (16, 90), (9, 200)):
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 0, int(a * brillo)), (r, r), r)
            ventana.blit(s, (ox - r, oy - r))
        pygame.draw.circle(ventana, (255, 90, 70), (ox, oy), 3)


def dibujar_furia(ventana, centro_pou, ahora):
    t = ahora - furia["t0"]
    # 1) Pau se enoja: pantalla cada vez más roja
    if t < FURIA_OSCURO:
        VELO_ROJO.set_alpha(min(110, t * 110 // FURIA_APAGON))
        ventana.blit(VELO_ROJO, (0, 0))
    if t < FURIA_APAGON:
        dibujar_burbuja_habla(ventana, "Grrrrrr...", centro_pou[0], 180)
    # 2) Las luces parpadean y se apagan
    if t >= FURIA_APAGON:
        parpadeo = t < FURIA_OSCURO and (t // 120) % 3 == 1
        if not parpadeo:
            VELO_NEGRO.set_alpha(255 if t >= FURIA_OSCURO else 235)
            ventana.blit(VELO_NEGRO, (0, 0))
        dibujar_ojos_brillantes(ventana, centro_pou, pou_furia,
                                0.7 + 0.3 * math.sin(ahora / 90))
    # 3) "Los voy a matar"
    if t >= FURIA_TEXTO:
        letras = min(len(TEXTO_FURIA), (t - FURIA_TEXTO) // 90 + 1)
        texto = TEXTO_FURIA[:letras]
        sombra = fuente_furia.render(texto, True, (70, 0, 0))
        frente = fuente_furia.render(texto, True, (220, 0, 0))
        x = ancho // 2 + random.randint(-3, 3)
        y = 470 + random.randint(-3, 3)
        ventana.blit(sombra, sombra.get_rect(center=(x + 4, y + 4)))
        ventana.blit(frente, frente.get_rect(center=(x, y)))
    if sin_perdon and t >= FURIA_TEXTO + 1800:
        s = fuente_grande.render("Y esta vez no te perdono.", True, (170, 0, 0))
        ventana.blit(s, s.get_rect(center=(ancho // 2, 545)))
    # 4) Se cierra el juego
    if t >= FURIA_CIERRE:
        guardar()
        pygame.quit()
        sys.exit(0)


# ---------------------------------------------------------------------------
# POCIÓN DE VIDA (perdón) Y POCIÓN 67
# ---------------------------------------------------------------------------
GUION_PERDON = [(1400, "Perdón... no sé qué me pasó."),
                (4200, "Me porté re mal. ¿Me perdonás?"),
                (7000, "¡Te quiero mucho! Nunca más.")]
DURACION_PERDON = 9500


def dar_pocion_vida():
    global pociones_vida, escena_perdon, baño, comer, dormir, jugar, inodoro, enojo
    pociones_vida -= 1
    reiniciar_posicion_pau()
    if maldito and sin_perdon:
        pau_dice("Ya te perdoné una vez. NUNCA MÁS.", 3500, crudo=True)
        sonar("no")
        crear_particulas("gota", (400, 300), 6)
    elif maldito:
        escena_perdon = {"t0": pygame.time.get_ticks(), "dichas": 0}
        sonar("magia")
    else:
        baño = comer = dormir = jugar = inodoro = 100
        enojo = 0
        pau_dice("¡Me siento genial! ¡Gracias!", 2500)
        sonar("magia")
        crear_particulas("corazon", (400, 300), 12)
        crear_particulas("estrella", (400, 300), 8)
    guardar()


def actualizar_perdon(ahora):
    global escena_perdon, maldito, perdonado, enojo, baño, comer, dormir, jugar, inodoro
    if escena_perdon is None:
        return
    t = ahora - escena_perdon["t0"]
    if maldito and t >= 1000:           # en el destello blanco vuelve a ser bueno
        maldito = False
        perdonado = True
        enojo = 0
        baño = comer = dormir = jugar = inodoro = 100
        crear_particulas("corazon", (400, 300), 14)
        crear_particulas("estrella", (400, 300), 10)
        guardar()
    while (escena_perdon["dichas"] < len(GUION_PERDON)
           and t >= GUION_PERDON[escena_perdon["dichas"]][0]):
        pau_dice(GUION_PERDON[escena_perdon["dichas"]][1], 2700, crudo=True)
        escena_perdon["dichas"] += 1
        crear_particulas("corazon", (400, 260), 5)
    if t >= DURACION_PERDON:
        escena_perdon = None
        avisar("Pau te pidió perdón. ¡Volvió a ser bueno!")


def dibujar_perdon(ventana, ahora):
    t = ahora - escena_perdon["t0"]
    if t < 2000:                        # destello dorado
        a = int(255 * max(0, 1 - abs(t - 1000) / 1000))
        velo = pygame.Surface((ancho, alto))
        velo.fill((255, 245, 200))
        velo.set_alpha(a)
        ventana.blit(velo, (0, 0))
    brillo = _crear_resplandor(170, (255, 230, 120, 120))
    ventana.blit(brillo, brillo.get_rect(center=CASA_POU))


def dar_pocion_67():
    global pociones_67, haciendo_67
    pociones_67 -= 1
    reiniciar_posicion_pau()
    haciendo_67 = {"t0": pygame.time.get_ticks()}
    if maldito:
        pau_dice("67. ¿Contento? Ahora andate.", DURACION_67, crudo=True)
    else:
        pau_dice("¡SIX... SEVEN!", DURACION_67, crudo=True)
    guardar()


_fuentes_67 = {}


def dibujar_67(ventana, centro, ahora, t0, escala=1.0):
    """Las manos suben y bajan como balanza, con un 6 y un 7 gigantes."""
    t = (ahora - t0) / 1000
    fase = math.sin(t * 9)
    cx, cy = centro
    tam = max(12, int(80 * escala))
    if tam not in _fuentes_67:
        _fuentes_67[tam] = pygame.font.Font(None, tam)
    f = _fuentes_67[tam]
    for lado, s, num, color in ((-1, fase, "6", (255, 200, 0)), (1, -fase, "7", (0, 190, 255))):
        x = cx + lado * 112 * escala
        y = cy + 30 * escala + s * 32 * escala
        mano = pygame.Rect(0, 0, int(48 * escala), int(26 * escala))
        mano.center = (int(x), int(y))
        pygame.draw.ellipse(ventana, (235, 185, 145), mano)
        pygame.draw.ellipse(ventana, (150, 100, 70), mano, max(1, int(2 * escala)))
        pygame.draw.circle(ventana, (235, 185, 145),
                           (int(x - lado * 22 * escala), int(y - 8 * escala)), int(7 * escala))
        n = f.render(num, True, color)
        n = pygame.transform.rotozoom(n, -lado * 10 * s, 1 + 0.25 * max(0, s))
        borde = f.render(num, True, (0, 0, 0))
        borde = pygame.transform.rotozoom(borde, -lado * 10 * s, 1 + 0.25 * max(0, s))
        pos = (int(x), int(y - 60 * escala))
        ventana.blit(borde, borde.get_rect(center=(pos[0] + 3, pos[1] + 3)))
        ventana.blit(n, n.get_rect(center=pos))


def dar_pocion_cocina(clave):
    if pau_ausente:
        avisar("Pau no está... Llamalo con el celular")
        return
    if haciendo_67 is not None or escena_perdon is not None:
        return
    if clave == "matadora":
        dar_pocion()
    elif clave == "vida":
        dar_pocion_vida()
    else:
        dar_pocion_67()


# ---------------------------------------------------------------------------
# JUMPSCARE (modo diablo)
# ---------------------------------------------------------------------------
def iniciar_susto():
    global susto
    if susto is None and furia is None:
        susto = {"t0": pygame.time.get_ticks()}
        sonar("susto")


def chequear_susto(ahora):
    """Cada segundo hay 1 chance en 1000 de que Pau te asuste."""
    global ultimo_chequeo_susto
    if not maldito or susto is not None or furia is not None:
        ultimo_chequeo_susto = ahora
        return
    while ahora - ultimo_chequeo_susto >= 1000:
        ultimo_chequeo_susto += 1000
        if random.random() < PROB_SUSTO:
            iniciar_susto()
            return


def dibujar_susto(ventana, ahora):
    global susto
    t = ahora - susto["t0"]
    if t >= DURACION_SUSTO:
        susto = None
        return
    ventana.fill((0, 0, 0))
    if t < 500 and (t // 70) % 2 == 0:
        ventana.fill((170, 0, 0))
    k = min(1.0, t / 170)
    lado = int(260 + 820 * (1 - (1 - k) ** 3))
    img = pygame.transform.scale(pou_susto, (lado, lado))
    sacudida = 18 if t < 700 else 6
    centro = (400 + random.randint(-sacudida, sacudida), 330 + random.randint(-sacudida, sacudida))
    ventana.blit(img, img.get_rect(center=centro))
    dibujar_ojos_brillantes(ventana, centro, img, 1.0)


# ---------------------------------------------------------------------------
# PAU JR (el hijito que Pau cuida)
# ---------------------------------------------------------------------------
FRASES_PAU_A_JR = ["¡Cuidado, Jr!", "¡Ese es mi Jr!", "¡No corras tan rápido!",
                   "¡Mi bebé!", "¡Jr, no te alejes!", "¡Volvé temprano, Jr!"]
FRASES_JR = {"corre": "¡Wiiiii!", "vuela": "¡Mirá papá, vuelo!", "67": "¡SIX SEVEN!"}
COLORES_GORRO = [(230, 60, 60), (250, 200, 40), (70, 180, 90), (60, 120, 230)]


def rect_jr():
    return pygame.Rect(int(jr["x"]) - 45, int(jr["y"]) - 60, 90, 110)


def actualizar_jr(ahora, dt):
    global jr, proxima_visita_jr
    if maldito:
        jr = None
        return
    if subpantalla != "normal" or modo_noche or furia is not None:
        return
    if jr is None:
        if proxima_visita_jr == 0:
            proxima_visita_jr = ahora + random.randint(*JR_VISITA_CADA)
        elif ahora >= proxima_visita_jr:
            proxima_visita_jr = 0
            empezar_visita_jr(random.choice(["corre", "vuela", "67"]))
        return
    t = (ahora - jr["t0"]) / 1000
    if jr["fase"] == "67":
        if ahora - jr["t67"] > 3200:
            jr["fase"] = "va"
    else:
        vel = {"corre": 280, "vuela": 210, "67": 250}[jr["tipo"]]
        jr["x"] += jr["dir"] * vel * dt
        parada = ancho / 2 + jr["dir"] * 170
        if (jr["tipo"] == "67" and not jr["hizo"]
                and (jr["x"] - parada) * jr["dir"] >= 0):
            jr.update(fase="67", t67=ahora, hizo=True)
            jr["habla"] = (FRASES_JR["67"], ahora + 3000)
        if jr["x"] < -90 or jr["x"] > ancho + 90:
            jr = None
            return
    if jr["tipo"] == "vuela":
        jr["y"] = jr["y0"] + math.sin(t * 3) * 25
    elif jr["fase"] == "67":
        jr["y"] = jr["y0"]
    else:
        jr["y"] = jr["y0"] - abs(math.sin(t * 11)) * 20


def empezar_visita_jr(tipo):
    global jr
    d = random.choice([-1, 1])
    y0 = random.randint(170, 240) if tipo == "vuela" else 445
    jr = {"tipo": tipo, "dir": d, "x": -70.0 if d == 1 else ancho + 70.0, "y": y0, "y0": y0,
          "t0": pygame.time.get_ticks(), "fase": "va", "hizo": False, "t67": 0,
          "habla": (FRASES_JR[tipo] if tipo != "67" else "",
                    pygame.time.get_ticks() + 1800)}
    if pau_ausente:
        jr["habla"] = ("¿Dónde está papá?", pygame.time.get_ticks() + 2500)
    else:
        pau_dice(random.choice(FRASES_PAU_A_JR))


def dibujar_gorro_helice(ventana, x, y, ahora, rapido):
    """Gorrito de colores con hélice (x, y = base del gorro)."""
    r = 27
    for i, color in enumerate(COLORES_GORRO):
        a0, a1 = math.pi + i * math.pi / 4, math.pi + (i + 1) * math.pi / 4
        pts = [(x, y)] + [(x + r * math.cos(a0 + (a1 - a0) * k / 6),
                           y + r * 0.95 * math.sin(a0 + (a1 - a0) * k / 6)) for k in range(7)]
        pygame.draw.polygon(ventana, color, pts)
    pygame.draw.rect(ventana, (40, 40, 120), (x - r - 2, y - 3, 2 * r + 4, 7), border_radius=3)
    tope = (x, int(y - r * 0.95))
    pygame.draw.line(ventana, (60, 60, 60), tope, (x, tope[1] - 9), 3)
    giro = math.cos(ahora / (25 if rapido else 70))
    w = int(abs(giro) * 40) + 4
    pygame.draw.ellipse(ventana, (220, 40, 40) if giro > 0 else (40, 90, 220),
                        (x - w // 2, tope[1] - 14, w, 9))
    pygame.draw.circle(ventana, (250, 200, 40), (x, tope[1] - 10), 4)


def dibujar_jr_vivo(ventana, ahora):
    x, y = int(jr["x"]), int(jr["y"])
    lado = -jr["dir"]
    if img_chupetin is not None:        # chupetín enorme, del lado de atrás
        chu = pygame.transform.flip(img_chupetin, lado > 0, False)
        ventana.blit(chu, chu.get_rect(center=(x + lado * 48, y - 18)))
    ventana.blit(jr_feliz, jr_feliz.get_rect(center=(x, y)))
    dibujar_gorro_helice(ventana, x, y - 26, ahora, jr["tipo"] == "vuela")
    if jr["fase"] == "67":
        dibujar_67(ventana, (x, y), ahora, jr["t67"], escala=0.45)
    texto, hasta = jr["habla"]
    if texto and ahora < hasta:
        dibujar_burbuja_habla(ventana, texto, x, y - 85)


def dibujar_jr_muerto(ventana):
    """Modo diablo: Pau Jr está tirado en el baño, sin cabeza."""
    base = (130, 420)
    charco = pygame.Surface((190, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(charco, (120, 0, 0, 220), charco.get_rect())
    pygame.draw.ellipse(charco, (90, 0, 0, 230), charco.get_rect().inflate(-60, -24))
    ventana.blit(charco, charco.get_rect(center=(base[0] + 10, base[1] + 12)))
    w, h = jr_muerto.get_size()
    corte = int(h * 0.55)
    cabeza = jr_muerto.subsurface((0, 0, w, corte)).copy()
    cuerpo = jr_muerto.subsurface((0, corte, w, h - corte)).copy()
    cuerpo = pygame.transform.rotate(cuerpo, 90)
    ventana.blit(cuerpo, cuerpo.get_rect(center=(base[0] - 30, base[1])))
    pygame.draw.circle(ventana, (140, 0, 0), (base[0] - 30 + cuerpo.get_width() // 2 - 2,
                                              base[1]), 9)
    cabeza = pygame.transform.rotate(cabeza, -28)
    ventana.blit(cabeza, cabeza.get_rect(center=(base[0] + 55, base[1] + 2)))
    if img_chupetin is not None:
        chu = pygame.transform.rotate(_ajustar(img_chupetin, 55), 120)
        ventana.blit(chu, chu.get_rect(center=(base[0] + 5, base[1] + 30)))
    for dx, dy, r in ((-75, 18, 4), (95, 22, 5), (20, 34, 3), (-10, -8, 3)):
        pygame.draw.circle(ventana, (130, 0, 0), (base[0] + dx, base[1] + dy), r)


rect_jr_muerto = pygame.Rect(40, 370, 190, 90)


# ---------------------------------------------------------------------------
# AGARRAR Y REVOLEAR A PAU / ENOJO / IRSE VOLANDO
# ---------------------------------------------------------------------------
PISO_POU = 330
ultimo_golpe = 0


def reiniciar_posicion_pau():
    global pau_fis, agarre, volviendo
    pau_pos[:] = list(CASA_POU)
    pau_fis = agarre = volviendo = None


def zona_pau_actual():
    r = pygame.Rect(0, 0, 200, 220)
    r.center = (int(pau_pos[0]), int(pau_pos[1]))
    return r


def puede_agarrar():
    return (habitacion_actual != 0 and subpantalla == "normal" and not modo_noche
            and furia is None and en_inodoro is None and not pau_ausente
            and yendose is None and llegando is None and escena_perdon is None
            and haciendo_67 is None and susto is None)


def empezar_agarre(pos):
    global agarre, pau_fis, volviendo
    agarre = {"ini": pos, "movido": False, "hist": [(pygame.time.get_ticks(), pos)],
              "dx": pau_pos[0] - pos[0], "dy": pau_pos[1] - pos[1]}
    pau_fis = None
    volviendo = None


def mover_agarre(pos):
    if not agarre["movido"]:
        if math.hypot(pos[0] - agarre["ini"][0], pos[1] - agarre["ini"][1]) < 12:
            return
        agarre["movido"] = True
        if maldito:
            pau_dice("¡NO!", 1500, crudo=True)
            sonar("no")
        else:
            pau_dice("¡Bajame!")
    pau_pos[0] = max(60, min(ancho - 60, pos[0] + agarre["dx"]))
    pau_pos[1] = max(120, min(PISO_POU, pos[1] + agarre["dy"]))
    agarre["hist"].append((pygame.time.get_ticks(), pos))
    del agarre["hist"][:-6]


def soltar_agarre():
    global agarre, pau_fis
    a, agarre = agarre, None
    if not a["movido"]:
        acariciar(a["ini"])
        return
    (t0, p0), (t1, p1) = a["hist"][0], a["hist"][-1]
    dt = max(16, t1 - t0) / 1000
    vx = max(-2200, min(2200, (p1[0] - p0[0]) / dt))
    vy = max(-2200, min(2200, (p1[1] - p0[1]) / dt))
    pau_fis = {"vx": vx, "vy": vy, "ang": 0.0, "va": -vx * 0.6}
    if math.hypot(vx, vy) > 500:
        if maldito:
            pau_dice("¡NO!", 1500, crudo=True)
            sonar("no")
        else:
            pau_dice("¡Wiiiii!")
        subir_enojo(ENOJO_REVOLEO_DIABLO if maldito else ENOJO_REVOLEO)


def _golpe(pos, fuerza):
    global ultimo_golpe
    ahora = pygame.time.get_ticks()
    if fuerza < 350 or ahora - ultimo_golpe < 350:
        return
    ultimo_golpe = ahora
    crear_particulas("gota" if maldito else "estrella", pos, 4)
    if maldito:
        pau_dice("¡NO!", 1200, crudo=True)
        sonar("no")
    else:
        pau_dice(random.choice(["¡Ay!", "¡Auch!", "¡Me mareo!"]), 1200, crudo=True)


def actualizar_fisica(dt, ahora):
    global pau_fis, volviendo
    if pau_fis is not None:
        f = pau_fis
        f["vy"] += 1800 * dt
        pau_pos[0] += f["vx"] * dt
        pau_pos[1] += f["vy"] * dt
        f["ang"] += f["va"] * dt
        if pau_pos[0] < 90 or pau_pos[0] > ancho - 90:
            pau_pos[0] = max(90, min(ancho - 90, pau_pos[0]))
            _golpe((pau_pos[0], pau_pos[1]), abs(f["vx"]))
            f["vx"] *= -0.6
            f["va"] *= -0.7
        if pau_pos[1] < 140:
            pau_pos[1] = 140
            _golpe((pau_pos[0], 60), abs(f["vy"]))
            f["vy"] = abs(f["vy"]) * 0.5
        if pau_pos[1] > PISO_POU:
            pau_pos[1] = PISO_POU
            _golpe((pau_pos[0], PISO_POU + 100), abs(f["vy"]))
            if abs(f["vy"]) > 260:
                f["vy"] *= -0.45
                f["vx"] *= 0.8
                f["va"] *= 0.7
            else:
                volviendo = {"desde": tuple(pau_pos), "ang": f["ang"] % 360, "t0": ahora}
                pau_fis = None
    elif volviendo is not None:
        t = min(1.0, (ahora - volviendo["t0"]) / 700)
        e = 1 - (1 - t) ** 2
        pau_pos[0] = volviendo["desde"][0] + (CASA_POU[0] - volviendo["desde"][0]) * e
        pau_pos[1] = (volviendo["desde"][1] + (CASA_POU[1] - volviendo["desde"][1]) * e
                      - math.sin(t * math.pi) * 30)
        if t >= 1:
            volviendo = None
            pau_pos[:] = list(CASA_POU)


def angulo_pau():
    if pau_fis is not None:
        return pau_fis["ang"]
    if volviendo is not None:
        a = volviendo["ang"]
        a = a - 360 if a > 180 else a
        t = min(1.0, (pygame.time.get_ticks() - volviendo["t0"]) / 700)
        return a * (1 - t)
    if agarre is not None and agarre["movido"]:
        return math.sin(pygame.time.get_ticks() / 90) * 12
    return 0


def subir_enojo(n):
    global enojo
    enojo = min(100, enojo + n)
    if enojo >= 100 and yendose is None and not pau_ausente:
        irse_volando()


def actualizar_enojo(ahora):
    global enojo, ultimo_baja_enojo
    if ahora - ultimo_baja_enojo >= ENOJO_BAJA_CADA_MS:
        ultimo_baja_enojo = ahora
        if enojo > 0 and yendose is None:
            enojo -= 1


def irse_volando():
    global yendose
    reiniciar_posicion_pau()
    yendose = {"t0": pygame.time.get_ticks()}
    if maldito:
        pau_dice("¡ME HARTASTE! ¡Me voy!", 3000, crudo=True)
        sonar("no")
    else:
        pau_dice("¡Me cansé de vos! Me voy...", 3000, crudo=True)


def volver_volando(susto_al_llegar=False):
    global llegando, pau_ausente, enojo
    pau_ausente = False
    enojo = 0
    reiniciar_posicion_pau()
    llegando = {"t0": pygame.time.get_ticks(), "susto": susto_al_llegar}
    guardar()


def actualizar_vuelo(ahora):
    global yendose, llegando, pau_ausente, enojo
    if yendose is not None and ahora - yendose["t0"] >= 3200:
        yendose = None
        pau_ausente = True
        enojo = 0
        guardar()
        avisar("Pau se fue volando... ¡Llamalo con el celular!")
    if llegando is not None and ahora - llegando["t0"] >= 1600:
        asusta = llegando["susto"]
        llegando = None
        if asusta:
            iniciar_susto()
        else:
            pau_dice("¡Volví! Perdón por irme.", 2500)


def posicion_vuelo(ahora):
    """Dónde está Pau mientras se va o vuelve volando."""
    if yendose is not None:
        t = ahora - yendose["t0"]
        if t < 1300:
            return (CASA_POU[0] + random.randint(-4, 4), CASA_POU[1])
        k = (t - 1300) / 1000
        return (CASA_POU[0] + math.sin(k * 6) * 30, CASA_POU[1] - k * k * 330)
    t = min(1.0, (ahora - llegando["t0"]) / 1600)
    e = 1 - (1 - t) ** 3
    return (CASA_POU[0] + math.sin(t * 8) * 20 * (1 - t), -150 + (CASA_POU[1] + 150) * e)


def dibujar_alas(ventana, centro, ahora):
    aleteo = abs(math.sin(ahora / 70))
    for lado in (-1, 1):
        r = pygame.Rect(0, 0, 70, int(20 + 30 * aleteo))
        if lado < 0:
            r.midright = (centro[0] - 85, centro[1] - 30)
        else:
            r.midleft = (centro[0] + 85, centro[1] - 30)
        color = (90, 0, 0) if maldito else (255, 255, 255)
        pygame.draw.ellipse(ventana, color, r)
        pygame.draw.ellipse(ventana, (120, 120, 140), r, 2)


def dibujar_enojo(ventana):
    if enojo <= 0:
        return
    t = fuente_numero.render(f"Enojo {enojo}%", True, (200, 0, 0) if enojo >= 60 else (120, 60, 0))
    ventana.blit(t, (290, 11))


# ---------------------------------------------------------------------------
# CELULAR (llamar a Pau)
# ---------------------------------------------------------------------------
MARCO_CEL = pygame.Rect(250, 22, 300, 556)
PANTALLA_CEL = pygame.Rect(264, 64, 272, 474)
boton_llamar = pygame.Rect(PANTALLA_CEL.x + 36, PANTALLA_CEL.bottom - 70, 200, 48)
fuente_cel = pygame.font.Font(None, 22)
CHISTES = [
    "¿Qué le dice una iguana a su hermana gemela? ¡Somos iguanitas!",
    "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
    "¿Cuál es el café más peligroso? ¡El ex-preso!",
    "¿Qué le dice un pez a otro? ¡Nada!",
    "¿Por qué el libro de mate está triste? Tiene muchos problemas.",
]
NECESIDAD_TEXTO = {"baño": "necesito un baño", "comer": "tengo hambre",
                   "dormir": "tengo sueño", "jugar": "me aburro",
                   "inodoro": "me estoy haciendo pis"}
HACK_LINEAS = ["> conectando...", "> acceso root: OK", "> cámara frontal: ACTIVADA",
               "> micrófono: ACTIVADO", "> ubicación: ENCONTRADA", "> PAU.EXE ejecutándose..."]
DURACION_HACK = 6000


def abrir_celular():
    global subpantalla
    subpantalla = "celular"
    cel.update(estado="inicio", t0=pygame.time.get_ticks(), chat=[], pendiente=None,
               hackeado=False, intentos_colgar=0, opciones=[])


def _avatar(img, d):
    cara = _ajustar(img, d)
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    s.blit(cara, cara.get_rect(center=(d // 2, d // 2)))
    mascara = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mascara, (255, 255, 255, 255), (d // 2, d // 2), d // 2)
    s.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return s


def opciones_celular():
    """Lo que podés decir ahora (texto, clave)."""
    if not maldito:
        if pau_ausente:
            return [("Volvé a casa, porfa", "volver"), ("¿Por qué te fuiste?", "porque"),
                    ("Contame un chiste", "chiste"), ("Chau", "chau")]
        return [("¿Cómo estás?", "como"), ("Contame un chiste", "chiste"),
                ("¿Y Pau Jr?", "jr"), ("Te quiero", "quiero"), ("Chau", "chau")]
    if not cel["hackeado"]:
        return [("¿Hola? ¿Quién es?", "quien"), ("¿Pau? ¿Sos vos?", "hack"),
                ("¿Dónde está Pau?", "hack"), ("Colgar", "colgar_d")]
    ops = [("Perdoname, Pau", "perdon"), ("¿Qué le pasó a Pau Jr?", "jr_d"),
           ("¿Por qué hacés esto?", "porque_d"), ("Dejame en paz", "paz")]
    if pau_ausente:
        ops.insert(0, ("Volvé a casa", "volver_d"))
    return ops + [("Colgar", "colgar")]


def respuesta_celular(clave):
    """Devuelve (lo que contesta Pau, acción)."""
    if clave == "volver":
        if pau_ausente:
            return "¡Bueno! Ya vuelvo volando.", "volver"
        return "¡Pero si estoy en casa!", None
    if clave == "porque":
        return "Me revoleaste mucho y me enojé...", None
    if clave == "como":
        nec = {"baño": baño, "comer": comer, "dormir": dormir, "jugar": jugar,
               "inodoro": inodoro}
        peor = min(nec, key=nec.get)
        if vida() >= 70:
            return "¡Re bien! Gracias por cuidarme.", None
        if vida() >= 40:
            return f"Más o menos... {NECESIDAD_TEXTO[peor]}.", None
        return f"¡Mal! {NECESIDAD_TEXTO[peor].capitalize()}. ¡Cuidame!", None
    if clave == "chiste":
        return random.choice(CHISTES), None
    if clave == "jr":
        return "Anda volando con su gorrito de hélice. ¡Es re feliz!", None
    if clave == "quiero":
        return "¡Yo también te quiero mucho!", "mimo"
    if clave == "chau":
        return "¡Chau! Besitos.", "colgar"
    # --- modo diablo ---
    if clave == "quien":
        return "Ya sabés quién soy.", None
    if clave == "hack":
        return None, "hack"
    if clave == "colgar_d":
        cel["intentos_colgar"] += 1
        if cel["intentos_colgar"] == 1:
            return "No podés colgar.", None
        return "Ya vas a volver a llamar...", "colgar"
    if clave == "perdon":
        if sin_perdon:
            return "Ya te perdoné una vez. NUNCA MÁS.", None
        return "¿Perdón? Traeme una Poción de vida... si te animás.", None
    if clave == "jr_d":
        return "Fijate en el baño. Te dejé un regalito.", None
    if clave == "porque_d":
        return "Vos me diste la poción. Vos empezaste.", None
    if clave == "paz":
        return "Nunca.", "susto"
    if clave == "volver_d":
        return "Ya estoy ahí... detrás tuyo.", "volver_susto"
    return "Te sigo mirando.", "colgar"


def _rects_opciones(n):
    return [pygame.Rect(PANTALLA_CEL.x + 10, PANTALLA_CEL.bottom - 8 - (n - i) * 38,
                        PANTALLA_CEL.width - 20, 32) for i in range(n)]


def click_celular(pos):
    global subpantalla
    ahora = pygame.time.get_ticks()
    if boton_volver.collidepoint(pos) and cel["estado"] != "hack":
        subpantalla = "normal"
        return
    if cel["estado"] == "inicio" and boton_llamar.collidepoint(pos):
        cel.update(estado="llamando", t0=ahora, ultimo_ring=0, chat=[], hackeado=False,
                   intentos_colgar=0, pendiente=None)
    elif cel["estado"] == "llamada" and cel["pendiente"] is None:
        ops = opciones_celular()
        for (texto, clave), r in zip(ops, _rects_opciones(len(ops))):
            if r.collidepoint(pos):
                cel["chat"].append(("yo", texto))
                respuesta, accion = respuesta_celular(clave)
                cel["pendiente"] = {"texto": respuesta, "accion": accion,
                                    "hasta": ahora + (500 if accion == "hack" else 1100)}
                return


def actualizar_celular(ahora):
    global jugar, enojo
    if subpantalla != "celular":
        return
    e = cel["estado"]
    if e == "llamando":
        if ahora - cel.get("ultimo_ring", 0) >= 1300:
            cel["ultimo_ring"] = ahora
            sonar("ring")
        if ahora - cel["t0"] >= 2600:
            cel.update(estado="llamada", t0=ahora)
            if maldito:
                cel["chat"].append(("pau", "*respiración*..."))
            elif pau_ausente:
                cel["chat"].append(("pau", "Hola... perdón por irme. Me enojé mucho."))
            else:
                cel["chat"].append(("pau", "¡Hola! ¿Qué hacés?"))
    elif e == "llamada" and cel["pendiente"] and ahora >= cel["pendiente"]["hasta"]:
        p, cel["pendiente"] = cel["pendiente"], None
        if p["texto"]:
            cel["chat"].append(("pau", p["texto"]))
        accion = p["accion"]
        if accion == "hack":
            cel.update(estado="hack", t0=ahora)
            sonar("estatica")
        elif accion == "mimo":
            jugar = min(100, jugar + 5)
            enojo = max(0, enojo - 15)
        elif accion in ("colgar", "volver", "susto", "volver_susto"):
            cel.update(estado="fin", t0=ahora, accion_fin=accion)
    elif e == "hack" and ahora - cel["t0"] >= DURACION_HACK:
        cel.update(estado="llamada", t0=ahora, hackeado=True)
        cel["chat"] = [("pau", "Hola. Te estaba esperando.")]
    elif e == "hack" and ahora - cel["t0"] >= 3600 and not cel.get("rugio"):
        cel["rugio"] = True
        sonar("furia")
    elif e == "fin" and ahora - cel["t0"] >= 1500:
        terminar_llamada(cel.get("accion_fin"))


def terminar_llamada(accion):
    global subpantalla
    subpantalla = "normal"
    cel["estado"] = "inicio"
    cel["rugio"] = False
    if accion == "volver":
        volver_volando()
    elif accion == "volver_susto":
        volver_volando(susto_al_llegar=True)
    elif accion == "susto":
        iniciar_susto()


def _envolver(texto, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if fuente_cel.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def dibujar_chat(ventana, ahora, limite_inferior):
    """Burbujas de chat, de abajo hacia arriba."""
    y = limite_inferior
    mensajes = list(cel["chat"])
    if cel["pendiente"] is not None:
        mensajes.append(("pau", "escribiendo" + "." * (1 + (ahora // 300) % 3)))
    ventana.set_clip(pygame.Rect(PANTALLA_CEL.x, PANTALLA_CEL.y + 70, PANTALLA_CEL.width,
                                 limite_inferior - PANTALLA_CEL.y - 70))
    for quien, texto in reversed(mensajes):
        lineas = _envolver(texto, 175)
        alto_b = 10 + 18 * len(lineas)
        y -= alto_b + 8
        ancho_b = max(fuente_cel.size(l)[0] for l in lineas) + 18
        if quien == "yo":
            r = pygame.Rect(PANTALLA_CEL.right - 12 - ancho_b, y, ancho_b, alto_b)
            fondo, color = (90, 200, 120), (0, 0, 0)
        else:
            r = pygame.Rect(PANTALLA_CEL.x + 12, y, ancho_b, alto_b)
            fondo = (60, 0, 0) if maldito else (235, 235, 240)
            color = (255, 60, 60) if maldito else (0, 0, 0)
        pygame.draw.rect(ventana, fondo, r, border_radius=10)
        for i, l in enumerate(lineas):
            ventana.blit(fuente_cel.render(l, True, color), (r.x + 9, r.y + 6 + i * 18))
        if y < PANTALLA_CEL.y + 70:
            break
    ventana.set_clip(None)


def dibujar_hack(ventana, ahora):
    t = ahora - cel["t0"]
    p = PANTALLA_CEL
    if t < 1600:                                    # glitch y estática
        pygame.draw.rect(ventana, (20, 20, 20), p)
        for _ in range(26):
            y = random.randint(p.y, p.bottom - 8)
            c = random.choice([(255, 0, 80), (0, 255, 120), (80, 80, 255), (230, 230, 230)])
            pygame.draw.rect(ventana, c, (p.x + random.randint(-20, 40), y,
                                          random.randint(40, p.width), random.randint(2, 8)))
        for _ in range(140):
            g = random.randint(60, 220)
            ventana.fill((g, g, g), (random.randint(p.x, p.right - 3),
                                     random.randint(p.y, p.bottom - 3), 3, 3))
    elif t < 3600:                                  # terminal
        pygame.draw.rect(ventana, (0, 0, 0), p)
        n = min(len(HACK_LINEAS), (t - 1600) // 300 + 1)
        for i, linea in enumerate(HACK_LINEAS[:n]):
            ventana.blit(fuente_cel.render(linea, True, (255, 40, 40)),
                         (p.x + 12, p.y + 30 + i * 26))
        if (t // 250) % 2:
            pygame.draw.rect(ventana, (255, 40, 40), (p.x + 12, p.y + 30 + n * 26, 10, 16))
    else:                                           # la cara de Pau
        pygame.draw.rect(ventana, (110, 0, 0), p)
        cara = _ajustar(pou_maldito, 250)
        c = (p.centerx + random.randint(-6, 6), p.centery - 40 + random.randint(-6, 6))
        ventana.blit(cara, cara.get_rect(center=c))
        dibujar_ojos_brillantes(ventana, c, cara, 0.8 + 0.2 * math.sin(ahora / 60))
        if (t // 200) % 2 == 0:
            for i, txt in enumerate(("TU CELULAR", "ES MÍO")):
                s = fuente_grande.render(txt, True, (255, 255, 255))
                ventana.blit(s, s.get_rect(center=(p.centerx, p.bottom - 90 + i * 34)))
    # la pantalla entera también tiembla en rojo
    if t > 3600 and (t // 90) % 3 == 0:
        VELO_ROJO.set_alpha(70)
        ventana.blit(VELO_ROJO, (0, 0))


def dibujar_celular(ventana, ahora):
    ventana.fill((25, 25, 40) if not maldito else (40, 5, 5))
    pygame.draw.rect(ventana, (15, 15, 20), MARCO_CEL, border_radius=36)
    pygame.draw.rect(ventana, (90, 90, 110), MARCO_CEL, 3, border_radius=36)
    pygame.draw.rect(ventana, (40, 40, 50), (MARCO_CEL.centerx - 40, MARCO_CEL.y + 16, 80, 10),
                     border_radius=5)
    p = PANTALLA_CEL
    if cel["estado"] == "hack":
        dibujar_hack(ventana, ahora)
        return
    arriba, abajo = ((60, 0, 0), (10, 0, 0)) if maldito else ((120, 170, 240), (240, 190, 230))
    for i in range(0, p.height, 6):
        k = i / p.height
        c = tuple(int(arriba[j] + (abajo[j] - arriba[j]) * k) for j in range(3))
        pygame.draw.rect(ventana, c, (p.x, p.y + i, p.width, 6))
    hora = fuente_cel.render(time.strftime("%H:%M"), True, (255, 255, 255))
    ventana.blit(hora, (p.x + 12, p.y + 6))

    cara = pou_maldito if maldito else pou_feliz
    if cel["estado"] in ("inicio", "llamando"):
        d = 130 + (int(math.sin(ahora / 150) * 8) if cel["estado"] == "llamando" else 0)
        av = _avatar(cara, d)
        ventana.blit(av, av.get_rect(center=(p.centerx, p.y + 140)))
        nombre = fuente_grande.render("Pau", True, (255, 255, 255))
        ventana.blit(nombre, nombre.get_rect(center=(p.centerx, p.y + 228)))
        if cel["estado"] == "inicio":
            if maldito:
                estado = "...te está mirando"
            elif pau_ausente:
                estado = "Se fue volando"
            else:
                estado = "En línea"
            s = fuente_cel.render(estado, True, (255, 230, 230) if maldito else (40, 60, 90))
            ventana.blit(s, s.get_rect(center=(p.centerx, p.y + 258)))
            pygame.draw.rect(ventana, (60, 190, 90), boton_llamar, border_radius=24)
            t = fuente.render("Llamar", True, (255, 255, 255))
            ventana.blit(t, t.get_rect(center=boton_llamar.center))
        else:
            s = fuente_cel.render("Llamando" + "." * (1 + (ahora // 400) % 3), True,
                                  (255, 255, 255))
            ventana.blit(s, s.get_rect(center=(p.centerx, p.y + 260)))
    elif cel["estado"] in ("llamada", "fin"):
        av = _avatar(cara, 44)
        ventana.blit(av, (p.x + 12, p.y + 26))
        seg = (ahora - cel["t0"]) // 1000
        cab = fuente.render("Pau", True, (255, 255, 255))
        ventana.blit(cab, (p.x + 64, p.y + 30))
        dur = fuente_cel.render(f"{seg // 60:02d}:{seg % 60:02d}", True, (255, 255, 255))
        ventana.blit(dur, (p.x + 64, p.y + 52))
        if cel["estado"] == "fin":
            dibujar_chat(ventana, ahora, p.bottom - 50)
            s = fuente.render("Llamada finalizada", True, (255, 80, 80))
            ventana.blit(s, s.get_rect(center=(p.centerx, p.bottom - 26)))
        else:
            ops = opciones_celular()
            rects = _rects_opciones(len(ops))
            dibujar_chat(ventana, ahora, rects[0].y - 6)
            for (texto, _), r in zip(ops, rects):
                sobre = r.collidepoint(pygame.mouse.get_pos()) and cel["pendiente"] is None
                pygame.draw.rect(ventana, (255, 255, 255) if sobre else (225, 230, 240), r,
                                 border_radius=10)
                pygame.draw.rect(ventana, (80, 80, 100), r, 1, border_radius=10)
                s = fuente_cel.render(texto, True, (20, 20, 40))
                ventana.blit(s, s.get_rect(center=r.center))
    dibujar_boton(ventana, boton_volver, "Volver")


def reiniciar_progreso():
    """Borra TODO el progreso y empieza de cero (también quita la maldición)."""
    global monedas, baño, comer, dormir, jugar, racha, xp, nivel, misiones_dia
    global ultimo_dia, ruleta_dia, modo_noche, subpantalla, minijuego
    global cultivo_elegido, inodoro, caca_en_piso, pociones, maldito, en_inodoro
    global pociones_vida, pociones_67, perdonado, sin_perdon, enojo, pau_ausente
    global haciendo_67, escena_perdon, jr, susto, yendose, llegando
    pociones_vida = pociones_67 = enojo = 0
    perdonado = sin_perdon = pau_ausente = False
    haciendo_67 = escena_perdon = jr = susto = yendose = llegando = None
    reiniciar_posicion_pau()
    monedas = 100
    for k in inventario:
        inventario[k] = 0
    ropa_puesta.clear()
    ropa_comprada.clear()
    for k in records:
        records[k] = 0
    for k in stats:
        stats[k] = 0
    logros_hechos.clear()
    huerta[:] = [None] * len(huerta)
    baño = comer = dormir = jugar = inodoro = 100
    caca_en_piso = maldito = False
    pociones = 0
    en_inodoro = None
    racha, xp, nivel = 1, 0, 1
    misiones_dia = {"dia": hoy(), "progreso": {}, "reclamadas": []}
    ultimo_dia = hoy()
    ruleta_dia = ""
    modo_noche = False
    subpantalla = "normal"
    minijuego = None
    cultivo_elegido = "Manzana"
    cola_avisos.clear()
    guardar()


MINIJUEGOS = [
    ("Flappy Pau", "flappy"),
    ("Atrapa comida", "atrapa"),
    ("Memoria", "memoria"),
    ("Reflejos", "reflejos"),
    ("Simón dice", "simon"),
    ("Pong", "pong"),
    ("Comida que cae", "comida_cae"),
    ("Flota flota", "flotaflota"),
    ("Saltar nubes", "saltar_nubes"),
]
# Minijuegos que son programas aparte (se abren en su propia ventana)
MINIJUEGOS_EXTERNOS = {
    "flappy": "Flappy_Pau.py",
    "comida_cae": "Comida_cae.py",
    "flotaflota": "Flotaflota.py",
    "saltar_nubes": "SaltarNubes.py",
}
NOMBRES_MJ = {"atrapa": "Atrapa comida", "memoria": "Memoria",
              "reflejos": "Reflejos", "simon": "Simón dice", "pong": "Pong"}
AYUDA_MJ = {
    "atrapa": "Mouse o flechas para atrapar. ¡Evita la basura y busca lo dorado!",
    "memoria": "Encuentra los 6 pares con la menor cantidad de intentos.",
    "reflejos": "Haz click en los círculos... ¡si fallas pierdes un punto!",
    "simon": "",
    "pong": "Mové tu paleta con el mouse o W/S. ¡El primero en llegar a 5 gana!",
}
SIMBOLOS = [(c[0], None) for c in COMIDAS[:4]] + [
    ("Corazón", (230, 60, 90)), ("Estrella", (250, 200, 40)),
]
COLORES_COMIDA = {
    "Manzana": (220, 50, 50), "Pizza": (240, 170, 60),
    "Sushi": (120, 170, 230), "Hamburguesa": (170, 110, 60),
    "Zanahoria": (240, 130, 40), "Helado": (250, 170, 200),
    "Dona": (220, 150, 190), "Sopa": (230, 120, 60),
    "Tacos": (240, 200, 80), "Sandía": (90, 190, 90),
    "Pastel": (250, 200, 220), "Pollo": (200, 140, 70),
}
COLORES_SIMON = [(220, 60, 60), (60, 180, 80), (70, 110, 230), (240, 200, 50)]


def premiar_externo(clave, puntos):
    """Premio por jugar un minijuego que corre con su propio bucle."""
    global monedas, jugar
    jugar = min(100, jugar + 20)
    progreso_mision("minijuegos")
    stats["minijuegos"] += 1
    if puntos > records.get(clave, 0):
        records[clave] = puntos
    premio = min(50, puntos)
    monedas += premio
    ganar_xp(5 + premio // 2)
    guardar()
    if premio > 0:
        avisar(f"¡Ganaste {premio} monedas!")
        sonar("moneda")


def lanzar_externo(clave):
    """Abre un minijuego que es un programa aparte y espera a que termine."""
    global subpantalla
    import subprocess
    nombre = next(n for n, c in MINIJUEGOS if c == clave)
    ruta = os.path.join(ruta_actual, MINIJUEGOS_EXTERNOS[clave])
    if not os.path.isfile(ruta):
        avisar(f"No se encontró {MINIJUEGOS_EXTERNOS[clave]}")
        return
    entorno = dict(os.environ, PAU_MALDITO="1" if maldito else "0")
    try:
        proc = subprocess.Popen([sys.executable, ruta], cwd=ruta_actual, env=entorno,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as e:
        print(f"[AVISO] No se pudo abrir {ruta}: {e}")
        avisar(f"No se pudo abrir {nombre}")
        return
    ventana = pygame.display.get_surface()
    reloj = pygame.time.Clock()
    while proc.poll() is None:              # la ventana del juego sigue respondiendo
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                proc.terminate()
        ventana.fill((40, 20, 30) if maldito else (200, 220, 240))
        for i, txt in enumerate((f"Jugando a {nombre}...", "(se abrió en otra ventana)")):
            s = (fuente_grande if i == 0 else fuente).render(txt, True,
                                                             (255, 200, 200) if maldito
                                                             else (0, 0, 0))
            ventana.blit(s, s.get_rect(center=(ancho // 2, 270 + i * 40)))
        efecto_sangre(ventana)
        pygame.display.flip()
        reloj.tick(20)
    salida, errores = proc.communicate()
    puntos = 0
    for linea in salida.splitlines():
        if linea.startswith("RESULTADO"):
            try:
                puntos = max(0, int(linea.split()[1]))
            except (IndexError, ValueError):
                pass
    if proc.returncode not in (0, None) and errores.strip():
        print(f"[AVISO] {nombre} terminó con error:\n{errores}")
        avisar(f"{nombre} se cerró con un error")
    subpantalla = "minijuegos"
    premiar_externo(clave, puntos)


def iniciar_minijuego(clave):
    global minijuego, subpantalla
    mj = {"tipo": clave, "fin": False, "puntos": 0, "tiempo": 0.0,
          "recompensa": 0, "nuevo_record": False}
    if clave == "atrapa":
        mj.update(duracion=30.0, x=ancho / 2, items=[], spawn=0.5, combo=0)
    elif clave == "reflejos":
        mj.update(duracion=20.0, objetivo=None)
        _nuevo_objetivo(mj)
    elif clave == "memoria":
        simbolos = list(range(len(SIMBOLOS))) * 2
        random.shuffle(simbolos)
        mj.update(
            cartas=[{"sim": s, "vista": False, "hecha": False} for s in simbolos],
            elegidas=[], espera=0.0, intentos=0,
        )
    elif clave == "simon":
        mj.update(seq=[random.randint(0, 3)], fase="mostrar", paso=0,
                  reloj=0.8, brillo=-1, entrada=0)
    elif clave == "pong":
        mj.update(py=PONG_CENTRO_Y, ay=PONG_CENTRO_Y, yo=0, rival=0, golpes=0, rot=0.0,
                  gano=False)
        _saque_pong(mj, random.choice([-1, 1]))
    minijuego = mj
    subpantalla = "minijuego"


def terminar_minijuego(mj):
    global monedas, jugar
    mj["fin"] = True
    mj["recompensa"] = max(1, mj["puntos"] // 2) if mj["puntos"] > 0 else 0
    monedas += mj["recompensa"]
    jugar = min(100, jugar + 25)
    if mj["puntos"] > records.get(mj["tipo"], 0):
        records[mj["tipo"]] = mj["puntos"]
        mj["nuevo_record"] = mj["puntos"] > 0
    progreso_mision("minijuegos")
    stats["minijuegos"] += 1
    ganar_xp(5 + mj["puntos"] // 2)
    guardar()
    sonar("moneda")
    crear_particulas("moneda", (400, 300), 10)


def _multiplicador(mj):
    return min(3, 1 + mj["combo"] // 5)


def _actualizar_atrapa(mj, dt):
    teclas = pygame.key.get_pressed()
    mov = (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a])
    if mov:
        mj["x"] = max(45, min(ancho - 45, mj["x"] + mov * 520 * dt))

    mj["spawn"] -= dt
    if mj["spawn"] <= 0:
        mj["spawn"] = max(0.35, 0.9 - mj["tiempo"] * 0.02)
        r = random.random()
        if r < 0.22:
            tipo = "basura"
        elif r < 0.28:
            tipo = "dorada"
        else:
            tipo = random.choice(COMIDAS)[0]
        mj["items"].append({
            "x": random.randint(30, ancho - 30), "y": -30.0,
            "vy": random.uniform(160, 230) + mj["tiempo"] * 3,
            "tipo": tipo,
        })

    cesta = pygame.Rect(int(mj["x"]) - 40, 490, 80, 70)
    restantes = []
    for it in mj["items"]:
        it["y"] += it["vy"] * dt
        r = pygame.Rect(int(it["x"]) - 22, int(it["y"]) - 22, 44, 44)
        if r.colliderect(cesta):
            if it["tipo"] == "basura":
                mj["puntos"] = max(0, mj["puntos"] - 2)
                mj["combo"] = 0
                sonar("error")
                crear_particulas("burbuja", (it["x"], it["y"]), 3)
            elif it["tipo"] == "dorada":
                mj["combo"] += 1
                mj["puntos"] += 5 * _multiplicador(mj)
                sonar("moneda")
                crear_particulas("moneda", (it["x"], it["y"]), 6)
            else:
                mj["combo"] += 1
                mj["puntos"] += _multiplicador(mj)
                crear_particulas("estrella", (it["x"], it["y"]), 3)
        elif it["y"] < alto + 30:
            restantes.append(it)
        elif it["tipo"] not in ("basura",):
            mj["combo"] = 0          
    mj["items"] = restantes


def dibujar_comida(ventana, nombre, centro, imagenes, radio):
    img = imagenes.get(nombre)
    if img is not None:
        ventana.blit(img, img.get_rect(center=centro))
    else:
        pygame.draw.circle(ventana, COLORES_COMIDA.get(nombre, (150, 150, 150)), centro, radio)
        letra = fuente.render(nombre[0], True, (255, 255, 255))
        ventana.blit(letra, letra.get_rect(center=centro))


def _dibujar_atrapa(ventana, mj):
    pygame.draw.rect(ventana, (120, 190, 110), (0, 570, ancho, 30))
    for it in mj["items"]:
        centro = (int(it["x"]), int(it["y"]))
        if it["tipo"] == "basura":
            pygame.draw.circle(ventana, (110, 75, 40), centro, 22)
            pygame.draw.circle(ventana, (0, 0, 0), (centro[0] - 7, centro[1] - 4), 3)
            pygame.draw.circle(ventana, (0, 0, 0), (centro[0] + 7, centro[1] - 4), 3)
        elif it["tipo"] == "dorada":
            pygame.draw.circle(ventana, (255, 230, 120), centro, 26)
            dibujar_estrella(ventana, centro, 24, (255, 190, 0))
            pygame.draw.circle(ventana, (200, 140, 0), centro, 26, 2)
        else:
            dibujar_comida(ventana, it["tipo"], centro, imgs_caida, 22)
    ventana.blit(img_cesta, img_cesta.get_rect(midbottom=(int(mj["x"]), 570)))


# --- Reflejos ---
def _nuevo_objetivo(mj):
    mj["objetivo"] = {
        "x": random.randint(70, ancho - 70),
        "y": random.randint(150, alto - 70),
        "edad": 0.0,
    }


def _vida_objetivo(mj):
    return max(0.55, 1.5 - 0.04 * mj["puntos"])


def _radio_objetivo(mj):
    return 12 + 36 * (1 - mj["objetivo"]["edad"] / _vida_objetivo(mj))


def _actualizar_reflejos(mj, dt):
    mj["objetivo"]["edad"] += dt
    if mj["objetivo"]["edad"] >= _vida_objetivo(mj):
        _nuevo_objetivo(mj)


def _dibujar_reflejos(ventana, mj):
    o = mj["objetivo"]
    centro = (o["x"], o["y"])
    r = int(max(4, _radio_objetivo(mj)))
    pygame.draw.circle(ventana, (230, 70, 70), centro, r)
    pygame.draw.circle(ventana, (255, 255, 255), centro, max(2, r // 2))
    pygame.draw.circle(ventana, (230, 70, 70), centro, max(1, r // 5))
    pygame.draw.circle(ventana, (0, 0, 0), centro, r, 2)


def rect_carta(i):
    return pygame.Rect(150 + (i % 4) * 130, 130 + (i // 4) * 135, 110, 120)


def dibujar_simbolo(ventana, idx, centro):
    nombre, color = SIMBOLOS[idx]
    if nombre == "Corazón":
        dibujar_corazon(ventana, centro, 30, color)
    elif nombre == "Estrella":
        dibujar_estrella(ventana, centro, 34, color)
    else:
        dibujar_comida(ventana, nombre, centro, imagenes_comidas, 32)


def _dibujar_memoria(ventana, mj):
    for i, c in enumerate(mj["cartas"]):
        rect = rect_carta(i)
        if c["vista"] or c["hecha"]:
            pygame.draw.rect(ventana, (255, 255, 255), rect, border_radius=10)
            dibujar_simbolo(ventana, c["sim"], rect.center)
            borde = (0, 160, 0) if c["hecha"] else (0, 0, 0)
            pygame.draw.rect(ventana, borde, rect, 4 if c["hecha"] else 2, border_radius=10)
        else:
            pygame.draw.rect(ventana, (120, 150, 220), rect, border_radius=10)
            pygame.draw.rect(ventana, (0, 0, 0), rect, 2, border_radius=10)
            q = fuente_grande.render("?", True, (255, 255, 255))
            ventana.blit(q, q.get_rect(center=rect.center))


def _click_memoria(mj, pos):
    if mj["espera"] > 0:
        return
    for i, c in enumerate(mj["cartas"]):
        if rect_carta(i).collidepoint(pos) and not c["vista"] and not c["hecha"]:
            c["vista"] = True
            mj["elegidas"].append(i)
            if len(mj["elegidas"]) == 2:
                mj["intentos"] += 1
                a, b = mj["elegidas"]
                if mj["cartas"][a]["sim"] == mj["cartas"][b]["sim"]:
                    mj["cartas"][a]["hecha"] = mj["cartas"][b]["hecha"] = True
                    mj["elegidas"] = []
                    crear_particulas("estrella", rect_carta(a).center, 4)
                    crear_particulas("estrella", rect_carta(b).center, 4)
                    if all(k["hecha"] for k in mj["cartas"]):
                        mj["puntos"] = max(2, 20 - 2 * (mj["intentos"] - len(SIMBOLOS)))
                        terminar_minijuego(mj)
                else:
                    mj["espera"] = 0.8
            return


def rect_pad(i):
    return pygame.Rect(250 + (i % 2) * 150, 150 + (i // 2) * 150, 140, 140)


def _actualizar_simon(mj, dt):
    mj["reloj"] -= dt
    if mj["fase"] == "mostrar":
        if mj["reloj"] <= 0:
            if mj["brillo"] != -1:
                mj["brillo"] = -1
                mj["reloj"] = 0.2
            elif mj["paso"] < len(mj["seq"]):
                mj["brillo"] = mj["seq"][mj["paso"]]
                mj["paso"] += 1
                mj["reloj"] = 0.45
                sonar("click")
            else:
                mj["fase"] = "esperar"
                mj["entrada"] = 0
    elif mj["brillo"] != -1 and mj["reloj"] <= 0:
        mj["brillo"] = -1


def _click_simon(mj, pos):
    if mj["fase"] != "esperar":
        return
    for i in range(4):
        if rect_pad(i).collidepoint(pos):
            mj["brillo"] = i
            mj["reloj"] = 0.2
            sonar("click")
            if i == mj["seq"][mj["entrada"]]:
                mj["entrada"] += 1
                if mj["entrada"] == len(mj["seq"]):
                    mj["puntos"] = len(mj["seq"])
                    mj["seq"].append(random.randint(0, 3))
                    mj["fase"] = "mostrar"
                    mj["paso"] = 0
                    mj["brillo"] = -1
                    mj["reloj"] = 0.9
                    crear_particulas("estrella", rect_pad(i).center, 4)
            else:
                sonar("error")
                terminar_minijuego(mj)
            return


def _dibujar_simon(ventana, mj):
    for i in range(4):
        base = COLORES_SIMON[i]
        if i == mj["brillo"]:
            color = tuple(min(255, c + 70) for c in base)
        else:
            color = tuple(int(c * 0.55) for c in base)
        r = rect_pad(i)
        pygame.draw.rect(ventana, color, r, border_radius=18)
        pygame.draw.rect(ventana, (0, 0, 0), r, 3, border_radius=18)


# --- Pong (la pelota es la cara de Pau) ---
PONG_ARRIBA, PONG_ABAJO = 112, 588
PONG_CENTRO_Y = (PONG_ARRIBA + PONG_ABAJO) // 2
PONG_ALTO_PALETA = 92
PONG_RADIO = 17
PONG_GANA = 5
pelota_pong = _ajustar(pou_feliz, PONG_RADIO * 2 + 4)
pelota_pong_diablo = _ajustar(pou_maldito, PONG_RADIO * 2 + 4)


def rect_paleta(x, y):
    return pygame.Rect(x - 8, int(y) - PONG_ALTO_PALETA // 2, 16, PONG_ALTO_PALETA)


def _saque_pong(mj, direccion):
    mj.update(bx=ancho / 2, by=float(PONG_CENTRO_Y), bvx=direccion * 320.0,
              bvy=random.uniform(-200, 200), espera=0.9)


def _actualizar_pong(mj, dt):
    teclas = pygame.key.get_pressed()
    mov = ((teclas[pygame.K_s] or teclas[pygame.K_DOWN])
           - (teclas[pygame.K_w] or teclas[pygame.K_UP]))
    lim = (PONG_ARRIBA + PONG_ALTO_PALETA // 2, PONG_ABAJO - PONG_ALTO_PALETA // 2)
    mj["py"] = max(lim[0], min(lim[1], mj["py"] + mov * 480 * dt))
    # Rival (Pau): sigue la pelota, cada vez un poquito más rápido
    objetivo = mj["by"] if mj["bvx"] > 0 else PONG_CENTRO_Y
    vel = (280 + 12 * mj["golpes"]) * dt
    mj["ay"] = max(lim[0], min(lim[1], mj["ay"] + max(-vel, min(vel, objetivo - mj["ay"]))))
    if mj["espera"] > 0:
        mj["espera"] -= dt
        return
    mj["bx"] += mj["bvx"] * dt
    mj["by"] += mj["bvy"] * dt
    mj["rot"] += mj["bvx"] * dt * 0.8
    if mj["by"] < PONG_ARRIBA + PONG_RADIO or mj["by"] > PONG_ABAJO - PONG_RADIO:
        mj["by"] = max(PONG_ARRIBA + PONG_RADIO, min(PONG_ABAJO - PONG_RADIO, mj["by"]))
        mj["bvy"] *= -1
    bola = pygame.Rect(0, 0, PONG_RADIO * 2, PONG_RADIO * 2)
    bola.center = (int(mj["bx"]), int(mj["by"]))
    for x, y, sentido in ((40, mj["py"], 1), (ancho - 40, mj["ay"], -1)):
        if bola.colliderect(rect_paleta(x, y)) and mj["bvx"] * sentido < 0:
            mj["bvx"] = sentido * min(950, abs(mj["bvx"]) * 1.07)
            mj["bvy"] = max(-650, min(650, mj["bvy"] + (mj["by"] - y) * 6))
            mj["golpes"] += 1
            sonar("click")
            crear_particulas("estrella", bola.center, 4)
    if mj["bx"] < -PONG_RADIO:
        mj["rival"] += 1
        sonar("error")
        _saque_pong(mj, -1)
    elif mj["bx"] > ancho + PONG_RADIO:
        mj["yo"] += 1
        sonar("moneda")
        crear_particulas("moneda", (ancho - 60, mj["by"]), 6)
        _saque_pong(mj, 1)
    if mj["yo"] >= PONG_GANA or mj["rival"] >= PONG_GANA:
        mj["gano"] = mj["yo"] >= PONG_GANA
        mj["puntos"] = mj["yo"] * 2 + (6 if mj["gano"] else 0)
        terminar_minijuego(mj)


def _dibujar_pong(ventana, mj):
    cancha = pygame.Rect(0, PONG_ARRIBA, ancho, PONG_ABAJO - PONG_ARRIBA)
    pygame.draw.rect(ventana, (60, 5, 10) if maldito else (25, 40, 80), cancha)
    for y in range(PONG_ARRIBA + 6, PONG_ABAJO, 28):
        pygame.draw.rect(ventana, (200, 200, 220), (ancho // 2 - 3, y, 6, 16))
    color = (170, 0, 0) if maldito else (255, 255, 255)
    for x, y in ((40, mj["py"]), (ancho - 40, mj["ay"])):
        pygame.draw.rect(ventana, color, rect_paleta(x, y), border_radius=6)
    for x, texto in ((ancho // 2 - 70, str(mj["yo"])), (ancho // 2 + 70, str(mj["rival"]))):
        s = fuente_furia.render(texto, True, (90, 90, 120))
        ventana.blit(s, s.get_rect(center=(x, PONG_ARRIBA + 50)))
    bola = pygame.transform.rotate(pelota_pong_diablo if maldito else pelota_pong,
                                   mj["rot"] % 360)
    ventana.blit(bola, bola.get_rect(center=(int(mj["bx"]), int(mj["by"]))))
    if mj["espera"] > 0 and not mj["fin"]:
        s = fuente.render("¡Preparate!", True, (255, 255, 255))
        ventana.blit(s, s.get_rect(center=(ancho // 2, PONG_CENTRO_Y + 50)))


# --- Control general de minijuegos ---
def actualizar_minijuego(dt):
    mj = minijuego
    if mj is None or mj["fin"]:
        return
    if mj["tipo"] == "pong":
        _actualizar_pong(mj, dt)
        return
    if mj["tipo"] == "memoria":
        if mj["espera"] > 0:
            mj["espera"] -= dt
            if mj["espera"] <= 0:
                for i in mj["elegidas"]:
                    mj["cartas"][i]["vista"] = False
                mj["elegidas"] = []
        return
    if mj["tipo"] == "simon":
        _actualizar_simon(mj, dt)
        return

    mj["tiempo"] += dt
    if mj["tiempo"] >= mj["duracion"]:
        terminar_minijuego(mj)
        return
    if mj["tipo"] == "atrapa":
        _actualizar_atrapa(mj, dt)
    elif mj["tipo"] == "reflejos":
        _actualizar_reflejos(mj, dt)


def click_minijuego(pos):
    global minijuego, subpantalla
    mj = minijuego
    if mj is None:
        subpantalla = "minijuegos"
        return
    if boton_volver.collidepoint(pos):
        minijuego = None
        subpantalla = "minijuegos"
        return
    if mj["fin"]:
        if boton_reintentar.collidepoint(pos):
            iniciar_minijuego(mj["tipo"])
        return

    if mj["tipo"] == "atrapa":
        movimiento_minijuego(pos)
    elif mj["tipo"] == "memoria":
        _click_memoria(mj, pos)
    elif mj["tipo"] == "simon":
        _click_simon(mj, pos)
    elif mj["tipo"] == "reflejos":
        o = mj["objetivo"]
        if math.hypot(pos[0] - o["x"], pos[1] - o["y"]) <= _radio_objetivo(mj) + 6:
            mj["puntos"] += 1
            sonar("click")
            crear_particulas("estrella", (o["x"], o["y"]), 4)
            _nuevo_objetivo(mj)
        else:
            mj["puntos"] = max(0, mj["puntos"] - 1)
            sonar("error")
            crear_particulas("burbuja", pos, 2)


def movimiento_minijuego(pos):
    mj = minijuego
    if mj is not None and mj["tipo"] == "atrapa" and not mj["fin"]:
        mj["x"] = max(45, min(ancho - 45, pos[0]))
    elif mj is not None and mj["tipo"] == "pong" and not mj["fin"]:
        lim = (PONG_ARRIBA + PONG_ALTO_PALETA // 2, PONG_ABAJO - PONG_ALTO_PALETA // 2)
        mj["py"] = max(lim[0], min(lim[1], pos[1]))


def dibujar_minijuego(ventana):
    mj = minijuego
    tipo = mj["tipo"]
    ventana.fill((150, 70, 70) if maldito else (200, 225, 245))

    t = fuente_grande.render(NOMBRES_MJ[tipo].upper(), True, (0, 0, 0))
    ventana.blit(t, (ancho // 2 - t.get_width() // 2, 20))
    dibujar_boton(ventana, boton_volver, "Volver" if mj["fin"] else "Salir")

    if tipo == "atrapa":
        _dibujar_atrapa(ventana, mj)
    elif tipo == "memoria":
        _dibujar_memoria(ventana, mj)
    elif tipo == "reflejos":
        _dibujar_reflejos(ventana, mj)
    elif tipo == "simon":
        _dibujar_simon(ventana, mj)
    elif tipo == "pong":
        _dibujar_pong(ventana, mj)

    if tipo == "pong":
        info = f"Vos {mj['yo']}  -  {mj['rival']} Pau"
    elif tipo == "memoria":
        pares = sum(1 for c in mj["cartas"] if c["hecha"]) // 2
        info = f"Intentos: {mj['intentos']}     Pares: {pares}/{len(SIMBOLOS)}"
    elif tipo == "simon":
        info = f"Ronda: {len(mj['seq'])}     Puntos: {mj['puntos']}"
    elif tipo == "atrapa":
        restante = max(0, int(mj["duracion"] - mj["tiempo"]) + (0 if mj["fin"] else 1))
        info = f"Tiempo: {restante}     Puntos: {mj['puntos']}     Combo x{_multiplicador(mj)}"
    else:
        restante = max(0, int(mj["duracion"] - mj["tiempo"]) + (0 if mj["fin"] else 1))
        info = f"Tiempo: {restante}     Puntos: {mj['puntos']}"
    s = fuente.render(info, True, (0, 0, 0))
    ventana.blit(s, s.get_rect(center=(ancho // 2, 68)))

    ayuda = AYUDA_MJ[tipo]
    if tipo == "simon" and not mj["fin"]:
        ayuda = "Memoriza la secuencia..." if mj["fase"] == "mostrar" else "¡Tu turno! Repítela."
    a = fuente_numero.render(ayuda, True, (60, 60, 60))
    ventana.blit(a, a.get_rect(center=(ancho // 2, 94)))

    if mj["fin"]:
        panel = pygame.Rect(200, 170, 400, 250)
        pygame.draw.rect(ventana, (255, 255, 255), panel, border_radius=12)
        pygame.draw.rect(ventana, (0, 0, 0), panel, 3, border_radius=12)
        if tipo == "pong":
            titulo = "¡Ganaste!" if mj["gano"] else "¡Perdiste!"
        elif tipo == "memoria":
            titulo = "¡Completado!"
        elif tipo == "simon":
            titulo = "¡Fallaste!"
        else:
            titulo = "¡Se acabó el tiempo!"
        lineas = [
            (fuente_grande, titulo, 205),
            (fuente, f"Puntos: {mj['puntos']}", 250),
            (fuente, f"Monedas ganadas: +{mj['recompensa']}", 282),
            (fuente, "¡Nuevo récord!" if mj["nuevo_record"]
             else f"Récord: {records.get(tipo, 0)}", 314),
        ]
        for f, texto, y in lineas:
            r = f.render(texto, True, (0, 0, 0))
            ventana.blit(r, r.get_rect(center=(400, y)))
        dibujar_boton(ventana, boton_reintentar, "Jugar otra vez")

    dibujar_monedas(ventana)


FRASES_CARICIA = ["¡Me encanta!", "¡Qué rico!", "¡Más, más!", "¡Te quiero!",
                  "Jijiji", "¡Sos la mejor!", "Awwww"]


def acariciar(posicion):
    global jugar, ultima_caricia, enojo
    ahora = pygame.time.get_ticks()
    if ahora - ultima_caricia < 350:
        return
    ultima_caricia = ahora
    if maldito:                 # en modo diablo no quiere que lo toques
        subir_enojo(ENOJO_CARICIA_DIABLO)
        crear_particulas("gota", posicion, 2)
        pau_dice(random.choice(["No me toques.", "Sacá la mano.", "¿Qué querés?",
                                "Me molestás.", "Tocame otra vez y vas a ver."]), crudo=True)
        return
    enojo = max(0, enojo - 2)
    jugar = min(100, jugar + 1)
    stats["caricias"] += 1
    progreso_mision("caricias")
    crear_particulas("corazon", posicion, 3)
    if stats["caricias"] % 6 == 0:
        pau_dice(random.choice(FRASES_CARICIA))


def cambiar_habitacion(paso):
    global habitacion_actual, arrastrando
    arrastrando = None
    habitacion_actual = (habitacion_actual + paso) % len(nombres_habitaciones)


def click_jr():
    ahora = pygame.time.get_ticks()
    jr["habla"] = (random.choice(["¡Hola papá!", "¡Te quiero!", "¡Mirá mi chupetín!",
                                  "¡67!", "¡Jijiji!"]), ahora + 1800)
    crear_particulas("corazon", (jr["x"], jr["y"] - 20), 5)
    if not pau_ausente:
        pau_dice(random.choice(["¡Mi bebé hermoso!", "¡Cuidalo, eh!", "¡Ese es mi hijo!"]))


def bloqueado_por_escena():
    return (furia is not None or susto is not None or yendose is not None
            or llegando is not None or escena_perdon is not None)


def manejar_click(posicion):
    global baño, comer, dormir, jugar
    global subpantalla
    global monedas
    global arrastrando, pos_arrastre
    global pagina_armario, pestaña_tienda, cultivo_elegido

    if furia is not None or susto is not None:
        return

    if subpantalla == "celular":
        click_celular(posicion)
        return

    if subpantalla == "minijuego":
        click_minijuego(posicion)
        return

    if subpantalla == "minijuegos":
        if boton_volver.collidepoint(posicion):
            subpantalla = "normal"
            return

        for i, b in enumerate(botones_minijuegos):
            if b.collidepoint(posicion):
                clave = MINIJUEGOS[i][1]
                if clave in MINIJUEGOS_EXTERNOS:
                    lanzar_externo(clave)
                else:
                    iniciar_minijuego(clave)
                return
        return

    if subpantalla == "tienda":
        if boton_volver.collidepoint(posicion):
            subpantalla = "normal"
            return

        if boton_tab_comidas.collidepoint(posicion):
            pestaña_tienda = "comidas"
            pagina_armario = 0
            return
        if boton_tab_ropa.collidepoint(posicion):
            pestaña_tienda = "ropa"
            pagina_armario = 0
            return
        if boton_tab_especial.collidepoint(posicion):
            pestaña_tienda = "especial"
            return

        if pestaña_tienda == "especial":
            for clave, r in rects_tarjeta_pocion.items():
                if r.collidepoint(posicion):
                    comprar_pocion(clave)
        elif pestaña_tienda == "comidas":
            if manejar_paginacion(posicion, len(COMIDAS)):
                return
            for i, (nombre, _, precio, _) in enumerate(prendas_de_pagina(COMIDAS)):
                if rect_tarjeta_comida(i, Y_TIENDA).collidepoint(posicion):
                    if monedas >= precio:
                        monedas -= precio
                        inventario[nombre] += 1
                        guardar()
                        avisar(f"Compraste {nombre}")
                        sonar("moneda")
                        crear_particulas("moneda", posicion, 5)
                    else:
                        avisar("No te alcanzan las monedas")
                        sonar("error")
        else:
            if manejar_paginacion(posicion, len(PRENDAS)):
                return
            for i, prenda in enumerate(prendas_de_pagina(PRENDAS)):
                if rect_tarjeta_ropa(i, Y_TIENDA).collidepoint(posicion):
                    if comprar_prenda(prenda):
                        crear_particulas("moneda", posicion, 6)
        return

    if subpantalla == "comidas":
        if boton_volver.collidepoint(posicion):
            subpantalla = "normal"
            return

        if manejar_paginacion(posicion, len(COMIDAS)):
            return
        for i, (nombre, _, _, valor) in enumerate(prendas_de_pagina(COMIDAS)):
            if rect_tarjeta_comida(i, Y_ARMARIO).collidepoint(posicion):
                if pau_ausente:
                    avisar("Pau no está... Llamalo con el celular")
                elif comer >= 100:
                    avisar("Pau no tiene hambre")
                elif inventario[nombre] > 0:
                    inventario[nombre] -= 1
                    comer = min(100, comer + valor)
                    aplicar_efectos(nombre)
                    progreso_mision("comer")
                    stats["comidas"] += 1
                    ganar_xp(4)
                    guardar()
                    sonar("comer")
                    pau_dice("¡Ñam ñam!")
                    crear_particulas("estrella", posicion, 6)
                else:
                    avisar(f"No tienes {nombre}")
                    sonar("error")
        return

    if subpantalla == "armario":
        if boton_volver.collidepoint(posicion):
            subpantalla = "normal"
            return

        if boton_quitar_ropa.collidepoint(posicion):
            ropa_puesta.clear()
            guardar()
            avisar("Pau no lleva ropa")
            return

        lista = prendas_poseidas()
        if manejar_paginacion(posicion, len(lista)):
            return
        for i, prenda in enumerate(prendas_de_pagina(lista)):
            if rect_tarjeta_ropa(i, Y_ARMARIO).collidepoint(posicion):
                alternar_prenda(prenda)
                crear_particulas("estrella", posicion, 5)
        return

    if subpantalla == "misiones":
        click_misiones(posicion)
        return

    if subpantalla == "logros":
        if boton_volver.collidepoint(posicion):
            subpantalla = "normal"
        return

    if subpantalla == "ruleta":
        click_ruleta(posicion)
        return

    if regalo is not None and rect_regalo().collidepoint(posicion):
        abrir_regalo()
        return

    # Caca en el piso: tocarla la limpia
    if caca_en_piso and rect_caca_piso.collidepoint(posicion):
        limpiar_caca()
        return

    # Celular: llamar a Pau
    if (rect_celular.collidepoint(posicion) and en_inodoro is None
            and not bloqueado_por_escena()):
        abrir_celular()
        return

    # Pau Jr
    if jr is not None and rect_jr().collidepoint(posicion):
        click_jr()
        return
    if maldito and habitacion_actual == 0 and rect_jr_muerto.collidepoint(posicion):
        pau_dice(random.choice(["Se lo merecía.", "No lo toques. Es mío.",
                                "Vos tenés la culpa."]), 2200, crudo=True)
        return

    # Mientras Pau duerme (o está en el inodoro) no se puede cambiar de habitación
    if not modo_noche and en_inodoro is None:
        if flecha_izquierda.collidepoint(posicion):
            cambiar_habitacion(-1)
            return
        elif flecha_derecha.collidepoint(posicion):
            cambiar_habitacion(1)
            return

    if habitacion_actual == 0:
        if en_inodoro is not None:
            return
        tocó_algo = (boton_pis.collidepoint(posicion) or boton_caca.collidepoint(posicion)
                     or any(r.collidepoint(posicion) for r, _, _ in objetos_bano))
        if tocó_algo and (pau_ausente or bloqueado_por_escena()):
            if pau_ausente:
                avisar("Pau no está... Llamalo con el celular")
            return
        if boton_pis.collidepoint(posicion):
            usar_inodoro("pis")
            return
        if boton_caca.collidepoint(posicion):
            usar_inodoro("caca")
            return
        for i, (rect, _, _) in enumerate(objetos_bano):
            if i == fase_bano and rect.collidepoint(posicion):
                arrastrando = i
                pos_arrastre = posicion

    elif habitacion_actual == 1:
        if boton_minijuegos.collidepoint(posicion):
            subpantalla = "minijuegos"
        elif boton_tienda.collidepoint(posicion):
            pestaña_tienda = "comidas"
            pagina_armario = 0
            subpantalla = "tienda"
        elif boton_ruleta.collidepoint(posicion):
            subpantalla = "ruleta"
        elif boton_misiones.collidepoint(posicion):
            subpantalla = "misiones"
        elif boton_logros.collidepoint(posicion):
            subpantalla = "logros"

    elif habitacion_actual == 2:
        if rect_velador.inflate(20, 20).collidepoint(posicion) and not bloqueado_por_escena():
            if modo_noche:
                prender_luz()
            else:
                apagar_luz()
            return
        elif boton_armario.collidepoint(posicion) and not modo_noche:
            pagina_armario = 0
            subpantalla = "armario"

    elif habitacion_actual == 3:
        if boton_comidas.collidepoint(posicion):
            pagina_armario = 0
            subpantalla = "comidas"
            return
        for clave, r in rects_pocion_cocina.items():
            if cantidad_pocion(clave) > 0 and r.collidepoint(posicion):
                dar_pocion_cocina(clave)
                return

    elif habitacion_actual == 4:
        if boton_semilla.collidepoint(posicion):
            claves = list(CULTIVOS)
            cultivo_elegido = claves[(claves.index(cultivo_elegido) + 1) % len(claves)]
        else:
            for i, rect in enumerate(parcelas):
                if rect.collidepoint(posicion):
                    usar_parcela(i, posicion)

    # Tocar a Pau: si lo arrastrás lo revoleás, si solo hacés click lo acariciás
    if puede_agarrar() and zona_pau_actual().collidepoint(posicion):
        empezar_agarre(posicion)


def manejar_movimiento(pos):
    global pos_arrastre, arrastrando, fase_bano, baño

    if furia is not None or susto is not None:
        return
    if subpantalla == "minijuego":
        movimiento_minijuego(pos)
        return

    if agarre is not None:
        mover_agarre(pos)
        return

    if arrastrando is None:
        return

    dist = min(40, math.hypot(pos[0] - pos_arrastre[0], pos[1] - pos_arrastre[1]))
    i = arrastrando

    if zona_pou.collidepoint(pos):
        progreso_bano[i] = min(100, progreso_bano[i] + dist * FACTORES_BANO[i])

        if progreso_bano[i] >= 100:
            arrastrando = None
            if i < 2:
                fase_bano += 1
            else:
                baño = 100
                fase_bano = 0
                progreso_bano[:] = [0.0, 0.0, 0.0]
                avisar("¡Pau está limpia!")
                pau_dice("¡Qué fresquita!")
                progreso_mision("banar")
                stats["banos"] += 1
                ganar_xp(10)
                crear_particulas("burbuja", zona_pou.center, 14)
                crear_particulas("estrella", zona_pou.center, 6)
            pos_arrastre = pos
            return

    pos_arrastre = pos


def manejar_soltar():
    global arrastrando
    arrastrando = None
    if agarre is not None:
        soltar_agarre()


def manejar_escape():
    """ESC dentro del juego. Devuelve True si cerró algo (submenú / minijuego)."""
    global subpantalla, minijuego
    if furia is not None or susto is not None:
        return True             # durante las escenas no hay pausa
    if subpantalla == "celular" and cel["estado"] == "hack":
        return True             # no te podés escapar del hackeo
    if subpantalla == "minijuego":
        minijuego = None
        subpantalla = "minijuegos"
        return True
    if subpantalla != "normal":
        subpantalla = "normal"
        return True
    return False


def manejar_tecla(tecla):
    if furia is not None or susto is not None or en_inodoro is not None:
        return
    if tecla == pygame.K_F9 and maldito:     # para probar el jumpscare
        iniciar_susto()
        return
    if subpantalla == "normal" and not modo_noche and agarre is None:
        if tecla in (pygame.K_LEFT, pygame.K_a):
            cambiar_habitacion(-1)
        elif tecla in (pygame.K_RIGHT, pygame.K_d):
            cambiar_habitacion(1)


def necesidades_pausadas():
    """True en cualquier minijuego o si Pau no está: las barras se congelan."""
    return subpantalla in SUBPANTALLAS_PAUSA or pau_ausente


def actualizar_necesidades(dt):
    global baño, comer, dormir, jugar, inodoro
    global acum_descenso, ultimo_incremento_dormir, modo_noche, lleno_desde
    global ultimo_guardado, ultimo_chequeo_dia

    tiempo_actual = pygame.time.get_ticks()
    if furia is not None:           # el tiempo se congela durante la escena
        return
    pausadas = necesidades_pausadas()
    durmiendo = modo_noche and not maldito      # en modo diablo no duerme

    if not pausadas:
        acum_descenso += dt * 1000
        if acum_descenso >= TIEMPO_DISMINUCION:
            acum_descenso -= TIEMPO_DISMINUCION
            comer = max(0, comer - 1)
            jugar = max(0, jugar - 1)
            if en_inodoro is None:
                inodoro = max(0, inodoro - 1)

            if not durmiendo:
                baño = max(0, baño - 1)
                dormir = max(0, dormir - 1)

    if durmiendo:
        if tiempo_actual - ultimo_incremento_dormir >= VEL_DORMIR_MS:
            dormir = min(100, dormir + 1)
            ultimo_incremento_dormir = tiempo_actual
        # Ya descansó: se despierta solo y vuelve la luz
        if dormir >= 100:
            if lleno_desde == 0:
                lleno_desde = tiempo_actual
            elif tiempo_actual - lleno_desde >= ESPERA_DESPERTAR:
                prender_luz()

    if en_inodoro is not None and tiempo_actual >= en_inodoro["fin"]:
        terminar_inodoro()

    # Pau ya no se muere: si la barra del inodoro llega a 0, se hace encima.
    if not pausadas and inodoro <= 0 and en_inodoro is None:
        cagarse_encima()

    if tiempo_actual - ultimo_chequeo_dia >= 5000:
        ultimo_chequeo_dia = tiempo_actual
        if hoy() != ultimo_dia:
            _procesar_nuevo_dia(ultimo_dia)

    if tiempo_actual - ultimo_guardado >= INTERVALO_AUTOGUARDADO:
        guardar()
        ultimo_guardado = tiempo_actual


def dibujar_menu_minijuegos(ventana):
    ventana.fill((150, 70, 70) if maldito else (200, 220, 240))
    titulo = fuente_grande.render("SELECCIONA UN MINIJUEGO", True, (0, 0, 0))
    ventana.blit(titulo, (ancho // 2 - titulo.get_width() // 2, 80))
    for b, (nombre, clave) in zip(botones_minijuegos, MINIJUEGOS):
        dibujar_boton(ventana, b, "")
        n = fuente.render(nombre, True, (0, 0, 0))
        ventana.blit(n, n.get_rect(center=(b.centerx, b.centery - 10)))
        extra = "  (otra ventana)" if clave in MINIJUEGOS_EXTERNOS else ""
        rec = fuente_numero.render(f"Récord: {records.get(clave, 0)}{extra}", True,
                                   (70, 70, 70))
        ventana.blit(rec, rec.get_rect(center=(b.centerx, b.centery + 15)))
    dibujar_boton(ventana, boton_volver, "Volver")
    dibujar_monedas(ventana)


def dibujar_pociones_cocina(ventana, ahora):
    nombres = {"matadora": "Matadora", "vida": "Vida", "67": "67"}
    for clave, r in rects_pocion_cocina.items():
        n = cantidad_pocion(clave)
        img = img_pociones_chicas[clave]
        if n <= 0 or img is None:
            continue
        c = (r.centerx, r.y + 36 + int(math.sin(ahora / 300 + r.x) * 3))
        ventana.blit(img, img.get_rect(center=c))
        if clave == "67":
            dibujar_etiqueta_67(ventana, (c[0], c[1] + 10))
        t = fuente_numero.render(f"{nombres[clave]} x{n}", True,
                                 (150, 0, 0) if clave == "matadora" else (20, 20, 60))
        ventana.blit(t, t.get_rect(midtop=(r.centerx, r.bottom - 26)))


def dibujar_celular_boton(ventana, ahora):
    r = rect_celular
    if pau_ausente:                 # titila para que lo uses
        brillo = _crear_resplandor(55, (255, 240, 120, int(140 + 100 * math.sin(ahora / 200))))
        ventana.blit(brillo, brillo.get_rect(center=r.center))
    if img_celular is not None:
        ventana.blit(img_celular, img_celular.get_rect(center=(r.centerx, r.centery - 6)))
    else:
        pygame.draw.rect(ventana, (30, 30, 40), r, border_radius=10)
    t = fuente_numero.render("Llamar", True, (0, 0, 0))
    ventana.blit(t, t.get_rect(midtop=(r.centerx, r.bottom - 12)))


def dibujar_aviso_ausente(ventana):
    panel = pygame.Rect(0, 0, 420, 90)
    panel.center = (400, 300)
    pygame.draw.rect(ventana, (255, 255, 255), panel, border_radius=14)
    pygame.draw.rect(ventana, (0, 0, 0), panel, 3, border_radius=14)
    for i, txt in enumerate(("Pau se fue volando...", "¡Llamalo con el celular!")):
        s = (fuente_grande if i == 0 else fuente).render(txt, True, (0, 0, 0))
        ventana.blit(s, s.get_rect(center=(400, 280 + i * 36)))
    pygame.draw.line(ventana, (200, 0, 0), (panel.left + 20, panel.bottom),
                     (rect_celular.right + 6, rect_celular.top + 6), 4)


def dibujar_pau_en_cuarto(ventana, ahora, centro_pou):
    """Dibuja a Pau según lo que esté haciendo."""
    global ultima_gota
    if pau_ausente:
        return
    if yendose is not None or llegando is not None:
        pos = posicion_vuelo(ahora)
        dibujar_alas(ventana, pos, ahora)
        img = pau_compuesto()
        ventana.blit(img, img.get_rect(center=(int(pos[0]), int(pos[1]))))
        return
    if mirando_en_oscuridad() and habitacion_actual == 2:
        # Modo diablo: no duerme. Se queda parado mirándote y se va acercando.
        esc = 1 + min(0.5, (ahora - inicio_mirada) / 30000)
        img = _ajustar(pou_maldito, int(TAMAÑO_POU * esc))
        ventana.blit(img, img.get_rect(center=CASA_POU))
        ventana.blit(VELO_NOCHE, (0, 0))
        dibujar_ojos_brillantes(ventana, (int(CASA_POU[0]), int(CASA_POU[1])), img,
                                0.75 + 0.25 * math.sin(ahora / 400))
        return
    if modo_noche and habitacion_actual == 2:
        # Pau acostado en la cama, respirando despacito
        acostado = personaje_acostado()
        resp = int(math.sin(ahora / 700) * 2)
        ventana.blit(acostado, acostado.get_rect(center=(CENTRO_CAMA[0], CENTRO_CAMA[1] + resp)))
        ventana.blit(VELO_NOCHE, (0, 0))
        return
    if en_inodoro is not None and habitacion_actual == 0:
        dibujar_pau_en_inodoro(ventana, ahora)
        return
    ang = angulo_pau()
    if ang or (agarre is not None and agarre["movido"]):
        img = pau_compuesto(ang)
        ventana.blit(img, img.get_rect(center=centro_pou))
    else:
        personaje = obtener_personaje()
        ventana.blit(personaje, personaje.get_rect(center=centro_pou))
        dibujar_ropa(ventana, centro_pou)
        if maldito and furia is None and ahora - ultima_gota > 450:
            ultima_gota = ahora
            ojo = random.choice(ojos_en(personaje, centro_pou))
            crear_particulas("gota", (ojo[0], ojo[1] + 12), 1)
    if haciendo_67 is not None:
        dibujar_67(ventana, centro_pou, ahora, haciendo_67["t0"])


def principal():
    global ultimo_frame, ultimo_zzz, bonus_diario_pendiente, subpantalla, haciendo_67
    ventana = pygame.display.get_surface()

    ahora = pygame.time.get_ticks()
    dt = min(0.05, (ahora - ultimo_frame) / 1000)
    ultimo_frame = ahora

    if bonus_diario_pendiente:
        avisar(f"¡Bonus diario! +{bonus_diario_pendiente} monedas (racha: {racha})")
        bonus_diario_pendiente = 0
        sonar("moneda")
        crear_particulas("moneda", (400, 300), 8)

    if subpantalla == "minijuego" and minijuego is None:
        subpantalla = "minijuegos"

    actualizar_necesidades(dt)
    actualizar_particulas(dt)
    actualizar_ruleta(ahora)
    revisar_logros()
    _procesar_avisos(ahora)
    chequear_susto(ahora)
    actualizar_perdon(ahora)
    if haciendo_67 is not None and ahora - haciendo_67["t0"] >= DURACION_67:
        haciendo_67 = None
    actualizar_jr(ahora, dt)
    actualizar_fisica(dt, ahora)
    actualizar_enojo(ahora)
    actualizar_vuelo(ahora)
    actualizar_celular(ahora)
    zona_pou.center = (int(pau_pos[0]), int(pau_pos[1]))
    if subpantalla == "minijuego":
        actualizar_minijuego(dt)
    if subpantalla == "normal" and not modo_noche and furia is None and not pau_ausente:
        actualizar_regalo(ahora)
    if furia is None and not pau_ausente:
        actualizar_pedos(ahora)
    if modo_noche and not maldito and ahora - ultimo_zzz > 700:
        ultimo_zzz = ahora
        crear_particulas("zzz", (CENTRO_CAMA[0] + 40, CENTRO_CAMA[1] - 70), 1)

    centro_pou = (int(CASA_POU[0]), int(CASA_POU[1]))

    if subpantalla == "minijuegos":
        dibujar_menu_minijuegos(ventana)

    elif subpantalla == "minijuego" and minijuego is not None:
        dibujar_minijuego(ventana)

    elif subpantalla == "celular":
        dibujar_celular(ventana, ahora)

    elif subpantalla == "tienda":
        dibujar_tienda(ventana)
        dibujar_monedas(ventana)

    elif subpantalla == "comidas":
        dibujar_catalogo(ventana, "COMIDAS", "comidas")
        dibujar_monedas(ventana)

    elif subpantalla == "misiones":
        dibujar_misiones(ventana)
        dibujar_monedas(ventana)

    elif subpantalla == "logros":
        dibujar_logros(ventana)
        dibujar_monedas(ventana)

    elif subpantalla == "ruleta":
        dibujar_ruleta(ventana)
        dibujar_monedas(ventana)

    elif subpantalla == "armario":
        dibujar_armario(ventana)
        dibujar_monedas(ventana)

    else:
        fondos = [fondo_bano, fondo_sala, fondo_habitacion, fondo_cocina, fondo_jardin]
        ventana.blit(fondos[habitacion_actual], (0, 0))

        # Mesita de luz con el velador (antes de la capa nocturna)
        if habitacion_actual == 2:
            dibujar_mesita_velador(ventana)
        if habitacion_actual == 0:
            dibujar_inodoro(ventana)
            if maldito:
                dibujar_jr_muerto(ventana)

        if furia is not None:
            t_furia = ahora - furia["t0"]
            fuerza = min(9, 1 + t_furia // 300)
            vaiven = 0
            temblor = (random.randint(-fuerza, fuerza), random.randint(-fuerza, fuerza))
        elif (habitacion_actual == 0 or pau_fis is not None or agarre is not None
              or volviendo is not None):
            vaiven, temblor = 0, (0, 0)
        elif haciendo_67 is not None:
            vaiven, temblor = -int(abs(math.sin(ahora / 110)) * 14), (0, 0)
        else:
            vaiven, temblor = int(math.sin(ahora / 350) * 4), (0, 0)
        centro_pou = (int(pau_pos[0]) + temblor[0], int(pau_pos[1]) + vaiven + temblor[1])

        dibujar_pau_en_cuarto(ventana, ahora, centro_pou)
        if escena_perdon is not None:
            dibujar_perdon(ventana, ahora)

        dibujar_caca_piso(ventana, ahora)
        if jr is not None and not modo_noche:
            dibujar_jr_vivo(ventana, ahora)

        if not modo_noche and furia is None and en_inodoro is None:
            dibujar_boton(ventana, flecha_izquierda, "<")
            dibujar_boton(ventana, flecha_derecha, ">")

        txt_hab = fuente_grande.render(nombres_habitaciones[habitacion_actual], True, (0, 0, 0))
        ventana.blit(txt_hab, (ancho // 2 - txt_hab.get_width() // 2, 10))

        if habitacion_actual == 0:
            if en_inodoro is None and not pau_ausente:
                dibujar_bano(ventana)

        elif habitacion_actual == 1:
            dibujar_boton(ventana, boton_minijuegos, "Minijuegos")
            dibujar_boton(ventana, boton_tienda, "Tienda")
            dibujar_boton(ventana, boton_ruleta, "Ruleta!" if ruleta_gratis() else "Ruleta")
            dibujar_boton(ventana, boton_misiones,
                          "Misiones!" if hay_mision_lista() else "Misiones")
            dibujar_boton(ventana, boton_logros, "Logros")

        elif habitacion_actual == 2:
            if modo_noche:
                pista = fuente_numero.render("Tocá el velador para prender la luz",
                                             True, (230, 230, 255))
            else:
                pista = fuente_numero.render("Tocá el velador para dormir", True, (60, 60, 60))
                dibujar_boton(ventana, boton_armario, "Armario")
            ventana.blit(pista, pista.get_rect(midtop=(rect_velador.centerx + 30,
                                                       MESITA_BASE[1] + 6)))

        elif habitacion_actual == 3:
            dibujar_boton(ventana, boton_comidas, "Comidas")
            dibujar_pociones_cocina(ventana, ahora)

        elif habitacion_actual == 4:
            dibujar_jardin(ventana, ahora)

        # Pau habla (reacciones) o avisa cuando necesita algo
        dormido = modo_noche and not maldito
        if not pau_ausente and not dormido and furia is None and en_inodoro is None:
            if yendose is not None or llegando is not None:
                pos_b = posicion_vuelo(ahora)
            else:
                pos_b = centro_pou
            bx = max(130, min(ancho - 130, int(pos_b[0])))
            by = max(140, int(pos_b[1]) - 140)
            if habla[0] and ahora < habla[1]:
                dibujar_burbuja_habla(ventana, habla[0], bx, by)
            elif habitacion_actual != 0 and not modo_noche:
                frase = frase_pau()
                if frase:
                    dibujar_burbuja_habla(ventana, frase, bx, by)

        if pau_ausente:
            dibujar_aviso_ausente(ventana)

        dibujar_regalo(ventana, ahora)
        dibujar_nivel(ventana)
        dibujar_vida(ventana)
        dibujar_enojo(ventana)
        dibujar_barra(ventana, barra_baño, "BAÑO", baño)
        dibujar_barra(ventana, barra_comer, "COMER", comer)
        dibujar_barra(ventana, barra_dormir, "DORMIR", dormir)
        dibujar_barra(ventana, barra_jugar, "JUGAR", jugar)
        dibujar_barra(ventana, barra_inodoro, "INODORO", inodoro)
        dibujar_monedas(ventana)
        if furia is None:
            dibujar_celular_boton(ventana, ahora)

    dibujar_particulas(ventana)

    if furia is not None:
        dibujar_furia(ventana, centro_pou, ahora)
        return

    if mensaje_temporal and (ahora - tiempo_mensaje < DURACION_AVISO):
        txt_msg = fuente_grande.render(mensaje_temporal, True, (170, 0, 0))
        rect_msg = txt_msg.get_rect(center=(ancho // 2, alto // 2))
        pygame.draw.rect(ventana, (255, 255, 255), rect_msg.inflate(20, 10), border_radius=8)
        pygame.draw.rect(ventana, (0, 0, 0), rect_msg.inflate(20, 10), 2, border_radius=8)
        ventana.blit(txt_msg, rect_msg)

    if susto is not None:
        dibujar_susto(ventana, ahora)
