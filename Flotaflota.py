
import pygame
import os
import random

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    return os.path.join(carpeta_raiz, "assets", "minijuegos", "flotaflota", nombre)

pygame.init()

jugando = True
game_over = False
pantalla_actual = "instrucciones"

ANCHO = 800
ALTO = 500

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flota Pau")

reloj = pygame.time.Clock()

fondo = pygame.image.load(encontrar_archivo("agua.jpg")).convert()
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

imagen_instrucciones = pygame.image.load(encontrar_archivo("intro.jpg")).convert()
imagen_instrucciones = pygame.transform.scale(imagen_instrucciones, (ANCHO, ALTO))

pau = pygame.image.load(encontrar_archivo("pauflotaflota.png")).convert_alpha()
pau = pygame.transform.scale(pau, (80, 80))

flota_flota_imagen = pygame.image.load(encontrar_archivo("uniflota.png")).convert_alpha()
flota_flota_imagen = pygame.transform.scale(flota_flota_imagen, (150, 150))

imagen_moneda = pygame.image.load(encontrar_archivo("moneda.png")).convert_alpha()
imagen_moneda = pygame.transform.scale(imagen_moneda, (35, 35))

imagen_reloj = pygame.image.load(encontrar_archivo("reloj.png")).convert_alpha()
imagen_reloj = pygame.transform.scale(imagen_reloj, (35, 35))

ANCHO_PAU = 80
ALTO_PAU = 80

ANCHO_FLOTA = 150
ALTO_FLOTA = 45
ALTURA_FLOTA = 370

MARGEN_SUPERIOR_FLOTA = 65
MARGEN_LATERAL_FLOTA = 10
MARGEN_PIES_PAU = 12
MARGEN_LATERAL_PAU = 12
OFFSET_X_APOYO = 20

DISTANCIA_LARGA = 100

TIEMPO_MAXIMO = 60
TIEMPO_EXTRA_RELOJ = 5

ANCHO_BARRA = 250
ALTO_BARRA = 22

PUNTOS_DIFICULTAD_MAX = 100

VELOCIDAD_TIEMPO_EXTRA = 0.8

LIMITE_FLOTA_INICIAL = 4.0
LIMITE_FLOTA_MINIMO = 1.4
HUNDIMIENTO_MAX = 40

fuente = pygame.font.Font(encontrar_archivo("HelloSummerPersonalUse.ttf"), 20)
fuente_grande = pygame.font.Font(encontrar_archivo("HelloSummerPersonalUse.ttf"), 50)
fuente_instrucciones = pygame.font.Font(encontrar_archivo("HelloSummerPersonalUse.ttf"), 20)
fuente_reinicio = pygame.font.Font(encontrar_archivo("HelloSummerPersonalUse.ttf"), 27)
fuente_tiempo = pygame.font.Font(encontrar_archivo("HelloSummerPersonalUse.ttf"), 15)

COLOR_CELESTE = (135, 220, 255)

boton_jugar = pygame.Rect(300, 405, 200, 60)
color_boton = (80, 190, 100)
color_boton_hover = (50, 160, 75)

def dificultad():
    return min(1.0, puntos / PUNTOS_DIFICULTAD_MAX)

def nivel_actual():
    return 1 + int(dificultad() * 9)

def limite_flota():
    return LIMITE_FLOTA_INICIAL - (
        LIMITE_FLOTA_INICIAL - LIMITE_FLOTA_MINIMO
    ) * dificultad()

def probabilidad_objeto():
    return 0.4 - 0.15 * dificultad()

def superficie_flota(flota):
    return flota.top + MARGEN_SUPERIOR_FLOTA

def y_pau_apoyado(flota):
    return superficie_flota(flota) - ALTO_PAU + MARGEN_PIES_PAU

def crear_flota(anterior):
    d = dificultad()

    tipo_distancia = random.choices(
        ["corta", "media", "larga"],
        weights=[3 - 2.5 * d, 3, 2 + 4 * d]
    )[0]

    if tipo_distancia == "corta":
        distancia = random.randint(25 + int(15 * d), 50 + int(20 * d))
    elif tipo_distancia == "media":
        distancia = random.randint(55 + int(15 * d), 95 + int(15 * d))
    else:
        distancia = random.randint(125 + int(10 * d), 180 + int(30 * d))

    amplitud = 15 + int(10 * d)
    cambio_altura = random.randint(-amplitud, amplitud)

    nueva_y = anterior.y + cambio_altura
    nueva_y = max(350 - int(10 * d), min(390 + int(5 * d), nueva_y))

    return pygame.Rect(
        anterior.right + distancia,
        nueva_y,
        ANCHO_FLOTA,
        ALTO_FLOTA
    )

