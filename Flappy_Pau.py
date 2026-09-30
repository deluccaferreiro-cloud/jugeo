import pygame
import random
import os


def encontrar_archivo(nombre):

    carpeta_raiz = os.path.dirname(__file__)

    archivo = os.path.join(
        carpeta_raiz,
        "assets",
        "minijuegos",
        "flappy",
        nombre
    )

    return archivo


def ejecutar_flappy():

    # ------------------------------------------------
    # CONFIGURACIÓN
    # ------------------------------------------------

    ANCHO = 800
    ALTO = 600

    jugando = True
    game_over = False

    reloj = pygame.time.Clock()

    ventana = pygame.display.get_surface()

    pygame.display.set_caption(
        "Flappy Pau"
    )


    # ------------------------------------------------
    # CARGAR IMÁGENES
    # ------------------------------------------------

    try:

        fondo = pygame.image.load(
            encontrar_archivo("flappy.png")
        )

        fondo = pygame.transform.smoothscale(
            fondo,
            (ANCHO, ALTO)
        )


        pau = pygame.image.load(
            encontrar_archivo("flappypau.png")
        )

    except pygame.error:

        fondo = pygame.Surface(
            (ANCHO, ALTO)
        )

        fondo.fill(
            (100, 180, 230)
        )

        pau = pygame.Surface(
            (100, 100)
        )

        pau.fill(
            (139, 69, 19)
        )


    # ------------------------------------------------
    # PAU
    # ------------------------------------------------

    x_pau = 150
    y_pau = 300

    ancho_pau = 100
    alto_pau = 100

    pau = pygame.transform.smoothscale(
        pau,
        (ancho_pau, alto_pau)
    )


    # ------------------------------------------------
    # FÍSICA
    # ------------------------------------------------

    velocidad_y = 0

    gravedad = 0.5

    salto = -9


    # ------------------------------------------------
    # TUBOS
    # ------------------------------------------------

    ancho_ob = 80

    espacio = 170

    velocidad_tubos = 4

    ob = []


    def crear_ob():

        altura = random.randint(
            100,
            300
        )

        ob.append(
            [
                ANCHO,
                altura
            ]
        )


    crear_ob()


    # ------------------------------------------------
    # PUNTOS
    # ------------------------------------------------

    puntos = 0

    fuente = pygame.font.Font(
        None,
        50
    )


    # ------------------------------------------------
    # LOOP DEL JUEGO
    # ------------------------------------------------

    while jugando:

        reloj.tick(60)


        # --------------------------------------------
        # EVENTOS
        # --------------------------------------------

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:

                jugando = False


            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_SPACE:

                    if game_over:

                        y_pau = 300

                        velocidad_y = 0

                        ob.clear()

                        crear_ob()

                        puntos = 0

                        game_over = False

                    else:

                        velocidad_y = salto


                # ESC PARA VOLVER
                if evento.key == pygame.K_ESCAPE:

                    jugando = False


        # --------------------------------------------
        # ACTUALIZAR JUEGO
        # --------------------------------------------

        if not game_over:

            velocidad_y += gravedad

            y_pau += velocidad_y


            # Mover tubos

            for tubo in ob:

                tubo[0] -= velocidad_tubos


            # Crear nuevos tubos

            if (
                len(ob) > 0
                and ob[-1][0] < 450
            ):

                crear_ob()


            # Eliminar tubos pasados

            if (
                len(ob) > 0
                and ob[0][0] < -ancho_ob
            ):

                ob.pop(0)

                puntos += 1


            # Rectángulo de Pau

            pau_rect = pygame.Rect(
                x_pau,
                y_pau,
                ancho_pau,
                alto_pau
            )


            # ----------------------------------------
            # COLISIONES
            # ----------------------------------------

            for tubo in ob:

                x = tubo[0]

                altura = tubo[1]


                tubo_arriba = pygame.Rect(
                    x,
                    0,
                    ancho_ob,
                    altura
                )


                tubo_abajo = pygame.Rect(
                    x,
                    altura + espacio,
                    ancho_ob,
                    ALTO -
                    (
                        altura + espacio
                    )
                )


                if pau_rect.colliderect(
                    tubo_arriba
                ):

                    game_over = True


                if pau_rect.colliderect(
                    tubo_abajo
                ):

                    game_over = True


            # ----------------------------------------
            # BORDES
            # ----------------------------------------

            if (
                y_pau + alto_pau
                >= ALTO
            ):

                game_over = True


            if y_pau <= 0:

                game_over = True


        # --------------------------------------------
        # DIBUJAR FONDO
        # --------------------------------------------

        ventana.blit(
            fondo,
            (0, 0)
        )


        # --------------------------------------------
        # DIBUJAR TUBOS
        # --------------------------------------------

        verde = (0, 128, 0)


        for tubo in ob:

            x = tubo[0]

            altura = tubo[1]


            pygame.draw.rect(
                ventana,
                verde,
                (
                    x,
                    0,
                    ancho_ob,
                    altura
                )
            )


            pygame.draw.rect(
                ventana,
                verde,
                (
                    x,
                    altura + espacio,
                    ancho_ob,
                    ALTO -
                    (
                        altura + espacio
                    )
                )
            )


        # --------------------------------------------
        # DIBUJAR PAU
        # --------------------------------------------

        ventana.blit(
            pau,
            (x_pau, y_pau)
        )


        # --------------------------------------------
        # PUNTOS
        # --------------------------------------------

        blanco = (255, 255, 255)


        texto = fuente.render(
            str(puntos),
            True,
            blanco
        )


        ventana.blit(
            texto,
            (
                ANCHO // 2 -
                texto.get_width() // 2,
                30
            )
        )


        # --------------------------------------------
        # GAME OVER
        # --------------------------------------------

        if game_over:

            texto_game_over = fuente.render(
                "GAME OVER...",
                True,
                blanco
            )


            fuente_reiniciar = pygame.font.Font(
                None,
                30
            )


            texto_reiniciar = (
                fuente_reiniciar.render(
                    "Presiona ESPACIO para reiniciar",
                    True,
                    blanco
                )
            )


            ventana.blit(
                texto_game_over,
                (
                    ANCHO // 2 -
                    texto_game_over.get_width() // 2,
                    ALTO // 2 - 40
                )
            )


            ventana.blit(
                texto_reiniciar,
                (
                    ANCHO // 2 -
                    texto_reiniciar.get_width() // 2,
                    ALTO // 2 + 20
                )
            )


        pygame.display.flip()


    # ------------------------------------------------
    # AL SALIR DE FLAPPY
    # ------------------------------------------------

    pygame.display.set_caption(
        "PAU"
    )