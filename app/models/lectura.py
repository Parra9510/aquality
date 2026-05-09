"""
app/models/lectura.py
Modelo ORM de LecturaHidrica – variables fisicoquímicas del agua.
Demuestra: herencia, polimorfismo mediante método evaluar().
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.database import Base
from config.settings import PARAMETROS_SEGUROS


class LecturaBase:
    """
    Clase base abstracta (no ORM) para lecturas fisicoquímicas.
    Implementa polimorfismo: cada subclase puede redefinir evaluar().
    """
    def evaluar(self) -> dict:
        raise NotImplementedError("Subclases deben implementar evaluar().")


class LecturaHidrica(Base, LecturaBase):
    """
    Registro de una medición de calidad hídrica en un estanque.
    Hereda de Base (ORM) y de LecturaBase (lógica de negocio).
    """
    __tablename__ = "lecturas_hidricas"

    id           = Column(Integer, primary_key=True, index=True)
    estanque_id  = Column(Integer, ForeignKey("estanques.id"), nullable=False)
    usuario_id   = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    temperatura  = Column(Float, nullable=False)   # °C
    ph           = Column(Float, nullable=False)
    oxigeno      = Column(Float, nullable=False)   # mg/L
    alerta       = Column(Boolean, default=False)
    observacion  = Column(String(300), nullable=True)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    estanque = relationship("Estanque", back_populates="lecturas")
    usuario  = relationship("Usuario",  back_populates="lecturas")

    def __init__(self, estanque_id: int, usuario_id: int,
                 temperatura: float, ph: float, oxigeno: float,
                 observacion: str = None) -> None:
        self._validar(temperatura, ph, oxigeno)
        self.estanque_id = estanque_id
        self.usuario_id  = usuario_id
        self.temperatura = temperatura
        self.ph          = ph
        self.oxigeno     = oxigeno
        self.observacion = observacion
        self.alerta      = not self._dentro_rango()

    # ── Validación de entrada ────────────────────────────────────────────────
    @staticmethod
    def _validar(temperatura: float, ph: float, oxigeno: float) -> None:
        if not (0 <= temperatura <= 40):
            raise ValueError(f"Temperatura fuera de rango físico: {temperatura}")
        if not (0 <= ph <= 14):
            raise ValueError(f"pH fuera de rango físico: {ph}")
        if oxigeno < 0:
            raise ValueError(f"Oxígeno disuelto no puede ser negativo: {oxigeno}")

    def _dentro_rango(self) -> bool:
        p = PARAMETROS_SEGUROS
        return (
            p["temperatura"]["min"] <= self.temperatura <= p["temperatura"]["max"]
            and p["ph"]["min"]      <= self.ph          <= p["ph"]["max"]
            and p["oxigeno"]["min"] <= self.oxigeno     <= p["oxigeno"]["max"]
        )

    # ── Polimorfismo: evaluar() ──────────────────────────────────────────────
    def evaluar(self) -> dict:
        """Devuelve diagnóstico de cada parámetro. Polimorfismo respecto a LecturaBase."""
        p = PARAMETROS_SEGUROS
        def estado(valor, param):
            rango = p[param]
            if valor < rango["min"]:
                return "BAJO"
            if valor > rango["max"]:
                return "ALTO"
            return "NORMAL"

        return {
            "temperatura": {"valor": self.temperatura, "estado": estado(self.temperatura, "temperatura")},
            "ph":          {"valor": self.ph,          "estado": estado(self.ph, "ph")},
            "oxigeno":     {"valor": self.oxigeno,     "estado": estado(self.oxigeno, "oxigeno")},
            "alerta_general": self.alerta,
        }

    def __repr__(self) -> str:
        return (f"<LecturaHidrica estanque={self.estanque_id} "
                f"T={self.temperatura} pH={self.ph} O2={self.oxigeno}>")

    def __str__(self) -> str:
        return (f"[{self.registrado_en}] Estanque #{self.estanque_id} – "
                f"T={self.temperatura}°C  pH={self.ph}  O₂={self.oxigeno}mg/L"
                f"{'  ⚠ ALERTA' if self.alerta else ''}")

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "estanque_id":   self.estanque_id,
            "usuario_id":    self.usuario_id,
            "temperatura":   self.temperatura,
            "ph":            self.ph,
            "oxigeno":       self.oxigeno,
            "alerta":        self.alerta,
            "observacion":   self.observacion,
            "registrado_en": self.registrado_en.isoformat() if self.registrado_en else None,
            "diagnostico":   self.evaluar(),
        }
