"""
api/models/estanque.py
Modelo ORM de Estanque con soporte de etapa productiva.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.database import Base


class EtapaProductiva:
    INCUBACION = "incubacion"
    ALEVINAJE  = "alevinaje"
    DEDINOS    = "dedinos"
    ENGORDE    = "engorde"
    TODAS      = [INCUBACION, ALEVINAJE, DEDINOS, ENGORDE]


class EstadoEstanque:
    ACTIVO   = "activo"
    INACTIVO = "inactivo"
    TODOS    = [ACTIVO, INACTIVO]


class Estanque(Base):
    __tablename__ = "estanques"

    id           = Column(Integer, primary_key=True, index=True)
    codigo       = Column(String(20), unique=True, nullable=False, index=True)
    nombre       = Column(String(100), nullable=False)
    etapa        = Column(
        SAEnum(*EtapaProductiva.TODAS, name="etapa_productiva"),
        nullable=True,
    )
    capacidad_kg = Column(Float, nullable=False)
    volumen_m3   = Column(Float, nullable=True)
    estado       = Column(
        SAEnum(*EstadoEstanque.TODOS, name="estado_estanque"),
        default=EstadoEstanque.ACTIVO,
    )
    creado_en    = Column(DateTime, default=datetime.utcnow)

    lecturas = relationship("LecturaHidrica", back_populates="estanque", lazy="select")

    def __init__(self, codigo: str, nombre: str, capacidad_kg: float,
                 volumen_m3: float = None, etapa: str = None) -> None:
        if capacidad_kg <= 0:
            raise ValueError("La capacidad debe ser mayor a 0 kg.")
        self.codigo       = codigo
        self.nombre       = nombre
        self.capacidad_kg = capacidad_kg
        self.volumen_m3   = volumen_m3
        self.etapa        = etapa
        self.estado       = EstadoEstanque.ACTIVO

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "codigo":       self.codigo,
            "nombre":       self.nombre,
            "etapa":        self.etapa,
            "capacidad_kg": self.capacidad_kg,
            "volumen_m3":   self.volumen_m3,
            "estado":       self.estado,
            "creado_en":    self.creado_en.isoformat() if self.creado_en else None,
        }