def crear_plataformas_iniciales():
    plataformas = []

    flota_inicial = pygame.Rect(
        100, ALTURA_FLOTA, ANCHO_FLOTA, ALTO_FLOTA
    )

    plataformas.append(flota_inicial)

    for i in range(1, 9):
        plataformas.append(crear_flota(plataformas[-1]))

    return plataformas

def crear_objeto(flota):
    tipo = random.choices(
        ["moneda", "reloj"],
        weights=[2, 1 - 0.6 * dificultad()]
    )[0]

    rect_objeto = pygame.Rect(
        flota.centerx - 17,
        superficie_flota(flota) - 45,
        35,
        35
    )

    return {
        "tipo": tipo,
        "rect": rect_objeto
    }

def agregar_objetos():
    objetos = []

    for flota in flota_flota_list:
        if random.random() < probabilidad_objeto():
            objetos.append(crear_objeto(flota))

    return objetos

gravedad = 0.6
f_salto_normal = -9
f_doble_salto = -15

def reiniciar_juego():
    global x_pau, y_pau, velocidad_y, saltando
    global puntos, indice_actual, indice_destino
    global camara_x, destino_x, flota_flota_list
    global game_over, tiempo_gastado, tiempo_restante
    global caer_al_agua, objetivo_caida_x
    global objetos, monedas, tiempo_extra
    global tiempo_en_flota, hundida_idx

    x_pau = 135 + OFFSET_X_APOYO
    velocidad_y = 0
    saltando = False

    puntos = 0
    monedas = 0
    tiempo_extra = 0

    indice_actual = 0
    indice_destino = 0

    camara_x = 0
    destino_x = x_pau

    flota_flota_list = crear_plataformas_iniciales()
    objetos = agregar_objetos()

    y_pau = y_pau_apoyado(flota_flota_list[0])

    tiempo_gastado = 0.0
    tiempo_restante = TIEMPO_MAXIMO

    tiempo_en_flota = 0.0
    hundida_idx = None

    caer_al_agua = False
    objetivo_caida_x = x_pau

    game_over = False

reiniciar_juego()

