import pygame
import minijuegos.Flappy_Pau as Flappy_Pau


pygame.init()


ancho = 800
alto = 600


TIEMPO_DISMINUCION = 1000
DURACION_NOCHE = 3000


baño = 100
comer = 100
dormir = 100
jugar = 100


ultimo_descenso = pygame.time.get_ticks()
ultimo_incremento_dormir = pygame.time.get_ticks()

inicio_noche = 0
modo_noche = False


mensaje_temporal = ""
tiempo_mensaje = 0


habitacion_actual = 0

nombres_habitaciones = [
    "BAÑO",
    "SALA DE ESTAR",
    "HABITACIÓN",
    "COCINA"
]


subpantalla = "normal"


# ============================================================
# FONDOS
# ============================================================

try:

    fondo_bano = pygame.transform.smoothscale(
        pygame.image.load("bano.png"),
        (ancho, alto)
    )

    fondo_sala = pygame.transform.smoothscale(
        pygame.image.load("principal.png"),
        (ancho, alto)
    )

    fondo_habitacion = pygame.transform.smoothscale(
        pygame.image.load("habitacion.png"),
        (ancho, alto)
    )

    fondo_cocina = pygame.transform.smoothscale(
        pygame.image.load("cocina.png"),
        (ancho, alto)
    )

except:

    fondo_bano = pygame.Surface((ancho, alto))
    fondo_bano.fill((173, 216, 230))

    fondo_sala = pygame.Surface((ancho, alto))
    fondo_sala.fill((240, 230, 140))

    fondo_habitacion = pygame.Surface((ancho, alto))
    fondo_habitacion.fill((230, 230, 250))

    fondo_cocina = pygame.Surface((ancho, alto))
    fondo_cocina.fill((255, 218, 185))


noche = pygame.Surface((ancho, alto))
noche.fill((20, 20, 50))


# ============================================================
# PERSONAJE
# ============================================================

def escalar_personaje(imagen, tamaño_maximo):

    ancho_orig, alto_orig = imagen.get_size()

    escala = min(
        tamaño_maximo / ancho_orig,
        tamaño_maximo / alto_orig
    )

    return pygame.transform.smoothscale(
        imagen,
        (
            int(ancho_orig * escala),
            int(alto_orig * escala)
        )
    )


tamaño_pou = 220


try:

    pou = escalar_personaje(
        pygame.image.load("pou.png"),
        tamaño_pou
    )

    paufeliz = escalar_personaje(
        pygame.image.load("paufeliz.png"),
        tamaño_pou
    )

    paumaso = escalar_personaje(
        pygame.image.load("paumaso.png"),
        tamaño_pou
    )

    paumuerto = escalar_personaje(
        pygame.image.load("paumuerto.png"),
        tamaño_pou
    )

    paudormido = escalar_personaje(
        pygame.image.load("poudormido.png"),
        tamaño_pou
    )

except:

    pou = pygame.Surface((150, 150))
    pou.fill((139, 69, 19))

    paufeliz = pou
    paumaso = pou
    paumuerto = pou
    paudormido = pou


# ============================================================
# FUENTES
# ============================================================

fuente = pygame.font.Font(None, 28)
fuente_grande = pygame.font.Font(None, 36)
fuente_numero = pygame.font.Font(None, 22)


# ============================================================
# FLECHAS
# ============================================================

flecha_izquierda = pygame.Rect(
    10, 270, 50, 60
)

flecha_derecha = pygame.Rect(
    740, 270, 50, 60
)


# ============================================================
# BOTONES
# ============================================================

boton_banar = pygame.Rect(
    325, 480, 150, 50
)

boton_minijuegos = pygame.Rect(
    230, 480, 160, 50
)

boton_tienda = pygame.Rect(
    410, 480, 160, 50
)

boton_dormir = pygame.Rect(
    325, 480, 150, 50
)

boton_comidas = pygame.Rect(
    325, 480, 150, 50
)


# ============================================================
# MENÚ DE MINIJUEGOS
# ============================================================

botones_minijuegos = [

    pygame.Rect(
        300,
        150 + i * 65,
        200,
        45
    )

    for i in range(5)

]


boton_volver_minijuegos = pygame.Rect(
    20, 20, 100, 40
)


