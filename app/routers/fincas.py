"""
app/routers/fincas.py
Gestión de Fincas — solo accesible por SUPERADMIN.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import require_superadmin
from app.domain.finca   import Finca
from app.domain.usuario import Usuario

router = APIRouter(prefix="/fincas", tags=["Fincas"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class FincaCreate(BaseModel):
    nombre:      str
    descripcion: Optional[str] = None


class FincaUpdate(BaseModel):
    nombre:      Optional[str] = None
    descripcion: Optional[str] = None
    activa:      Optional[bool] = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/", summary="Listar todas las fincas (SUPERADMIN)")
def listar_fincas(
    db:      Session  = Depends(get_db),
    _:       Usuario  = Depends(require_superadmin),
):
    fincas = db.query(Finca).order_by(Finca.id).all()
    return [f.to_dict() for f in fincas]


@router.post("/", summary="Crear finca (SUPERADMIN)")
def crear_finca(
    body:    FincaCreate,
    db:      Session  = Depends(get_db),
    _:       Usuario  = Depends(require_superadmin),
):
    nueva = Finca(nombre=body.nombre, descripcion=body.descripcion)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva.to_dict()


@router.get("/{finca_id}", summary="Ver finca (SUPERADMIN)")
def obtener_finca(
    finca_id: int,
    db:       Session  = Depends(get_db),
    _:        Usuario  = Depends(require_superadmin),
):
    finca = db.get(Finca, finca_id)
    if not finca:
        raise HTTPException(404, "Finca no encontrada")
    return finca.to_dict()


@router.put("/{finca_id}", summary="Actualizar finca (SUPERADMIN)")
def actualizar_finca(
    finca_id: int,
    body:     FincaUpdate,
    db:       Session  = Depends(get_db),
    _:        Usuario  = Depends(require_superadmin),
):
    finca = db.get(Finca, finca_id)
    if not finca:
        raise HTTPException(404, "Finca no encontrada")
    if body.nombre      is not None: finca.nombre      = body.nombre
    if body.descripcion is not None: finca.descripcion = body.descripcion
    if body.activa      is not None: finca.activa      = body.activa
    db.commit()
    db.refresh(finca)
    return finca.to_dict()


@router.delete("/{finca_id}", summary="Eliminar finca (SUPERADMIN)")
def eliminar_finca(
    finca_id: int,
    db:       Session  = Depends(get_db),
    _:        Usuario  = Depends(require_superadmin),
):
    finca = db.get(Finca, finca_id)
    if not finca:
        raise HTTPException(404, "Finca no encontrada")
    db.delete(finca)
    db.commit()
    return {"ok": True, "mensaje": f"Finca {finca_id} eliminada"}
