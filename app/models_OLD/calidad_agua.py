from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from app.models.database import Base

class CalidadAgua(Base):
    __tablename__ = "calidad_agua"

    id = Column(Integer, primary_key=True)

    oxigeno = Column(Float)
    temperatura = Column(Float)
    ph = Column(Float)

    amonio = Column(Float)
    nitritos = Column(Float)
    nitratos = Column(Float)

    transparencia = Column(Float)

    fecha = Column(DateTime(timezone=True), server_default=func.now())