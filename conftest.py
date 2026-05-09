"""
conftest.py – Configuración global de pytest.
Asegura que el directorio raíz del proyecto esté en sys.path.
"""
import sys
import os

# Permite importar los módulos del proyecto sin instalar el paquete
sys.path.insert(0, os.path.dirname(__file__))