while jugando:

    dt = min(reloj.tick(60) / 1000, 0.05)

    if pantalla_actual == "juego" and not game_over:

        velocidad_tiempo = 1 + VELOCIDAD_TIEMPO_EXTRA * dificultad()
        tiempo_gastado += dt * velocidad_tiempo

        tiempo_restante = max(
            0, TIEMPO_MAXIMO + tiempo_extra - tiempo_gastado
        )

        if tiempo_restante <= 0:
            game_over = True

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1 and pantalla_actual == "instrucciones":

                if boton_jugar.collidepoint(evento.pos):
                    reiniciar_juego()
                    pantalla_actual = "juego"

        if evento.type == pygame.KEYDOWN:

            if pantalla_actual == "juego" and not game_over:

                if not saltando:

                    if evento.key == pygame.K_LEFT:

                        nuevo_indice = indice_actual + 1

                        if nuevo_indice < len(flota_flota_list):

                            flota_actual = flota_flota_list[indice_actual]
                            flota_destino = flota_flota_list[nuevo_indice]

                            distancia = (
                                flota_destino.left - flota_actual.right
                            )

                            indice_destino = nuevo_indice

                            destino_x = (
                                flota_destino.centerx
                                - ANCHO_PAU // 2
                                + OFFSET_X_APOYO
                            )

                            velocidad_y = f_salto_normal
                            saltando = True
                            puntos += 1

                            if distancia > DISTANCIA_LARGA:
                                caer_al_agua = True
                                objetivo_caida_x = (
                                    flota_actual.right
                                    + distancia // 2
                                    - ANCHO_PAU // 2
                                )
                            else:
                                caer_al_agua = False

                    elif evento.key == pygame.K_RIGHT:

                        nuevo_indice = indice_actual + 1

                        if nuevo_indice < len(flota_flota_list):

                            indice_destino = nuevo_indice

                            destino_x = (
                                flota_flota_list[indice_destino].centerx
                                - ANCHO_PAU // 2
                                + OFFSET_X_APOYO
                            )

                            velocidad_y = f_doble_salto
                            saltando = True
                            puntos += 2
                            caer_al_agua = False

            if evento.key == pygame.K_r and game_over:
                reiniciar_juego()
                pantalla_actual = "juego"

    if pantalla_actual == "instrucciones":

        ventana.blit(imagen_instrucciones, (0, 0))

        titulo = fuente_grande.render(
            "WATER HOP", True, COLOR_CELESTE
        )

        ventana.blit(
            titulo,
            (ANCHO // 2 - titulo.get_width() // 2, 45)
        )

        instrucciones = [
            "Objetivo: saltar de flota en flota, para que PAU no caiga al agua",
            "PAU pueda avanzar, utiliuza las flechas derecha e izquierda del teclado",
            "Flecha izquierda: salto normal (1 punto)",
            "Flecha derecha: salto doble (2 puntos)",
            "TIP: agarrar los objetos que estan en los flota",
            "Cada vez es mas dificil: mas distancia y el tiempo corre mas rapido",
            "Cuidado: las flotas se hunden si te quedas mucho tiempo en ellas"
        ]

        for i, linea in enumerate(instrucciones):

            texto = fuente_instrucciones.render(
                linea, True, COLOR_CELESTE
            )

            ventana.blit(
                texto,
                (
                    ANCHO // 2 - texto.get_width() // 2,
                    140 + i * 36
                )
            )

        if boton_jugar.collidepoint(pygame.mouse.get_pos()):
            color_actual = color_boton_hover
        else:
            color_actual = color_boton

        pygame.draw.rect(
            ventana, color_actual, boton_jugar, border_radius=12
        )

        texto_boton = fuente.render(
            "JUGAR", True, (255, 255, 255)
        )

        ventana.blit(
            texto_boton,
            (
                boton_jugar.centerx - texto_boton.get_width() // 2,
                boton_jugar.centery - texto_boton.get_height() // 2
            )
        )

    elif pantalla_actual == "juego":

        if not game_over:

            if not saltando:

                tiempo_en_flota += dt

                if tiempo_en_flota >= limite_flota():
                    hundida_idx = indice_actual
                    saltando = True
                    caer_al_agua = True
                    objetivo_caida_x = x_pau
                    velocidad_y = 0

            if saltando:

                y_anterior = y_pau

                velocidad_y += gravedad
                y_pau += velocidad_y

                if caer_al_agua:
                    diferencia_x = objetivo_caida_x - x_pau
                else:
                    diferencia_x = destino_x - x_pau

                x_pau += diferencia_x * 0.12

                if not caer_al_agua:

                    flotaflota = flota_flota_list[indice_destino]
                    superficie = superficie_flota(flotaflota)

                    pies_anterior = (
                        y_anterior + ALTO_PAU - MARGEN_PIES_PAU
                    )

                    pies_actual = (
                        y_pau + ALTO_PAU - MARGEN_PIES_PAU
                    )

                    izquierda = (
                        flotaflota.left + MARGEN_LATERAL_FLOTA
                    )

                    derecha = (
                        flotaflota.right - MARGEN_LATERAL_FLOTA
                    )

                    pau_izquierda = x_pau + MARGEN_LATERAL_PAU
                    pau_derecha = (
                        x_pau + ANCHO_PAU - MARGEN_LATERAL_PAU
                    )

                    if (
                        velocidad_y > 0
                        and pies_anterior <= superficie
                        and pies_actual >= superficie
                        and pau_derecha > izquierda
                        and pau_izquierda < derecha
                    ):

                        y_pau = y_pau_apoyado(flotaflota)

                        x_pau = (
                            flotaflota.centerx
                            - ANCHO_PAU // 2
                            + OFFSET_X_APOYO
                        )

                        velocidad_y = 0
                        saltando = False
                        indice_actual = indice_destino
                        tiempo_en_flota = 0.0

            if x_pau > camara_x + 400:
                camara_x = x_pau - 400

            while flota_flota_list[-1].x < camara_x + ANCHO + 300:

                anterior = flota_flota_list[-1]
                nueva_flota = crear_flota(anterior)
                flota_flota_list.append(nueva_flota)

                if random.random() < probabilidad_objeto():
                    objetos.append(crear_objeto(nueva_flota))

            rect_pau = pygame.Rect(
                int(x_pau + MARGEN_LATERAL_PAU),
                int(y_pau + MARGEN_PIES_PAU),
                ANCHO_PAU - MARGEN_LATERAL_PAU * 2,
                ALTO_PAU - MARGEN_PIES_PAU
            )

            for objeto in objetos[:]:

                rect_objeto = objeto["rect"]

                if rect_pau.colliderect(rect_objeto):

                    if objeto["tipo"] == "moneda":
                        monedas += 1

                    elif objeto["tipo"] == "reloj":
                        tiempo_extra += max(
                            2,
                            int(round(
                                TIEMPO_EXTRA_RELOJ - 3 * dificultad()
                            ))
                        )

                    objetos.remove(objeto)

            if y_pau > ALTO + 100:
                game_over = True

        hundimiento = 0

        if not saltando:
            fraccion = tiempo_en_flota / limite_flota()

            if fraccion > 0.5:
                hundimiento = int(
                    (fraccion - 0.5) / 0.5 * HUNDIMIENTO_MAX
                )

        ventana.blit(fondo, (0, 0))

        for i, flotaflota in enumerate(flota_flota_list):

            x_pantalla = flotaflota.x - camara_x

            if -ANCHO_FLOTA <= x_pantalla <= ANCHO:

                if i == hundida_idx:
                    desplazamiento_y = HUNDIMIENTO_MAX
                elif i == indice_actual and not saltando:
                    desplazamiento_y = hundimiento
                else:
                    desplazamiento_y = 0

                ventana.blit(
                    flota_flota_imagen,
                    (int(x_pantalla), flotaflota.y + desplazamiento_y)
                )

        for objeto in objetos:

            x_objeto = objeto["rect"].x - camara_x
            y_objeto = objeto["rect"].y

            if -40 <= x_objeto <= ANCHO:

                if objeto["tipo"] == "moneda":

                    ventana.blit(
                        imagen_moneda,
                        (int(x_objeto), int(y_objeto))
                    )

                else:

                    ventana.blit(
                        imagen_reloj,
                        (int(x_objeto), int(y_objeto))
                    )

        ventana.blit(
            pau,
            (int(x_pau - camara_x), int(y_pau + hundimiento))
        )

        texto_puntos = fuente_tiempo.render(
            "Puntos: " + str(puntos),
            True,
            (255, 255, 255)
        )
        ventana.blit(texto_puntos, (20, 15))

        texto_monedas = fuente_tiempo.render(
            "Monedas: " + str(monedas),
            True,
            (255, 255, 255)
        )
        ventana.blit(texto_monedas, (20, 50))

        texto_nivel = fuente_tiempo.render(
            "Nivel: " + str(nivel_actual()),
            True,
            (255, 255, 255)
        )
        ventana.blit(texto_nivel, (20, 85))

        texto_tiempo = fuente_tiempo.render(
            "Tiempo: " + str(int(tiempo_restante)) + " s",
            True,
            (255, 255, 255)
        )
        ventana.blit(
            texto_tiempo,
            (ANCHO - texto_tiempo.get_width() - 25, 24)
        )

        barra_x = ANCHO - 275
        barra_y = 60

        pygame.draw.rect(
            ventana,
            (50, 50, 50),
            (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
            border_radius=8
        )

        tiempo_total = TIEMPO_MAXIMO + tiempo_extra

        ancho_actual = int(
            ANCHO_BARRA * tiempo_restante / tiempo_total
        )

        if tiempo_restante > 30:
            color_barra = (40, 210, 80)
        elif tiempo_restante > 10:
            color_barra = (255, 200, 40)
        else:
            color_barra = (230, 50, 50)

        if ancho_actual > 0:
            pygame.draw.rect(
                ventana,
                color_barra,
                (barra_x, barra_y, ancho_actual, ALTO_BARRA),
                border_radius=8
            )

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
            2,
            border_radius=8
        )

        if game_over:

            pygame.draw.rect(
                ventana,
                (25, 25, 25),
                (100, 140, 600, 230),
                border_radius=18
            )

            texto = fuente_grande.render(
                "GAME OVER",
                True,
                (255, 80, 80)
            )

            ventana.blit(
                texto,
                (ANCHO // 2 - texto.get_width() // 2, 155)
            )

            texto_puntos_finales = fuente.render(
                "Puntos conseguidos: " + str(puntos),
                True,
                (255, 255, 255)
            )

            ventana.blit(
                texto_puntos_finales,
                (
                    ANCHO // 2 - texto_puntos_finales.get_width() // 2,
                    225
                )
            )

            texto_monedas_finales = fuente.render(
                "Monedas conseguidas: " + str(monedas),
                True,
                (255, 255, 255)
            )

            ventana.blit(
                texto_monedas_finales,
                (
                    ANCHO // 2 - texto_monedas_finales.get_width() // 2,
                    260
                )
            )

            texto_reinicio = fuente_reinicio.render(
                "Presiona R para reiniciar",
                True,
                (255, 255, 255)
            )

            ventana.blit(
                texto_reinicio,
                (
                    ANCHO // 2 - texto_reinicio.get_width() // 2,
                    315
                )
            )

    pygame.display.update()

pygame.quit()