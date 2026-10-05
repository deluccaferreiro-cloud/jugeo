import pygame
import random, os

jugando=True
game_over=False

def encontrar_archivo(nombre):
    carpeta_raiz=os.path.dirname(__file__)
    archivo=os.path.join(carpeta_raiz, "assets", "minijuegos", "comidaquecae", nombre)
    return archivo
pygame.init()

ANCHO=800
ALTO=500

ventana=pygame.display.set_mode((ANCHO, ALTO))

reloj=pygame.time.Clock()

fondo=pygame.image.load(encontrar_archivo("comida.png"))

pau_masticando=pygame.image.load(encontrar_archivo("paumasticando.png"))
pau_masticando=pygame.transform.scale(pau_masticando,(100,100))

pau_agarrar_comida=pygame.image.load(encontrar_archivo("paubocaabiertaparaM2.png"))
pau_agarrar_comida=pygame.transform.scale(pau_agarrar_comida,(100,100))

x_pau=350
y_pau=400

ancho_pau=100
alto_pau=100

velocidad_pau=7

vidas_pau=3

comida_lista=[]

velocidad_comida=5

contador_comida=0

comida_buena=pygame.image.load(encontrar_archivo("comidabuena.png"))
comida_buena=pygame.transform.scale(comida_buena,(50,50))

comida_mala=pygame.image.load(encontrar_archivo("comidamala.png"))
comida_mala=pygame.transform.scale(comida_mala,(50,50))

puntaje_comidita=0

fuente=pygame.font.Font(None,50)

contador_comiendo=0

while jugando:

    reloj.tick(60)

    for eventos in pygame.event.get():

        if eventos.type==pygame.QUIT:
            jugando=False

        if eventos.type==pygame.KEYDOWN:

            if eventos.key==pygame.K_SPACE and game_over:

                x_pau=350
                puntaje_comidita=0
                vidas_pau=3

                comida_lista.clear()

                contador_comida=0
                contador_comiendo=0

                game_over=False

    if not game_over:

        teclas=pygame.key.get_pressed()

        if teclas[pygame.K_LEFT]:
            x_pau-=velocidad_pau

        if teclas[pygame.K_RIGHT]:
            x_pau+=velocidad_pau

        if x_pau<0:
            x_pau=0

        if x_pau>ANCHO-100:
            x_pau=ANCHO-100

        contador_comida+=1

        if contador_comida>=50:

            contador_comida=0

            x_comida=random.randint(0,ANCHO-50)

            tipo=random.randint(1,10)

            if tipo<=7:
                tipo_comida="buena"
            else:
                tipo_comida="mala"

            comida_lista.append([x_comida,-50,tipo_comida])

        for comida in comida_lista:
            comida[1]+=velocidad_comida

        pau_rect=pygame.Rect(
            x_pau,
            y_pau,
            100,
            100
        )

        for comida in comida_lista:

            comida_rect=pygame.Rect(
                comida[0],
                comida[1],
                50,
                50
            )

            if pau_rect.colliderect(comida_rect):

                if comida[2]=="buena":

                    puntaje_comidita+=1
                    contador_comiendo=15

                else:

                    vidas_pau-=1

                    if vidas_pau<=0:
                        vidas_pau=0
                        game_over=True

                comida[1]=ALTO+100

        comida_lista=[
            comida for comida in comida_lista
            if comida[1]<ALTO+50
        ]

        if contador_comiendo>0:

            contador_comiendo-=1
            esta_comiendo=True

        else:

            esta_comiendo=False

    ventana.blit(fondo,(0,0))

    for comida in comida_lista:

        if comida[2]=="buena":

            ventana.blit(
                comida_buena,
                (comida[0],comida[1])
            )

        else:

            ventana.blit(
                comida_mala,
                (comida[0],comida[1])
            )

    if esta_comiendo:

        ventana.blit(
            pau_masticando,
            (x_pau,y_pau)
        )

    else:

        ventana.blit(
            pau_agarrar_comida,
            (x_pau,y_pau)
        )

    texto_punto=fuente.render(
        "Puntos: "+str(puntaje_comidita),
        True,
        (255,255,255)
    )

    ventana.blit(
        texto_punto,
        (20,20)
    )

    texto_vidas=fuente.render(
        "Vidas: "+str(vidas_pau),
        True,
        (255,255,255)
    )

    ventana.blit(
        texto_vidas,
        (20,60)
    )

    if game_over:

        texto_game_over=fuente.render(
            "GAME OVER",
            True,
            (255,0,0)
        )

        texto_reiniciar=pygame.font.Font(
            None,30
        ).render(
            "Presiona ESPACIO para volver a jugar",
            True,
            (255,255,255)
        )

        ventana.blit(
            texto_game_over,
            (320,270)
        )

        ventana.blit(
            texto_reiniciar,
            (220,320)
        )

    pygame.display.update()

pygame.quit()