"""
api/models/usuario.py
Modelo ORM de Usuario con roles y autenticación por hash SHA-256.
"""
from __future__ import annotations
import hashlib
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base


class RolUsuario:
    ADMINISTRADOR = "administrador"
    SUPERVISOR    = "supervisor"
    OPERARIO      = "operario"
    TODOS         = [ADMINISTRADOR, SUPERVISOR, OPERARIO]


class Usuario(Base):
    __tablename__ = "usuarios"

    id             = Column(Integer, primary_key=True, index=True)
    nombre         = Column(String(100), nullable=False)
    email          = Column(String(150), unique=True, nullable=False, index=True)
    _password_hash = Column("password_hash", String(64), nullable=False)
    rol = Column(String(20), nullable=False, default=RolUsuario.OPERARIO)
    creado_en = Column(DateTime, default=datetime.utcnow)

    lecturas    = relationship("LecturaHidrica",  back_populates="usuario",   lazy="select")
    inventarios = relationship("MovimientoStock", back_populates="usuario",   lazy="select")

    def __init__(self, nombre: str, email: str, password: str,
                 rol: str = RolUsuario.OPERARIO) -> None:
        self.nombre = nombre
        self.email  = email
        self.rol    = rol
        self.set_password(password)

    def set_password(self, password: str) -> None:
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        self._password_hash = hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password: str) -> bool:
        return self._password_hash == hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "nombre":    self.nombre,
            "email":     self.email,
            "rol":       self.rol,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }