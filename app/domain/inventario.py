from __future__ import annotations
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# --- ESTO ES LO QUE FALTABA ---
class TipoMovimiento(str, Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"

class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    unidad_medida = Column(String(20), default="kg")
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=10.0)
    descripcion = Column(String(255), nullable=True)

    # Relación con movimientos
    movimientos = relationship("Movimiento", back_populates="insumo", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "unidad_medida": self.unidad_medida,
            "stock_actual": self.stock_actual,
            "stock_minimo": self.stock_minimo,
            "alerta_stock": self.stock_actual <= self.stock_minimo
        }

class Movimiento(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    insumo_id = Column(Integer, ForeignKey("insumos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cantidad = Column(Float, nullable=False)
    tipo = Column(String(20), default=TipoMovimiento.ENTRADA) 
    motivo = Column(String(255), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    insumo = relationship("Insumo", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "insumo_id": self.insumo_id,
            "cantidad": self.cantidad,
            "tipo": self.tipo,
            "fecha": self.fecha.isoformat() if self.fecha else None
        }