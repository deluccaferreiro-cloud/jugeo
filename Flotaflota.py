import pygame
import os

def encontrar_archivo(nombre):
    carpeta_raiz=os.path.dirname(__file__)
    archivo=os.path.join(carpeta_raiz, "assets", "minijuegos", "flotaflota", nombre)
    return archivo

pygame.init()
jugando=True
game_over=False

ANCHO=800
ALTO=500
ventana=pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flota Pau")

reloj=pygame.time.Clock()

fondo=pygame.image.load(encontrar_archivo("flotaflota.png"))
pau=pygame.image.load(encontrar_archivo("pauflotaflota.png"))
pau=pygame.transform.scale(pau,(100, 100))

x_pau=100
y_pau=350

velocidad_x=5
velocidad_y=0

gravedad=0.5
f_salto= -12

flota_flota_imagen=pygame.image.load(encontrar_archivo("ob_flota.png"))

flota_flota_list=[]

flota_flota_list.append(pygame.Rect(50, 430, 180, 25))
flota_flota_list.append(pygame.Rect(250, 430, 180, 25))
flota_flota_list.append(pygame.Rect(450, 430, 180, 25))
flota_flota_list.append(pygame.Rect(650, 430, 180, 25))

en_flota=False

puntos=0
contador_puntaje_salto=0 

while jugando:
    reloj.tick(60)
    for evento in pygame.event.get():
        if evento.type==pygame.QUIT:
            jugando=False
            
        if evento.type==pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and en_flota:
                velocidad_y=f_salto

        if evento.key==pygame.K_r and game_over:
                x_pau=100
                y_pau=350
                velocidad_y=0
                game_over=False

    if not game_over:
         teclas= pygame.key.get_pressed()

    if teclas[pygame.K_LEFT]:
         x_pau-= velocidad_x
    if teclas[pygame.K_RIGHT]:
        x_pau += velocidad_x

    velocidad_y += gravedad
    y_pau += velocidad_y

    rect_pau=pygame.Rect(x_pau,y_pau,60,60)
    en_flota= False

    for flotaflota in flota_flota_list:
         if rect_pau.collidedict(flotaflota):
            if velocidad_y > 0 and rect_pau.bottom <=flotaflota.bottom + 20:
                y_pau=flotaflota.top-60
                velocidad_y= 0
                en_flota= True

            if x_pau<0:
                x_pau==0

            if x_pau > ANCHO - 60:
                x_pau = ANCHO - 60

            if y_pau > ALTO:
                game_over= True

    ventana.blit(fondo,(0,0))

    for flotaflota in flota_flota_list:
        pygame.draw.rect(ventana,(80,180,80),flotaflota)

    ventana.blit(pau, (x_pau, y_pau))

    if game_over:

        fuente = pygame.font.Font(None, 60)
        texto = fuente.render("GAME OVER", True, (255, 255, 255))
        ventana.blit(texto, (270, 200))

        fuente2 = pygame.font.Font(None, 35)
        texto2 = fuente2.render("Presiona R para volver a jugar", True, (255, 255, 255))
        ventana.blit(texto2, (230, 270))

    pygame.display.update()

    reloj.tick(60)

pygame.quit()
            
