"""
app/models/personal.py
Modelo ORM de Personal (trabajadores de la piscifactoría).
"""
from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean
from app.models.database import Base


class Personal(Base):
    """Administración de colaboradores de la unidad productiva."""
    __tablename__ = "personal"

    id            = Column(Integer, primary_key=True, index=True)
    cedula        = Column(String(20), unique=True, nullable=False, index=True)
    nombre        = Column(String(100), nullable=False)
    cargo         = Column(String(80), nullable=False)
    telefono      = Column(String(20), nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    activo        = Column(Boolean, default=True)
    creado_en     = Column(DateTime, default=datetime.utcnow)

    def __init__(self, cedula: str, nombre: str, cargo: str,
                 fecha_ingreso: date, telefono: str = None) -> None:
        self.cedula        = cedula
        self.nombre        = nombre
        self.cargo         = cargo
        self.telefono      = telefono
        self.fecha_ingreso = fecha_ingreso
        self.activo        = True

    def __repr__(self) -> str:
        return f"<Personal {self.nombre!r} cargo={self.cargo}>"

    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} – {self.cargo} ({estado})"

    @property
    def dias_laborados(self) -> int:
        return (date.today() - self.fecha_ingreso).days

    def desactivar(self) -> None:
        self.activo = False

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
