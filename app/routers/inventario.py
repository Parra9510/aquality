"""
app/routers/inventario.py
Gestión de inventario (insumos + movimientos) con aislamiento por finca.
Cada insumo pertenece a una sola finca. Usuarios de otras fincas no pueden verlos.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database   import get_db
from app.core.security   import get_current_active_user, require_admin, assert_same_finca, get_finca_id_or_raise
from app.domain.inventario import Insumo, Movimiento, TipoMovimiento
from app.domain.usuario    import Usuario
from app.domain.finca      import Finca
from app.services.inventario_service import InventarioService

router = APIRouter(prefix="/inventario", tags=["Inventario"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class InsumoCreate(BaseModel):
    nombre:        str
    unidad_medida: Optional[str]   = "kg"
    stock_minimo:  Optional[float] = 10.0
    descripcion:   Optional[str]   = None
    finca_id:      Optional[int]   = None  # Solo SUPERADMIN


class InsumoUpdate(BaseModel):
    nombre:        Optional[str]   = None
    unidad_medida: Optional[str]   = None
    stock_minimo:  Optional[float] = None
    descripcion:   Optional[str]   = None


class MovimientoCreate(BaseModel):
    insumo_id: int
    tipo:      TipoMovimiento
    cantidad:  float
    motivo:    Optional[str] = None


# ─── Helpers ────────────────────────────────────────────────────────────────

def _verificar_insumo(db: Session, insumo_id: int, user: Usuario) -> Insumo:
    insumo = db.get(Insumo, insumo_id)
    if not insumo:
        raise HTTPException(404, f"Insumo {insumo_id} no encontrado")
    assert_same_finca(user, insumo.finca_id)
    return insumo


# ─── Endpoints — Insumos ────────────────────────────────────────────────────

@router.get("/insumos", summary="Listar insumos de mi finca")
def listar_insumos(
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    q = db.query(Insumo)
    if not current_user.es_superadmin:
        q = q.filter(Insumo.finca_id == current_user.finca_id)
    return [i.to_dict() for i in q.order_by(Insumo.nombre).all()]


@router.post("/insumos", summary="Crear insumo en mi finca")
def crear_insumo(
    body:         InsumoCreate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    if current_user.es_superadmin and body.finca_id:
        finca_id = body.finca_id
        if not db.get(Finca, finca_id):
            raise HTTPException(404, "Finca no encontrada")
    else:
        finca_id = get_finca_id_or_raise(current_user)

    # Nombre único dentro de la misma finca
    existe = db.query(Insumo).filter(
        Insumo.nombre == body.nombre,
        Insumo.finca_id == finca_id,
    ).first()
    if existe:
        raise HTTPException(400, f"Ya existe un insumo '{body.nombre}' en esta finca")

    insumo = Insumo(
        nombre        = body.nombre,
        unidad_medida = body.unidad_medida,
        stock_minimo  = body.stock_minimo,
        descripcion   = body.descripcion,
        finca_id      = finca_id,
    )
    db.add(insumo)
    db.commit()
    db.refresh(insumo)
    return insumo.to_dict()


@router.get("/insumos/bajo-stock", summary="Insumos bajo stock mínimo de mi finca")
def insumos_bajo_stock(
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    q = db.query(Insumo)
    if not current_user.es_superadmin:
        q = q.filter(Insumo.finca_id == current_user.finca_id)
    insumos = q.all()
    bajos = [i.to_dict() for i in insumos if i.stock_actual <= i.stock_minimo]
    return bajos


@router.get("/insumos/{insumo_id}", summary="Ver insumo")
def obtener_insumo(
    insumo_id:    int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    insumo = _verificar_insumo(db, insumo_id, current_user)
    return insumo.to_dict()


@router.put("/insumos/{insumo_id}", summary="Actualizar insumo")
def actualizar_insumo(
    insumo_id:    int,
    body:         InsumoUpdate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    insumo = _verificar_insumo(db, insumo_id, current_user)
    svc    = InventarioService(db)
    kwargs = body.dict(exclude_none=True)
    return svc.actualizar_insumo(insumo_id, **kwargs).to_dict()


@router.delete("/insumos/{insumo_id}", summary="Eliminar insumo (ADMIN)")
def eliminar_insumo(
    insumo_id:    int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    _verificar_insumo(db, insumo_id, current_user)
    svc = InventarioService(db)
    svc.eliminar_insumo(insumo_id)
    return {"ok": True}


# ─── Endpoints — Movimientos ─────────────────────────────────────────────────

@router.post("/movimientos", summary="Registrar movimiento de inventario")
def registrar_movimiento(
    body:         MovimientoCreate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    _verificar_insumo(db, body.insumo_id, current_user)
    svc = InventarioService(db)
    mov = svc.registrar_movimiento(
        insumo_id  = body.insumo_id,
        usuario_id = current_user.id,
        tipo       = body.tipo,
        cantidad   = body.cantidad,
        motivo     = body.motivo,
    )
    return mov.to_dict()


@router.get("/movimientos/{insumo_id}", summary="Historial de movimientos de un insumo")
def historial_movimientos(
    insumo_id:    int,
    limite:       int     = 50,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    _verificar_insumo(db, insumo_id, current_user)
    movs = (
        db.query(Movimiento)
        .filter(Movimiento.insumo_id == insumo_id)
        .order_by(Movimiento.registrado_en.desc())
        .limit(limite)
        .all()
    )
    return [m.to_dict() for m in movs]
