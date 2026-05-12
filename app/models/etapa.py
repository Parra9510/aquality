from sqlalchemy import Column, Integer, String
from app.models.database import Base

class Etapa(Base):
    __tablename__ = "etapas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True)