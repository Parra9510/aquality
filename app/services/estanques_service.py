"""
app/services/estanques_service.py
Lógica de negocio para gestión de estanques, con filtro por finca.
"""
from sqlalchemy.orm import Session
from app.domain.estanque import Estanque


class EstanquesService:

    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self, finca_id: int = None) -> list[Estanque]:
        q = self.db.query(Estanque)
        if finca_id is not None:
            q = q.filter(Estanque.finca_id == finca_id)
        return q.all()

    def obtener_por_id(self, estanque_id: int) -> Estanque | None:
        return self.db.get(Estanque, estanque_id)

    def crear_estanque(self, nombre: str, capacidad_litros: float,
                       finca_id: int, ubicacion: str = None) -> Estanque:
        if capacidad_litros <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")
        count     = self.db.query(Estanque).filter(Estanque.finca_id == finca_id).count()
        codigo    = f"EST-{count + 1:02d}"
        nuevo     = Estanque(
            codigo       = codigo,
            nombre       = nombre,
            capacidad_kg = capacidad_litros,
            finca_id     = finca_id,
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def eliminar_estanque(self, estanque_id: int) -> bool:
        estanque = self.obtener_por_id(estanque_id)
        if not estanque:
            return False
        self.db.delete(estanque)
        self.db.commit()
        return True
