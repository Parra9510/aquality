"""
app/services/inventario_service.py
Lógica de negocio para gestión de inventario de insumos.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.domain.inventario import Insumo, Movimiento


class InventarioService:
    """Servicio de dominio para CRUD de insumos y movimientos de stock."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Insumos ──────────────────────────────────────────────────────────────
    def crear_insumo(self, nombre: str, unidad_medida: str = "kg",
                     stock_minimo: float = 10.0, descripcion: str = None) -> Insumo:
        """CRUD – CREATE insumo."""
        existente = self._db.query(Insumo).filter(Insumo.nombre == nombre).first()
        if existente:
            raise ValueError(f"Ya existe un insumo con el nombre '{nombre}'.")
        insumo = Insumo(nombre=nombre, unidad_medida=unidad_medida,
                        stock_minimo=stock_minimo, descripcion=descripcion)
        self._db.add(insumo)
        self._db.commit()
        self._db.refresh(insumo)
        return insumo

    def listar_insumos(self) -> list[Insumo]:
        """CRUD – READ todos los insumos."""
        return self._db.query(Insumo).order_by(Insumo.nombre).all()

    def obtener_insumo(self, insumo_id: int) -> Insumo | None:
        return self._db.get(Insumo, insumo_id)

    def actualizar_insumo(self, insumo_id: int, **kwargs) -> Insumo:
        """CRUD – UPDATE campos del insumo."""
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            raise ValueError(f"Insumo id={insumo_id} no encontrado.")
        campos_permitidos = {"nombre", "unidad_medida", "stock_minimo", "descripcion"}
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                setattr(insumo, campo, valor)
        self._db.commit()
        self._db.refresh(insumo)
        return insumo

    def eliminar_insumo(self, insumo_id: int) -> bool:
        """CRUD – DELETE insumo (solo si stock = 0)."""
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            return False
        if insumo.stock_actual > 0:
            raise ValueError("No se puede eliminar un insumo con stock > 0.")
        self._db.delete(insumo)
        self._db.commit()
        return True

    # ── Movimientos de stock ─────────────────────────────────────────────────
    def registrar_movimiento(self, insumo_id: int, usuario_id: int,
                              tipo: str, cantidad: float,
                              motivo: str = None) -> MovimientoStock:
        """Registra entrada, salida o ajuste de stock y actualiza el saldo."""
        insumo = self._db.get(Insumo, insumo_id)
        if not insumo:
            raise ValueError(f"Insumo id={insumo_id} no encontrado.")

        mov = MovimientoStock(insumo_id=insumo_id, usuario_id=usuario_id,
                              tipo=tipo, cantidad=cantidad, motivo=motivo)

        # Actualizar stock según tipo
        if tipo == TipoMovimiento.ENTRADA:
            insumo.stock_actual += cantidad
        elif tipo == TipoMovimiento.SALIDA:
            if insumo.stock_actual < cantidad:
                raise ValueError(
                    f"Stock insuficiente: disponible={insumo.stock_actual}, "
                    f"solicitado={cantidad}."
                )
            insumo.stock_actual -= cantidad
        elif tipo == TipoMovimiento.AJUSTE:
            insumo.stock_actual = cantidad  # ajuste manual al valor exacto

        self._db.add(mov)
        self._db.commit()
        self._db.refresh(mov)
        return mov

    def insumos_bajo_stock(self) -> list[Insumo]:
        """Retorna insumos que requieren reabastecimiento."""
        return [i for i in self.listar_insumos() if i.requiere_reabastecimiento]
