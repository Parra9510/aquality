"""
app/services/lectura_service.py
Lógica de negocio para el módulo de monitoreo hídrico.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.domain.lectura  import Lectura
from app.domain.estanque import Estanque


class LecturaService:

    def __init__(self, db: Session) -> None:
        self._db = db

    def registrar(self, estanque_id: int, usuario_id: int,
                  temperatura: float, ph: float, oxigeno: float,
                  observacion: str = None) -> Lectura:
        if not self._db.get(Estanque, estanque_id):
            raise ValueError(f"Estanque con id={estanque_id} no existe.")
        lectura = Lectura(
            estanque_id=estanque_id,
            usuario_id=usuario_id,
            temperatura=temperatura,
            ph=ph,
            oxigeno=oxigeno,
            observacion=observacion,
        )
        self._db.add(lectura)
        self._db.commit()
        self._db.refresh(lectura)
        return lectura

    def listar_por_estanque(self, estanque_id: int, limite: int = 50) -> list[Lectura]:
        return (
            self._db.query(Lectura)
            .filter(Lectura.estanque_id == estanque_id)
            .order_by(Lectura.registrado_en.desc())
            .limit(limite)
            .all()
        )

    def obtener(self, lectura_id: int) -> Lectura | None:
        return self._db.get(Lectura, lectura_id)

    def eliminar(self, lectura_id: int) -> bool:
        lectura = self._db.get(Lectura, lectura_id)
        if not lectura:
            return False
        self._db.delete(lectura)
        self._db.commit()
        return True

    def alertas_activas(self) -> list[Lectura]:
        return (
            self._db.query(Lectura)
            .filter(Lectura.alerta.is_(True))
            .order_by(Lectura.registrado_en.desc())
            .limit(100)
            .all()
        )

    def resumen_estanque(self, estanque_id: int) -> dict:
        lecturas = self.listar_por_estanque(estanque_id, limite=50)
        if not lecturas:
            return {"mensaje": "Sin lecturas registradas."}
        def stats(vals):
            return {"promedio": round(sum(vals)/len(vals), 2),
                    "minimo":   round(min(vals), 2),
                    "maximo":   round(max(vals), 2)}
        return {
            "estanque_id":      estanque_id,
            "total_lecturas":   len(lecturas),
            "alertas":          sum(1 for l in lecturas if l.alerta),
            "temperatura":      stats([l.temperatura for l in lecturas]),
            "ph":               stats([l.ph          for l in lecturas]),
            "oxigeno_disuelto": stats([l.oxigeno     for l in lecturas]),
        }
