import math
import random

import pygame
import principal

pygame.init()

ancho = principal.ancho
alto = principal.alto

ventana = pygame.display.get_surface()
pygame.display.set_caption("PAU")
reloj = pygame.time.Clock()

fuente_titulo = pygame.font.Font(None, 120)
fuente_boton = pygame.font.Font(None, 36)
fuente_sub = pygame.font.Font(None, 30)
fuente_texto = pygame.font.Font(None, 26)
fuente_chica = pygame.font.Font(None, 22)

COLOR_TEXTO_BOTON = (60, 90, 140)
COLOR_TITULO = (255, 255, 255)
COLOR_SOMBRA = (60, 70, 120)

# ---------------------------------------------------------------------------
# FONDO
# ---------------------------------------------------------------------------
fondo_img = principal.cargar_imagen("PAU.png", tamaño=(ancho, alto), opaca=True)
TIENE_FONDO = fondo_img is not None


def _crear_degradado(arriba, abajo):
    s = pygame.Surface((ancho, alto)).convert()
    for y in range(alto):
        t = y / alto
        color = tuple(int(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3))
        pygame.draw.line(s, color, (0, y), (ancho, y))
    return s


fondo_degradado = _crear_degradado((120, 175, 235), (240, 195, 235))

burbujas = [
    {"x": random.uniform(0, ancho), "y": random.uniform(0, alto),
     "r": random.randint(6, 26), "v": random.uniform(12, 40),
     "f": random.uniform(0, 6.28)}
    for _ in range(26)
]


def actualizar_burbujas(dt, t):
    for b in burbujas:
        b["y"] -= b["v"] * dt
        b["x"] += math.sin(t * 1.2 + b["f"]) * 12 * dt
        if b["y"] < -40:
            b["y"] = alto + 40
            b["x"] = random.uniform(0, ancho)


def dibujar_burbujas(sup):
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for b in burbujas:
        c = (int(b["x"]), int(b["y"]))
        pygame.draw.circle(capa, (255, 255, 255, 60), c, b["r"])
        pygame.draw.circle(capa, (255, 255, 255, 140), c, b["r"], 2)
    sup.blit(capa, (0, 0))


def dibujar_fondo(sup, t):
    sup.blit(fondo_img if TIENE_FONDO else fondo_degradado, (0, 0))
    dibujar_burbujas(sup)


def texto_con_sombra(sup, texto, fuente, color, centro, sombra=COLOR_SOMBRA, desp=4):
    s = fuente.render(texto, True, sombra)
    sup.blit(s, s.get_rect(center=(centro[0] + desp, centro[1] + desp)))
    t = fuente.render(texto, True, color)
    sup.blit(t, t.get_rect(center=centro))


def dibujar_titulo(sup, t):
    if TIENE_FONDO:
        return          # la imagen PAU.png ya trae su propio título
    rebote = int(math.sin(t * 2.2) * 6)
    texto_con_sombra(sup, "PAU", fuente_titulo, COLOR_TITULO, (400, 90 + rebote))
    texto_con_sombra(sup, "tu mascota virtual", fuente_sub, (255, 255, 255),
                     (400, 150), desp=2)
    # Pau a un lado, respirando
    img = principal.pou_feliz
    esc = 1.0 + math.sin(t * 3) * 0.02
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (int(w * 0.8 * esc), int(h * 0.8 * esc)))
    sup.blit(img, img.get_rect(center=(125, 400 + int(math.sin(t * 3) * 5))))


# ---------------------------------------------------------------------------
# BOTONES
# ---------------------------------------------------------------------------
class Boton:
    def __init__(self, rect, texto):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.hover = 0.0

    def actualizar(self, dt, pos):
        objetivo = 1.0 if self.rect.collidepoint(pos) else 0.0
        self.hover += (objetivo - self.hover) * min(1.0, dt * 14)

    def dibujar(self, sup, texto=None):
        h = self.hover
        r = self.rect.inflate(int(14 * h), int(6 * h))
        sombra = r.move(0, 4)
        pygame.draw.rect(sup, (50, 60, 100), sombra, border_radius=12)
        relleno = (int(255 - 30 * h), int(255 - 17 * h), 255)
        pygame.draw.rect(sup, relleno, r, border_radius=12)
        pygame.draw.rect(sup, (0, 0, 0), r, 2, border_radius=12)
        s = fuente_boton.render(texto or self.texto, True, COLOR_TEXTO_BOTON)
        sup.blit(s, s.get_rect(center=r.center))

    def click(self, pos):
        return self.rect.collidepoint(pos)


def fila_botones(textos, x, y0, w=280, h=52, sep=66):
    return [Boton((x, y0 + i * sep, w, h), t) for i, t in enumerate(textos)]


