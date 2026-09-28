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

comida_lista=[]
velocidad_comida=0
contador_comida=0
comida_buena1=pygame.image.load()
comida_buena2=pygame.image.load()
comida_mala1=pygame.image.load()
comida_mala2=pygame.image.load()
puntaje_comidita=0

while jugando:
    reloj.tick(60)

    for eventos in pygame.even.get():
        if eventos.type==pygame.quit:
            jugando=False

        if eventos.type==pygame.KEYDOWN:
                if eventos.key==pygame.K_SPACE and game_over:
                    x_pau
                    puntaje_comidita
                    vidas_pau
                    comida_lista.clear()
                    game_over= False
if not game_over:
        teclas=pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            x_pau -= velocidad_pau
        if teclas[pygame.K_RIGHT]:
             x_pau += velocidad_pau

        if x_pau < 0: 
            x_pau = 0 
        if x_pau > ANCHO - 100: 
          x_pau = ANCHO - 100

contador_comida +=1
if contador_comida >= 50: 
    contador_comida = 0 
    x_comida = random.randint(0, ANCHO - 50)
    tipo = random.randint(1, 10) 
    if tipo <= 7: tipo_comida = "buena" 
    else: tipo_comida = "mala" 
    comida_lista.append([ x_comida, -50, tipo_comida ])

    for comida in comida_lista:
         comida[1]+=velocidad_comida

pau_rect=pygame.Rect(
     x_pau,
     y_pau,
     100,
     100
)
esta_comiendo= False
for comida in comida_lista:
     comida_rect = pygame.Rect( 
        comida[0],
        comida[1], 
        50, 
        50 
)
if pau_rect.collidedict(comida_rect):
     if comida[2]=="buena":
        puntaje_comidita+=1
        esta_comiendo=True
        contador_comida=15
else:
        vidas_pau -=1

if vidas_pau <= 0: 
        game_over = True
comida[1] = ALTO+ 100

comidas =[ 
    comida for comida in comida_lista
     if comida[1] < ALTO + 50 
]

if comida_lista >0:
     
     
     
     