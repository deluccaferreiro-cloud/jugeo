import pygame
import random
jugando=True
game_over= False

pygame.init()
ANCHO=800
ALTO=500
ventana= pygame.display.set_mode(ANCHO,ALTO)
reloj=pygame.time.Clock()

fondo= pygame.image.load("comida.png")
pau_masticando=pygame.image.load("paumasticando.png")
pau_agarrar_comida=pygame.image.load("paubocaabiertaparaM2.png")
x_pau=350
y_pau=450
ancho_pau=100
alto_pau=100
velocidad_pau=7 
vidas_pau=3

comida_diccionario={}
contador_comida=0
comida_buena1=pygame.image.load()
comida_buena2=pygame.image.load()
comida_mala1=pygame.image.load()
comida_mala2=pygame.image.load()
puntaje_comidita=0

while jugando:
    for eventos in pygame.even.get():
        if eventos.type==pygame.quit:
            jugando=False

        if eventos.type==pygame.KEYDOWN:
                if eventos.key==pygame.K_SPACE and game_over:
                    x_pau
                    puntaje_comidita
                    vidas_pau
                    comida_diccionario.clear()
                    game_over= False

if not game_over:
     teclas=pygame.key.get.pressed()
if teclas[pygame.K_RIGHT]:
        x_pau -= velocidad_pau
        if x_pau < 0:
             x_pau=0
        if x_pau> ancho_pau - 100:
             x_pau= ancho_pau-100
contador_comida +=1
if contador_comida >=50:
         contador_comida= 0
x_comida=random.random(0,50)
             
                     