botones_menu = fila_botones(["JUGAR", "INSTRUCCIONES", "OPCIONES", "SALIR"], 260, 200)
botones_opciones = fila_botones(["", "Pantalla completa", "Borrar progreso", "Volver"],
                                260, 190, sep=72)
botones_pausa = fila_botones(["Continuar", "", "Menú principal"], 260, 230, sep=75)
botones_confirmar = [Boton((200, 330, 180, 52), "Sí, borrar"),
                     Boton((420, 330, 180, 52), "Cancelar")]
boton_volver_ins = Boton((300, 540, 200, 42), "Volver")
cruz = pygame.Rect(740, 10, 40, 40)

# ---------------------------------------------------------------------------
# INSTRUCCIONES (con scroll)
# ---------------------------------------------------------------------------
SECCIONES = [
    ("Objetivo", "Cuida a Pau: que ninguna barra llegue a cero. Si se desmaya, "
                 "puedes revivirla con monedas. El progreso se guarda solo."),
    ("Cómo moverte", "Usa las flechas del juego, o las teclas ← → / A D, para "
                     "cambiar de cuarto. ESC cierra ventanas y abre la pausa."),
    ("Baño", "Arrastra jabón, ducha y toalla sobre Pau para dejarla limpia."),
    ("Cocina", "Dale de comer. Algunas comidas dan efectos extra: el helado "
               "divierte, la sopa da sueño y las comidas pesadas ensucian. "
               "Pau tiene comidas favoritas (corazón) y una que odia y escupe (X): "
               "¡descúbrelas probando! Las que tienen ? aún no las probó."),
    ("Habitación", "La almohada la hace dormir (no puedes salir del cuarto). "
                   "En el armario eliges su ropa."),
    ("Sala de estar", "Minijuegos, tienda de comida y ropa, misiones diarias, "
                      "logros y la RULETA: un giro gratis cada día."),
    ("Minijuegos", "Atrapa comida (¡combos y comida dorada!), Memoria, Reflejos "
                   "(fallar resta puntos) y Simón dice. Intenta batir tus récords."),
    ("Jardín", "Planta, riega y cosecha tus propios ingredientes."),
    ("Caricias", "Toca distintas partes de Pau: la cabeza la relaja, la panza y "
                 "los costados le dan cosquillas, los pies la hacen saltar... "
                 "¡pero si la tocas demasiado seguido se enoja!"),
    ("Extras", "Atrapa los regalos sorpresa y sube de "
               "nivel. Entra cada día para ganar bonus y mantener tu racha."),
]


def construir_instrucciones():
    lineas = []          # (texto, tipo)
    for titulo, cuerpo in SECCIONES:
        lineas.append((titulo, "titulo"))
        actual = ""
        for palabra in cuerpo.split():
            prueba = (actual + " " + palabra).strip()
            if fuente_texto.size(prueba)[0] <= 580:
                actual = prueba
            else:
                lineas.append((actual, "texto"))
                actual = palabra
        if actual:
            lineas.append((actual, "texto"))
        lineas.append(("", "espacio"))
    return lineas


LINEAS_INS = construir_instrucciones()
ALTO_LINEA = {"titulo": 30, "texto": 22, "espacio": 10}
ALTO_TOTAL_INS = sum(ALTO_LINEA[t] for _, t in LINEAS_INS)
AREA_INS = pygame.Rect(90, 100, 620, 420)
scroll_ins = 0


def limitar_scroll():
    global scroll_ins
    maximo = max(0, ALTO_TOTAL_INS - AREA_INS.height + 10)
    scroll_ins = max(0, min(maximo, scroll_ins))


def dibujar_instrucciones(sup, t, dt, pos):
    dibujar_fondo(sup, t)
    texto_con_sombra(sup, "INSTRUCCIONES", fuente_boton, COLOR_TITULO, (400, 55), desp=2)
    panel = pygame.Surface(AREA_INS.inflate(30, 20).size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (255, 255, 255, 215), panel.get_rect(), border_radius=16)
    sup.blit(panel, AREA_INS.inflate(30, 20).topleft)

    sup.set_clip(AREA_INS)
    y = AREA_INS.y - scroll_ins
    for linea, tipo in LINEAS_INS:
        if linea:
            if tipo == "titulo":
                s = fuente_sub.render(linea, True, (200, 90, 130))
            else:
                s = fuente_texto.render(linea, True, (50, 50, 70))
            sup.blit(s, (AREA_INS.x + 15, y))
        y += ALTO_LINEA[tipo]
    sup.set_clip(None)

    if ALTO_TOTAL_INS > AREA_INS.height:      # barra de scroll
        maximo = ALTO_TOTAL_INS - AREA_INS.height + 10
        alto_b = max(30, int(AREA_INS.height * AREA_INS.height / ALTO_TOTAL_INS))
        yb = AREA_INS.y + int((AREA_INS.height - alto_b) * (scroll_ins / maximo))
        pygame.draw.rect(sup, (200, 90, 130), (AREA_INS.right + 6, yb, 6, alto_b),
                         border_radius=3)

    boton_volver_ins.actualizar(dt, pos)
    boton_volver_ins.dibujar(sup)


