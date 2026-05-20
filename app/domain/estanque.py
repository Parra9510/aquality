"""
app/domain/estanque.py
Modelo ORM de Estanque, aislado por finca.
"""
from __future__ import annotations
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class EstadoEstanque(str, enum.Enum):
    ACTIVO    = "activo"
    VACIO     = "vacio"
    LIMPIEZA  = "limpieza"
    BAJA      = "baja"


class EtapaProductiva(str, enum.Enum):
    ALEVINAJE  = "alevinaje"
    LEVANTE    = "levante"
    ENGORDE    = "engorde"
    COSECHA    = "cosecha"
    DESCANSO   = "descanso"


class Estanque(Base):
    __tablename__ = "estanques"

    id             = Column(Integer, primary_key=True, index=True)
    codigo         = Column(String(20), nullable=False, index=True)
    nombre         = Column(String(100), nullable=False)
    capacidad_kg   = Column(Float, default=0.0)
    estado         = Column(Enum(EstadoEstanque), default=EstadoEstanque.ACTIVO)
    etapa          = Column(Enum(EtapaProductiva), nullable=True)
    activo         = Column(Boolean, default=True)
    creado_en      = Column(DateTime, default=datetime.utcnow)

    # FK a Finca — OBLIGATORIA
    finca_id       = Column(Integer, ForeignKey("fincas.id"), nullable=False, index=True)
    finca          = relationship("Finca", back_populates="estanques")

    # Relaciones
    lecturas       = relationship("Lectura", back_populates="estanque",
                                  cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "codigo":       self.codigo,
            "nombre":       self.nombre,
            "capacidad_kg": self.capacidad_kg,
            "estado":       self.estado,
            "etapa":        self.etapa,
            "activo":       self.activo,
            "finca_id":     self.finca_id,
        }
