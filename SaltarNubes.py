
import pygame
import os
import random

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    archivo = os.path.join(carpeta_raiz, "assets", "minijuegos", "salto_nubes", nombre)
    return archivo

def crear_plataforma(anterior):
    y = anterior.y - random.randint(100, 125)
    desplazamiento = random.randint(140, 230)

    if anterior.centerx < ANCHO // 2:
        direccion = random.choice([-1, 1, 1])
    else:
        direccion = random.choice([-1, -1, 1])

    x = anterior.x + desplazamiento * direccion
    x = max(15, min(x, ANCHO - ANCHO_PLATAFORMA - 15))

    return pygame.Rect(x, y, ANCHO_PLATAFORMA, ALTO_PLATAFORMA)

def obtener_zona(puntos):
    if puntos < 50:
        return 0
    elif puntos < 150:
        return 1
    elif puntos < 300:
        return 2
    elif puntos < 500:
        return 3
    else:
        return 4

def tiempo_juego():
    tiempo_transcurrido = (pygame.time.get_ticks() - tiempo_inicio) // 1000
    return max(0, DURACION_JUEGO - tiempo_transcurrido)

pygame.init()

ANCHO = 800
ALTO = 500

DURACION_JUEGO = 60
pantalla_actual = "instrucciones"
tiempo_inicio = 0

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SaltoPAUUU")

reloj = pygame.time.Clock()

fondos = [
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("resubdelsuelo.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("salto.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("salto.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("spacebar.jpg")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("paraisopau.jpg")).convert(),
        (ANCHO, ALTO)
    )
]

imagen_instrucciones = pygame.transform.scale(
    pygame.image.load(encontrar_archivo("intro.jpg")).convert(),
    (ANCHO, ALTO)
)

pau = pygame.image.load(
    encontrar_archivo("paulanube.png")
).convert_alpha()
pau = pygame.transform.scale(pau, (55, 55))

plataformas_imagenes = [
    pygame.image.load(encontrar_archivo("piedraplat.png")).convert_alpha(),
    pygame.image.load(encontrar_archivo("plataforma.png")).convert_alpha(),
    pygame.image.load(encontrar_archivo("nubepau.png")).convert_alpha()
]

plataformas_imagenes = [
    pygame.transform.scale(imagen, (100, 100))
    for imagen in plataformas_imagenes
]

nube_peligrosa = pygame.image.load(
    encontrar_archivo("nube_peligrosa.png")
).convert_alpha()
nube_peligrosa = pygame.transform.scale(nube_peligrosa, (100, 100))

ANCHO_PAU = 55
ALTO_PAU = 55

ANCHO_PLATAFORMA = 100
ALTO_PLATAFORMA = 100

MARGEN_SUPERIOR_PLAT = 35
MARGEN_LATERAL_PLAT = 15
MARGEN_PIES_PAU = 8

ANCHO_BARRA = 220
ALTO_BARRA = 20

fuente = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 30)
fuente_grande = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 48)
fuente_barra = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 26)

boton_jugar = pygame.Rect(300, 390, 200, 60)
color_boton = (80, 190, 100)
color_boton_hover = (50, 160, 75)

x_pau = ANCHO // 2
y_pau = ALTO - 150

velocidad_x = 0
velocidad_y = 0
gravedad = 0.4
salto = -14

plataformas = [
    pygame.Rect(
        ANCHO // 2 - 50,
        ALTO - 70,
        ANCHO_PLATAFORMA,
        ALTO_PLATAFORMA
    )
]

for i in range(8):
    plataformas.append(crear_plataforma(plataformas[-1]))

nubes_peligrosas = []

puntos = 0
record = 0
zona_anterior = 0

jugando = True
game_over = False