# ---------------------------------------------------------------------------
# PANTALLAS
# ---------------------------------------------------------------------------
def dibujar_menu(sup, t, dt, pos):
    dibujar_fondo(sup, t)
    dibujar_titulo(sup, t)
    for b in botones_menu:
        b.actualizar(dt, pos)
        b.dibujar(sup)

    resumen = (f"Nv. {principal.nivel}    Monedas: {principal.monedas}    "
               f"Racha: {principal.racha}    Logros: {len(principal.logros_hechos)}"
               f"/{len(principal.LOGROS)}")
    s = fuente_texto.render(resumen, True, (255, 255, 255))
    sombra = fuente_texto.render(resumen, True, COLOR_SOMBRA)
    r = s.get_rect(center=(400, 560))
    sup.blit(sombra, r.move(2, 2))
    sup.blit(s, r)


def dibujar_opciones(sup, t, dt, pos):
    dibujar_fondo(sup, t)
    texto_con_sombra(sup, "OPCIONES", fuente_boton, COLOR_TITULO, (400, 90), desp=2)
    for i, b in enumerate(botones_opciones):
        b.actualizar(dt, pos)
        if i == 0:
            b.dibujar(sup, "Sonido: " + ("SÍ" if principal.config["sonido"] else "NO"))
        else:
            b.dibujar(sup)
    ayuda = fuente_chica.render("F11 también activa la pantalla completa", True, (255, 255, 255))
    sup.blit(ayuda, ayuda.get_rect(center=(400, 520)))


def dibujar_panel(sup, rect, titulo):
    pygame.draw.rect(sup, (255, 255, 255), rect, border_radius=16)
    pygame.draw.rect(sup, (0, 0, 0), rect, 3, border_radius=16)
    s = fuente_boton.render(titulo, True, (40, 40, 70))
    sup.blit(s, s.get_rect(center=(rect.centerx, rect.y + 45)))


def dibujar_confirmar(sup, t, dt, pos):
    dibujar_fondo(sup, t)
    sup.blit(velo, (0, 0))
    dibujar_panel(sup, pygame.Rect(170, 200, 460, 220), "¿Borrar TODO el progreso?")
    s = fuente_texto.render("Esta acción no se puede deshacer.", True, (160, 0, 0))
    sup.blit(s, s.get_rect(center=(400, 275)))
    for b in botones_confirmar:
        b.actualizar(dt, pos)
        b.dibujar(sup)


def dibujar_pausa(sup, t, dt, pos):
    sup.blit(snapshot, (0, 0))
    sup.blit(velo, (0, 0))
    dibujar_panel(sup, pygame.Rect(230, 130, 340, 330), "PAUSA")
    for i, b in enumerate(botones_pausa):
        b.actualizar(dt, pos)
        if i == 1:
            b.dibujar(sup, "Sonido: " + ("SÍ" if principal.config["sonido"] else "NO"))
        else:
            b.dibujar(sup)


velo = pygame.Surface((ancho, alto))
velo.set_alpha(120)
velo.fill((20, 20, 50))
snapshot = pygame.Surface((ancho, alto))

# ---------------------------------------------------------------------------
# TRANSICIONES (fundido a negro)
# ---------------------------------------------------------------------------
negro = pygame.Surface((ancho, alto))
negro.fill((0, 0, 0))
pantalla_actual = "menu"
destino = None
fade = 0.0              # 0..255
fade_fase = None        # None / "out" / "in"
VEL_FADE = 1300.0


def ir_a(nueva):
    global destino, fade_fase
    if fade_fase is None:
        destino = nueva
        fade_fase = "out"


def actualizar_fade(dt):
    global fade, fade_fase, pantalla_actual
    if fade_fase == "out":
        fade += VEL_FADE * dt
        if fade >= 255:
            fade = 255
            cambiar_ahora(destino)
            fade_fase = "in"
    elif fade_fase == "in":
        fade -= VEL_FADE * dt
        if fade <= 0:
            fade = 0
            fade_fase = None


def cambiar_ahora(nueva):
    global pantalla_actual, scroll_ins
    if nueva == "juego":
        principal.ultimo_frame = pygame.time.get_ticks()
    if nueva == "instrucciones":
        scroll_ins = 0
    pantalla_actual = nueva


def entrar_pausa():
    global snapshot
    principal.guardar()
    snapshot = pygame.display.get_surface().copy()
    cambiar_ahora("pausa")


