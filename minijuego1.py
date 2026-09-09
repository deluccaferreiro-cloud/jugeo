import pygame
x = 300 

pygame.init()
ANCHO=800
ALTO=500
ventana = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()
ejecutando= True
pygame.image.load("flappy.png")
texto1= "JUGAR"
texto2= "INSTRUCCIONES"
rect1=pygame.draw.rect(x,300, 200, 50)
rect2=pygame.draw.rect(x,300, 200, 50)

                            