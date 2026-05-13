from sqlalchemy import Column, Integer, Float, String
from app.models.database import Base

class Cosecha(Base):
    __tablename__ = "cosechas"

    id = Column(Integer, primary_key=True)

    peso_promedio = Column(Float)
    biomasa_total = Column(Float)
    cliente = Column(String)
    precio_kg = Column(Float)
    ingresos = Column(Float)