# ============================================================
# BARRAS
# ============================================================

pos_y_barras = 65


barra_baño = pygame.Rect(
    30, pos_y_barras, 170, 20
)

barra_comer = pygame.Rect(
    220, pos_y_barras, 170, 20
)

barra_dormir = pygame.Rect(
    410, pos_y_barras, 170, 20
)

barra_jugar = pygame.Rect(
    600, pos_y_barras, 170, 20
)


# ============================================================
# POSICIÓN DE PAU
# ============================================================

posicion_pou = (400, 320)

rect_pou = pygame.Rect(
    290,
    210,
    220,
    220
)


# ============================================================
# OBJETOS DE COMIDA
# ============================================================

comidas = [

    {
        "nombre": "Bife",
        "archivo": "objetos/bife.png",
        "valor": 30
    },

    {
        "nombre": "Caramelo",
        "archivo": "objetos/caramelo.png",
        "valor": 10
    },

    {
        "nombre": "Chocolate",
        "archivo": "objetos/chocolate.png",
        "valor": 15
    },

    {
        "nombre": "Pizza",
        "archivo": "objetos/pizza.png",
        "valor": 25
    },

    {
        "nombre": "Sanguche",
        "archivo": "objetos/sanguche.png",
        "valor": 20
    },

    {
        "nombre": "Sushi",
        "archivo": "objetos/sushi.png",
        "valor": 35
    }

]


# Cargar imágenes de las comidas

for comida in comidas:

    try:

        comida["imagen"] = pygame.image.load(
            comida["archivo"]
        ).convert_alpha()

        comida["imagen"] = pygame.transform.smoothscale(
            comida["imagen"],
            (70, 70)
        )

    except:

        comida["imagen"] = pygame.Surface(
            (70, 70),
            pygame.SRCALPHA
        )

        comida["imagen"].fill(
            (200, 100, 100)
        )


# ============================================================
# INVENTARIO DE COMIDA
# ============================================================

inventario_rect = pygame.Rect(
    100,
    100,
    600,
    400
)


boton_volver_comidas = pygame.Rect(
    20,
    20,
    100,
    40
)


# ============================================================
# SISTEMA DE ARRASTRAR COMIDA
# ============================================================

comida_arrastrando = None

posicion_comida_arrastrando = (0, 0)


# ============================================================
# OBJETOS DEL BAÑO
# ============================================================

try:

    imagen_jabon = pygame.image.load(
        "objetos/jabon.png"
    ).convert_alpha()

    imagen_espuma = pygame.image.load(
        "objetos/espuma.png"
    ).convert_alpha()

    imagen_ducha = pygame.image.load(
        "objetos/ducha.png"
    ).convert_alpha()

    imagen_toalla = pygame.image.load(
        "objetos/toalla.png"
    ).convert_alpha()


    imagen_jabon = pygame.transform.smoothscale(
        imagen_jabon,
        (90, 90)
    )

    imagen_espuma = pygame.transform.smoothscale(
        imagen_espuma,
        (230, 230)
    )

    imagen_ducha = pygame.transform.smoothscale(
        imagen_ducha,
        (100, 100)
    )

    imagen_toalla = pygame.transform.smoothscale(
        imagen_toalla,
        (100, 100)
    )

except:

    imagen_jabon = pygame.Surface(
        (90, 90),
        pygame.SRCALPHA
    )

    imagen_jabon.fill(
        (255, 200, 200)
    )


    imagen_espuma = pygame.Surface(
        (230, 230),
        pygame.SRCALPHA
    )

    imagen_espuma.fill(
        (255, 255, 255, 180)
    )


    imagen_ducha = pygame.Surface(
        (100, 100),
        pygame.SRCALPHA
    )

    imagen_ducha.fill(
        (100, 180, 255)
    )


    imagen_toalla = pygame.Surface(
        (100, 100),
        pygame.SRCALPHA
    )

    imagen_toalla.fill(
        (255, 180, 180)
    )


# ============================================================
# ESTADOS DEL BAÑO
# ============================================================

# 0 = esperando jabón
# 1 = Pau enjabonado
# 2 = Pau mojado
# 3 = baño terminado

estado_baño = 0


objeto_baño_arrastrando = None

