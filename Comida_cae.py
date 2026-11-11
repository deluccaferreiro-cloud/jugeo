
import pygame
import random
import os

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    return os.path.join(
        carpeta_raiz,
        "assets",
        "minijuegos",
        "comidaquecae",
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

ANCHO = 800
ALTO = 500

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Food droppp")

reloj = pygame.time.Clock()

jugando = True
game_over = False
pantalla_actual = "instrucciones"
motivo_game_over = ""

fondo = cargar_imagen("comida.png", (ANCHO, ALTO), False)
introduccion = cargar_imagen("intro.jpg", (ANCHO, ALTO), False)

ruta_fuente = encontrar_archivo("CatCafe.ttf")

fuente = pygame.font.Font(ruta_fuente, 32)
fuente_grande = pygame.font.Font(ruta_fuente, 54)
fuente_chica = pygame.font.Font(ruta_fuente, 22)
fuente_titulo = pygame.font.Font(ruta_fuente, 64)

pau_masticando = cargar_imagen("paumasticando.png", (100, 100))
pau_agarrar_comida = cargar_imagen("paubocaabiertaparaM2.png", (100, 100))

ANCHO_PAU = 100
ALTO_PAU = 100

x_pau = 350
y_pau = 400
velocidad_pau = 7

puntaje_comidita = 0
alimentos_perdidos = 0
ALIMENTOS_PERDIDOS_MAX = 8

comida_lista = []

contador_comida = 0
contador_comiendo = 0
esta_comiendo = False

ANCHO_COMIDA = 48
ALTO_COMIDA = 48

PUNTOS_DIFICULTAD_MAX = 80

VELOCIDAD_INICIAL = 4
VELOCIDAD_MAXIMA = 9.5

INTERVALO_INICIAL = 45
INTERVALO_MINIMO = 20

PROB_BUENA_INICIAL = 0.70
PROB_BUENA_MINIMA = 0.40

velocidad_comida = VELOCIDAD_INICIAL
intervalo_comida = INTERVALO_INICIAL

boton_jugar = pygame.Rect(300, 405, 200, 60)

alimentos_buenos = [
    "crumblcookie.png",
    "helado.png",
    "huevo.png",
    "sushi.png",
    "tortilla.png",
    "manzana.png",
    "cupcake.png",
    "banana.png"
]

alimentos_malos = [
    "cd.png",
    "destornillador.png",
    "router.png",
    "ram.png",
    "zapatillas_rotas.png",
    "pendrive.png",
    "tornillo.png"
]

imagenes_buenas = {
    nombre: cargar_imagen(nombre, (ANCHO_COMIDA, ALTO_COMIDA))
    for nombre in alimentos_buenos
}

imagenes_malas = {
    nombre: cargar_imagen(nombre, (ANCHO_COMIDA, ALTO_COMIDA))
    for nombre in alimentos_malos
}

def dificultad():
    return min(1.0, puntaje_comidita / PUNTOS_DIFICULTAD_MAX)

def nivel_actual():
    return 1 + int(dificultad() * 9)

def probabilidad_buena():
    return PROB_BUENA_INICIAL - (
        PROB_BUENA_INICIAL - PROB_BUENA_MINIMA
    ) * dificultad()

def reiniciar_juego():
    global x_pau, puntaje_comidita
    global alimentos_perdidos, comida_lista
    global contador_comida, velocidad_comida
    global intervalo_comida, contador_comiendo
    global esta_comiendo, game_over, motivo_game_over

    x_pau = 350
    puntaje_comidita = 0
    alimentos_perdidos = 0

    comida_lista = []

    contador_comida = 0
    velocidad_comida = VELOCIDAD_INICIAL
    intervalo_comida = INTERVALO_INICIAL
    contador_comiendo = 0
    esta_comiendo = False

    motivo_game_over = ""
    game_over = False

def crear_comida():
    es_buena = random.random() < probabilidad_buena()

    if es_buena:
        nombre = random.choice(alimentos_buenos)
        tipo = "buena"
    else:
        nombre = random.choice(alimentos_malos)
        tipo = "mala"

    return {
        "x": random.randint(0, ANCHO - ANCHO_COMIDA),
        "y": -ALTO_COMIDA,
        "tipo": tipo,
        "nombre": nombre,
        "rect": pygame.Rect(
            0, -ALTO_COMIDA,
            ANCHO_COMIDA, ALTO_COMIDA
        )
    }

def dibujar_texto(texto, fuente_usada, color, centro_x, y):
    superficie = fuente_usada.render(texto, True, color)
    ventana.blit(
        superficie,
        (centro_x - superficie.get_width() // 2, y)
    )

reiniciar_juego()

while jugando:
    reloj.tick(60)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if (
                evento.button == 1
                and pantalla_actual == "instrucciones"
                and boton_jugar.collidepoint(evento.pos)
            ):
                reiniciar_juego()
                pantalla_actual = "juego"

        if evento.type == pygame.KEYDOWN:

            if pantalla_actual == "instrucciones":
                if evento.key == pygame.K_SPACE:
                    reiniciar_juego()
                    pantalla_actual = "juego"

            elif game_over:
                if evento.key == pygame.K_SPACE:
                    reiniciar_juego()

    if pantalla_actual == "instrucciones":

        ventana.blit(introduccion, (0, 0))

        dibujar_texto(
            "FOOD DROP",
            fuente_titulo,
            (0, 0, 0),
            ANCHO // 2,
            35
        )

        instrucciones = [
            "Evita que PAU coma los alimentos malos",
            "moviendolo con las flechas izquierda y derecha.",
            "CUIDADO: si dejas caer 8 alimentos buenos, perdés el juego.",
            "TIP: intenta ser rapido porque despues los alimentos van a caer mas rapido",
            "Cada vez cae mas comida y hay mas alimentos malos."
        ]

        for i, linea in enumerate(instrucciones):
            dibujar_texto(
                linea,
                fuente_chica,
                (0, 0, 0),
                ANCHO // 2,
                145 + i * 35
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
            boton_jugar.centery - 17
        )

        pygame.display.update()
        continue

    if not game_over:

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_LEFT]:
            x_pau -= velocidad_pau

        if teclas[pygame.K_RIGHT]:
            x_pau += velocidad_pau

        x_pau = max(0, min(x_pau, ANCHO - ANCHO_PAU))

        d = dificultad()

        velocidad_comida = (
            VELOCIDAD_INICIAL + (VELOCIDAD_MAXIMA - VELOCIDAD_INICIAL) * d
        )

        intervalo_comida = max(
            INTERVALO_MINIMO,
            int(INTERVALO_INICIAL - (INTERVALO_INICIAL - INTERVALO_MINIMO) * d)
        )

        contador_comida += 1

        if contador_comida >= intervalo_comida:
            contador_comida = 0
            comida_lista.append(crear_comida())

        pau_rect = pygame.Rect(
            x_pau + 10,
            y_pau + 10,
            ANCHO_PAU - 20,
            ALTO_PAU - 20
        )

        for comida in comida_lista[:]:

            comida["y"] += velocidad_comida

            comida["rect"].topleft = (
                comida["x"],
                int(comida["y"])
            )

            if pau_rect.colliderect(comida["rect"]):

                if comida["tipo"] == "buena":
                    puntaje_comidita += 1
                    contador_comiendo = 15
                    esta_comiendo = True
                else:
                    game_over = True
                    motivo_game_over = "Atrapaste comida mala."

                comida_lista.remove(comida)

                if game_over:
                    break

            elif comida["y"] >= ALTO:

                if comida["tipo"] == "buena":
                    alimentos_perdidos += 1

                    if alimentos_perdidos >= ALIMENTOS_PERDIDOS_MAX:
                        game_over = True
                        motivo_game_over = "Dejaste caer 8 alimentos buenos."

                comida_lista.remove(comida)

                if game_over:
                    break

        if contador_comiendo > 0:
            contador_comiendo -= 1
            esta_comiendo = True
        else:
            esta_comiendo = False

    ventana.blit(fondo, (0, 0))

    for comida in comida_lista:

        if comida["tipo"] == "buena":
            imagen = imagenes_buenas[comida["nombre"]]
        else:
            imagen = imagenes_malas[comida["nombre"]]

        ventana.blit(
            imagen,
            (comida["x"], int(comida["y"]))
        )

    if esta_comiendo:
        ventana.blit(pau_masticando, (x_pau, y_pau))
    else:
        ventana.blit(pau_agarrar_comida, (x_pau, y_pau))

    texto_puntos = fuente.render(
        "Puntos: " + str(puntaje_comidita),
        True,
        (0, 0, 0)
    )
    ventana.blit(texto_puntos, (20, 15))

    texto_nivel = fuente_chica.render(
        "Nivel: " + str(nivel_actual()),
        True,
        (0, 0, 0)
    )
    ventana.blit(texto_nivel, (20, 55))

    texto_perdidos = fuente_chica.render(
        "Alimentos perdidos: "
        + str(alimentos_perdidos)
        + "/"
        + str(ALIMENTOS_PERDIDOS_MAX),
        True,
        (0, 0, 0)
    )
    ventana.blit(texto_perdidos, (20, 90))

    if game_over:

        pygame.draw.rect(
            ventana,
            (25, 25, 25),
            (100, 140, 600, 230),
            border_radius=18
        )

        dibujar_texto(
            "GAME OVER",
            fuente_grande,
            (255, 80, 80),
            ANCHO // 2,
            155
        )

        dibujar_texto(
            "Puntos conseguidos: " + str(puntaje_comidita),
            fuente,
            (255, 255, 255),
            ANCHO // 2,
            225
        )

        dibujar_texto(
            motivo_game_over,
            fuente_chica,
            (255, 255, 255),
            ANCHO // 2,
            270
        )

        dibujar_texto(
            "Presiona ESPACIO para reiniciar",
            fuente_chica,
            (255, 255, 255),
            ANCHO // 2,
            315
        )

    pygame.display.update()

pygame.quit()