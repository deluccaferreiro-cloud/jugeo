import pygame
import random
jugando= True
game_over= False


pygame.init()
ANCHO=800
ALTO=500
ventana = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()

fondo=pygame.imagine.load("flappy.png")

pau=pygame.image.load("flappypau.png")
x_pau=150
y_pau=300
ancho_pau=40
alto_pau=40

velocidad_y = 0
gravedad = 0.5
salto = -9

ancho_ob= 80
espacio= 170
velocidad_tubos=4
ob= []


x_tubo = 800
altura_arriba = random.randint(100, 350)
ob.append([
x_tubo,
altura_arriba
])

puntos=0
fuente = pygame.font.Font(None, 50)

def crear_ob(ob):
    altura = random.randint(100, 350)
    ob.append([800, altura])

while jugando:
    reloj.tick(60)
    for evento in pygame.event.get():   
            if evento.type == pygame.QUIT:
                jugando = False
    if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if game_over:
                    y_pau = 300
                    velocidad_y = 0
                    ob.clear()
                    ob.append([800, random.randint(100, 350)])
                    puntos = 0
                    game_over = False

                else:
                    velocidad_y = salto
    if not game_over:
        velocidad_y += gravedad
        y_pau += velocidad_y
    for tubo in ob:
            tubo[0] -= velocidad_tubos

    if len(ob) > 0 and ob[-1][0] < 450:
            crear_ob()

    if ob[0][0] < -ancho_ob:
            ob.pop(0)
            puntos += 1

    pau_rect = pygame.Rect(
            x_pau,
            y_pau,
            ancho_pau,
            alto_pau
        )

    for tubos in ob :
          