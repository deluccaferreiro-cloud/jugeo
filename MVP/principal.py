import pygame

ancho = 800
alto = 600

# Ahora las necesidades bajan cada 1 segundo
TIEMPO_DISMINUCION = 1000

DURACION_NOCHE = 3000

bano = 100
comer = 100
dormir = 100
jugar = 100

ultimo_descenso = pygame.time.get_ticks()

inicio_noche = 0
modo_noche = False


# ---------------- IMAGENES ----------------

dia = pygame.image.load("dia.png")
noche = pygame.image.load("noche.png")

pou = pygame.image.load("pou.png")
paufeliz = pygame.image.load("paufeliz.png")
paumaso = pygame.image.load("paumaso.png")
paumuerto = pygame.image.load("paumuerto.png")


dia = pygame.transform.smoothscale(
    dia,
    (800, 600)
)

noche = pygame.transform.smoothscale(
    noche,
    (800, 600)
)


# ---------------- ESCALAR PERSONAJE ----------------

def escalar_personaje(imagen, tamaño_maximo):

    ancho_original, alto_original = imagen.get_size()

    escala = min(
        tamaño_maximo / ancho_original,
        tamaño_maximo / alto_original
    )

    nuevo_ancho = int(ancho_original * escala)
    nuevo_alto = int(alto_original * escala)

    return pygame.transform.smoothscale(
        imagen,
        (nuevo_ancho, nuevo_alto)
    )


tamaño_pou = 220

pou = escalar_personaje(
    pou,
    tamaño_pou
)

paufeliz = escalar_personaje(
    paufeliz,
    tamaño_pou
)

paumaso = escalar_personaje(
    paumaso,
    tamaño_pou
)

paumuerto = escalar_personaje(
    paumuerto,
    tamaño_pou
)


# ---------------- FUENTES ----------------

fuente = pygame.font.Font(None, 28)


# ---------------- BOTONES ----------------

boton_bano = pygame.Rect(
    70,
    210,
    150,
    55
)

boton_comer = pygame.Rect(
    580,
    210,
    150,
    55
)

boton_dormir = pygame.Rect(
    70,
    430,
    150,
    55
)

boton_jugar = pygame.Rect(
    580,
    430,
    150,
    55
)


# ---------------- BARRAS ----------------

barra_bano = pygame.Rect(
    30,
    65,
    170,
    25
)

barra_comer = pygame.Rect(
    220,
    65,
    170,
    25
)

barra_dormir = pygame.Rect(
    410,
    65,
    170,
    25
)

barra_jugar = pygame.Rect(
    600,
    65,
    170,
    25
)


# ---------------- DIBUJAR BARRA ----------------

def dibujar_barra(ventana, rectangulo, valor):

    # Fondo de la barra
    pygame.draw.rect(
        ventana,
        (220, 220, 220),
        rectangulo
    )

    # Parte llena
    ancho_barra = int(
        rectangulo.width * valor / 100
    )

    parte_llena = pygame.Rect(
        rectangulo.x,
        rectangulo.y,
        ancho_barra,
        rectangulo.height
    )

    pygame.draw.rect(
        ventana,
        (100, 200, 100),
        parte_llena
    )

    # Borde
    pygame.draw.rect(
        ventana,
        (255, 255, 255),
        rectangulo,
        2
    )


# ---------------- DIBUJAR BOTON ----------------

def dibujar_boton(ventana, rectangulo, texto):

    # Botón blanco
    pygame.draw.rect(
        ventana,
        (255, 255, 255),
        rectangulo
    )

    # Borde negro
    pygame.draw.rect(
        ventana,
        (0, 0, 0),
        rectangulo,
        2
    )

    # Texto negro
    texto_renderizado = fuente.render(
        texto,
        True,
        (0, 0, 0)
    )

    posicion_texto = texto_renderizado.get_rect(
        center=rectangulo.center
    )

    ventana.blit(
        texto_renderizado,
        posicion_texto
    )


# ---------------- PERSONAJE ----------------

def obtener_personaje():

    if (
        bano <= 5
        or comer <= 5
        or dormir <= 5
        or jugar <= 5
    ):
        return paumuerto

    if (
        bano <= 40
        or comer <= 40
        or dormir <= 40
        or jugar <= 40
    ):
        return pou

    if (
        bano < 95
        or comer < 95
        or dormir < 95
        or jugar < 95
    ):
        return paumaso

    return paufeliz


# ---------------- CLICKS ----------------

def manejar_click(posicion):

    global bano
    global comer
    global dormir
    global jugar
    global modo_noche
    global inicio_noche

    if boton_bano.collidepoint(posicion):

        bano = min(
            100,
            bano + 10
        )

    elif boton_comer.collidepoint(posicion):

        comer = min(
            100,
            comer + 10
        )

    elif boton_dormir.collidepoint(posicion):

        dormir = min(
            100,
            dormir + 10
        )

        modo_noche = True

        inicio_noche = pygame.time.get_ticks()

    elif boton_jugar.collidepoint(posicion):

        jugar = min(
            100,
            jugar + 10
        )


# ---------------- ACTUALIZAR NECESIDADES ----------------

def actualizar_necesidades():

    global bano
    global comer
    global dormir
    global jugar
    global ultimo_descenso
    global modo_noche

    tiempo_actual = pygame.time.get_ticks()

    # Las barras bajan cada 1 segundo
    if tiempo_actual - ultimo_descenso >= TIEMPO_DISMINUCION:

        bano = max(
            0,
            bano - 1
        )

        comer = max(
            0,
            comer - 1
        )

        dormir = max(
            0,
            dormir - 1
        )

        jugar = max(
            0,
            jugar - 1
        )

        ultimo_descenso = tiempo_actual

    # Terminar modo noche
    if modo_noche:

        if tiempo_actual - inicio_noche >= DURACION_NOCHE:

            modo_noche = False


# ---------------- PANTALLA PRINCIPAL ----------------

def principal():

    ventana = pygame.display.get_surface()

    actualizar_necesidades()

    # ---------------- FONDO ----------------

    # Ahora el fondo es SIEMPRE negro
    ventana.fill((0, 0, 0))


    # ---------------- BARRAS ----------------

    # Solamente se muestran las barras.
    # Ya no tienen nombres ni números.

    dibujar_barra(
        ventana,
        barra_bano,
        bano
    )

    dibujar_barra(
        ventana,
        barra_comer,
        comer
    )

    dibujar_barra(
        ventana,
        barra_dormir,
        dormir
    )

    dibujar_barra(
        ventana,
        barra_jugar,
        jugar
    )


    # ---------------- BOTONES ----------------

    dibujar_boton(
        ventana,
        boton_bano,
        "BAÑO"
    )

    dibujar_boton(
        ventana,
        boton_comer,
        "COMER"
    )

    dibujar_boton(
        ventana,
        boton_dormir,
        "DORMIR"
    )

    dibujar_boton(
        ventana,
        boton_jugar,
        "JUGAR"
    )


    # ---------------- POU ----------------

    personaje_actual = obtener_personaje()

    posicion_pou = personaje_actual.get_rect(
        center=(400, 315)
    )

    ventana.blit(
        personaje_actual,
        posicion_pou
    )