"""
config/settings.py
Configuración central de AQUALITY.
"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aquality.db")

# API externa: Open-Meteo (datos climáticos/ambientales, sin API key)
WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast"

# Umbrales fisicoquímicos seguros para trucha arcoíris
PARAMETROS_SEGUROS = {
    "temperatura": {"min": 10.0, "max": 18.0, "unidad": "°C"},
    "ph":          {"min": 6.5,  "max": 8.5,  "unidad": "pH"},
    "oxigeno":     {"min": 7.0,  "max": 12.0, "unidad": "mg/L"},
}

APP_TITLE   = "AQUALITY – Sistema Integral para la Optimización Acuícola"
APP_VERSION = "0.1.0-beta"
