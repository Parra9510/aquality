"""
app/services/lectura_service.py
Lógica de negocio para el módulo de monitoreo hídrico.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.lectura import LecturaHidrica
from app.models.estanque import Estanque


class LecturaService:
    """Servicio de dominio para gestión de lecturas hidricas."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def registrar(self, estanque_id: int, usuario_id: int,
                  temperatura: float, ph: float, oxigeno: float,
                  observacion: str = None) -> LecturaHidrica:
        """Crea y persiste una nueva lectura hídrica. CRUD – CREATE."""
        estanque = self._db.get(Estanque, estanque_id)
        if not estanque:
            raise ValueError(f"Estanque con id={estanque_id} no existe.")

        try:
            lectura = LecturaHidrica(
                estanque_id=estanque_id,
                usuario_id=usuario_id,
                temperatura=temperatura,
                ph=ph,
                oxigeno=oxigeno,
                observacion=observacion,
            )
        except ValueError as exc:
            raise ValueError(f"Datos de lectura inválidos: {exc}") from exc

        self._db.add(lectura)
        self._db.commit()
        self._db.refresh(lectura)
        return lectura

    def listar_por_estanque(self, estanque_id: int,
                             limite: int = 50) -> list[LecturaHidrica]:
        """CRUD – READ: últimas lecturas de un estanque."""
        return (
            self._db.query(LecturaHidrica)
            .filter(LecturaHidrica.estanque_id == estanque_id)
            .order_by(LecturaHidrica.registrado_en.desc())
            .limit(limite)
            .all()
        )

    def obtener(self, lectura_id: int) -> LecturaHidrica | None:
        """CRUD – READ: una lectura por id."""
        return self._db.get(LecturaHidrica, lectura_id)

    def eliminar(self, lectura_id: int) -> bool:
        """CRUD – DELETE."""
        lectura = self._db.get(LecturaHidrica, lectura_id)
        if not lectura:
            return False
        self._db.delete(lectura)
        self._db.commit()
        return True

    def alertas_activas(self) -> list[LecturaHidrica]:
        """Lecturas con parámetros fuera de rango (alertas no resueltas)."""
        return (
            self._db.query(LecturaHidrica)
            .filter(LecturaHidrica.alerta == True)  # noqa: E712
            .order_by(LecturaHidrica.registrado_en.desc())
            .limit(100)
            .all()
        )

    def resumen_estanque(self, estanque_id: int) -> dict:
        """Estadísticas básicas de un estanque (últimas 50 lecturas)."""
        lecturas = self.listar_por_estanque(estanque_id, limite=50)
        if not lecturas:
            return {"mensaje": "Sin lecturas registradas."}

        temps = [l.temperatura for l in lecturas]
        phs   = [l.ph          for l in lecturas]
        o2s   = [l.oxigeno     for l in lecturas]

        def stats(vals):
            return {"promedio": round(sum(vals)/len(vals), 2),
                    "minimo":   round(min(vals), 2),
                    "maximo":   round(max(vals), 2)}

        return {
            "estanque_id":       estanque_id,
            "total_lecturas":    len(lecturas),
            "alertas":           sum(1 for l in lecturas if l.alerta),
            "temperatura":       stats(temps),
            "ph":                stats(phs),
            "oxigeno_disuelto":  stats(o2s),
        }
