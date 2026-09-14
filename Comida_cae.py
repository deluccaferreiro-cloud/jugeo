import pygame 
jugador=True
game_over=False

pygame.init()
ANCHO=800
ALTO=500
ventana=pygame.display.set_mode((ANCHO,ALTO))
reloj=pygame.time.Clock()

fondo=pygame.image.load("comida.png")
pau_N=pygame.image.load("paufeliz.png")
pau_M=pygame.image.load("pou.png")
