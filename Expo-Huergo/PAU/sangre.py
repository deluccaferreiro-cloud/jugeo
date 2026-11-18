"""Efecto de sangre para el "modo diablo" (Pau tomó la poción matadora).

Lo usa el juego principal y también los minijuegos que se abren en otra
ventana: esos lo activan con la variable de entorno PAU_MALDITO=1.
"""
import math
import os
import random

import pygame

_cache = {}


def activo():
    return os.environ.get("PAU_MALDITO") == "1"


def _preparar(ancho, alto):
    """Manchas fijas (viñeta, sangre del techo, salpicaduras) y chorros."""
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    azar = random.Random(666)
    for i in range(40):                             # viñeta roja oscura
        a = int(160 * (1 - i / 40) ** 2)
        pygame.draw.rect(s, (70, 0, 0, a), (i * 4, i * 4, ancho - i * 8, alto - i * 8), 4)
    for _ in range(26):                             # sangre que cae del techo
        x = azar.randint(0, ancho)
        r = azar.randint(10, 28)
        pygame.draw.circle(s, (120, 0, 0, 230), (x, azar.randint(-r, 4)), r)
    for _ in range(9):                              # salpicaduras
        cx, cy = azar.randint(40, ancho - 40), azar.randint(120, alto - 40)
        pygame.draw.circle(s, (110, 0, 0, 170), (cx, cy), azar.randint(6, 14))
        for _ in range(9):
            ang = azar.uniform(0, math.tau)
            d = azar.uniform(10, 38)
            pygame.draw.circle(s, (110, 0, 0, 170),
                               (int(cx + math.cos(ang) * d), int(cy + math.sin(ang) * d)),
                               azar.randint(2, 5))
    chorros = [{"x": azar.randint(5, ancho - 5), "ancho": azar.randint(4, 11),
                "largo": azar.randint(60, int(alto * 0.53)), "vel": azar.uniform(8, 25),
                "fase": azar.uniform(0, 1)} for _ in range(22)]
    return s, chorros


def aplicar(sup, forzar=False):
    """Tiñe TODO de rojo y le pone sangre chorreando."""
    if not (forzar or activo()):
        return
    tam = sup.get_size()
    if tam not in _cache:
        _cache[tam] = _preparar(*tam)
    manchas, chorros = _cache[tam]
    sup.fill((255, 105, 100), special_flags=pygame.BLEND_RGB_MULT)
    sup.blit(manchas, (0, 0))
    t = pygame.time.get_ticks() / 1000
    for c in chorros:
        ciclo = c["largo"] / c["vel"] + 3
        prog = ((t / ciclo) + c["fase"]) % 1
        largo = int(min(1, prog * 1.4) * c["largo"])
        pygame.draw.rect(sup, (125, 0, 0), (c["x"] - c["ancho"] // 2, 0, c["ancho"], largo))
        pygame.draw.circle(sup, (125, 0, 0), (c["x"], largo), c["ancho"] // 2 + 3)
