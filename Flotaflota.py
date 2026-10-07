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

fondo = pygame.image.load(encontrar_archivo("flotaflota.png"))
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

pau = pygame.image.load(encontrar_archivo("pauflotaflota.png"))
pau = pygame.transform.scale(pau, (80, 80))

flota_flota_imagen = pygame.image.load(encontrar_archivo("ob_flota.png"))
flota_flota_imagen = pygame.transform.scale(flota_flota_imagen, (130, 40))

x_pau = 150
y_pau = 350

velocidad_y = 0
gravedad = 0.6
f_salto = -12

en_flota = True
saltando = False

flota_flota_list = []

flota_inicial = pygame.Rect(100, 420, 130, 40)
flota_flota_list.append(flota_inicial)

for i in range(1, 7):
    distancia = random.randint(100, 220)
    x = flota_flota_list[-1].x + distancia
    y = random.randint(300, 420)
    flota_flota_list.append(pygame.Rect(x, y, 130, 40))

flota_actual = 0

puntos = 0

camara_x = 0

destino_x = x_pau
destino_y = y_pau

while jugando:

    reloj.tick(60)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.KEYDOWN:

            if not game_over:

                if evento.key == pygame.K_LEFT and not saltando:

                    if flota_actual + 1 < len(flota_flota_list):

                        flota_actual += 1

                        destino_x = flota_flota_list[flota_actual].centerx - 40
                        destino_y = flota_flota_list[flota_actual].top - 80

                        velocidad_y = f_salto
                        saltando = True

                        puntos += 1

                if evento.key == pygame.K_RIGHT and not saltando:

                    if flota_actual + 2 < len(flota_flota_list):

                        flota_actual += 2

                        destino_x = flota_flota_list[flota_actual].centerx - 40
                        destino_y = flota_flota_list[flota_actual].top - 80

                        velocidad_y = f_salto - 1
                        saltando = True

                        puntos += 2

            if evento.key == pygame.K_r and game_over:

                x_pau = 150
                y_pau = 350

                velocidad_y = 0

                flota_flota_list = []

                flota_inicial = pygame.Rect(100, 420, 130, 40)
                flota_flota_list.append(flota_inicial)

                for i in range(1, 7):

                    distancia = random.randint(100, 220)

                    x = flota_flota_list[-1].x + distancia
                    y = random.randint(300, 420)

                    flota_flota_list.append(
                        pygame.Rect(x, y, 130, 40)
                    )

                flota_actual = 0

                puntos = 0

                camara_x = 0

                destino_x = x_pau
                destino_y = y_pau

                saltando = False
                game_over = False

    if not game_over:

        if saltando:

            velocidad_y += gravedad
            y_pau += velocidad_y

            diferencia_x = destino_x - x_pau

            x_pau += diferencia_x * 0.08

            if velocidad_y > 0:

                rect_pau = pygame.Rect(
                    x_pau,
                    y_pau,
                    80,
                    80
                )

                flotaflota = flota_flota_list[flota_actual]

                if rect_pau.colliderect(flotaflota):

                    if rect_pau.bottom <= flotaflota.bottom + 20:

                        y_pau = flotaflota.top - 80

                        velocidad_y = 0
                        saltando = False

        if x_pau > camara_x + 400:

            camara_x = x_pau - 400

        while flota_flota_list[-1].x < camara_x + ANCHO + 300:

            distancia = random.randint(100, 240)

            x = flota_flota_list[-1].right + distancia

            y = random.randint(280, 420)

            nueva_flota = pygame.Rect(
                x,
                y,
                130,
                40
            )

            flota_flota_list.append(nueva_flota)

        while len(flota_flota_list) > 0 and flota_flota_list[0].right < camara_x - 200:

            flota_flota_list.pop(0)
            flota_actual -= 1

        if y_pau > ALTO + 100:

            game_over = True

    ventana.blit(fondo, (0, 0))

    for flotaflota in flota_flota_list:

        x_pantalla = flotaflota.x - camara_x

        ventana.blit(
            flota_flota_imagen,
            (x_pantalla, flotaflota.y)
        )

    ventana.blit(
        pau,
        (x_pau - camara_x, y_pau)
    )

    fuente = pygame.font.Font(None, 40)

    texto_puntos = fuente.render(
        "Puntos: " + str(puntos),
        True,
        (255, 255, 255)
    )

    ventana.blit(
        texto_puntos,
        (20, 20)
    )

    if game_over:

        fuente = pygame.font.Font(None, 60)

        texto = fuente.render(
            "GAME OVER",
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto,
            (270, 190)
        )

        fuente2 = pygame.font.Font(None, 35)

        texto2 = fuente2.render(
            "Presiona R para volver a jugar",
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto2,
            (230, 260)
        )

    pygame.display.update()

pygame.quit()