posicion_objeto_baño = (0, 0)


# Objetos que aparecen abajo durante el baño

rect_jabon = pygame.Rect(
    80,
    480,
    90,
    90
)

rect_ducha = pygame.Rect(
    250,
    480,
    100,
    100
)

rect_toalla = pygame.Rect(
    500,
    480,
    100,
    100
)


# ============================================================
# DIBUJAR BARRAS
# ============================================================

def dibujar_barra(
    ventana,
    rectangulo,
    nombre,
    valor
):

    pygame.draw.rect(
        ventana,
        (220, 220, 220),
        rectangulo
    )

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

    pygame.draw.rect(
        ventana,
        (0, 0, 0),
        rectangulo,
        2
    )

    texto_nombre = fuente.render(
        nombre,
        True,
        (0, 0, 0)
    )

    ventana.blit(
        texto_nombre,
        (
            rectangulo.centerx -
            texto_nombre.get_width() // 2,
            rectangulo.y - 22
        )
    )

    texto_numero = fuente_numero.render(
        str(valor),
        True,
        (0, 0, 0)
    )

    ventana.blit(
        texto_numero,
        (
            rectangulo.centerx -
            texto_numero.get_width() // 2,
            rectangulo.bottom + 2
        )
    )


# ============================================================
# DIBUJAR BOTÓN
# ============================================================

def dibujar_boton(
    ventana,
    rectangulo,
    texto
):

    pygame.draw.rect(
        ventana,
        (255, 255, 255),
        rectangulo
    )

    pygame.draw.rect(
        ventana,
        (0, 0, 0),
        rectangulo,
        2
    )

    texto_render = fuente.render(
        texto,
        True,
        (0, 0, 0)
    )

    ventana.blit(
        texto_render,
        texto_render.get_rect(
            center=rectangulo.center
        )
    )


# ============================================================
# PERSONAJE SEGÚN NECESIDADES
# ============================================================

def obtener_personaje():

    if (
        baño <= 5
        or comer <= 5
        or dormir <= 5
        or jugar <= 5
    ):

        return paumuerto


    if (
        baño <= 40
        or comer <= 40
        or dormir <= 40
        or jugar <= 40
    ):

        return pou


    if (
        baño < 95
        or comer < 95
        or dormir < 95
        or jugar < 95
    ):

        return paumaso


    return paufeliz


# ============================================================
# INVENTARIO DE COMIDA
# ============================================================

def dibujar_inventario_comidas(ventana):

    ventana.fill(
        (245, 220, 180)
    )

    titulo = fuente_grande.render(
        "INVENTARIO DE COMIDA",
        True,
        (0, 0, 0)
    )

    ventana.blit(
        titulo,
        (
            ancho // 2 -
            titulo.get_width() // 2,
            40
        )
    )


    dibujar_boton(
        ventana,
        boton_volver_comidas,
        "Volver"
    )


    for i, comida in enumerate(comidas):

        columna = i % 3
        fila = i // 3

        x = 150 + columna * 190
        y = 130 + fila * 170

        rect = pygame.Rect(
            x,
            y,
            100,
            100
        )

        comida["rect"] = rect


        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            rect
        )

        pygame.draw.rect(
            ventana,
            (0, 0, 0),
            rect,
            2
        )


        imagen = comida["imagen"]

        ventana.blit(
            imagen,
            imagen.get_rect(
                center=rect.center
            )
        )


        nombre = fuente.render(
            comida["nombre"],
            True,
            (0, 0, 0)
        )

        ventana.blit(
            nombre,
            (
                rect.centerx -
                nombre.get_width() // 2,
                rect.bottom + 5
            )
        )


        valor = fuente_numero.render(
            "+" + str(comida["valor"]),
            True,
            (0, 120, 0)
        )

        ventana.blit(
            valor,
            (
                rect.centerx -
                valor.get_width() // 2,
                rect.bottom + 30
            )
        )


# ============================================================
# DIBUJAR BAÑO
# ============================================================

