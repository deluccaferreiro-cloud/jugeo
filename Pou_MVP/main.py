
import pygame
import os
import json
import random
import sys

# =========================================================
# CONFIGURACIÓN
# =========================================================

ANCHO = 800
ALTO = 600
FPS = 60

pygame.init()

PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pou MVP")

RELOJ = pygame.time.Clock()

# =========================================================
# RUTAS DE LAS IMÁGENES
# =========================================================

CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_ASSETS = os.path.join(CARPETA_PROYECTO, "assets")

RUTA_POU = os.path.join(CARPETA_ASSETS, "pau.png")
RUTA_POU_FELIZ = os.path.join(CARPETA_ASSETS, "paufeliz.png")

# =========================================================
# CARGAR IMÁGENES
# =========================================================

def cargar_imagen(ruta, nombre):
    if not os.path.exists(ruta):
        print()
        print("==========================================")
        print("ERROR: NO SE ENCONTRÓ LA IMAGEN")
        print("==========================================")
        print("Buscando:", ruta)
        print()
        print("Asegurate de tener:")
        print("assets/")
        print("   pau.png")
        print("   paufeliz.png")
        print("==========================================")
        print()
        return None

    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        print("Imagen cargada correctamente:", nombre)
        return imagen
    except Exception as e:
        print()
        print("ERROR AL CARGAR:", nombre)
        print(e)
        return None


POU_NORMAL = cargar_imagen(RUTA_POU, "pau.png")
POU_FELIZ = cargar_imagen(RUTA_POU_FELIZ, "paufeliz.png")


# =========================================================
# FUENTES
# =========================================================

FUENTE = pygame.font.SysFont("Arial", 20, bold=True)
FUENTE_GRANDE = pygame.font.SysFont("Arial", 28, bold=True)
FUENTE_PEQUENA = pygame.font.SysFont("Arial", 16)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def limitar(valor, minimo=0, maximo=100):
    return max(minimo, min(maximo, valor))


def texto(superficie, contenido, fuente, color, x, y, centrado=True):
    imagen = fuente.render(contenido, True, color)

    if centrado:
        rect = imagen.get_rect(center=(x, y))
    else:
        rect = imagen.get_rect(topleft=(x, y))

    superficie.blit(imagen, rect)


# =========================================================
# CLASE POU
# =========================================================

class Pou:

    def __init__(self):
        self.coins = 100

        self.health = 80
        self.food = 80
        self.energy = 80
        self.fun = 80

        self.mensaje = "¡Hola!"

        self.imagen_actual = POU_NORMAL

    # -----------------------------------------------------
    # ¿ESTÁ FELIZ?
    # -----------------------------------------------------

    def esta_feliz(self):
        return (
            self.health >= 100
            and self.food >= 100
            and self.energy >= 100
            and self.fun >= 100
        )

    # -----------------------------------------------------
    # ACTUALIZAR IMAGEN
    # -----------------------------------------------------

    def actualizar_imagen(self):

        if self.esta_feliz():

            if POU_FELIZ is not None:
                self.imagen_actual = POU_FELIZ

        else:

            if POU_NORMAL is not None:
                self.imagen_actual = POU_NORMAL

    # -----------------------------------------------------
    # COMIDA
    # -----------------------------------------------------

    def comer(self):

        self.food = limitar(self.food + 20)
        self.health = limitar(self.health + 5)

        self.mensaje = "¡Ñam ñam!"

        self.actualizar_imagen()

    # -----------------------------------------------------
    # BAÑO
    # -----------------------------------------------------

    def banarse(self):

        self.health = limitar(self.health + 10)

        self.mensaje = "¡Qué limpio!"

        self.actualizar_imagen()

    # -----------------------------------------------------
    # JUGAR
    # -----------------------------------------------------

    def jugar(self):

        self.fun = limitar(self.fun + 25)
        self.energy = limitar(self.energy - 10)

        self.mensaje = "¡Qué divertido!"

        self.actualizar_imagen()

    # -----------------------------------------------------
    # DORMIR
    # -----------------------------------------------------

    def dormir(self):

        self.energy = limitar(self.energy + 30)

        self.mensaje = "Zzz..."

        self.actualizar_imagen()

    # -----------------------------------------------------
    # PASO DEL TIEMPO
    # -----------------------------------------------------

    def actualizar(self):

        self.food = limitar(self.food - 0.003)
        self.energy = limitar(self.energy - 0.002)
        self.fun = limitar(self.fun - 0.002)

        if self.food < 20:
            self.health = limitar(self.health - 0.002)

        self.actualizar_imagen()

    # -----------------------------------------------------
    # DIBUJAR POU
    # -----------------------------------------------------

    def dibujar(self, superficie):

        if self.imagen_actual is None:

            # Si por alguna razón no cargó la imagen,
            # mostramos un aviso en pantalla.

            pygame.draw.rect(
                superficie,
                (220, 220, 220),
                (300, 160, 200, 250),
                border_radius=20
            )

            texto(
                superficie,
                "NO SE ENCONTRÓ",
                FUENTE,
                (180, 0, 0),
                400,
                250
            )

            texto(
                superficie,
                "pau.png",
                FUENTE,
                (180, 0, 0),
                400,
                280
            )

            return

        ancho_original = self.imagen_actual.get_width()
        alto_original = self.imagen_actual.get_height()

        # Tamaño máximo del Pou
        max_ancho = 220
        max_alto = 300

        escala = min(
            max_ancho / ancho_original,
            max_alto / alto_original
        )

        nuevo_ancho = int(ancho_original * escala)
        nuevo_alto = int(alto_original * escala)

        imagen_redimensionada = pygame.transform.smoothscale(
            self.imagen_actual,
            (nuevo_ancho, nuevo_alto)
        )

        rect = imagen_redimensionada.get_rect(
            center=(400, 315)
        )

        superficie.blit(
            imagen_redimensionada,
            rect
        )


