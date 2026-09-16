import pygame 
import random
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
vidas_pau=3

comida_diccio= []
contador_comida=0
comida1_B=pygame.image.load()
comida2_B=pygame.image.load()
comida1_M=pygame.image.load()
comida2_M=pygame.image.load()
puntaje_comidita=0


while ejecutando:
    for eventos in pygame.even.get():
        if eventos.type==pygame.quit:
            ejecutando= False

        if eventos.type==pygame.KEYDOWN:
                if eventos.key==pygame.K_SPACE and game_over:
                    x_pau
                    puntaje_comidita
                    vidas_pau
                    comida_diccio.clear()
                    game_over= False
        if not game_over:
             teclas=pygame.key.get_pressed()
        if teclas[pygame.K_RIGHT]:
            x_pau -= velocidad_pau
        if x_pau < 0:
             x_pau=0
        if x_pau> ancho_pau - 100:
             x_pau= ancho_pau-100

    contador_comida +=1
    if contador_comida >=50:
         contador_comida= 0
    x_comida= random.randit(0,50)
             
             


          