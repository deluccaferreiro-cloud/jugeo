import pygame 
pygame.init() 
 
ancho = 800 
alto = 600 
ventana = pygame.display.set_mode((ancho, alto)) 
pygame.display.set_caption("Juego") 
ejecutando = True 
reloj = pygame.time.Clock() 
y = 225 
x = 300 
velocidad = 5 
texto1 = "JUGAR" 
texto2 = "INSTRUCCIONES" 
texto3 = "SALIR" 
fuente = pygame.font.Font(None, 32) 
pantalla_actual = "menu" 
cuadro1 = pygame.Rect(x, y, 200, 50) 
cuadro2 = pygame.Rect(x, 300, 200, 50) 
cuadro3 = pygame.Rect(x, 375, 200, 50) 

fondo = pygame.image.load("PAU.png")

pou = pygame.image.load("pou.png")

tamaño_maximo = 400
ancho_pou, alto_pou = pou.get_size()

escala = min(tamaño_maximo / ancho_pou, tamaño_maximo / alto_pou)

nuevo_ancho = int(ancho_pou * escala)
nuevo_alto = int(alto_pou * escala)

pou = pygame.transform.smoothscale(pou, (nuevo_ancho, nuevo_alto))

cruz = pygame.Rect(20, 20, 40, 40)
 
while ejecutando: 
     
    for evento in pygame.event.get(): 
        if evento.type == pygame.QUIT: 
            ejecutando = False 
 
        if evento.type == pygame.MOUSEBUTTONDOWN: 
            if evento.button == 1: 
 
                if pantalla_actual == "menu": 
                    if cuadro1.collidepoint(evento.pos): 
                        pantalla_actual = "juego" 
 
                    elif cuadro2.collidepoint(evento.pos): 
                        pantalla_actual = "instrucciones" 
 
                    elif cuadro3.collidepoint(evento.pos): 
                        ejecutando = False 
 
                elif pantalla_actual == "instrucciones": 
                    if cruz.collidepoint(evento.pos): 
                        pantalla_actual = "menu" 
 
                elif pantalla_actual == "juego": 
                    if cruz.collidepoint(evento.pos): 
                        pantalla_actual = "menu" 
 
    if pantalla_actual == "menu": 
        ventana.blit(fondo, (0, 0))
 
        pygame.draw.rect(ventana, (255, 255, 255), cuadro1) 
        pygame.draw.rect(ventana, (255, 255, 255), cuadro2) 
        pygame.draw.rect(ventana, (255, 255, 255), cuadro3) 
 
        superficietexto1 = fuente.render(texto1, True, (212, 232, 244)) 
        ventana.blit(superficietexto1, (x + 60, 225 + 14)) 
 
        superficietexto2 = fuente.render(texto2, True, (212, 232, 244)) 
        ventana.blit(superficietexto2, (x + 6, 300 + 14)) 
 
        superficietexto3 = fuente.render(texto3, True, (212, 232, 244)) 
        ventana.blit(superficietexto3, (x + 60, 375 + 14)) 
 
    elif pantalla_actual == "instrucciones": 
        ventana.fill((223, 186, 201)) 
 
        texto_instrucc = fuente.render("Instrucciones:", True, (255, 255, 255)) 
        texto_instrucc2 = fuente.render( 
            "Aca tengo que escribir las instrucciones", 
            True, 
            (255, 255, 255) 
        ) 
 
        ventana.blit(texto_instrucc, (250, 200)) 
        ventana.blit(texto_instrucc2, (250, 250)) 
 
        pygame.draw.line(
            ventana, 
            (255, 255, 255), 
            (25, 25), 
            (55, 55), 
            5
        )

        pygame.draw.line(
            ventana, 
            (255, 255, 255), 
            (55, 25), 
            (25, 55), 
            5
        )
 
    elif pantalla_actual == "juego": 
        ventana.fill((50, 150, 50)) 
 
        posicion_pou = pou.get_rect(center=(ancho // 2, alto // 2))
        ventana.blit(pou, posicion_pou)

        pygame.draw.line(
            ventana, 
            (255, 255, 255), 
            (25, 25), 
            (55, 55), 
            5
        )

        pygame.draw.line(
            ventana, 
            (255, 255, 255), 
            (55, 25), 
            (25, 55), 
            5
        )
 
    pygame.display.flip() 
    reloj.tick(60) 
 
pygame.quit()