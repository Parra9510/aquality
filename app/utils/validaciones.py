"""
app/utils/validaciones.py
Funciones de validación reutilizables en toda la aplicación.
"""
import re
from typing import Any


def validar_email(email: str) -> bool:
    """Valida formato básico de correo electrónico."""
    patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(patron, email))


def validar_cedula(cedula: str) -> bool:
    """Valida que la cédula tenga entre 6 y 10 dígitos."""
    return cedula.isdigit() and 6 <= len(cedula) <= 10


def validar_rango_numerico(valor: Any, minimo: float, maximo: float,
                            nombre_campo: str = "valor") -> float:
    """Convierte y valida que un valor esté dentro de un rango."""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{nombre_campo}' debe ser un número, se recibió: {valor!r}")
    if not (minimo <= v <= maximo):
        raise ValueError(
            f"'{nombre_campo}' debe estar entre {minimo} y {maximo}. Recibido: {v}"
        )
    return v


def sanitizar_texto(texto: str, max_len: int = 200) -> str:
    """Elimina espacios extremos y trunca el texto."""
    if not isinstance(texto, str):
        raise TypeError("Se esperaba una cadena de texto.")
    return texto.strip()[:max_len]
