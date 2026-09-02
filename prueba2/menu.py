import pygame

pygame.init()

ancho = 800
alto = 600

ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PAU")

# Importamos principal después de pygame.init()
import principal

ejecutando = True
reloj = pygame.time.Clock()

# -----------------------------
# CONFIGURACIÓN DEL MENÚ
# -----------------------------

x = 300
velocidad = 5

texto1 = "JUGAR"
texto2 = "INSTRUCCIONES"
texto3 = "SALIR"

fuente = pygame.font.Font(None, 32)

pantalla_actual = "menu"

# Botones del menú
cuadro1 = pygame.Rect(x, 225, 200, 50)
cuadro2 = pygame.Rect(x, 300, 200, 50)
cuadro3 = pygame.Rect(x, 375, 200, 50)

# -----------------------------
# IMÁGENES DEL MENÚ
# -----------------------------
# Todas las imágenes se buscan dentro de "imagenes"

fondo = pygame.image.load("imagenes/PAU.png")

# La imagen del Pou del menú ya no se dibuja
# porque principal.py se encarga del personaje
# cuando estamos en la pantalla de juego.

# Botón/cruz para volver
cruz = pygame.Rect(20, 20, 40, 40)


# -----------------------------
# BUCLE PRINCIPAL
# -----------------------------

while ejecutando:

    for evento in pygame.event.get():

        # Cerrar ventana
        if evento.type == pygame.QUIT:
            ejecutando = False

        # Detectar clic izquierdo
        if evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

                # -------------------------
                # PANTALLA DEL MENÚ
                # -------------------------
                if pantalla_actual == "menu":

                    # Botón JUGAR
                    if cuadro1.collidepoint(evento.pos):
                        pantalla_actual = "juego"

                    # Botón INSTRUCCIONES
                    elif cuadro2.collidepoint(evento.pos):
                        pantalla_actual = "instrucciones"

                    # Botón SALIR
                    elif cuadro3.collidepoint(evento.pos):
                        ejecutando = False

                # -------------------------
                # PANTALLA DE INSTRUCCIONES
                # -------------------------
                elif pantalla_actual == "instrucciones":

                    if cruz.collidepoint(evento.pos):
                        pantalla_actual = "menu"

                # -------------------------
                # PANTALLA DEL JUEGO
                # -------------------------
                elif pantalla_actual == "juego":

                    # Volver al menú
                    if cruz.collidepoint(evento.pos):
                        pantalla_actual = "menu"

                    # Si no se hizo clic en la cruz,
                    # le pasamos el clic a principal.py
                    else:
                        principal.manejar_click(evento.pos)

    # -----------------------------
    # DIBUJAR EL MENÚ
    # -----------------------------

    if pantalla_actual == "menu":

        ventana.blit(fondo, (0, 0))

        # Botones
        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro1
        )

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro2
        )

        pygame.draw.rect(
            ventana,
            (255, 255, 255),
            cuadro3
        )

        # Textos
        superficietexto1 = fuente.render(
            texto1,
            True,
            (212, 232, 244)
        )

        superficietexto2 = fuente.render(
            texto2,
            True,
            (212, 232, 244)
        )

        superficietexto3 = fuente.render(
            texto3,
            True,
            (212, 232, 244)
        )

        ventana.blit(
            superficietexto1,
            (x + 60, 225 + 14)
        )

        ventana.blit(
            superficietexto2,
            (x + 6, 300 + 14)
        )

        ventana.blit(
            superficietexto3,
            (x + 60, 375 + 14)
        )

    # -----------------------------
    # PANTALLA DE INSTRUCCIONES
    # -----------------------------

    elif pantalla_actual == "instrucciones":

        ventana.fill((223, 186, 201))

        texto_instrucc = fuente.render(
            "Instrucciones:",
            True,
            (255, 255, 255)
        )

        texto_instrucc2 = fuente.render(
            "Aca tengo que escribir las instrucciones",
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto_instrucc,
            (250, 200)
        )

        ventana.blit(
            texto_instrucc2,
            (250, 250)
        )

        # Cruz para volver
        pygame.draw.line(
            ventana,
            (255, 255, 255),
            (25, 25),
            (55, 55),
            5
        )

        pygame.draw.line(
            ventana,
            (255, 255, 255),
            (55, 25),
            (25, 55),
            5
        )

    # -----------------------------
    # PANTALLA DEL JUEGO
    # -----------------------------

    elif pantalla_actual == "juego":

        # principal.py se encarga de TODO:
        # fondo, barras, botones y personaje.
        principal.principal()

        # Cruz para volver al menú
        pygame.draw.line(
            ventana,
            (0, 0, 0),
            (25, 25),
            (55, 55),
            5
        )

        pygame.draw.line(
            ventana,
            (0, 0, 0),
            (55, 25),
            (25, 55),
            5
        )

    # Actualizar pantalla
    pygame.display.flip()

    # 60 FPS
    reloj.tick(60)


pygame.quit()