"""
app/services/clima_service.py
Servicio de consumo de API externa: Open-Meteo (datos climáticos).
Se usa para obtener temperatura ambiente de la zona piscícola,
lo que correlaciona con la temperatura del agua en estanques a cielo abierto.

API pública sin autenticación: https://open-meteo.com/
"""
from __future__ import annotations
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError

# --- IMPORT CORREGIDO ---
from app.core.config import settings


class ClimaAPIError(Exception):
    """Error personalizado para fallos en el consumo de la API de clima."""
    pass


class ClimaService:
    """
    Servicio para obtener datos climáticos desde la API Open-Meteo.
    Aplica manejo de errores y procesamiento de respuestas JSON.
    """

    TIMEOUT_SEGUNDOS = 8

    def __init__(self) -> None:
        # Usamos el objeto settings centralizado
        self._base_url = settings.WEATHER_API_BASE

    def __repr__(self) -> str:
        return f"<ClimaService url={self._base_url!r}>"

    # ── Método principal (GET) ────────────────────────────────────────────────
    def obtener_clima_actual(
        self,
        latitud: float = 4.8133,    # Santa Rosa de Cabal, Risaralda
        longitud: float = -75.6189,
    ) -> dict:
        """
        Consulta temperatura ambiente actual y otras variables meteorológicas.
        Retorna un dict con los datos procesados o lanza ClimaAPIError.
        """
        params = {
            "latitude":        latitud,
            "longitude":       longitud,
            "current":         "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "timezone":        "America/Bogota",
            "forecast_days":   1,
        }

        try:
            response = requests.get(
                self._base_url,
                params=params,
                timeout=self.TIMEOUT_SEGUNDOS,
            )
            response.raise_for_status()          # lanza HTTPError si status >= 400
            datos = response.json()              # procesamiento JSON

        except Timeout:
            raise ClimaAPIError("Tiempo de espera agotado al consultar la API de clima.")
        except ConnectionError:
            raise ClimaAPIError("No se pudo establecer conexión con la API de clima.")
        except HTTPError as exc:
            codigo = exc.response.status_code if exc.response else "Desconocido"
            raise ClimaAPIError(f"La API de clima respondió con error HTTP {codigo}.")
        except ValueError:
            raise ClimaAPIError("La respuesta de la API de clima no es JSON válido.")

        return self._procesar_respuesta(datos)

    # ── Procesamiento de respuesta JSON ──────────────────────────────────────
    @staticmethod
    def _procesar_respuesta(datos: dict) -> dict:
        """Extrae y normaliza los campos relevantes de la respuesta JSON."""
        try:
            actual = datos["current"]
            return {
                "temperatura_ambiente_c":  actual.get("temperature_2m"),
                "humedad_relativa_pct":    actual.get("relative_humidity_2m"),
                "precipitacion_mm":        actual.get("precipitation"),
                "viento_kmh":              actual.get("wind_speed_10m"),
                "hora_lectura":            actual.get("time"),
                "zona_horaria":            datos.get("timezone"),
            }
        except (KeyError, TypeError) as exc:
            raise ClimaAPIError(f"Estructura inesperada en la respuesta de la API: {exc}")

    def estimar_temperatura_agua(self, latitud: float = 4.8133,
                                 longitud: float = -75.6189) -> float | None:
        """
        Retorna una estimación de temperatura del agua basada en temperatura
        ambiente (correlación empírica para estanques en la región).
        Devuelve None si la API falla.
        """
        try:
            clima = self.obtener_clima_actual(latitud, longitud)
            t_amb = clima["temperatura_ambiente_c"]
            if t_amb is None:
                return None
            # Estimación empírica: agua ≈ ambiente × 0.85 (estanques sombreados)
            return round(float(t_amb) * 0.85, 2)
        except ClimaAPIError:
            return None