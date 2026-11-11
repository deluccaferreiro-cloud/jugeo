
import pygame
import os
import random
import math

def encontrar_archivo(nombre):
    carpeta_raiz = os.path.dirname(__file__)
    return os.path.join(carpeta_raiz, "assets", "minijuegos", "salto_nubes", nombre)

def crear_plataforma(anterior):
    y = anterior.y - random.randint(85, 110)
    desplazamiento = random.randint(55, 110)
    direccion = random.choice([-1, 1])
    x = anterior.x + desplazamiento * direccion
    x = max(15, min(x, ANCHO - ANCHO_PLATAFORMA - 15))
    return pygame.Rect(x, y, ANCHO_PLATAFORMA, ALTO_PLATAFORMA)

def obtener_zona(puntos):
    if puntos < 50:
        return 0
    elif puntos < 150:
        return 1
    elif puntos < 300:
        return 2
    elif puntos < 500:
        return 3
    return 4

def indice_img_plat(z):
    return 0 if z == 0 else (1 if z == 1 else 2)

def tiempo_juego():
    transcurrido = (pygame.time.get_ticks() - tiempo_inicio) // 1000
    return max(0, DURACION_JUEGO + tiempo_extra - transcurrido)

def crear_objeto(plataforma):
    tipo = random.choice([
        "moneda", "moneda", "moneda",
        "reloj", "resorte", "paraguas", "iman"
    ])

    x = random.randint(plataforma.left + 10, plataforma.right - 42)
    y = plataforma.top + MARGEN_SUPERIOR_PLAT - 32

    return {
        "tipo": tipo,
        "rect": pygame.Rect(x, y, 32, 32),
        "activo": True,
        "plataforma": plataforma
    }

def crear_nube_plataforma(y=None, x=None):
    if x is None:
        x = random.randint(0, ANCHO - ANCHO_NUBE)

    if y is None:
        y = plataformas[-1].y - random.randint(80, 115)

    x = max(0, min(x, ANCHO - ANCHO_NUBE))

    return pygame.Rect(x, y, ANCHO_NUBE, ALTO_NUBE)

def crear_avion(y):
    direccion = random.choice([-1, 1])

    if direccion == 1:
        x = -ANCHO_AVION
    else:
        x = ANCHO

    return {
        "rect": pygame.Rect(x, y, ANCHO_AVION, ALTO_AVION),
        "velocidad": direccion * random.randint(3, 5)
    }

pygame.init()

ANCHO = 800
ALTO = 500

DURACION_JUEGO = 60

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("SaltoPAUUU")

reloj = pygame.time.Clock()

pantalla_actual = "instrucciones"
jugando = True
game_over = False

tiempo_inicio = 0
tiempo_extra = 0

fondos = [
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("resubdelsuelo.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("salto.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("atmosfera.png")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("spacebar.jpg")).convert(),
        (ANCHO, ALTO)
    ),
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo("paraisopau.jpg")).convert(),
        (ANCHO, ALTO)
    )
]

ALTO_CAMBIO = 220

fondos_cambio = [
    pygame.transform.scale(
        pygame.image.load(encontrar_archivo(f"cambio{i}.png")).convert_alpha(),
        (ANCHO, ALTO_CAMBIO)
    )
    for i in range(1, 5)
]

transicion = None

imagen_instrucciones = pygame.transform.scale(
    pygame.image.load(encontrar_archivo("intro.jpg")).convert(),
    (ANCHO, ALTO)
)

pau = pygame.image.load(
    encontrar_archivo("paulanube.png")
).convert_alpha()

pau = pygame.transform.scale(pau, (55, 55))

plataformas_imagenes = [
    pygame.image.load(encontrar_archivo("piedraplat.png")).convert_alpha(),
    pygame.image.load(encontrar_archivo("plataforma.png")).convert_alpha(),
    pygame.image.load(encontrar_archivo("nubepau.png")).convert_alpha()
]

plataformas_imagenes = [
    pygame.transform.scale(imagen, (100, 100))
    for imagen in plataformas_imagenes
]

nube_imagen = pygame.image.load(
    encontrar_archivo("nube_peligrosa.png")
).convert_alpha()

nube_imagen = pygame.transform.scale(nube_imagen, (100, 60))

ANCHO_NUBE = 100
ALTO_NUBE = 60

avion_imagen = pygame.image.load(
    encontrar_archivo("avion.png")
).convert_alpha()

