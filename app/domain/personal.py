"""
app/domain/personal.py
Modelo ORM de Personal.
"""
from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Personal(Base):
    __tablename__ = "personal"

    id            = Column(Integer, primary_key=True, index=True)
    cedula        = Column(String(20), unique=True, nullable=False, index=True)
    nombre        = Column(String(100), nullable=False)
    cargo         = Column(String(80), nullable=False, default="")
    telefono      = Column(String(20), nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    activo        = Column(Boolean, default=True)
    creado_en     = Column(DateTime, default=datetime.utcnow)
    # FK opcional — no bloquea si no existe usuario
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    usuario_responsable = relationship("Usuario", back_populates="personal_asignado")

    def desactivar(self) -> None:
        self.activo = False

    @property
    def dias_laborados(self) -> int:
        if self.fecha_ingreso:
            return (date.today() - self.fecha_ingreso).days
        return 0

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "cedula":         self.cedula,
            "nombre":         self.nombre,
            "cargo":          self.cargo,
            "telefono":       self.telefono,
            "fecha_ingreso":  self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            "activo":         self.activo,
            "dias_laborados": self.dias_laborados,
        }
