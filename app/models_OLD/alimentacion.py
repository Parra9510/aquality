from sqlalchemy import Column, Integer, Float, String
from app.models.database import Base

class Alimentacion(Base):
    __tablename__ = "alimentacion"

    id = Column(Integer, primary_key=True)

    tipo_alimento = Column(String)
    proteina = Column(Float)
    etapa = Column(String)

    cantidad = Column(Float)
    frecuencia = Column(Integer)
    costo = Column(Float)