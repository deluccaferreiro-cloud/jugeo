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
pygame.display.set_caption("Flota Flota")