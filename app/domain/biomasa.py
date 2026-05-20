"""
app/domain/biomasa.py
Modelos ORM para Biomasa (siembras) y Alimentación, aislados por finca.
"""
from __future__ import annotations
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class EtapaBiomasa(str, enum.Enum):
    INCUBACION = "incubacion"
    ALEVINAJE  = "alevinaje"
    DEDINOS    = "dedinos"
    ENGORDE    = "engorde"


class TipoAlimento(str, enum.Enum):
    INICIACION = "iniciacion"
    LEVANTE    = "levante"
    ENGORDE    = "engorde"


class Siembra(Base):
    __tablename__ = "siembras"

    id            = Column(Integer, primary_key=True, index=True)
    estanque_id   = Column(Integer, ForeignKey("estanques.id"), nullable=False, index=True)
    finca_id      = Column(Integer, ForeignKey("fincas.id"),    nullable=False, index=True)
    usuario_id    = Column(Integer, ForeignKey("usuarios.id"),  nullable=False)
    fecha         = Column(String(20), nullable=False)
    cantidad      = Column(Integer, nullable=False)          # número de peces
    peso_inicial_g = Column(Float, nullable=False)           # peso en gramos
    biomasa_kg    = Column(Float, nullable=False)            # cantidad × peso / 1000
    proveedor     = Column(String(150), nullable=True)
    etapa         = Column(Enum(EtapaBiomasa), default=EtapaBiomasa.ALEVINAJE)
    observacion   = Column(Text, nullable=True)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    estanque = relationship("Estanque")
    finca    = relationship("Finca")
    usuario  = relationship("Usuario")

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "estanque_id":    self.estanque_id,
            "finca_id":       self.finca_id,
            "usuario_id":     self.usuario_id,
            "fecha":          self.fecha,
            "cantidad":       self.cantidad,
            "peso_inicial_g": self.peso_inicial_g,
            "biomasa_kg":     self.biomasa_kg,
            "proveedor":      self.proveedor,
            "etapa":          self.etapa,
            "observacion":    self.observacion,
            "registrado_en":  self.registrado_en.isoformat() if self.registrado_en else None,
        }


class Alimentacion(Base):
    __tablename__ = "alimentacion"

    id             = Column(Integer, primary_key=True, index=True)
    estanque_id    = Column(Integer, ForeignKey("estanques.id"), nullable=False, index=True)
    finca_id       = Column(Integer, ForeignKey("fincas.id"),    nullable=False, index=True)
    usuario_id     = Column(Integer, ForeignKey("usuarios.id"),  nullable=False)
    fecha          = Column(String(20), nullable=False)
    tipo_alimento  = Column(Enum(TipoAlimento), nullable=False)
    cantidad_kg    = Column(Float, nullable=False)           # ración del día
    alimento_acum_kg = Column(Float, nullable=True)          # acumulado para FCR
    ganancia_peso_kg = Column(Float, nullable=True)          # ganancia para FCR
    fcr            = Column(Float, nullable=True)            # factor conversión
    registrado_en  = Column(DateTime, default=datetime.utcnow)

    estanque = relationship("Estanque")
    finca    = relationship("Finca")
    usuario  = relationship("Usuario")

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "estanque_id":      self.estanque_id,
            "finca_id":         self.finca_id,
            "usuario_id":       self.usuario_id,
            "fecha":            self.fecha,
            "tipo_alimento":    self.tipo_alimento,
            "cantidad_kg":      self.cantidad_kg,
            "alimento_acum_kg": self.alimento_acum_kg,
            "ganancia_peso_kg": self.ganancia_peso_kg,
            "fcr":              self.fcr,
            "registrado_en":    self.registrado_en.isoformat() if self.registrado_en else None,
        }