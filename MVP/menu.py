import pygame

pygame.init()

import principal

ancho = 800
alto = 600

ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("PAU")

ejecutando = True
reloj = pygame.time.Clock()

fuente = pygame.font.Font(None, 32)

pantalla_actual = "menu"

cuadro1 = pygame.Rect(300, 225, 200, 50)
cuadro2 = pygame.Rect(300, 300, 200, 50)
cuadro3 = pygame.Rect(300, 375, 200, 50)

cruz = pygame.Rect(20, 20, 40, 40)

while ejecutando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:

                if pantalla_actual == "menu":

                    if cuadro1.collidepoint(evento.pos):
                        pantalla_actual = "juego"

                    elif cuadro2.collidepoint(evento.pos):
                        pantalla_actual = "instrucciones"

                    elif cuadro3.collidepoint(evento.pos):
                        ejecutando = False

                elif pantalla_actual == "instrucciones":

                    if cruz.collidepoint(evento.pos):
                        pantalla_actual = "menu"

                elif pantalla_actual == "juego":

                    if cruz.collidepoint(evento.pos):
                        pantalla_actual = "menu"

                    else:
                        principal.manejar_click(evento.pos)

    if pantalla_actual == "menu":

        ventana.fill((0, 0, 0))

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

        texto1 = fuente.render(
            "JUGAR",
            True,
            (0, 0, 0)
        )

        texto2 = fuente.render(
            "INSTRUCCIONES",
            True,
            (0, 0, 0)
        )

        texto3 = fuente.render(
            "SALIR",
            True,
            (0, 0, 0)
        )

        ventana.blit(
            texto1,
            texto1.get_rect(center=cuadro1.center)
        )

        ventana.blit(
            texto2,
            texto2.get_rect(center=cuadro2.center)
        )

        ventana.blit(
            texto3,
            texto3.get_rect(center=cuadro3.center)
        )

    elif pantalla_actual == "instrucciones":

        # Fondo negro
        ventana.fill((0, 0, 0))

        texto_instrucc = fuente.render(
            "Instrucciones:",
            True,
            (255, 255, 255)
        )

        texto_instrucc2 = fuente.render(
            "Aca tengo que escribir las instrucciones",
            True,
            (255, 255, 255, 255)
        )

        ventana.blit(
            texto_instrucc,
            (250, 200)
        )

        ventana.blit(
            texto_instrucc2,
            (250, 250)
        )

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

    elif pantalla_actual == "juego":

        principal.principal()

        # Cruz negra
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

    pygame.display.flip()

    reloj.tick(60)

pygame.quit()