def alternar_pantalla_completa():
    try:
        pygame.display.toggle_fullscreen()
    except pygame.error:
        pass


# ---------------------------------------------------------------------------
# BUCLE PRINCIPAL
# ---------------------------------------------------------------------------
ejecutando = True
tiempo = 0.0

while ejecutando:
    dt = min(0.05, reloj.tick(60) / 1000)
    tiempo += dt
    ventana = pygame.display.get_surface()
    pos = pygame.mouse.get_pos()
    bloqueado = fade_fase is not None       # sin clicks durante el fundido

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                alternar_pantalla_completa()
                continue
            if bloqueado:
                continue

            if evento.key == pygame.K_ESCAPE:
                if pantalla_actual in ("instrucciones", "opciones"):
                    ir_a("menu")
                elif pantalla_actual == "confirmar":
                    cambiar_ahora("opciones")
                elif pantalla_actual == "pausa":
                    ir_a("juego")
                elif pantalla_actual == "juego":
                    if not principal.manejar_escape():
                        entrar_pausa()
            elif pantalla_actual == "menu" and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                ir_a("juego")
            elif pantalla_actual == "juego":
                principal.manejar_tecla(evento.key)
            elif pantalla_actual == "instrucciones":
                if evento.key == pygame.K_DOWN:
                    scroll_ins += 30
                elif evento.key == pygame.K_UP:
                    scroll_ins -= 30
                limitar_scroll()

        elif evento.type == pygame.MOUSEWHEEL and pantalla_actual == "instrucciones":
            scroll_ins -= evento.y * 30
            limitar_scroll()

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not bloqueado:

            if pantalla_actual == "menu":
                if botones_menu[0].click(evento.pos):
                    ir_a("juego")
                elif botones_menu[1].click(evento.pos):
                    ir_a("instrucciones")
                elif botones_menu[2].click(evento.pos):
                    ir_a("opciones")
                elif botones_menu[3].click(evento.pos):
                    ejecutando = False

            elif pantalla_actual == "instrucciones":
                if boton_volver_ins.click(evento.pos) or cruz.collidepoint(evento.pos):
                    ir_a("menu")

            elif pantalla_actual == "opciones":
                if botones_opciones[0].click(evento.pos):
                    principal.alternar_sonido()
                elif botones_opciones[1].click(evento.pos):
                    alternar_pantalla_completa()
                elif botones_opciones[2].click(evento.pos):
                    cambiar_ahora("confirmar")
                elif botones_opciones[3].click(evento.pos):
                    ir_a("menu")

            elif pantalla_actual == "confirmar":
                if botones_confirmar[0].click(evento.pos):
                    principal.reiniciar_progreso()
                    cambiar_ahora("opciones")
                elif botones_confirmar[1].click(evento.pos):
                    cambiar_ahora("opciones")

            elif pantalla_actual == "pausa":
                if botones_pausa[0].click(evento.pos):
                    ir_a("juego")
                elif botones_pausa[1].click(evento.pos):
                    principal.alternar_sonido()
                elif botones_pausa[2].click(evento.pos):
                    principal.guardar()
                    ir_a("menu")

            elif pantalla_actual == "juego":
                if cruz.collidepoint(evento.pos):
                    entrar_pausa()
                else:
                    principal.manejar_click(evento.pos)

        elif evento.type == pygame.MOUSEMOTION and pantalla_actual == "juego":
            principal.manejar_movimiento(evento.pos)

        elif (evento.type == pygame.MOUSEBUTTONUP and evento.button == 1
              and pantalla_actual == "juego"):
            principal.manejar_soltar()

    # --- Dibujo -------------------------------------------------------------
    actualizar_burbujas(dt, tiempo)

    if pantalla_actual == "menu":
        dibujar_menu(ventana, tiempo, dt, pos)

    elif pantalla_actual == "instrucciones":
        dibujar_instrucciones(ventana, tiempo, dt, pos)

    elif pantalla_actual == "opciones":
        dibujar_opciones(ventana, tiempo, dt, pos)

    elif pantalla_actual == "confirmar":
        dibujar_confirmar(ventana, tiempo, dt, pos)

    elif pantalla_actual == "pausa":
        dibujar_pausa(ventana, tiempo, dt, pos)

    elif pantalla_actual == "juego":
        principal.principal()
        resaltar = cruz.collidepoint(pos)
        color = (200, 0, 0) if resaltar else (0, 0, 0)
        pygame.draw.line(ventana, color, (740, 10), (770, 40), 5)
        pygame.draw.line(ventana, color, (770, 10), (740, 40), 5)

    actualizar_fade(dt)
    if fade > 0:
        negro.set_alpha(int(fade))
        ventana.blit(negro, (0, 0))

    pygame.display.flip()


principal.guardar()
pygame.quit()