while jugando:

    reloj.tick(60)

    if pantalla_actual == "juego" and not game_over:
        tiempo_restante = tiempo_juego()

        if tiempo_restante <= 0:
            game_over = True
    elif pantalla_actual == "instrucciones":
        tiempo_restante = DURACION_JUEGO
    else:
        tiempo_restante = tiempo_juego()

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1 and pantalla_actual == "instrucciones":
                if boton_jugar.collidepoint(evento.pos):
                    pantalla_actual = "juego"
                    tiempo_inicio = pygame.time.get_ticks()

        if evento.type == pygame.KEYDOWN:

            if pantalla_actual == "juego" and not game_over:

                if evento.key == pygame.K_LEFT:
                    velocidad_x = -5

                if evento.key == pygame.K_RIGHT:
                    velocidad_x = 5

            if evento.key == pygame.K_r and game_over:

                x_pau = ANCHO // 2
                y_pau = ALTO - 150

                velocidad_x = 0
                velocidad_y = 0
                puntos = 0
                zona_anterior = 0
                tiempo_inicio = pygame.time.get_ticks()

                plataformas = [
                    pygame.Rect(
                        ANCHO // 2 - 50,
                        ALTO - 70,
                        ANCHO_PLATAFORMA,
                        ALTO_PLATAFORMA
                    )
                ]

                for i in range(8):
                    plataformas.append(crear_plataforma(plataformas[-1]))

                nubes_peligrosas = []
                game_over = False

        if evento.type == pygame.KEYUP:

            if evento.key == pygame.K_LEFT and velocidad_x < 0:
                velocidad_x = 0

            if evento.key == pygame.K_RIGHT and velocidad_x > 0:
                velocidad_x = 0

    if pantalla_actual == "instrucciones":

        ventana.blit(imagen_instrucciones, (0, 0))

        titulo = fuente_grande.render(
            "SKY PAU", True, (255, 255, 255)
        )

        ventana.blit(
            titulo,
            (ANCHO // 2 - titulo.get_width() // 2, 35)
        )

        instrucciones = [
        "OBJETIVO: Hacer que PAU salte de plataforma en plataforma",
        "evitando que se muera. Para mover",
        "a PAU utiliza las flechas tanto izquierda como derecha.",
        "TIP: Agarra los objetos que aparecen en las plataformas!"
        ]

        for i, linea in enumerate(instrucciones):
            texto = fuente.render(
                linea, True, (255, 255, 255)
            )

            ventana.blit(
                texto,
                (ANCHO // 2 - texto.get_width() // 2, 115 + i * 48)
            )

        if boton_jugar.collidepoint(pygame.mouse.get_pos()):
            color_actual = color_boton_hover
        else:
            color_actual = color_boton

        pygame.draw.rect(
            ventana,
            color_actual,
            boton_jugar,
            border_radius=12
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

        pygame.display.update()
        continue

    if not game_over:

        y_anterior = y_pau

        x_pau += velocidad_x
        velocidad_y += gravedad
        y_pau += velocidad_y

        if x_pau < -ANCHO_PAU:
            x_pau = ANCHO

        if x_pau > ANCHO:
            x_pau = -ANCHO_PAU

        rect_pau = pygame.Rect(
            x_pau + 10,
            y_pau + 10,
            ANCHO_PAU - 20,
            ALTO_PAU - 20
        )

        if velocidad_y > 0:

            pies_anterior = y_anterior + ALTO_PAU - MARGEN_PIES_PAU
            pies_actual = y_pau + ALTO_PAU - MARGEN_PIES_PAU

            for plataforma in plataformas:

                superficie = plataforma.top + MARGEN_SUPERIOR_PLAT
                izquierda = plataforma.left + MARGEN_LATERAL_PLAT
                derecha = plataforma.right - MARGEN_LATERAL_PLAT

                if (
                    pies_anterior <= superficie
                    and pies_actual >= superficie
                    and rect_pau.right > izquierda
                    and rect_pau.left < derecha
                ):

                    y_pau = superficie - ALTO_PAU + MARGEN_PIES_PAU
                    velocidad_y = salto
                    puntos += 1
                    break

        if y_pau < ALTO // 2:

            diferencia = ALTO // 2 - y_pau
            y_pau = ALTO // 2

            for plataforma in plataformas:
                plataforma.y += diferencia

            for nube in nubes_peligrosas:
                nube.y += diferencia

        plataformas = [
            plataforma for plataforma in plataformas
            if plataforma.y < ALTO + 100
        ]

        nubes_peligrosas = [
            nube for nube in nubes_peligrosas
            if nube.y < ALTO + 100
        ]

        while plataformas and plataformas[-1].y > -100:

            nueva_plataforma = crear_plataforma(plataformas[-1])
            plataformas.append(nueva_plataforma)

            if obtener_zona(puntos) == 1 and random.random() < 0.90:

                x_nube = random.randint(0, ANCHO - 85)
                y_nube = nueva_plataforma.y + random.randint(35, 100)

                nubes_peligrosas.append(
                    pygame.Rect(x_nube, y_nube, 85, 55)
                )

        zona = obtener_zona(puntos)

        if zona == 1:
            for nube in nubes_peligrosas:
                if rect_pau.colliderect(nube):
                    game_over = True
                    break

        if y_pau > ALTO:
            game_over = True

        if puntos > record:
            record = puntos

    zona = obtener_zona(puntos)

    ventana.blit(fondos[zona], (0, 0))

    if zona == 0:
        imagen_plataforma = plataformas_imagenes[0]
    elif zona == 1:
        imagen_plataforma = plataformas_imagenes[1]
    else:
        imagen_plataforma = plataformas_imagenes[2]

    for plataforma in plataformas:
        ventana.blit(imagen_plataforma, plataforma)

    if zona == 1:
        for nube in nubes_peligrosas:
            ventana.blit(nube_peligrosa, nube)

    ventana.blit(pau, (x_pau, y_pau))

    texto_puntos = fuente.render(
        "Puntos: " + str(puntos), True, (255, 255, 255)
    )
    ventana.blit(texto_puntos, (20, 20))

    texto_record = fuente.render(
        "Record: " + str(record), True, (255, 255, 255)
    )
    ventana.blit(texto_record, (20, 55))

    texto_tiempo = fuente_barra.render(
        "Tiempo: " + str(tiempo_restante) + " s",
        True,
        (255, 255, 255)
    )

    barra_x = ANCHO - ANCHO_BARRA - 20
    barra_y = 55

    ventana.blit(texto_tiempo, (barra_x, 20))

    pygame.draw.rect(
        ventana,
        (45, 45, 45),
        (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
        border_radius=8
    )

    ancho_actual = int(
        ANCHO_BARRA * tiempo_restante / DURACION_JUEGO
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

    nombres_zonas = [
        "Subsuelo",
        "Superficie",
        "Atmósfera",
        "Espacio",
        "Paraíso"
    ]

    texto_zona = fuente.render(
        nombres_zonas[zona], True, (255, 255, 255)
    )

    ventana.blit(
        texto_zona,
        (ANCHO - texto_zona.get_width() - 20, 90)
    )

    if game_over:

        texto = fuente_grande.render(
            "GAME OVER", True, (255, 255, 255)
        )
        ventana.blit(
            texto,
            (ANCHO // 2 - texto.get_width() // 2, 190)
        )

        texto2 = fuente.render(
            "Presiona R para volver a jugar",
            True,
            (255, 255, 255)
        )
        ventana.blit(
            texto2,
            (ANCHO // 2 - texto2.get_width() // 2, 260)
        )

    pygame.display.update()

pygame.quit()