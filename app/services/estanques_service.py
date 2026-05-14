
from sqlalchemy.orm import Session
from app.domain.estanque import Estanque  

class EstanquesService:
    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self):
        """Retorna todos los estanques registrados."""
        return self.db.query(Estanque).all()

    def obtener_por_id(self, estanque_id: int):
        """Busca un estanque específico por su ID."""
        return self.db.query(Estanque).filter(Estanque.id == estanque_id).first()

    def crear_estanque(self, nombre: str, capacidad_litros: float, ubicacion: str = None):
        """Crea un nuevo estanque en la base de datos."""
        # Ejemplo de regla de negocio: No permitir estanques con capacidad negativa
        if capacidad_litros <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")

        nuevo_estanque = Estanque(
            nombre=nombre,
            capacidad_litros=capacidad_litros,
            ubicacion=ubicacion
        )
        
        self.db.add(nuevo_estanque)
        self.db.commit()
        self.db.refresh(nuevo_estanque)
        return nuevo_estanque

    def eliminar_estanque(self, estanque_id: int):
        """Elimina un estanque si existe."""
        estanque = self.obtener_por_id(estanque_id)
        if estanque:
            self.db.delete(estanque)
            self.db.commit()
            return True
        return False