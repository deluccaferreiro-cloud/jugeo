"""Cada sistema vive en su propio módulo.

Regla de oro: estos módulos NUNCA importan 'principal' (evita imports
circulares, porque principal.py ejecuta código al importarse). Reciben datos
por parámetro y devuelven resultados; principal.py los aplica.
"""