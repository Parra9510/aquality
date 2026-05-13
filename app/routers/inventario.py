"""
app/routers/inventario.py
Endpoints REST para gestión de inventario de insumos.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- IMPORTS CORREGIDOS ---
from app.core.database import get_db
from app.domain.inventario import TipoMovimiento  # Antes en app.models
from app.services.inventario_service import InventarioService

router = APIRouter(prefix="/inventario", tags=["Inventario"])

# ── Schemas Pydantic ─────────────────────────────────────────────────────────
class InsumoCrear(BaseModel):
    nombre:        str
    unidad_medida: str = "kg"
    stock_minimo:  float = 10.0
    descripcion:   str | None = None


class InsumoActualizar(BaseModel):
    nombre:        str | None = None
    stock_minimo:  float | None = None
    descripcion:   str | None = None


class MovimientoCrear(BaseModel):
    insumo_id:  int
    usuario_id: int
    tipo:       str   # entrada | salida | ajuste
    cantidad:   float
    motivo:     str | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/insumos", status_code=status.HTTP_201_CREATED)
def crear_insumo(datos: InsumoCrear, db: Session = Depends(get_db)):
    svc = InventarioService(db)
    try:
        insumo = svc.crear_insumo(**datos.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Insumo creado.", "insumo": insumo.to_dict()}


@router.get("/insumos")
def listar_insumos(db: Session = Depends(get_db)):
    svc = InventarioService(db)
    return [i.to_dict() for i in svc.listar_insumos()]


@router.get("/insumos/{insumo_id}")
def obtener_insumo(insumo_id: int, db: Session = Depends(get_db)):
    svc = InventarioService(db)
    insumo = svc.obtener_insumo(insumo_id)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo no encontrado.")
    return insumo.to_dict()


@router.patch("/insumos/{insumo_id}")
def actualizar_insumo(insumo_id: int, datos: InsumoActualizar,
                       db: Session = Depends(get_db)):
    svc = InventarioService(db)
    try:
        insumo = svc.actualizar_insumo(
            insumo_id, **{k: v for k, v in datos.model_dump().items() if v is not None}
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Insumo actualizado.", "insumo": insumo.to_dict()}


@router.delete("/insumos/{insumo_id}")
def eliminar_insumo(insumo_id: int, db: Session = Depends(get_db)):
    svc = InventarioService(db)
    try:
        eliminado = svc.eliminar_insumo(insumo_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not eliminado:
        raise HTTPException(status_code=404, detail="Insumo no encontrado.")
    return {"mensaje": f"Insumo id={insumo_id} eliminado."}


@router.post("/movimientos", status_code=status.HTTP_201_CREATED)
def registrar_movimiento(datos: MovimientoCrear, db: Session = Depends(get_db)):
    svc = InventarioService(db)
    try:
        mov = svc.registrar_movimiento(**datos.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Movimiento registrado.", "movimiento": mov.to_dict()}


@router.get("/alertas/bajo-stock")
def insumos_bajo_stock(db: Session = Depends(get_db)):
    svc = InventarioService(db)
    return [i.to_dict() for i in svc.insumos_bajo_stock()]