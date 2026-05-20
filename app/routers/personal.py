"""
app/routers/personal.py
Gestión de personal con aislamiento por finca.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database  import get_db
from app.core.security  import get_current_active_user, require_admin, assert_same_finca, get_finca_id_or_raise
from app.domain.personal import Personal
from app.domain.usuario  import Usuario
from app.domain.finca    import Finca

router = APIRouter(prefix="/personal", tags=["Personal"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class PersonalCreate(BaseModel):
    cedula:        str
    nombre:        str
    cargo:         Optional[str]  = ""
    telefono:      Optional[str]  = None
    fecha_ingreso: Optional[date] = None
    finca_id:      Optional[int]  = None  # Solo SUPERADMIN


class PersonalUpdate(BaseModel):
    nombre:        Optional[str]  = None
    cargo:         Optional[str]  = None
    telefono:      Optional[str]  = None
    fecha_ingreso: Optional[date] = None
    activo:        Optional[bool] = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/", summary="Listar personal de mi finca")
def listar_personal(
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    q = db.query(Personal)
    if not current_user.es_superadmin:
        q = q.filter(Personal.finca_id == current_user.finca_id)
    return [p.to_dict() for p in q.order_by(Personal.nombre).all()]


@router.post("/", summary="Añadir personal a mi finca")
def crear_personal(
    body:         PersonalCreate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    if current_user.es_superadmin and body.finca_id:
        finca_id = body.finca_id
        if not db.get(Finca, finca_id):
            raise HTTPException(404, "Finca no encontrada")
    else:
        finca_id = get_finca_id_or_raise(current_user)

    # Cédula única dentro de la misma finca
    existe = db.query(Personal).filter(
        Personal.cedula   == body.cedula,
        Personal.finca_id == finca_id,
    ).first()
    if existe:
        raise HTTPException(400, f"Ya existe personal con cédula '{body.cedula}' en esta finca")

    persona = Personal(
        cedula        = body.cedula,
        nombre        = body.nombre,
        cargo         = body.cargo or "",
        telefono      = body.telefono,
        fecha_ingreso = body.fecha_ingreso,
        finca_id      = finca_id,
        usuario_id    = current_user.id,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return persona.to_dict()


@router.get("/{persona_id}", summary="Ver persona")
def obtener_personal(
    persona_id:   int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(404, "Personal no encontrado")
    assert_same_finca(current_user, persona.finca_id)
    return persona.to_dict()


@router.put("/{persona_id}", summary="Actualizar persona")
def actualizar_personal(
    persona_id:   int,
    body:         PersonalUpdate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(404, "Personal no encontrado")
    assert_same_finca(current_user, persona.finca_id)

    if body.nombre        is not None: persona.nombre        = body.nombre
    if body.cargo         is not None: persona.cargo         = body.cargo
    if body.telefono      is not None: persona.telefono      = body.telefono
    if body.fecha_ingreso is not None: persona.fecha_ingreso = body.fecha_ingreso
    if body.activo        is not None: persona.activo        = body.activo

    db.commit()
    db.refresh(persona)
    return persona.to_dict()


@router.delete("/{persona_id}", summary="Eliminar persona (ADMIN)")
def eliminar_personal(
    persona_id:   int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(404, "Personal no encontrado")
    assert_same_finca(current_user, persona.finca_id)
    db.delete(persona)
    db.commit()
    return {"ok": True}
