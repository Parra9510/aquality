def validar_oxigeno(valor):

    if valor < 4:
        return "CRÍTICO"

    elif valor < 5:
        return "ADVERTENCIA"

    return "NORMAL"