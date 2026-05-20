"""
app/domain/usuario.py
Modelo ORM de Usuario con soporte multi-tenant (finca_id) y rol SUPERADMIN.

Reglas:
  - SUPERADMIN: vm.parra10@ciaf.edu.co — acceso total, sin restricción de finca.
  - ADMIN: administrador de su propia finca.
  - OPERADOR: usuario estándar de su finca.
  - Un usuario sin finca_id solo puede existir si es SUPERADMIN.
"""
from __future__ import annotations
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

SUPERADMIN_EMAIL = "vm.parra10@ciaf.edu.co"


class RolUsuario(str, enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN      = "admin"
    OPERADOR   = "operador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id          = Column(Integer, primary_key=True, index=True)
    email       = Column(String(150), unique=True, nullable=False, index=True)
    nombre      = Column(String(100), nullable=False)
    hashed_pwd  = Column(String(256), nullable=False)
    rol         = Column(Enum(RolUsuario), default=RolUsuario.OPERADOR, nullable=False)
    activo      = Column(Boolean, default=True)
    creado_en   = Column(DateTime, default=datetime.utcnow)

    # FK a Finca — NULL solo para SUPERADMIN
    finca_id    = Column(Integer, ForeignKey("fincas.id"), nullable=True, index=True)
    finca       = relationship("Finca", back_populates="usuarios")

    # Relaciones existentes
    lecturas         = relationship("Lectura",   back_populates="usuario")
    movimientos      = relationship("Movimiento", back_populates="usuario")
    personal_asignado = relationship("Personal",  back_populates="usuario_responsable")

    @property
    def es_superadmin(self) -> bool:
        return self.rol == RolUsuario.SUPERADMIN or self.email == SUPERADMIN_EMAIL

    @property
    def es_admin(self) -> bool:
        return self.rol in (RolUsuario.ADMIN, RolUsuario.SUPERADMIN)

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "email":    self.email,
            "nombre":   self.nombre,
            "rol":      self.rol,
            "activo":   self.activo,
            "finca_id": self.finca_id,
        }
