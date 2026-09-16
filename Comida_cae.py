import pygame 
jugador=True
game_over=False

pygame.init()
ejecutando= True
game_over=False

ANCHO=800
ALTO=500
ventana=pygame.display.set_mode((ANCHO,ALTO))
reloj=pygame.time.Clock()

fondo=pygame.image.load("comida.png")

pau_N=pygame.image.load("paufeliz.png")
alto_pau=100
ancho_pau=100
x_pau= 350
y_pau= 450
velocidad_pau=7
pau_M=pygame.image.load("pou.png")

comida_diccio= []
contador_comida=0
comida1_B=pygame.image.load()
comida2_B=pygame.image.load()
comida1_M=pygame.image.load()
comida2_M=pygame.image.load()

puntaje_comidita=0
vida_pau=3

while ejecutando:
    for eventos in pygame.even.get():
        if eventos.type==pygame.quit:
            ejecutando= False

        if eventos.type==pygame.KEYDOWN:
                if eventos.key==pygame.K_SPACE and game_over:
                
          