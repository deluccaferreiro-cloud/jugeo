import random

from . import config as C


class Caricias:
    def __init__(self):
        self.conteo = {}            # zona -> veces acariciada (para personalidad/álbum)
        self._historial = []        # ms de las últimas caricias (detecta exceso)
        self._ultima = -10 ** 9
        self._ultima_zona = None
        self._molesta_hasta = 0

    def reiniciar(self):
        self.__init__()

    # --- Geometría ----------------------------------------------------------
    def rects_zonas(self, centro):
        """[(nombre, (x, y, ancho, alto)), ...] en coordenadas de pantalla."""
        res = []
        for nombre, rects in C.CARICIAS_ZONAS:
            for dx, dy, w, h in rects:
                res.append((nombre, (centro[0] + dx, centro[1] + dy, w, h)))
        return res

    def zona_en(self, pos, centro):
        for nombre, (x, y, w, h) in self.rects_zonas(centro):
            if x <= pos[0] < x + w and y <= pos[1] < y + h:
                return nombre
        return "cuerpo"

    def esta_molesta(self, ahora):
        return ahora < self._molesta_hasta

    # --- Acción -------------------------------------------------------------
    def tocar(self, pos, centro, ahora):
        """Devuelve un dict con la reacción, o None si hay que ignorar el toque."""
        if ahora - self._ultima < C.CARICIA_COOLDOWN_MS or self.esta_molesta(ahora):
            return None
        self._ultima = ahora

        self._historial = [t for t in self._historial if ahora - t < C.CARICIA_VENTANA_MS]
        self._historial.append(ahora)
        if len(self._historial) > C.CARICIA_MAX_EN_VENTANA:
            self._historial = []
            self._molesta_hasta = ahora + C.CARICIA_MOLESTA_MS
            self._ultima_zona = None
            return self._reaccion("molesta", C.CARICIA_MOLESTA_MS, decir=True)

        zona = self.zona_en(pos, centro)
        self.conteo[zona] = self.conteo.get(zona, 0) + 1
        decir = zona != self._ultima_zona or random.random() < C.CARICIA_PROB_FRASE
        self._ultima_zona = zona
        return self._reaccion(zona, C.CARICIA_REACCION_MS, decir)

    def _reaccion(self, zona, ms, decir):
        datos = C.CARICIAS_REACCIONES[zona]
        return {
            "zona": zona,
            "jugar": datos["jugar"],
            "cara": datos["cara"],
            "anim": datos["anim"],
            "particula": datos["particula"],
            "frase": random.choice(datos["frases"]) if decir and datos["frases"] else None,
            "ms": ms,
        }

    # --- Guardado -----------------------------------------------------------
    def a_dict(self):
        return {"conteo": dict(self.conteo)}

    def desde_dict(self, datos):
        self.reiniciar()
        if isinstance(datos, dict) and isinstance(datos.get("conteo"), dict):
            for k, v in datos["conteo"].items():
                try:
                    self.conteo[str(k)] = max(0, int(v))
                except (TypeError, ValueError):
                    pass