"""
app/routers/biomasa.py
Endpoints para Biomasa (siembras) y Alimentación con aislamiento por finca.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, require_admin, assert_same_finca
from app.domain.usuario import Usuario
from app.domain.estanque import Estanque
from app.domain.biomasa import Siembra, Alimentacion, EtapaBiomasa, TipoAlimento

router = APIRouter(prefix="/biomasa", tags=["Biomasa"])


# ─── Helpers ────────────────────────────────────────────────────────────────

def _verificar_estanque(db: Session, estanque_id: int, user: Usuario) -> Estanque:
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(404, f"Estanque {estanque_id} no encontrado")
    assert_same_finca(user, estanque.finca_id)
    return estanque


# ─── Schemas ────────────────────────────────────────────────────────────────

class SiembraCreate(BaseModel):
    estanque_id:    int
    fecha:          str
    cantidad:       int
    peso_inicial_g: float
    proveedor:      Optional[str] = None
    etapa:          EtapaBiomasa  = EtapaBiomasa.ALEVINAJE
    observacion:    Optional[str] = None


class AlimentacionCreate(BaseModel):
    estanque_id:      int
    fecha:            str
    tipo_alimento:    TipoAlimento
    cantidad_kg:      float
    alimento_acum_kg: Optional[float] = None
    ganancia_peso_kg: Optional[float] = None


# ─── Siembras ───────────────────────────────────────────────────────────────

@router.post("/siembras", summary="Registrar siembra")
def registrar_siembra(
    body:         SiembraCreate,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    estanque = _verificar_estanque(db, body.estanque_id, current_user)
    biomasa_kg = round((body.cantidad * body.peso_inicial_g) / 1000, 2)

    siembra = Siembra(
        estanque_id    = body.estanque_id,
        finca_id       = estanque.finca_id,
        usuario_id     = current_user.id,
        fecha          = body.fecha,
        cantidad       = body.cantidad,
        peso_inicial_g = body.peso_inicial_g,
        biomasa_kg     = biomasa_kg,
        proveedor      = body.proveedor,
        etapa          = body.etapa,
        observacion    = body.observacion,
    )
    db.add(siembra)
    db.commit()
    db.refresh(siembra)
    return siembra.to_dict()


@router.get("/siembras", summary="Listar siembras de mi finca")
def listar_siembras(
    estanque_id:  Optional[int] = None,
    limite:       int           = 50,
    db:           Session       = Depends(get_db),
    current_user: Usuario       = Depends(get_current_active_user),
):
    q = db.query(Siembra)
    if not current_user.es_superadmin:
        q = q.filter(Siembra.finca_id == current_user.finca_id)
    if estanque_id:
        q = q.filter(Siembra.estanque_id == estanque_id)
    return [s.to_dict() for s in q.order_by(Siembra.registrado_en.desc()).limit(limite).all()]


@router.delete("/siembras/{siembra_id}", summary="Eliminar siembra (ADMIN)")
def eliminar_siembra(
    siembra_id:   int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    siembra = db.get(Siembra, siembra_id)
    if not siembra:
        raise HTTPException(404, "Siembra no encontrada")
    assert_same_finca(current_user, siembra.finca_id)
    db.delete(siembra)
    db.commit()
    return {"ok": True}


# ─── Alimentación ───────────────────────────────────────────────────────────

@router.post("/alimentacion", summary="Registrar ración de alimentación")
def registrar_alimentacion(
    body:         AlimentacionCreate,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    estanque = _verificar_estanque(db, body.estanque_id, current_user)

    fcr = None
    if body.alimento_acum_kg and body.ganancia_peso_kg and body.ganancia_peso_kg > 0:
        fcr = round(body.alimento_acum_kg / body.ganancia_peso_kg, 2)

    alim = Alimentacion(
        estanque_id      = body.estanque_id,
        finca_id         = estanque.finca_id,
        usuario_id       = current_user.id,
        fecha            = body.fecha,
        tipo_alimento    = body.tipo_alimento,
        cantidad_kg      = body.cantidad_kg,
        alimento_acum_kg = body.alimento_acum_kg,
        ganancia_peso_kg = body.ganancia_peso_kg,
        fcr              = fcr,
    )
    db.add(alim)
    db.commit()
    db.refresh(alim)
    return alim.to_dict()


@router.get("/alimentacion", summary="Listar registros de alimentación de mi finca")
def listar_alimentacion(
    estanque_id:  Optional[int] = None,
    limite:       int           = 50,
    db:           Session       = Depends(get_db),
    current_user: Usuario       = Depends(get_current_active_user),
):
    q = db.query(Alimentacion)
    if not current_user.es_superadmin:
        q = q.filter(Alimentacion.finca_id == current_user.finca_id)
    if estanque_id:
        q = q.filter(Alimentacion.estanque_id == estanque_id)
    return [a.to_dict() for a in q.order_by(Alimentacion.registrado_en.desc()).limit(limite).all()]


@router.delete("/alimentacion/{alim_id}", summary="Eliminar registro de alimentación (ADMIN)")
def eliminar_alimentacion(
    alim_id:      int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    alim = db.get(Alimentacion, alim_id)
    if not alim:
        raise HTTPException(404, "Registro no encontrado")
    assert_same_finca(current_user, alim.finca_id)
    db.delete(alim)
    db.commit()
    return {"ok": True}