# =========================================================
# BOTONES CIRCULARES
# =========================================================

botones = [

    {
        "nombre": "COMIDA",
        "pos": (80, 525)
    },

    {
        "nombre": "BAÑO",
        "pos": (240, 525)
    },

    {
        "nombre": "JUGAR",
        "pos": (400, 525)
    },

    {
        "nombre": "DORMIR",
        "pos": (560, 525)
    },

    {
        "nombre": "TIENDA",
        "pos": (720, 525)
    }
]


def dibujar_boton(superficie, boton):

    x, y = boton["pos"]

    pygame.draw.circle(
        superficie,
        (245, 245, 245),
        (x, y),
        43
    )

    pygame.draw.circle(
        superficie,
        (80, 80, 80),
        (x, y),
        43,
        2
    )

    texto(
        superficie,
        boton["nombre"],
        pygame.font.SysFont("Arial", 12, bold=True),
        (30, 30, 30),
        x,
        y
    )


# =========================================================
# ESTADÍSTICAS
# =========================================================

def dibujar_barra(superficie, nombre, valor, x, y):

    texto(
        superficie,
        nombre,
        FUENTE_PEQUENA,
        (40, 40, 40),
        x,
        y - 2,
        False
    )

    pygame.draw.rect(
        superficie,
        (220, 220, 220),
        (x + 75, y, 150, 15),
        border_radius=8
    )

    pygame.draw.rect(
        superficie,
        (80, 180, 100),
        (x + 75, y, int(150 * valor / 100), 15),
        border_radius=8
    )

    texto(
        superficie,
        str(int(valor)),
        FUENTE_PEQUENA,
        (40, 40, 40),
        x + 235,
        y + 7
    )


def dibujar_estadisticas(superficie, pou):

    dibujar_barra(
        superficie,
        "SALUD",
        pou.health,
        30,
        25
    )

    dibujar_barra(
        superficie,
        "COMIDA",
        pou.food,
        30,
        55
    )

    dibujar_barra(
        superficie,
        "ENERGÍA",
        pou.energy,
        30,
        85
    )

    dibujar_barra(
        superficie,
        "DIVERSIÓN",
        pou.fun,
        30,
        115
    )


# =========================================================
# MENSAJE
# =========================================================

def dibujar_mensaje(superficie, pou):

    texto(
        superficie,
        pou.mensaje,
        FUENTE,
        (40, 40, 40),
        400,
        465
    )


# =========================================================
# GUARDAR PARTIDA
# =========================================================

def guardar(pou):

    datos = {
        "coins": pou.coins,
        "health": pou.health,
        "food": pou.food,
        "energy": pou.energy,
        "fun": pou.fun
    }

    with open(
        os.path.join(CARPETA_PROYECTO, "save.json"),
        "w"
    ) as archivo:

        json.dump(datos, archivo)


# =========================================================
# CARGAR PARTIDA
# =========================================================

