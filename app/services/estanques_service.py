"""
app/services/estanques_service.py
Lógica de negocio para gestión de estanques.
"""
from sqlalchemy.orm import Session
from app.domain.estanque import Estanque


class EstanquesService:

    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self) -> list[Estanque]:
        return self.db.query(Estanque).all()

    def obtener_por_id(self, estanque_id: int) -> Estanque | None:
        return self.db.get(Estanque, estanque_id)

    def crear_estanque(self, nombre: str, capacidad_litros: float,
                       ubicacion: str = None) -> Estanque:
        """
        El router usa capacidad_litros pero el modelo internamente
        los guarda como capacidad_kg (1 litro ≈ 1 kg para agua).
        """
        if capacidad_litros <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")
        # Generamos código automático si no se provee
        count = self.db.query(Estanque).count()
        codigo_auto = f"EST-{count + 1:02d}"
        nuevo = Estanque(
            codigo=codigo_auto,
            nombre=nombre,
            capacidad_kg=capacidad_litros,  # mapeo capacidad_litros → capacidad_kg
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