def dibujar_baño(ventana):

    # Dibujamos los objetos disponibles

    if estado_baño == 0:

        ventana.blit(
            imagen_jabon,
            rect_jabon
        )

        texto = fuente.render(
            "Arrastra el jabón sobre Pau",
            True,
            (0, 0, 0)
        )

        ventana.blit(
            texto,
            (
                50,
                430
            )
        )


    elif estado_baño == 1:

        ventana.blit(
            imagen_ducha,
            rect_ducha
        )

        texto = fuente.render(
            "Ahora usa la ducha",
            True,
            (0, 0, 0)
        )

        ventana.blit(
            texto,
            (
                60,
                430
            )
        )


    elif estado_baño == 2:

        ventana.blit(
            imagen_toalla,
            rect_toalla
        )

        texto = fuente.render(
            "Ahora seca a Pau",
            True,
            (0, 0, 0)
        )

        ventana.blit(
            texto,
            (
                60,
                430
            )
        )


    elif estado_baño == 3:

        texto = fuente_grande.render(
            "¡Pau está limpio!",
            True,
            (0, 130, 0)
        )

        ventana.blit(
            texto,
            (
                ancho // 2 -
                texto.get_width() // 2,
                470
            )
        )


    # Mostrar espuma cuando Pau está enjabonado

    if estado_baño >= 1 and estado_baño < 3:

        ventana.blit(
            imagen_espuma,
            imagen_espuma.get_rect(
                center=posicion_pou
            )
        )


# ============================================================
# MANEJAR CLICK
# ============================================================

def manejar_click(posicion):

    global baño
    global comer
    global dormir
    global jugar

    global modo_noche
    global inicio_noche

    global habitacion_actual
    global subpantalla

    global mensaje_temporal
    global tiempo_mensaje

    global comida_arrastrando
    global posicion_comida_arrastrando

    global objeto_baño_arrastrando
    global posicion_objeto_baño

    global estado_baño


    # ========================================================
    # MINIJUEGOS
    # ========================================================

    if subpantalla == "minijuegos":

        if boton_volver_minijuegos.collidepoint(posicion):

            subpantalla = "normal"

            return


        for i, b in enumerate(
            botones_minijuegos
        ):

            if b.collidepoint(posicion):

                if i == 0:

                    Flappy_Pau.ejecutar_flappy()

                    subpantalla = "minijuegos"

                    return

                else:

                    mensaje_temporal = (
                        f"Minijuego {i + 1} en desarrollo"
                    )

                    tiempo_mensaje = (
                        pygame.time.get_ticks()
                    )


        return


    # ========================================================
    # INVENTARIO
    # ========================================================

    if subpantalla == "comidas":

        if boton_volver_comidas.collidepoint(posicion):

            subpantalla = "normal"

            return


        for comida in comidas:

            if comida["rect"].collidepoint(posicion):

                comida_arrastrando = comida

                posicion_comida_arrastrando = posicion

                return


        return


    # ========================================================
    # CAMBIO DE HABITACIÓN
    # ========================================================

    if flecha_izquierda.collidepoint(posicion):

        habitacion_actual = (
            habitacion_actual - 1
        ) % 4

        return


    elif flecha_derecha.collidepoint(posicion):

        habitacion_actual = (
            habitacion_actual + 1
        ) % 4

        return


    # ========================================================
    # BAÑO
    # ========================================================

    if habitacion_actual == 0:

        if estado_baño == 0:

            if rect_jabon.collidepoint(posicion):

                objeto_baño_arrastrando = "jabon"

                posicion_objeto_baño = posicion

                return


        elif estado_baño == 1:

            if rect_ducha.collidepoint(posicion):

                objeto_baño_arrastrando = "ducha"

                posicion_objeto_baño = posicion

                return


        elif estado_baño == 2:

            if rect_toalla.collidepoint(posicion):

                objeto_baño_arrastrando = "toalla"

                posicion_objeto_baño = posicion

                return


    # ========================================================
    # SALA
    # ========================================================

    elif habitacion_actual == 1:

        if boton_minijuegos.collidepoint(posicion):

            subpantalla = "minijuegos"


        elif boton_tienda.collidepoint(posicion):

            mensaje_temporal = (
                "Tienda todavía no disponible"
            )

            tiempo_mensaje = (
                pygame.time.get_ticks()
            )


    # ========================================================
    # HABITACIÓN
    # ========================================================

    elif habitacion_actual == 2:

        if (
            boton_dormir.collidepoint(posicion)
            and not modo_noche
        ):

            modo_noche = True

            inicio_noche = (
                pygame.time.get_ticks()
            )


    # ========================================================
    # COCINA
    # ========================================================

    elif habitacion_actual == 3:

        if boton_comidas.collidepoint(posicion):

            subpantalla = "comidas"

            return


