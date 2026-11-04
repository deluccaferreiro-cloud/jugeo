
import pygame
import random
import os

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    return os.path.join(
        carpeta_raiz,
        "assets",
        "minijuegos",
        "flappy",
        nombre
    )

def cargar_imagen(nombre, tamaño, transparencia=True):
    imagen = pygame.image.load(encontrar_archivo(nombre))

    if transparencia:
        imagen = imagen.convert_alpha()
    else:
        imagen = imagen.convert()

    return pygame.transform.scale(imagen, tamaño)

pygame.init()

jugando = True
game_over = False
pantalla_actual = "intro"

ANCHO = 800
ALTO = 500

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flappy Pau")

reloj = pygame.time.Clock()

fondo = cargar_imagen("flappy.png", (ANCHO, ALTO), False)
introduccion = cargar_imagen("intro.jpg", (ANCHO, ALTO), False)

pau = cargar_imagen("flappypau.png", (67, 67))

moneda_img = cargar_imagen("moneda.png", (32, 32))
saco_moneda_img = cargar_imagen("sacomonedas.png", (55, 55))

ANCHO_TUBO = 80
ESPACIO = 170
VELOCIDAD_TUBOS = 4

tuberia_original = pygame.image.load(
    encontrar_archivo("tuberia.png")
).convert_alpha()

tuberia_vertical = pygame.transform.scale(
    tuberia_original,
    (ANCHO_TUBO, ALTO)
)

tuberia_arriba_img = pygame.transform.flip(
    tuberia_vertical,
    False,
    True
)

x_pau = 150
y_pau = 300

ancho_pau = 67
alto_pau = 67

velocidad_y = 0
gravedad = 0.5
salto = -9

ob = []
monedas_lista = []

puntos = 0
monedas = 0

fuente = pygame.font.Font(
    encontrar_archivo("CloudySunday.ttf"),
    40
)

fuente_grande = pygame.font.Font(
    encontrar_archivo("CloudySunday.ttf"),
    65
)

fuente_chica = pygame.font.Font(
    encontrar_archivo("CloudySunday.ttf"),
    25
)

boton_jugar = pygame.Rect(300, 405, 200, 60)

