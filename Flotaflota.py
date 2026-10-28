import pygame
import os
import random

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    archivo = os.path.join(carpeta_raiz, "assets", "minijuegos", "flotaflota", nombre)
    return archivo

pygame.init()

jugando = True
game_over = False

ANCHO = 800
ALTO = 500

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flota Pau")

reloj = pygame.time.Clock()

fondo = pygame.image.load(encontrar_archivo("agua.jpg"))
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

pau = pygame.image.load(encontrar_archivo("pauflotaflota.png"))
pau = pygame.transform.scale(pau, (80, 80))

flota_flota_imagen = pygame.image.load(encontrar_archivo("uniflota.png"))
flota_flota_imagen = pygame.transform.scale(flota_flota_imagen, (150, 150))

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
tiempo_inicio = pygame.time.get_ticks()
tiempo_restante = TIEMPO_MAXIMO

ANCHO_BARRA = 250
ALTO_BARRA = 22

DEBUG = False

def superficie_flota(flota):
    return flota.top + MARGEN_SUPERIOR_FLOTA

def y_pau_apoyado(flota):
    return superficie_flota(flota) - ALTO_PAU + MARGEN_PIES_PAU

def crear_flota(anterior):
    tipo_distancia = random.choice([
        "corta", "corta", "media", "media",
        "larga", "corta", "larga", "media"
    ])

    if tipo_distancia == "corta":
        distancia = random.randint(25, 50)
    elif tipo_distancia == "media":
        distancia = random.randint(55, 95)
    else:
        distancia = random.randint(125, 180)

    cambio_altura = random.choice([
        random.randint(-12, -4),
        random.randint(4, 12),
        random.randint(-5, 5),
        random.randint(-15, 15)
    ])

    nueva_y = anterior.y + cambio_altura
    nueva_y = max(350, min(390, nueva_y))

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

def reiniciar_juego():
    global x_pau, y_pau, velocidad_y, saltando
    global puntos, indice_actual, indice_destino
    global camara_x, destino_x, flota_flota_list
    global game_over, tiempo_inicio, tiempo_restante
    global caer_al_agua, objetivo_caida_x

    x_pau = 135 + OFFSET_X_APOYO
    velocidad_y = 0
    saltando = False

    puntos = 0
    indice_actual = 0
    indice_destino = 0
    camara_x = 0
    destino_x = x_pau

    flota_flota_list = crear_plataformas_iniciales()
    y_pau = globals()["y_pau"] = y_pau_apoyado(flota_flota_list[0])

    tiempo_inicio = pygame.time.get_ticks()
    tiempo_restante = TIEMPO_MAXIMO

    caer_al_agua = False
    objetivo_caida_x = x_pau
    game_over = False

gravedad = 0.6
f_salto_normal = -9
f_doble_salto = -15

x_pau = 135 + OFFSET_X_APOYO
velocidad_y = 0
saltando = False

flota_flota_list = crear_plataformas_iniciales()
y_pau = y_pau_apoyado(flota_flota_list[0])

indice_actual = 0
indice_destino = 0

destino_x = x_pau
camara_x = 0
puntos = 0

caer_al_agua = False
objetivo_caida_x = x_pau

fuente = pygame.font.Font(None, 40)
fuente_game_over = pygame.font.Font(None, 60)
fuente_reinicio = pygame.font.Font(None, 35)
fuente_tiempo = pygame.font.Font(None, 28)

while jugando:

    reloj.tick(60)

    if not game_over:
        tiempo_transcurrido = (
            pygame.time.get_ticks() - tiempo_inicio
        ) / 1000

        tiempo_restante = max(
            0, TIEMPO_MAXIMO - tiempo_transcurrido
        )

        if tiempo_restante <= 0:
            game_over = True

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.KEYDOWN:

            if not game_over and not saltando:

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

    if not game_over:

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

        if x_pau > camara_x + 400:
            camara_x = x_pau - 400

        while flota_flota_list[-1].x < camara_x + ANCHO + 300:
            anterior = flota_flota_list[-1]
            flota_flota_list.append(crear_flota(anterior))

        if y_pau > ALTO + 100:
            game_over = True

    ventana.blit(fondo, (0, 0))

    for flotaflota in flota_flota_list:

        x_pantalla = flotaflota.x - camara_x

        if -ANCHO_FLOTA <= x_pantalla <= ANCHO:
            ventana.blit(
                flota_flota_imagen,
                (int(x_pantalla), flotaflota.y)
            )

    ventana.blit(
        pau,
        (int(x_pau - camara_x), int(y_pau))
    )

    texto_puntos = fuente.render(
        "Puntos: " + str(puntos),
        True,
        (255, 255, 255)
    )

    ventana.blit(texto_puntos, (20, 20))

    texto_tiempo = fuente_tiempo.render(
        "Tiempo: " + str(int(tiempo_restante)) + " s",
        True,
        (255, 255, 255)
    )

    ventana.blit(texto_tiempo, (ANCHO - 290, 20))

    barra_x = ANCHO - 290
    barra_y = 50

    pygame.draw.rect(
        ventana,
        (50, 50, 50),
        (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
        border_radius=8
    )

    ancho_actual = int(
        ANCHO_BARRA * tiempo_restante / TIEMPO_MAXIMO
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

        texto = fuente_game_over.render(
            "GAME OVER",
            True,
            (255, 255, 255)
        )

        ventana.blit(texto, (270, 190))

        texto2 = fuente_reinicio.render(
            "Presiona R para volver a jugar",
            True,
            (255, 255, 255)
        )

        ventana.blit(texto2, (230, 260))

    pygame.display.update()

pygame.quit()
