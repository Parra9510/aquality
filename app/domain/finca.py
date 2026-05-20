"""
app/domain/finca.py
Modelo ORM de Finca (unidad multi-tenant del sistema).
Cada usuario registrado pertenece a UNA finca.
Todos los datos (estanques, lecturas, inventario, personal) están aislados por finca.
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Finca(Base):
    __tablename__ = "fincas"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    activa      = Column(Boolean, default=True)
    creada_en   = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    usuarios   = relationship("Usuario",   back_populates="finca", cascade="all, delete-orphan")
    estanques  = relationship("Estanque",  back_populates="finca", cascade="all, delete-orphan")
    insumos    = relationship("Insumo",    back_populates="finca", cascade="all, delete-orphan")
    personal   = relationship("Personal",  back_populates="finca", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "activa":      self.activa,
            "creada_en":   self.creada_en.isoformat() if self.creada_en else None,
        }