def dibujar_texto(texto, fuente_usada, color, centro_x, y):
    superficie = fuente_usada.render(texto, True, color)
    ventana.blit(
        superficie,
        (centro_x - superficie.get_width() // 2, y)
    )

def crear_ob(ob, numero_tubo=None):

    altura = random.randint(100, 300)

    ob.append([
        800,
        altura
    ])

    if numero_tubo is not None:

        centro_y = altura + ESPACIO // 2

        if numero_tubo % 2 == 0:

            monedas_lista.append({
                "x": 800 + 20,
                "y": centro_y - 35,
                "tipo": "individual",
                "valor": 1,
                "rect": pygame.Rect(0, 0, 32, 32)
            })

        if numero_tubo % 20 == 0:

            cantidad = random.choice([3, 5])

            monedas_lista.append({
                "x": 800 + 20,
                "y": centro_y + 25,
                "tipo": "saco",
                "valor": cantidad,
                "rect": pygame.Rect(0, 0, 55, 55)
            })

def reiniciar_juego():

    global x_pau, y_pau
    global velocidad_y
    global puntos, game_over
    global ob, monedas_lista

    x_pau = 150
    y_pau = 300

    velocidad_y = 0

    puntos = 0

    ob = []
    monedas_lista = []

    game_over = False

    crear_ob(ob)

reiniciar_juego()

while jugando:

    reloj.tick(60)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if (
                evento.button == 1
                and pantalla_actual == "intro"
                and boton_jugar.collidepoint(evento.pos)
            ):
                reiniciar_juego()
                pantalla_actual = "juego"

        if evento.type == pygame.KEYDOWN:

            if pantalla_actual == "intro":

                if evento.key == pygame.K_SPACE:
                    reiniciar_juego()
                    pantalla_actual = "juego"

            elif game_over:

                if evento.key == pygame.K_SPACE:
                    reiniciar_juego()

            else:

                if evento.key == pygame.K_SPACE:
                    velocidad_y = salto

    if pantalla_actual == "intro":

        ventana.blit(introduccion, (0, 0))

        dibujar_texto(
            "FLAPPY PAU",
            fuente_grande,
            (255, 255, 255),
            ANCHO // 2,
            70
        )

        instrucciones = [
            "Presiona ESPACIO para hacer volar a Pou.",
            "Esquiva las tuberias para conseguir puntos.",
            "Junta monedas mientras avanzas.",
            "Cada 2 tuberias aparece una moneda.",
            "Cada 20 tuberias aparece un puñado especial.",
            "No choques contra las tuberias ni los bordes."
        ]

        for i, linea in enumerate(instrucciones):

            dibujar_texto(
                linea,
                fuente_chica,
                (255, 255, 255),
                ANCHO // 2,
                175 + i * 32
            )

        color_boton = (
            (50, 160, 75)
            if boton_jugar.collidepoint(pygame.mouse.get_pos())
            else (80, 190, 100)
        )

        pygame.draw.rect(
            ventana,
            color_boton,
            boton_jugar,
            border_radius=12
        )

        dibujar_texto(
            "JUGAR",
            fuente,
            (255, 255, 255),
            boton_jugar.centerx,
            boton_jugar.centery - 20
        )

        pygame.display.update()
        continue

    if not game_over:

        velocidad_y += gravedad
        y_pau += velocidad_y

        for tubo in ob:
            tubo[0] -= VELOCIDAD_TUBOS

        if len(ob) > 0 and ob[-1][0] < 450:

            numero_proximo = puntos + len(ob) + 1
            crear_ob(ob, numero_proximo)

        if len(ob) > 0 and ob[0][0] < -ANCHO_TUBO:

            ob.pop(0)
            puntos += 1

        for moneda in monedas_lista:

            moneda["x"] -= VELOCIDAD_TUBOS

            moneda["rect"].topleft = (
                moneda["x"],
                moneda["y"]
            )

        pau_rect = pygame.Rect(
            x_pau + 15,
            y_pau + 15,
            ancho_pau - 30,
            alto_pau - 30
        )

        for tubo in ob:

            x = tubo[0]
            altura = tubo[1]

            tubo_arriba = pygame.Rect(
                x,
                0,
                ANCHO_TUBO,
                altura
            )

            tubo_abajo = pygame.Rect(
                x,
                altura + ESPACIO,
                ANCHO_TUBO,
                ALTO - (altura + ESPACIO)
            )

            if pau_rect.colliderect(tubo_arriba):
                game_over = True

            if pau_rect.colliderect(tubo_abajo):
                game_over = True

        for moneda in monedas_lista[:]:

            if pau_rect.colliderect(moneda["rect"]):

                monedas += moneda["valor"]
                monedas_lista.remove(moneda)

            elif moneda["x"] < -60:

                monedas_lista.remove(moneda)

        if y_pau + alto_pau >= ALTO:
            game_over = True

        if y_pau <= 0:
            game_over = True

    ventana.blit(fondo, (0, 0))

    for tubo in ob:

        x = tubo[0]
        altura = tubo[1]

        ventana.blit(
            tuberia_arriba_img,
            (x, altura - ALTO)
        )

        ventana.blit(
            tuberia_vertical,
            (x, altura + ESPACIO)
        )

    for moneda in monedas_lista:

        if moneda["tipo"] == "individual":

            ventana.blit(
                moneda_img,
                (moneda["x"], moneda["y"])
            )

        else:

            ventana.blit(
                saco_moneda_img,
                (moneda["x"], moneda["y"])
            )

    ventana.blit(
        pau,
        (x_pau, y_pau)
    )

    texto_puntos = fuente.render(
        "Puntos: " + str(puntos),
        True,
        (255, 255, 255)
    )

    ventana.blit(
        texto_puntos,
        (20, 20)
    )

    texto_monedas = fuente.render(
        "Monedas: " + str(monedas),
        True,
        (255, 230, 70)
    )

    ventana.blit(
        texto_monedas,
        (20, 65)
    )

    if game_over:

        pygame.draw.rect(
            ventana,
            (25, 25, 25),
            (100, 170, 600, 180),
            border_radius=18
        )

        dibujar_texto(
            "GAME OVER",
            fuente_grande,
            (255, 80, 80),
            ANCHO // 2,
            185
        )

        dibujar_texto(
            "Puntos conseguidos: " + str(puntos),
            fuente,
            (255, 255, 255),
            ANCHO // 2,
            255
        )

        dibujar_texto(
            "Presiona ESPACIO para reiniciar",
            fuente_chica,
            (255, 255, 255),
            ANCHO // 2,
            305
        )

    pygame.display.update()

pygame.quit()
