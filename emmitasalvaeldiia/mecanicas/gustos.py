import random

from . import config as C

FAVORITA = "favorita"
ODIADA = "odiada"
NORMAL = "normal"


class Gustos:
    def __init__(self, nombres_comidas, azar=None):
        self.comidas = list(nombres_comidas)
        self._azar = azar or random.Random()
        self.favoritas = []
        self.odiadas = []
        self.probadas = set()
        self.generar()

    # --- Creación -----------------------------------------------------------
    def generar(self):
        """Sortea gustos nuevos (Pau recién nacida) y olvida lo descubierto."""
        mezcladas = list(self.comidas)
        self._azar.shuffle(mezcladas)

        n_fav = self._azar.randint(*C.GUSTOS_CANT_FAVORITAS)
        n_fav = max(0, min(n_fav, len(mezcladas) - C.GUSTOS_CANT_ODIADAS))
        self.favoritas = mezcladas[:n_fav]

        candidatas = [c for c in mezcladas[n_fav:] if c not in C.NUNCA_ODIADAS]
        self.odiadas = candidatas[:C.GUSTOS_CANT_ODIADAS]
        self.probadas = set()

    # --- Consultas ----------------------------------------------------------
    def tipo(self, nombre):
        if nombre in self.favoritas:
            return FAVORITA
        if nombre in self.odiadas:
            return ODIADA
        return NORMAL

    def tipo_visible(self, nombre):
        """Lo que el jugador sabe: None si todavía no la probó."""
        return self.tipo(nombre) if nombre in self.probadas else None

    def descubiertos(self):
        """(especiales descubiertos, total de especiales) para mostrar progreso."""
        especiales = self.favoritas + self.odiadas
        return sum(1 for c in especiales if c in self.probadas), len(especiales)

    # --- Acción -------------------------------------------------------------
    def probar(self, nombre):
        """Pau prueba una comida. Devuelve (tipo, es_la_primera_vez)."""
        nueva = nombre not in self.probadas
        self.probadas.add(nombre)
        return self.tipo(nombre), nueva

    # --- Guardado -----------------------------------------------------------
    def a_dict(self):
        return {
            "favoritas": list(self.favoritas),
            "odiadas": list(self.odiadas),
            "probadas": sorted(self.probadas),
        }

    def desde_dict(self, datos):
        """Carga lo guardado. Si no hay datos válidos (partida vieja), sortea
        gustos nuevos. Devuelve True si cargó, False si tuvo que generar."""
        if not isinstance(datos, dict):
            self.generar()
            return False
        validas = set(self.comidas)
        fav = [c for c in datos.get("favoritas", []) if c in validas]
        odi = [c for c in datos.get("odiadas", []) if c in validas and c not in fav]
        if not fav or not odi:
            self.generar()
            return False
        self.favoritas = fav
        self.odiadas = odi
        self.probadas = {c for c in datos.get("probadas", []) if c in validas}
        return True