import pygame
import random, os

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

gravidad=0.5
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
            if evento.key == pygame.K_SPACE and flota_flota_list:
                