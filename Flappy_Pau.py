import pygame
import random, os

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    archivo = os.path.join(carpeta_raiz, "assets", "minijuegos", "flappy", nombre)
    return archivo

pygame.init()

jugando = True
game_over = False

ANCHO = 800
ALTO = 500

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Flappy Pau")

reloj = pygame.time.Clock()

fondo = pygame.image.load(encontrar_archivo("flappy.png"))
pau = pygame.image.load(encontrar_archivo("flappypau.png"))

x_pau = 150
y_pau = 300

ancho_pau = 67
alto_pau = 67


pau = pygame.transform.scale(pau, (ancho_pau, alto_pau))

velocidad_y = 0
gravedad = 0.5
salto = -9

ancho_ob = 80
espacio = 170
velocidad_tubos = 4

ob = []

x_tubo = 800
altura_arriba = random.randint(100, 300)

ob.append([
    x_tubo,
    altura_arriba
])

puntos = 0

fuente = pygame.font.Font(None, 50)


def crear_ob(ob):
    altura = random.randint(100, 300)
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
                    ob.append([800, random.randint(100, 300)])

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
            crear_ob(ob)

       
        if len(ob) > 0 and ob[0][0] < -ancho_ob:
            ob.pop(0)
            puntos += 1

        
        pau_rect = pygame.Rect(
            x_pau,
            y_pau,
            ancho_pau,
            alto_pau
        )

        
        for tubo in ob:

            x = tubo[0]
            altura = tubo[1]

            tubo_arriba = pygame.Rect(
                x,
                0,
                ancho_ob,
                altura
            )

            tubo_abajo = pygame.Rect(
                x,
                altura + espacio,
                ancho_ob,
                ALTO - (altura + espacio)
            )

            if pau_rect.colliderect(tubo_arriba):
                game_over = True

            if pau_rect.colliderect(tubo_abajo):
                game_over = True

    
        if y_pau + alto_pau >= ALTO:
            game_over = True

        
        if y_pau <= 0:
            game_over = True

    ventana.blit(fondo, (0, 0))


    verde = (0, 128, 0)

    for tubo in ob:

        x = tubo[0]
        altura = tubo[1]

        pygame.draw.rect(
            ventana,
            verde,
            (x, 0, ancho_ob, altura)
        )

        pygame.draw.rect(
            ventana,
            verde,
            (
                x,
                altura + espacio,
                ancho_ob,
                ALTO - (altura + espacio)
            )
        )

  
    ventana.blit(
        pau,
        (x_pau, y_pau)
    )

   
    blanco = (255, 255, 255)

    texto = fuente.render(
        str(puntos),
        True,
        blanco
    )

    ventana.blit(
        texto,
        (ANCHO // 2, 30)
    )

    
    if game_over:

        texto_game_over = fuente.render(
            "GAME OVER...",
            True,
            blanco
        )

        texto_reiniciar = pygame.font.Font(
            None,
            30
        ).render(
            "Presiona ESPACIO para reiniciar",
            True,
            blanco
        )

        ventana.blit(
            texto_game_over,
            (ANCHO // 2 - 110, ALTO // 2 - 40)
        )

        ventana.blit(
            texto_reiniciar,
            (ANCHO // 2 - 150, ALTO // 2 + 20)
        )

    pygame.display.update()


pygame.quit()