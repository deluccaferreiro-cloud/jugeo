import pygame
import ultima.principal as principal


pygame.init()


# ============================================================
# CONFIGURACIÓN
# ============================================================

ancho = 800
alto = 600

ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PAU")

reloj = pygame.time.Clock()

ejecutando = True


# ============================================================
# FUENTES
# ============================================================

fuente = pygame.font.Font(None, 32)


# ============================================================
# MENÚ
# ============================================================

x = 300

texto1 = "JUGAR"
texto2 = "INSTRUCCIONES"
texto3 = "SALIR"


cuadro1 = pygame.Rect(
    x,
    225,
    200,
    50
)

cuadro2 = pygame.Rect(
    x,
    300,
    200,
    50
)

cuadro3 = pygame.Rect(
    x,
    375,
    200,
    50
)


# ============================================================
# CRUZ PARA VOLVER
# ============================================================

cruz = pygame.Rect(
    740,
    10,
    40,
    40
)


# ============================================================
# FONDO
# ============================================================

try:

    fondo = pygame.image.load(
        "PAU.png"
    )

    fondo = pygame.transform.smoothscale(
        fondo,
        (ancho, alto)
    )

except:

    fondo = pygame.Surface(
        (ancho, alto)
    )

    fondo.fill(
        (100, 150, 200)
    )


# ============================================================
# PANTALLA ACTUAL
# ============================================================

pantalla_actual = "menu"


# ============================================================
# BUCLE PRINCIPAL
# ============================================================

while ejecutando:

    # ========================================================
    # EVENTOS
    # ========================================================

    for evento in pygame.event.get():

        # ----------------------------------------------------
        # CERRAR VENTANA
        # ----------------------------------------------------

        if evento.type == pygame.QUIT:

            ejecutando = False


        # ----------------------------------------------------
        # CLIC DEL MOUSE
        # ----------------------------------------------------

        elif evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

                posicion = evento.pos


                # ==================================================
                # MENÚ PRINCIPAL
                # ==================================================

                if pantalla_actual == "menu":

                    # JUGAR

                    if cuadro1.collidepoint(posicion):

                        print("JUGAR")

                        pantalla_actual = "juego"


                    # INSTRUCCIONES

                    elif cuadro2.collidepoint(posicion):

                        print("INSTRUCCIONES")

                        pantalla_actual = "instrucciones"


                    # SALIR

                    elif cuadro3.collidepoint(posicion):

                        print("SALIR")

                        ejecutando = False


                # ==================================================
                # INSTRUCCIONES
                # ==================================================

                elif pantalla_actual == "instrucciones":

                    if cruz.collidepoint(posicion):

                        pantalla_actual = "menu"


                # ==================================================
                # JUEGO
                # ==================================================

                elif pantalla_actual == "juego":

                    # Cruz para volver al menú

                    if cruz.collidepoint(posicion):

                        pantalla_actual = "menu"

                    else:

                        principal.manejar_click(
                            posicion
                        )


        # ----------------------------------------------------
        # MOVER MOUSE
        # ----------------------------------------------------

        elif evento.type == pygame.MOUSEMOTION:

            if pantalla_actual == "juego":

                principal.manejar_movimiento_mouse(
                    evento.pos
                )


        # ----------------------------------------------------
        # SOLTAR MOUSE
        # ----------------------------------------------------

        elif evento.type == pygame.MOUSEBUTTONUP:

            if evento.button == 1:

                if pantalla_actual == "juego":

                    principal.manejar_soltar(
                        evento.pos
                    )


    # ========================================================
    # DIBUJAR MENÚ
    # ========================================================

    if pantalla_actual == "menu":

        ventana.blit(
            fondo,
            (0, 0)
        )


        # ----------------------------------------------------
        # BOTÓN JUGAR
        # ----------------------------------------------------

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro1
        )


        # ----------------------------------------------------
        # BOTÓN INSTRUCCIONES
        # ----------------------------------------------------

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro2
        )


        # ----------------------------------------------------
        # BOTÓN SALIR
        # ----------------------------------------------------

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro3
        )


        # ----------------------------------------------------
        # TEXTOS
        # ----------------------------------------------------

        superficietexto1 = fuente.render(
            texto1,
            True,
            (194, 228, 255)
        )


        superficietexto2 = fuente.render(
            texto2,
            True,
            (194, 228, 255)
        )


        superficietexto3 = fuente.render(
            texto3,
            True,
            (194, 228, 255)
        )


        ventana.blit(
            superficietexto1,
            (
                cuadro1.centerx -
                superficietexto1.get_width() // 2,
                cuadro1.centery -
                superficietexto1.get_height() // 2
            )
        )


        ventana.blit(
            superficietexto2,
            (
                cuadro2.centerx -
                superficietexto2.get_width() // 2,
                cuadro2.centery -
                superficietexto2.get_height() // 2
            )
        )


        ventana.blit(
            superficietexto3,
            (
                cuadro3.centerx -
                superficietexto3.get_width() // 2,
                cuadro3.centery -
                superficietexto3.get_height() // 2
            )
        )


    # ========================================================
    # INSTRUCCIONES
    # ========================================================

    elif pantalla_actual == "instrucciones":

        ventana.fill(
            (223, 186, 201)
        )


        texto_instrucc = fuente.render(
            "Instrucciones:",
            True,
            (255, 255, 255)
        )


        texto_instrucc2 = fuente.render(
            "Usa las flechas para moverte de habitación.",
            True,
            (255, 255, 255)
        )


        texto_instrucc3 = fuente.render(
            "Arrastra los objetos hacia Pau para usarlos.",
            True,
            (255, 255, 255)
        )


        ventana.blit(
            texto_instrucc,
            (250, 200)
        )


        ventana.blit(
            texto_instrucc2,
            (200, 250)
        )


        ventana.blit(
            texto_instrucc3,
            (190, 300)
        )


        # ----------------------------------------------------
        # CRUZ
        # ----------------------------------------------------

        pygame.draw.line(
            ventana,
            (255, 255, 255),
            (740, 10),
            (770, 40),
            5
        )


        pygame.draw.line(
            ventana,
            (255, 255, 255),
            (770, 10),
            (740, 40),
            5
        )


    # ========================================================
    # JUEGO
    # ========================================================

    elif pantalla_actual == "juego":

        principal.principal()


        # ----------------------------------------------------
        # CRUZ
        # ----------------------------------------------------

        pygame.draw.line(
            ventana,
            (0, 0, 0),
            (740, 10),
            (770, 40),
            5
        )


        pygame.draw.line(
            ventana,
            (0, 0, 0),
            (770, 10),
            (740, 40),
            5
        )


    # ========================================================
    # ACTUALIZAR PANTALLA
    # ========================================================

    pygame.display.flip()

    reloj.tick(60)


pygame.quit()
