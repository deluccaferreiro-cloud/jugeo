_oyentes = {}


def suscribir(evento, funcion):
    lista = _oyentes.setdefault(evento, [])
    if funcion not in lista:
        lista.append(funcion)


def desuscribir(evento, funcion):
    if funcion in _oyentes.get(evento, []):
        _oyentes[evento].remove(funcion)


def emitir(evento, **datos):
    for funcion in list(_oyentes.get(evento, [])):
        try:
            funcion(**datos)
        except Exception as e:          # un sistema roto no debe tirar el juego
            print(f"[AVISO] Error en oyente de '{evento}': {e}")