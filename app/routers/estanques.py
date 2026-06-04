"""
app/routers/estanques.py
CRUD de estanques con aislamiento por finca.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database  import get_db
from app.core.security  import get_current_active_user, require_admin, assert_same_finca, get_finca_id_or_raise
from app.domain.estanque import Estanque, EstadoEstanque, EtapaProductiva
from app.domain.usuario  import Usuario
from app.domain.finca    import Finca

router = APIRouter(prefix="/estanques", tags=["Estanques"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class EstanqueCreate(BaseModel):
    codigo:           Optional[str]   = None
    nombre:           str
    etapa:            Optional[str]   = None
    largo:            Optional[float] = None
    ancho:            Optional[float] = None
    profundidad:      Optional[float] = None
    capacidad_kg:     Optional[float] = None
    capacidad_litros: Optional[float] = None
    ubicacion:        Optional[str]   = None
    finca_id:         Optional[int]   = None


class EstanqueUpdate(BaseModel):
    nombre:           Optional[str]             = None
    capacidad_litros: Optional[float]           = None
    estado:           Optional[EstadoEstanque]  = None
    etapa:            Optional[EtapaProductiva] = None
    activo:           Optional[bool]            = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/", summary="Listar estanques de mi finca")
def listar_estanques(
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    q = db.query(Estanque)
    if not current_user.es_superadmin:
        q = q.filter(Estanque.finca_id == current_user.finca_id)
    estanques = q.order_by(Estanque.id).all()
    return [e.to_dict() for e in estanques]


@router.post("/", summary="Crear estanque en mi finca")
def crear_estanque(
    body:         EstanqueCreate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    if current_user.es_superadmin and body.finca_id:
        finca_id = body.finca_id
        if not db.get(Finca, finca_id):
            raise HTTPException(404, "Finca no encontrada")
    else:
        finca_id = get_finca_id_or_raise(current_user)

    capacidad = body.capacidad_kg or body.capacidad_litros or 0
    if capacidad <= 0:
        raise HTTPException(400, "La capacidad debe ser mayor a cero")

    etapa_valor = None
    if body.etapa:
        etapa_map = {
            "incubacion": "alevinaje", "incubación": "alevinaje",
            "alevinaje": "alevinaje", "dedinos": "levante",
            "engorde": "engorde", "cosecha": "cosecha", "descanso": "descanso",
        }
        clave = body.etapa.lower().strip()
        try:
            etapa_valor = EtapaProductiva(etapa_map.get(clave, clave))
        except ValueError:
            etapa_valor = None

    count = db.query(Estanque).filter(Estanque.finca_id == finca_id).count()
    nuevo = Estanque(
        codigo       = body.codigo or f"EST-{count + 1:02d}",
        nombre       = body.nombre,
        capacidad_kg = capacidad,
        etapa        = etapa_valor,
        finca_id     = finca_id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo.to_dict()


@router.get("/{estanque_id}", summary="Ver estanque")
def obtener_estanque(
    estanque_id:  int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(404, "Estanque no encontrado")
    assert_same_finca(current_user, estanque.finca_id)
    return estanque.to_dict()


@router.put("/{estanque_id}", summary="Actualizar estanque")
def actualizar_estanque(
    estanque_id:  int,
    body:         EstanqueUpdate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(404, "Estanque no encontrado")
    assert_same_finca(current_user, estanque.finca_id)

    if body.nombre           is not None: estanque.nombre       = body.nombre
    if body.capacidad_litros is not None: estanque.capacidad_kg = body.capacidad_litros
    if body.estado           is not None: estanque.estado       = body.estado
    if body.etapa            is not None: estanque.etapa        = body.etapa
    if body.activo           is not None: estanque.activo       = body.activo

    db.commit()
    db.refresh(estanque)
    return estanque.to_dict()


@router.delete("/{estanque_id}", summary="Eliminar estanque (ADMIN)")
def eliminar_estanque(
    estanque_id:  int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(404, "Estanque no encontrado")
    assert_same_finca(current_user, estanque.finca_id)
    db.delete(estanque)
    db.commit()
    return {"ok": True}
