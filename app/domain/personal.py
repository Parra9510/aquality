"""
app/domain/personal.py
Modelo ORM de Personal vinculado a un Usuario responsable.
"""
from __future__ import annotations
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Personal(Base):
    __tablename__ = "personal"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    cargo = Column(String(50))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    # Relación sincronizada con Usuario
    usuario_responsable = relationship("Usuario", back_populates="personal_asignado")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cargo": self.cargo,
            "usuario_id": self.usuario_id
        }