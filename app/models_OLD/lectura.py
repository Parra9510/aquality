"""
api/models/lectura.py
Modelo ORM de LecturaHidrica – variables fisicoquímicas del agua.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from config.settings import PARAMETROS_SEGUROS


class LecturaHidrica(Base):
    __tablename__ = "lecturas_hidricas"

    id            = Column(Integer, primary_key=True, index=True)
    estanque_id   = Column(Integer, ForeignKey("estanques.id"), nullable=False)
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"),  nullable=False)
    temperatura   = Column(Float, nullable=False)
    ph            = Column(Float, nullable=False)
    oxigeno       = Column(Float, nullable=False)
    alerta        = Column(Boolean, default=False)
    observacion   = Column(String(300), nullable=True)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    estanque = relationship("Estanque", back_populates="lecturas")
    usuario  = relationship("Usuario",  back_populates="lecturas")

    def __init__(self, estanque_id: int, usuario_id: int,
                 temperatura: float, ph: float, oxigeno: float,
                 observacion: str = None) -> None:
        _validar(temperatura, ph, oxigeno)
        self.estanque_id = estanque_id
        self.usuario_id  = usuario_id
        self.temperatura = temperatura
        self.ph          = ph
        self.oxigeno     = oxigeno
        self.observacion = observacion
        self.alerta      = not _dentro_rango(temperatura, ph, oxigeno)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "estanque_id":   self.estanque_id,
            "usuario_id":    self.usuario_id,
            "temperatura":   self.temperatura,
            "ph":            self.ph,
            "oxigeno":       self.oxigeno,
            "alerta":        self.alerta,
            "observacion":   self.observacion,
            "registrado_en": self.registrado_en.isoformat() if self.registrado_en else None,
        }


# ── Funciones auxiliares (sin estado, puras) ─────────────────────────────────
def _validar(temperatura: float, ph: float, oxigeno: float) -> None:
    if not (0 <= temperatura <= 40):
        raise ValueError(f"Temperatura fuera de rango físico: {temperatura}")
    if not (0 <= ph <= 14):
        raise ValueError(f"pH fuera de rango físico: {ph}")
    if oxigeno < 0:
        raise ValueError(f"Oxígeno disuelto no puede ser negativo: {oxigeno}")


def _dentro_rango(temperatura: float, ph: float, oxigeno: float) -> bool:
    p = PARAMETROS_SEGUROS
    return (
        p["temperatura"]["min"] <= temperatura <= p["temperatura"]["max"]
        and p["ph"]["min"]      <= ph          <= p["ph"]["max"]
        and p["oxigeno"]["min"] <= oxigeno     <= p["oxigeno"]["max"]
    )