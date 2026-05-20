"""
app/domain/inventario.py
Modelos ORM de Inventario (Insumo + Movimiento), aislados por finca.
"""
from __future__ import annotations
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipoMovimiento(str, enum.Enum):
    ENTRADA = "entrada"
    SALIDA  = "salida"
    AJUSTE  = "ajuste"


class Insumo(Base):
    __tablename__ = "insumos"

    id            = Column(Integer, primary_key=True, index=True)
    nombre        = Column(String(150), nullable=False, index=True)
    descripcion   = Column(Text, nullable=True)
    unidad_medida = Column(String(20), default="kg")
    stock_actual  = Column(Float, default=0.0)
    stock_minimo  = Column(Float, default=10.0)
    creado_en     = Column(DateTime, default=datetime.utcnow)

    # FK a Finca — OBLIGATORIA
    finca_id      = Column(Integer, ForeignKey("fincas.id"), nullable=False, index=True)
    finca         = relationship("Finca", back_populates="insumos")

    movimientos   = relationship("Movimiento", back_populates="insumo",
                                  cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "nombre":        self.nombre,
            "descripcion":   self.descripcion,
            "unidad_medida": self.unidad_medida,
            "stock_actual":  self.stock_actual,
            "stock_minimo":  self.stock_minimo,
            "finca_id":      self.finca_id,
            "bajo_stock":    self.stock_actual <= self.stock_minimo,
        }


class Movimiento(Base):
    __tablename__ = "movimientos"

    id           = Column(Integer, primary_key=True, index=True)
    insumo_id    = Column(Integer, ForeignKey("insumos.id"),   nullable=False, index=True)
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"),  nullable=False)
    tipo         = Column(Enum(TipoMovimiento), nullable=False)
    cantidad     = Column(Float, nullable=False)
    motivo       = Column(String(300), nullable=True)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    insumo  = relationship("Insumo",  back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "insumo_id":     self.insumo_id,
            "usuario_id":    self.usuario_id,
            "tipo":          self.tipo,
            "cantidad":      self.cantidad,
            "motivo":        self.motivo,
            "registrado_en": self.registrado_en.isoformat() if self.registrado_en else None,
        }
