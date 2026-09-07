import pygame

imagen = pygame.image.load("pai.png")

imagen = pygame.transform.scale(
    imagen,
    (800, 600)
)


def principal():

    ventana = pygame.display.get_surface()

    ventana.blit(
        imagen,
        (0, 0)
    )