"""
app/services/inventario_service.py
Lógica de negocio para gestión de inventario de insumos.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.domain.inventario import Insumo, Movimiento, TipoMovimiento


class InventarioService:

    def __init__(self, db: Session) -> None:
        self._db = db

    def crear_insumo(self, nombre: str, unidad_medida: str = "kg",
                     stock_minimo: float = 10.0, descripcion: str = None) -> Insumo:
        if self._db.query(Insumo).filter(Insumo.nombre == nombre).first():
            raise ValueError(f"Ya existe un insumo con el nombre '{nombre}'.")
        insumo = Insumo(nombre=nombre, unidad_medida=unidad_medida,
                        stock_minimo=stock_minimo, descripcion=descripcion)
        self._db.add(insumo)
        self._db.commit()
        self._db.refresh(insumo)
        return insumo

    def listar_insumos(self) -> list[Insumo]:
        return self._db.query(Insumo).order_by(Insumo.nombre).all()

    def obtener_insumo(self, insumo_id: int) -> Insumo | None:
        return self._db.get(Insumo, insumo_id)

    def actualizar_insumo(self, insumo_id: int, **kwargs) -> Insumo:
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            raise ValueError(f"Insumo id={insumo_id} no encontrado.")
        for campo in ("nombre", "unidad_medida", "stock_minimo", "descripcion"):
            if campo in kwargs:
                setattr(insumo, campo, kwargs[campo])
        self._db.commit()
        self._db.refresh(insumo)
        return insumo

    def eliminar_insumo(self, insumo_id: int) -> bool:
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            return False
        if insumo.stock_actual > 0:
            raise ValueError("No se puede eliminar un insumo con stock > 0.")
        self._db.delete(insumo)
        self._db.commit()
        return True

    def registrar_movimiento(self, insumo_id: int, usuario_id: int,
                              tipo: str, cantidad: float,
                              motivo: str = None) -> Movimiento:
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            raise ValueError(f"Insumo id={insumo_id} no encontrado.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")

        mov = Movimiento(insumo_id=insumo_id, usuario_id=usuario_id,
                         tipo=tipo, cantidad=cantidad, motivo=motivo)

        if tipo == TipoMovimiento.ENTRADA or tipo == "entrada":
            insumo.stock_actual += cantidad
        elif tipo == TipoMovimiento.SALIDA or tipo == "salida":
            if insumo.stock_actual < cantidad:
                raise ValueError(
                    f"Stock insuficiente: disponible={insumo.stock_actual}, "
                    f"solicitado={cantidad}."
                )
            insumo.stock_actual -= cantidad
        elif tipo == TipoMovimiento.AJUSTE or tipo == "ajuste":
            insumo.stock_actual = cantidad

        self._db.add(mov)
        self._db.commit()
        self._db.refresh(mov)
        return mov

    def insumos_bajo_stock(self) -> list[Insumo]:
        return [i for i in self.listar_insumos() if i.stock_actual <= i.stock_minimo]