ANCHO_AVION = 120
ALTO_AVION = 65

avion_imagen = pygame.transform.scale(
    avion_imagen, (ANCHO_AVION, ALTO_AVION)
)

imagenes_objetos = {}

for nombre in ["reloj", "resorte", "moneda", "paraguas", "iman"]:
    imagen = pygame.image.load(
        encontrar_archivo(nombre + ".png")
    ).convert_alpha()

    imagenes_objetos[nombre] = pygame.transform.scale(imagen, (35, 35))

ANCHO_PAU = 55
ALTO_PAU = 55

ANCHO_PLATAFORMA = 100
ALTO_PLATAFORMA = 100

MARGEN_SUPERIOR_PLAT = 35
MARGEN_LATERAL_PLAT = 15
MARGEN_PIES_PAU = 8

ANCHO_BARRA = 220
ALTO_BARRA = 20

fuente = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 30)
fuente_grande = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 48)
fuente_barra = pygame.font.Font(encontrar_archivo("Cloudee.ttf"), 26)

boton_jugar = pygame.Rect(300, 390, 200, 60)
boton_salir = pygame.Rect(20, 435, 120, 45)

color_boton = (80, 190, 100)
color_boton_hover = (50, 160, 75)

color_salir = (190, 55, 55)
color_salir_hover = (230, 65, 65)

gravedad_normal = 0.45
gravedad = gravedad_normal

salto = -13

DURACION_PARAGUAS = 5000
DURACION_IMAN = 6000

tiempo_paraguas = 0
tiempo_iman = 0

record = 0

def dibujar_boton_salir():
    color_actual = (
        color_salir_hover
        if boton_salir.collidepoint(pygame.mouse.get_pos())
        else color_salir
    )

    pygame.draw.rect(
        ventana,
        color_actual,
        boton_salir,
        border_radius=10
    )

    texto_salir = fuente.render("SALIR", True, (255, 255, 255))

    ventana.blit(
        texto_salir,
        (
            boton_salir.centerx - texto_salir.get_width() // 2,
            boton_salir.centery - texto_salir.get_height() // 2
        )
    )

def reiniciar_juego():
    global x_pau, y_pau, velocidad_x, velocidad_y
    global puntos, zona_anterior, tiempo_inicio, tiempo_extra
    global plataformas, nubes_plataformas, objetos, aviones
    global velocidades_plataformas, game_over
    global gravedad, tiempo_paraguas, tiempo_iman
    global transicion
    global transiciones_mostradas, contador_nubes

    x_pau = ANCHO // 2
    y_pau = ALTO - 150

    velocidad_x = 0
    velocidad_y = 0

    gravedad = gravedad_normal

    tiempo_paraguas = 0
    tiempo_iman = 0

    puntos = 0
    zona_anterior = 0
    tiempo_extra = 0

    tiempo_inicio = pygame.time.get_ticks()

    transicion = None

    transiciones_mostradas = set()
    contador_nubes = 0

    plataformas = [
        pygame.Rect(
            ANCHO // 2 - 50,
            ALTO - 70,
            ANCHO_PLATAFORMA,
            ALTO_PLATAFORMA
        )
    ]

    nubes_plataformas = []
    aviones = []
    velocidades_plataformas = {}
    objetos = []

    for i in range(8):
        nueva = crear_plataforma(plataformas[-1])
        plataformas.append(nueva)

        if random.random() < 0.25:
            velocidades_plataformas[id(nueva)] = random.choice([-2, 2])

        if random.random() < 0.18:
            objetos.append(crear_objeto(nueva))

    game_over = False

reiniciar_juego()

while jugando:
    reloj.tick(60)

    if pantalla_actual == "juego" and not game_over:
        tiempo_restante = tiempo_juego()

        if tiempo_restante <= 0:
            game_over = True

    elif pantalla_actual == "instrucciones":
        tiempo_restante = DURACION_JUEGO

    else:
        tiempo_restante = tiempo_juego()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if boton_salir.collidepoint(evento.pos):
                    jugando = False

                elif pantalla_actual == "instrucciones":
                    if boton_jugar.collidepoint(evento.pos):
                        reiniciar_juego()
                        pantalla_actual = "juego"

        if evento.type == pygame.KEYDOWN:
            if pantalla_actual == "juego" and not game_over:
                if evento.key == pygame.K_LEFT:
                    velocidad_x = -5

                if evento.key == pygame.K_RIGHT:
                    velocidad_x = 5

            if evento.key == pygame.K_r and game_over:
                reiniciar_juego()
                pantalla_actual = "juego"

        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_LEFT and velocidad_x < 0:
                velocidad_x = 0

            if evento.key == pygame.K_RIGHT and velocidad_x > 0:
                velocidad_x = 0

    if not jugando:
        break

    if pantalla_actual == "instrucciones":
        ventana.blit(imagen_instrucciones, (0, 0))

        titulo = fuente_grande.render("SKY PAU", True, (255, 255, 255))
        ventana.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 35))

        instrucciones = [
            "Evita que PAU caiga al vacio", 
            "saltando de plataqforma en plataforma",
            "PAU se mueve utilizando las flechas derecha e izquierda",
            "NIVELES: 0-50: subsuelo",
            "50-150: superficie",
            "150-300: atmosfera",
            "300-500: espacio",
            "500 - +: paraiso",
        ]

        for i, linea in enumerate(instrucciones):
            texto = fuente.render(linea, True, (255, 255, 255))

            ventana.blit(
                texto,
                (ANCHO // 2 - texto.get_width() // 2, 90 + i * 35)
            )

        color_actual = (
            color_boton_hover
            if boton_jugar.collidepoint(pygame.mouse.get_pos())
            else color_boton
        )

        pygame.draw.rect(
            ventana, color_actual, boton_jugar, border_radius=12
        )

        texto_boton = fuente.render("JUGAR", True, (255, 255, 255))

        ventana.blit(
            texto_boton,
            (
                boton_jugar.centerx - texto_boton.get_width() // 2,
                boton_jugar.centery - texto_boton.get_height() // 2
            )
        )

        dibujar_boton_salir()

        pygame.display.update()
        continue

    if not game_over:
        y_anterior = y_pau

        x_pau += velocidad_x

        velocidad_y += gravedad
        y_pau += velocidad_y

        if x_pau < -ANCHO_PAU:
            x_pau = ANCHO

        if x_pau > ANCHO:
            x_pau = -ANCHO_PAU

        rect_pau = pygame.Rect(
            x_pau + 10,
            y_pau + 10,
            ANCHO_PAU - 20,
            ALTO_PAU - 20
        )

        for plataforma in plataformas:
            velocidad_plataforma = velocidades_plataformas.get(id(plataforma), 0)

            if velocidad_plataforma != 0:
                x_anterior_plataforma = plataforma.x

                plataforma.x += velocidad_plataforma

                if plataforma.left <= 0:
                    plataforma.left = 0
                    velocidades_plataformas[id(plataforma)] *= -1

                if plataforma.right >= ANCHO:
                    plataforma.right = ANCHO
                    velocidades_plataformas[id(plataforma)] *= -1

                desplazamiento_x = plataforma.x - x_anterior_plataforma

                for objeto in objetos:
                    if objeto["plataforma"] is plataforma:
                        objeto["rect"].x += desplazamiento_x

        for avion in aviones:
            avion["rect"].x += avion["velocidad"]

        aviones = [
            avion for avion in aviones
            if avion["rect"].right > 0 and avion["rect"].left < ANCHO
        ]

        if velocidad_y > 0:
            pies_anterior = y_anterior + ALTO_PAU - MARGEN_PIES_PAU
            pies_actual = y_pau + ALTO_PAU - MARGEN_PIES_PAU

            todas_plataformas = plataformas + nubes_plataformas

            for plataforma in todas_plataformas:
                es_nube = plataforma in nubes_plataformas

                if es_nube:
                    superficie = plataforma.top + 10
                    izquierda = plataforma.left + 12
                    derecha = plataforma.right - 12
                else:
                    superficie = plataforma.top + MARGEN_SUPERIOR_PLAT
                    izquierda = plataforma.left + MARGEN_LATERAL_PLAT
                    derecha = plataforma.right - MARGEN_LATERAL_PLAT

                if (
                    pies_anterior <= superficie
                    and pies_actual >= superficie
                    and rect_pau.right > izquierda
                    and rect_pau.left < derecha
                ):
                    y_pau = superficie - ALTO_PAU + MARGEN_PIES_PAU
                    velocidad_y = salto
                    puntos += 1

                    if es_nube:
                        nubes_plataformas.remove(plataforma)

                    break

        if y_pau < ALTO // 2:
            diferencia = ALTO // 2 - y_pau
            y_pau = ALTO // 2

            for plataforma in plataformas:
                plataforma.y += diferencia

            for nube in nubes_plataformas:
                nube.y += diferencia

            for objeto in objetos:
                objeto["rect"].y += diferencia

            for avion in aviones:
                avion["rect"].y += diferencia

            if transicion is not None:
                transicion["y"] += diferencia

        plataformas = [
            plataforma for plataforma in plataformas
            if plataforma.y < ALTO + 100
        ]

        velocidades_plataformas = {
            id(plataforma): velocidades_plataformas[id(plataforma)]
            for plataforma in plataformas
            if id(plataforma) in velocidades_plataformas
        }

        nubes_plataformas = [
            nube for nube in nubes_plataformas
            if nube.y < ALTO + 100
        ]

        objetos = [
            objeto for objeto in objetos
            if objeto["rect"].y < ALTO + 100
        ]

        while plataformas and plataformas[-1].y > -100:
            nueva_plataforma = crear_plataforma(plataformas[-1])
            plataformas.append(nueva_plataforma)

            if random.random() < 0.25:
                velocidades_plataformas[id(nueva_plataforma)] = random.choice([-2, 2])

            if random.random() < 0.18:
                objetos.append(crear_objeto(nueva_plataforma))

            zona_actual = obtener_zona(puntos)

            if zona_actual >= 1 and random.random() < 0.20:
                aviones.append(
                    crear_avion(
                        nueva_plataforma.y + random.randint(-30, 40)
                    )
                )

            if zona_actual == 1 and random.random() < 0.35:
                desplazamiento_nube = -115 if contador_nubes % 2 == 0 else 115

                x_nube = nueva_plataforma.x + desplazamiento_nube
                x_nube = max(0, min(x_nube, ANCHO - ANCHO_NUBE))

                y_nube = nueva_plataforma.y + 55

                nubes_plataformas.append(
                    crear_nube_plataforma(y_nube, x_nube)
                )

                contador_nubes += 1

        ahora = pygame.time.get_ticks()

        if ahora > tiempo_paraguas:
            gravedad = gravedad_normal
        else:
            gravedad = gravedad_normal * 0.45

        iman_activo = ahora <= tiempo_iman

        for objeto in objetos[:]:
            rect_objeto = objeto["rect"]

            if objeto["tipo"] == "moneda" and iman_activo:
                dx = x_pau + ANCHO_PAU // 2 - rect_objeto.centerx
                dy = y_pau + ALTO_PAU // 2 - rect_objeto.centery

                distancia = math.hypot(dx, dy)

                if 0 < distancia < 220:
                    rect_objeto.x += int(dx / distancia * 4)
                    rect_objeto.y += int(dy / distancia * 4)

            if rect_pau.colliderect(rect_objeto):
                tipo = objeto["tipo"]

                if tipo == "moneda":
                    puntos += 1

                elif tipo == "reloj":
                    tiempo_extra += 5

                elif tipo == "resorte":
                    velocidad_y = -20

                elif tipo == "paraguas":
                    tiempo_paraguas = ahora + DURACION_PARAGUAS
                    gravedad = gravedad_normal * 0.45

                elif tipo == "iman":
                    tiempo_iman = ahora + DURACION_IMAN
                    iman_activo = True

                objetos.remove(objeto)

        if y_pau > ALTO:
            game_over = True

        if puntos > record:
            record = puntos

    zona = obtener_zona(puntos)

    limites_transicion = [47, 147, 297, 497]

    if pantalla_actual == "juego":
        for i, limite in enumerate(limites_transicion):
            if puntos >= limite and i not in transiciones_mostradas:
                transicion = {"i": i, "y": -ALTO_CAMBIO}
                transiciones_mostradas.add(i)

    corte = None

    if transicion is None:
        ventana.blit(fondos[zona], (0, 0))
    else:
        corte = transicion["y"] + ALTO_CAMBIO // 2

        if corte >= ALTO:
            transicion = None
            corte = None
            ventana.blit(fondos[zona], (0, 0))
        else:
            ventana.blit(fondos[transicion["i"] + 1], (0, 0))

            corte_y = max(0, corte)
            ventana.blit(
                fondos[transicion["i"]],
                (0, corte_y),
                pygame.Rect(0, corte_y, ANCHO, ALTO - corte_y)
            )

    for plataforma in plataformas:
        if transicion is not None and corte is not None:
            if plataforma.centery < corte:
                z_plat = transicion["i"] + 1
            else:
                z_plat = transicion["i"]
        else:
            z_plat = zona

        ventana.blit(plataformas_imagenes[indice_img_plat(z_plat)], plataforma)

    if zona == 1:
        for nube in nubes_plataformas:
            ventana.blit(nube_imagen, nube)

    for avion in aviones:
        ventana.blit(avion_imagen, avion["rect"])

    for objeto in objetos:
        tipo = objeto["tipo"]
        rect_objeto = objeto["rect"]

        if tipo in imagenes_objetos:
            ventana.blit(imagenes_objetos[tipo], rect_objeto)

    if transicion is not None:
        ventana.blit(fondos_cambio[transicion["i"]], (0, transicion["y"]))

    ventana.blit(pau, (x_pau, y_pau))

    texto_puntos = fuente.render(
        "Puntos: " + str(puntos), True, (255, 255, 255)
    )

    ventana.blit(texto_puntos, (20, 20))

    texto_record = fuente.render(
        "Record: " + str(record), True, (255, 255, 255)
    )

    ventana.blit(texto_record, (20, 55))

    texto_tiempo = fuente_barra.render(
        "Tiempo: " + str(tiempo_restante) + " s",
        True, (255, 255, 255)
    )

    barra_x = ANCHO - ANCHO_BARRA - 20
    barra_y = 55

    ventana.blit(texto_tiempo, (barra_x, 20))

    pygame.draw.rect(
        ventana, (45, 45, 45),
        (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
        border_radius=8
    )

    ancho_actual = int(
        ANCHO_BARRA * tiempo_restante / DURACION_JUEGO
    )

    ancho_actual = max(0, min(ANCHO_BARRA, ancho_actual))

    if tiempo_restante > 30:
        color_barra = (40, 210, 80)
    elif tiempo_restante > 10:
        color_barra = (255, 200, 40)
    else:
        color_barra = (230, 50, 50)

    if ancho_actual > 0:
        pygame.draw.rect(
            ventana, color_barra,
            (barra_x, barra_y, ancho_actual, ALTO_BARRA),
            border_radius=8
        )

    pygame.draw.rect(
        ventana, (255, 255, 255),
        (barra_x, barra_y, ANCHO_BARRA, ALTO_BARRA),
        2, border_radius=8
    )

    nombres_zonas = [
        "Subsuelo",
        "Superficie",
        "Atmósfera",
        "Espacio",
        "Paraíso"
    ]

    texto_zona = fuente.render(
        nombres_zonas[zona], True, (255, 255, 255)
    )

    ventana.blit(
        texto_zona,
        (ANCHO - texto_zona.get_width() - 20, 90)
    )

    if tiempo_paraguas > pygame.time.get_ticks():
        texto_efecto = fuente.render(
            "Paraguas activo", True, (255, 255, 255)
        )

        ventana.blit(texto_efecto, (ANCHO - 230, 125))

    if tiempo_iman > pygame.time.get_ticks():
        texto_efecto = fuente.render(
            "Iman activo", True, (255, 255, 255)
        )

        ventana.blit(texto_efecto, (ANCHO - 230, 160))

    if game_over:
        pygame.draw.rect(
            ventana,
            (25, 25, 25),
            (100, 140, 600, 230),
            border_radius=18
        )

        texto = fuente_grande.render(
            "GAME OVER",
            True,
            (255, 80, 80)
        )

        ventana.blit(
            texto,
            (ANCHO // 2 - texto.get_width() // 2, 155)
        )

        texto_puntos_finales = fuente.render(
            "Puntos conseguidos: " + str(puntos),
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto_puntos_finales,
            (
                ANCHO // 2 - texto_puntos_finales.get_width() // 2,
                225
            )
        )

        texto_record_final = fuente.render(
            "Record: " + str(record),
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto_record_final,
            (
                ANCHO // 2 - texto_record_final.get_width() // 2,
                265
            )
        )

        texto_reinicio = fuente.render(
            "Presiona R para reiniciar",
            True,
            (255, 255, 255)
        )

        ventana.blit(
            texto_reinicio,
            (
                ANCHO // 2 - texto_reinicio.get_width() // 2,
                315
            )
        )

    dibujar_boton_salir()

    pygame.display.update()

pygame.quit()