def cargar(pou):

    ruta = os.path.join(
        CARPETA_PROYECTO,
        "save.json"
    )

    if not os.path.exists(ruta):
        return

    try:

        with open(ruta, "r") as archivo:
            datos = json.load(archivo)

        pou.coins = datos.get("coins", 100)
        pou.health = datos.get("health", 80)
        pou.food = datos.get("food", 80)
        pou.energy = datos.get("energy", 80)
        pou.fun = datos.get("fun", 80)

        pou.actualizar_imagen()

    except Exception as e:

        print("No se pudo cargar save.json:", e)


# =========================================================
# TIENDA
# =========================================================

def mostrar_tienda(superficie, pou):

    overlay = pygame.Surface((ANCHO, ALTO))
    overlay.set_alpha(220)
    overlay.fill((255, 255, 255))

    superficie.blit(overlay, (0, 0))

    texto(
        superficie,
        "TIENDA",
        FUENTE_GRANDE,
        (30, 30, 30),
        400,
        80
    )

    texto(
        superficie,
        "Monedas: " + str(pou.coins),
        FUENTE,
        (30, 30, 30),
        400,
        120
    )

    texto(
        superficie,
        "La tienda estará disponible próximamente",
        FUENTE,
        (50, 50, 50),
        400,
        280
    )

    texto(
        superficie,
        "Presioná ESC para volver",
        FUENTE_PEQUENA,
        (100, 100, 100),
        400,
        500
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    pou = Pou()

    cargar(pou)

    ejecutando = True
    en_tienda = False

    while ejecutando:

        dt = RELOJ.tick(FPS)

        # -------------------------------------------------
        # EVENTOS
        # -------------------------------------------------

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                ejecutando = False

            if evento.type == pygame.KEYDOWN:

                if evento.key == pygame.K_ESCAPE:

                    if en_tienda:
                        en_tienda = False

                    else:
                        ejecutando = False

            if evento.type == pygame.MOUSEBUTTONDOWN:

                if evento.button == 1:

                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    if en_tienda:

                        continue

                    # -----------------------------
                    # COMIDA
                    # -----------------------------

                    if pygame.Vector2(
                        mouse_x,
                        mouse_y
                    ).distance_to(
                        botones[0]["pos"]
                    ) <= 43:

                        pou.comer()

                    # -----------------------------
                    # BAÑO
                    # -----------------------------

                    elif pygame.Vector2(
                        mouse_x,
                        mouse_y
                    ).distance_to(
                        botones[1]["pos"]
                    ) <= 43:

                        pou.banarse()

                    # -----------------------------
                    # JUGAR
                    # -----------------------------

                    elif pygame.Vector2(
                        mouse_x,
                        mouse_y
                    ).distance_to(
                        botones[2]["pos"]
                    ) <= 43:

                        pou.jugar()

                    # -----------------------------
                    # DORMIR
                    # -----------------------------

                    elif pygame.Vector2(
                        mouse_x,
                        mouse_y
                    ).distance_to(
                        botones[3]["pos"]
                    ) <= 43:

                        pou.dormir()

                    # -----------------------------
                    # TIENDA
                    # -----------------------------

                    elif pygame.Vector2(
                        mouse_x,
                        mouse_y
                    ).distance_to(
                        botones[4]["pos"]
                    ) <= 43:

                        en_tienda = True

                    guardar(pou)

        # -------------------------------------------------
        # ACTUALIZAR
        # -------------------------------------------------

        if not en_tienda:

            pou.actualizar()

        # -------------------------------------------------
        # FONDO
        # -------------------------------------------------

        PANTALLA.fill((174, 228, 255))

        # -------------------------------------------------
        # ESTADÍSTICAS
        # -------------------------------------------------

        if not en_tienda:

            dibujar_estadisticas(
                PANTALLA,
                pou
            )

            # -------------------------------------------------
            # POU
            # -------------------------------------------------

            pou.dibujar(PANTALLA)

            # -------------------------------------------------
            # MENSAJE
            # -------------------------------------------------

            dibujar_mensaje(
                PANTALLA,
                pou
            )

            # -------------------------------------------------
            # BOTONES
            # -------------------------------------------------

            for boton in botones:

                dibujar_boton(
                    PANTALLA,
                    boton
                )

        else:

            mostrar_tienda(
                PANTALLA,
                pou
            )

        pygame.display.flip()

    guardar(pou)

    pygame.quit()
    sys.exit()


# =========================================================
# INICIAR
# =========================================================

if __name__ == "__main__":
    main()