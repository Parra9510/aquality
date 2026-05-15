"""
app/core/config.py
Configuración central de AQUALITY.
Lee variables de entorno con valores por defecto seguros.
"""
import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# --- Variables de Conexión ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aquality.db")
SECRET_KEY = os.getenv("SECRET_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Vercel/Neon a veces usa "postgres://" → SQLAlchemy necesita "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- API externa: Open-Meteo ---
WEATHER_API_BASE = "https://api.open-meteo.com/v1/forecast"
LAT_DEFAULT: float = float(os.getenv("LAT_PISCIFACTORIA", "4.8133"))
LON_DEFAULT: float = float(os.getenv("LON_PISCIFACTORIA", "-75.6189"))

# --- Parámetros fisicoquímicos seguros para trucha arcoíris ---
PARAMETROS_SEGUROS = {
    "temperatura": {"min": 10.0, "max": 18.0, "unidad": "°C"},
    "ph":           {"min": 6.5,  "max": 8.5,  "unidad": "pH"},
    "oxigeno":      {"min": 7.0,  "max": 12.0, "unidad": "mg/L"},
}

# --- Metadatos de la app ---
APP_TITLE   = "AQUALITY – Sistema Integral para la Optimización Acuícola"
APP_VERSION = "1.0.0"

# --- ESTRUCTURA PROFESIONAL PARA IMPORTS ---
# Esto permite que main.py haga: from app.core.config import settings
class Settings:
    DATABASE_URL = DATABASE_URL
    SECRET_KEY = SECRET_KEY
    OPENWEATHER_API_KEY = OPENWEATHER_API_KEY
    WEATHER_API_BASE = WEATHER_API_BASE
    LAT_DEFAULT = LAT_DEFAULT
    LON_DEFAULT = LON_DEFAULT
    PARAMETROS_SEGUROS = PARAMETROS_SEGUROS
    APP_TITLE = APP_TITLE
    APP_VERSION = APP_VERSION

# Instancia única de configuración
settings = Settings()
