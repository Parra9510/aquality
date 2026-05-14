"""
app/domain/usuario.py
Modelo ORM de Usuario con roles y autenticación por hash SHA-256.
"""
from __future__ import annotations
import hashlib
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class RolUsuario:
    ADMINISTRADOR = "administrador"
    SUPERVISOR    = "supervisor"
    OPERARIO      = "operario"
    TODOS         = [ADMINISTRADOR, SUPERVISOR, OPERARIO]

class Usuario(Base):
    __tablename__ = "usuarios"

    # Definición de Columnas
    id        = Column(Integer, primary_key=True, index=True)
    nombre    = Column(String(100), nullable=False)
    email     = Column(String(150), unique=True, nullable=False, index=True)
    password  = Column(String(255), nullable=False)  # Sincronizado con el INSERT de tu error
    rol       = Column(String(20), nullable=False, default=RolUsuario.OPERARIO)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # --- RELACIONES SINCRONIZADAS ---
    # Asegúrate de que los back_populates coincidan en lectura.py, inventario.py y personal.py
    lecturas          = relationship("Lectura", back_populates="usuario")
    movimientos       = relationship("Movimiento", back_populates="usuario")
    personal_asignado = relationship("Personal", back_populates="usuario_responsable")

    def __init__(self, nombre: str, email: str, password: str,
                 rol: str = RolUsuario.OPERARIO) -> None:
        self.nombre = nombre
        self.email  = email
        self.rol    = rol
        # Hasheamos la contraseña antes de guardarla en la columna 'password'
        self.password = self._hash_password(password)

    def _hash_password(self, password: str) -> str:
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password: str) -> bool:
        """Compara una contraseña plana con el hash almacenado."""
        return self.password == hashlib.sha256(password.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "nombre":    self.nombre,
            "email":     self.email,
            "rol":       self.rol,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }