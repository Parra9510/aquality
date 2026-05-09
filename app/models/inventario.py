"""
app/models/inventario.py
Modelos ORM de Insumo y MovimientoStock (inventario de alimentos e insumos).
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.models.database import Base


class TipoMovimiento:
    ENTRADA  = "entrada"
    SALIDA   = "salida"
    AJUSTE   = "ajuste"
    TODOS    = [ENTRADA, SALIDA, AJUSTE]


class Insumo(Base):
    """Catálogo de insumos/alimentos disponibles en la piscifactoría."""
    __tablename__ = "insumos"

    id              = Column(Integer, primary_key=True, index=True)
    nombre          = Column(String(150), nullable=False, unique=True)
    unidad_medida   = Column(String(20), nullable=False, default="kg")
    stock_actual    = Column(Float, nullable=False, default=0.0)
    stock_minimo    = Column(Float, nullable=False, default=10.0)
    descripcion     = Column(String(300), nullable=True)
    creado_en       = Column(DateTime, default=datetime.utcnow)

    movimientos = relationship("MovimientoStock", back_populates="insumo", lazy="select")

    def __init__(self, nombre: str, unidad_medida: str = "kg",
                 stock_minimo: float = 10.0, descripcion: str = None) -> None:
        self.nombre        = nombre
        self.unidad_medida = unidad_medida
        self.stock_actual  = 0.0
        self.stock_minimo  = stock_minimo
        self.descripcion   = descripcion

    def __repr__(self) -> str:
        return f"<Insumo {self.nombre!r} stock={self.stock_actual}{self.unidad_medida}>"

    def __str__(self) -> str:
        return f"{self.nombre} – {self.stock_actual} {self.unidad_medida}"

    @property
    def requiere_reabastecimiento(self) -> bool:
        return self.stock_actual <= self.stock_minimo

    def to_dict(self) -> dict:
        return {
            "id":                       self.id,
            "nombre":                   self.nombre,
            "unidad_medida":            self.unidad_medida,
            "stock_actual":             self.stock_actual,
            "stock_minimo":             self.stock_minimo,
            "descripcion":              self.descripcion,
            "requiere_reabastecimiento": self.requiere_reabastecimiento,
        }


class MovimientoStock(Base):
    """Registra entradas y salidas del inventario (CRUD completo sobre stock)."""
    __tablename__ = "movimientos_stock"

    id          = Column(Integer, primary_key=True, index=True)
    insumo_id   = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo        = Column(SAEnum(*TipoMovimiento.TODOS, name="tipo_movimiento"), nullable=False)
    cantidad    = Column(Float, nullable=False)
    motivo      = Column(String(200), nullable=True)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    insumo  = relationship("Insumo",   back_populates="movimientos")
    usuario = relationship("Usuario",  back_populates="inventarios")

    def __init__(self, insumo_id: int, usuario_id: int,
                 tipo: str, cantidad: float, motivo: str = None) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad del movimiento debe ser positiva.")
        self.insumo_id  = insumo_id
        self.usuario_id = usuario_id
        self.tipo       = tipo
        self.cantidad   = cantidad
        self.motivo     = motivo

    def __repr__(self) -> str:
        return f"<Movimiento {self.tipo} {self.cantidad} insumo={self.insumo_id}>"

    def __str__(self) -> str:
        signo = "+" if self.tipo == TipoMovimiento.ENTRADA else "-"
        return f"{signo}{self.cantidad} – {self.tipo.upper()}"

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "insumo_id":      self.insumo_id,
            "usuario_id":     self.usuario_id,
            "tipo":           self.tipo,
            "cantidad":       self.cantidad,
            "motivo":         self.motivo,
            "registrado_en":  self.registrado_en.isoformat() if self.registrado_en else None,
        }