# ============================================================
# SOLTAR OBJETOS
# ============================================================

def manejar_soltar(posicion):

    global mensaje_temporal
    global tiempo_mensaje


    global comida_arrastrando
    global objeto_baño_arrastrando

    global posicion_comida_arrastrando
    global posicion_objeto_baño

    global comer
    global baño

    global estado_baño


    # ========================================================
    # COMIDA
    # ========================================================

    if comida_arrastrando is not None:

        # Si se soltó encima de Pau

        if rect_pou.collidepoint(posicion):

            valor = comida_arrastrando["valor"]

            comer = min(
                100,
                comer + valor
            )

            mensaje_temporal = (
                f"¡Pau comió {comida_arrastrando['nombre']}! "
                f"+{valor}"
            )

        comida_arrastrando = None

        return


    # ========================================================
    # BAÑO
    # ========================================================

    if objeto_baño_arrastrando is not None:

        if rect_pou.collidepoint(posicion):

            if (
                objeto_baño_arrastrando == "jabon"
                and estado_baño == 0
            ):

                estado_baño = 1


            elif (
                objeto_baño_arrastrando == "ducha"
                and estado_baño == 1
            ):

                estado_baño = 2


            elif (
                objeto_baño_arrastrando == "toalla"
                and estado_baño == 2
            ):

                estado_baño = 3

                baño = min(
                    100,
                    baño + 25
                )


        objeto_baño_arrastrando = None

        return


# ============================================================
# ACTUALIZAR NECESIDADES
# ============================================================

def actualizar_necesidades():

    global baño
    global comer
    global dormir
    global jugar

    global ultimo_descenso
    global ultimo_incremento_dormir

    global modo_noche


    tiempo_actual = pygame.time.get_ticks()


    if (
        tiempo_actual - ultimo_descenso
        >= TIEMPO_DISMINUCION
    ):

        baño = max(
            0,
            baño - 1
        )

        comer = max(
            0,
            comer - 1
        )

        jugar = max(
            0,
            jugar - 1
        )


        if not modo_noche:

            dormir = max(
                0,
                dormir - 1
            )


        ultimo_descenso = tiempo_actual


    if modo_noche:

        if (
            tiempo_actual -
            ultimo_incremento_dormir
            >= 100
        ):

            dormir = min(
                100,
                dormir + 2
            )

            ultimo_incremento_dormir = (
                tiempo_actual
            )


        if (
            tiempo_actual -
            inicio_noche
            >= DURACION_NOCHE
        ):

            modo_noche = False


# ============================================================
# PRINCIPAL
# ============================================================

def principal():

    ventana = pygame.display.get_surface()


    actualizar_necesidades()


    # ========================================================
    # INVENTARIO DE COMIDAS
    # ========================================================

    if subpantalla == "comidas":

        dibujar_inventario_comidas(
            ventana
        )


        # Mostrar comida que se está arrastrando

        if comida_arrastrando is not None:

            imagen = comida_arrastrando["imagen"]

            ventana.blit(
                imagen,
                imagen.get_rect(
                    center=posicion_comida_arrastrando
                )
            )


    # ========================================================
    # MINIJUEGOS
    # ========================================================

    elif subpantalla == "minijuegos":

        ventana.fill(
            (200, 220, 240)
        )


        titulo = fuente_grande.render(
            "SELECCIONA UN MINIJUEGO",
            True,
            (0, 0, 0)
        )


        ventana.blit(
            titulo,
            (
                ancho // 2 -
                titulo.get_width() // 2,
                80
            )
        )


        for i, b in enumerate(
            botones_minijuegos
        ):

            dibujar_boton(
                ventana,
                b,
                f"Minijuego {i + 1}"
            )


        dibujar_boton(
            ventana,
            boton_volver_minijuegos,
            "Volver"
        )


    # ========================================================
    # PANTALLA NORMAL
    # ========================================================

    else:

        fondos = [
            fondo_bano,
            fondo_sala,
            fondo_habitacion,
            fondo_cocina
        ]


        ventana.blit(
            fondos[habitacion_actual],
            (0, 0)
        )


        # ----------------------------------------------------
        # NOCHE
        # ----------------------------------------------------

        if (
            modo_noche
            and habitacion_actual == 2
        ):

            s = pygame.Surface(
                (ancho, alto)
            )

            s.set_alpha(180)

            s.fill(
                (0, 0, 50)
            )

            ventana.blit(
                s,
                (0, 0)
            )


        # ----------------------------------------------------
        # FLECHAS
        # ----------------------------------------------------

        dibujar_boton(
            ventana,
            flecha_izquierda,
            "<"
        )

        dibujar_boton(
            ventana,
            flecha_derecha,
            ">"
        )


        # ----------------------------------------------------
        # NOMBRE HABITACIÓN
        # ----------------------------------------------------

        txt_hab = fuente_grande.render(
            nombres_habitaciones[
                habitacion_actual
            ],
            True,
            (0, 0, 0)
        )


        ventana.blit(
            txt_hab,
            (
                ancho // 2 -
                txt_hab.get_width() // 2,
                10
            )
        )


        # ----------------------------------------------------
        # PAU
        # ----------------------------------------------------

        personaje = obtener_personaje()


        ventana.blit(
            personaje,
            personaje.get_rect(
                center=posicion_pou
            )
        )


        # ----------------------------------------------------
        # BOTONES DE HABITACIONES
        # ----------------------------------------------------

        if habitacion_actual == 0:

            dibujar_baño(
                ventana
            )


        elif habitacion_actual == 1:

            dibujar_boton(
                ventana,
                boton_minijuegos,
                "Minijuegos"
            )


            dibujar_boton(
                ventana,
                boton_tienda,
                "Tienda"
            )


        elif habitacion_actual == 2:

            dibujar_boton(
                ventana,
                boton_dormir,
                "Dormir"
            )


        elif habitacion_actual == 3:

            dibujar_boton(
                ventana,
                boton_comidas,
                "Comidas"
            )


        # ----------------------------------------------------
        # OBJETO DE BAÑO ARRASTRADO
        # ----------------------------------------------------

        if objeto_baño_arrastrando is not None:

            if objeto_baño_arrastrando == "jabon":

                imagen = imagen_jabon

            elif objeto_baño_arrastrando == "ducha":

                imagen = imagen_ducha

            else:

                imagen = imagen_toalla


            ventana.blit(
                imagen,
                imagen.get_rect(
                    center=posicion_objeto_baño
                )
            )


        # ----------------------------------------------------
        # BARRAS
        # ----------------------------------------------------

        dibujar_barra(
            ventana,
            barra_baño,
            "BAÑO",
            baño
        )


        dibujar_barra(
            ventana,
            barra_comer,
            "COMER",
            comer
        )


        dibujar_barra(
            ventana,
            barra_dormir,
            "DORMIR",
            dormir
        )


        dibujar_barra(
            ventana,
            barra_jugar,
            "JUGAR",
            jugar
        )


    # ========================================================
    # MENSAJE TEMPORAL
    # ========================================================

    if (
        mensaje_temporal
        and (
            pygame.time.get_ticks()
            - tiempo_mensaje
            < 2000
        )
    ):

        txt_msg = fuente_grande.render(
            mensaje_temporal,
            True,
            (200, 0, 0)
        )


        rect_msg = txt_msg.get_rect(
            center=(
                ancho // 2,
                alto // 2
            )
        )


        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            rect_msg.inflate(20, 10)
        )


        pygame.draw.rect(
            ventana,
            (0, 0, 0),
            rect_msg.inflate(20, 10),
            2
        )


        ventana.blit(
            txt_msg,
            rect_msg
        )


# ============================================================
# FUNCIONES PARA EL MOUSE
# ============================================================

def manejar_movimiento_mouse(posicion):

    global posicion_comida_arrastrando
    global posicion_objeto_baño


    if comida_arrastrando is not None:

        posicion_comida_arrastrando = posicion


    if objeto_baño_arrastrando is not None:

        posicion_objeto_baño = posicion
