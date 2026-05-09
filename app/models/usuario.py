"""
app/models/usuario.py
Modelo ORM de Usuario con encapsulamiento y métodos especiales.
"""
from __future__ import annotations
import hashlib
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.database import Base


class RolUsuario:
    """Constantes de roles – evita cadenas mágicas."""
    ADMINISTRADOR = "administrador"
    SUPERVISOR    = "supervisor"
    OPERARIO      = "operario"

    TODOS = [ADMINISTRADOR, SUPERVISOR, OPERARIO]


class Usuario(Base):
    """
    Representa a un usuario del sistema AQUALITY.
    Implementa encapsulamiento, herencia (Base) y métodos especiales.
    """
    __tablename__ = "usuarios"

    # ── Atributos de columna ─────────────────────────────────────────────────
    id             = Column(Integer, primary_key=True, index=True)
    nombre         = Column(String(100), nullable=False)
    email          = Column(String(150), unique=True, nullable=False, index=True)
    _password_hash = Column("password_hash", String(64), nullable=False)
    rol            = Column(
        SAEnum(*RolUsuario.TODOS, name="rol_usuario"),
        nullable=False,
        default=RolUsuario.OPERARIO,
    )
    creado_en      = Column(DateTime, default=datetime.utcnow)

    # ── Relaciones ───────────────────────────────────────────────────────────
    lecturas    = relationship("LecturaHidrica",  back_populates="usuario", lazy="select")
    inventarios = relationship("MovimientoStock", back_populates="usuario", lazy="select")

    # ── Métodos especiales ───────────────────────────────────────────────────
    def __init__(self, nombre: str, email: str, password: str,
                 rol: str = RolUsuario.OPERARIO) -> None:
        self.nombre = nombre
        self.email  = email
        self.rol    = rol
        self.set_password(password)

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email!r} rol={self.rol}>"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.rol})"

    # ── Encapsulamiento: contraseña ──────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Guarda el hash SHA-256 de la contraseña (encapsulamiento)."""
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        self._password_hash = hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password: str) -> bool:
        """Compara la contraseña ingresada con el hash almacenado."""
        return self._password_hash == hashlib.sha256(password.encode()).hexdigest()

    def es_administrador(self) -> bool:
        return self.rol == RolUsuario.ADMINISTRADOR

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "nombre":     self.nombre,
            "email":      self.email,
            "rol":        self.rol,
            "creado_en":  self.creado_en.isoformat() if self.creado_en else None,
        }
