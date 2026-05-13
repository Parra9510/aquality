from sqlalchemy import Column, Integer, String, Float
from app.models.database import Base

class Tratamiento(Base):
    __tablename__ = "tratamientos"

    id = Column(Integer, primary_key=True)

    medicamento = Column(String)
    dosis = Column(Float)
    responsable = Column(String)
    observaciones = Column(String)