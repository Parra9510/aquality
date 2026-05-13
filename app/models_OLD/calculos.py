
def calcular_volumen(largo, ancho, profundidad):
    return largo * ancho * profundidad


def calcular_biomasa(cantidad, peso_promedio):
    return cantidad * peso_promedio


def calcular_fcr(alimento, ganancia):
    return alimento / ganancia


def calcular_gdp(peso_actual, peso_anterior, dias):
    return (peso_actual - peso_anterior) / dias