
# ---------------------------------------------------------------------------
# 1. GUSTOS Y COMIDAS ODIADAS
# ---------------------------------------------------------------------------
GUSTOS_CANT_FAVORITAS = (2, 3)     # (mínimo, máximo) de comidas favoritas
GUSTOS_CANT_ODIADAS = 1            # cuántas comidas odia
NUNCA_ODIADAS = []                 # comidas que nunca pueden salir odiadas, ej: ["Manzana"]

# Comida favorita (además de lo normal que da esa comida)
FAVORITA_BONUS_JUGAR = 15          # felicidad extra
FAVORITA_BONUS_XP = 3              # XP extra
FAVORITA_CORAZONES = 8             # partículas de corazón

# Comida odiada: la escupe
ODIADA_SUBE_COMER = 0              # cuánto llena igual (0 = nada)
ODIADA_PENALIZA_JUGAR = 8          # cuánta felicidad pierde
ODIADA_CIERRA_CATALOGO = True      # vuelve a la cocina para que se vea la reacción
DURACION_ASCO_MS = 2200            # cuánto dura la cara de asco

# Animación de la comida escupida
ESCUPIDA_BOCA = (400, 345)         # desde dónde sale (boca de Pau)
ESCUPIDA_VX = (170, 260)           # velocidad horizontal (px/s, al azar)
ESCUPIDA_VY = (240, 320)           # velocidad hacia arriba (px/s, al azar)
ESCUPIDA_GRAVEDAD = 750            # px/s²
ESCUPIDA_DURACION = 1.3            # segundos

# ---------------------------------------------------------------------------
# 2. CARICIAS POR ZONA
# ---------------------------------------------------------------------------
# Zonas del cuerpo como rectángulos (dx, dy, ancho, alto) RELATIVOS al centro
# de Pau (y negativo = más arriba). Pau mide ~220 px. Se revisan en este
# orden: la primera que contenga el click gana. Apretá F3 en el juego para
# VER las zonas y ajustarlas a tu PNG.
CARICIAS_ZONAS = [
    ("cabeza",   [(-70, -112, 140, 50)]),
    ("cara",     [(-60, -62, 120, 55)]),
    ("costados", [(-108, -25, 45, 95), (63, -25, 45, 95)]),
    ("panza",    [(-63, -7, 126, 82)]),
    ("pies",     [(-85, 75, 170, 37)]),
]

CARICIA_COOLDOWN_MS = 350          # tiempo mínimo entre caricias
CARICIA_REACCION_MS = 900          # cuánto dura la cara/animación de cada zona
CARICIA_PROB_FRASE = 0.35          # prob. de hablar si repite la misma zona

# Si la tocás demasiado seguido se enoja
CARICIA_VENTANA_MS = 3000          # en esta ventana de tiempo...
CARICIA_MAX_EN_VENTANA = 7         # ...más de estas caricias = se molesta
CARICIA_MOLESTA_MS = 2200          # cuánto dura enojada (ignora caricias)

# Reacción de cada zona. "cuerpo" = tocó a Pau pero fuera de las zonas.
#   jugar: felicidad que suma   cara: cara temporal (o None)
#   anim : temblor / saltitos / hundir (o None)   particula: tipo y cantidad
CARICIAS_REACCIONES = {
    "cabeza":   {"jugar": 2, "cara": "contenta", "anim": "hundir",
                 "particula": ("corazon", 3),
                 "frases": ["Mmm...", "¡Qué rico!", "Ahh, sí..."]},
    "cara":     {"jugar": 0, "cara": "enojo", "anim": None,
                 "particula": None,
                 "frases": ["¡Ey, mi cara!", "¡No veo nada!", "¡Mis ojos!"]},
    "costados": {"jugar": 1, "cara": "risa", "anim": "temblor",
                 "particula": ("ja", 2),
                 "frases": ["¡Cosquillas!", "¡Ay, ay, ay!"]},
    "panza":    {"jugar": 2, "cara": "risa", "anim": "temblor",
                 "particula": ("ja", 3),
                 "frases": ["¡Jajaja!", "¡Jijiji, basta!", "¡Mi pancita!"]},
    "pies":     {"jugar": 1, "cara": "risa", "anim": "saltitos",
                 "particula": ("estrella", 2),
                 "frases": ["¡Mis patitas!", "¡Jiji, no!"]},
    "cuerpo":   {"jugar": 1, "cara": None, "anim": None,
                 "particula": ("corazon", 3),
                 "frases": ["¡Me encanta!", "¡Más, más!", "¡Te quiero!",
                            "¡Eres la mejor!"]},
    "molesta":  {"jugar": -3, "cara": "enojo", "anim": "temblor",
                 "particula": None,
                 "frases": ["¡Basta ya!", "¡Déjame tranquila!"]},
}

# Animaciones (px)
ANIM_TEMBLOR_PX = 5
ANIM_SALTITOS_PX = 16
ANIM_HUNDIR_PX = 6