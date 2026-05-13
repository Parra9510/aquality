from sqlalchemy import Column, Integer, Float
from app.models.database import Base

class Biomasa(Base):
    __tablename__ = "biomasa"

    id = Column(Integer, primary_key=True)

    peces_actuales = Column(Integer)
    peso_promedio = Column(Float)
    biomasa_total = Column(Float)