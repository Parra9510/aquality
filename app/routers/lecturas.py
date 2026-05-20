"""
app/routers/lecturas.py
Monitoreo de calidad del agua con aislamiento por finca.
El aislamiento se garantiza verificando que el estanque pertenezca a la finca del usuario.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database  import get_db
from app.core.security  import get_current_active_user, require_admin, assert_same_finca
from app.domain.lectura  import Lectura
from app.domain.estanque import Estanque
from app.domain.usuario  import Usuario
from app.services.lectura_service import LecturaService
from app.services.clima_service import ClimaService, ClimaAPIError

router = APIRouter(prefix="/lecturas", tags=["Lecturas"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class LecturaCreate(BaseModel):
    estanque_id:  int
    temperatura:  float
    ph:           float
    oxigeno:      float
    observacion:  Optional[str] = None


# ─── Helpers ────────────────────────────────────────────────────────────────

def _verificar_estanque(db: Session, estanque_id: int, user: Usuario) -> Estanque:
    """Carga el estanque y verifica que pertenezca a la finca del usuario."""
    estanque = db.get(Estanque, estanque_id)
    if not estanque:
        raise HTTPException(404, f"Estanque {estanque_id} no encontrado")
    assert_same_finca(user, estanque.finca_id)
    return estanque


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("/clima/actual", summary="Clima actual de la piscifactoría")
def clima_actual(
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Devuelve temperatura ambiente, humedad, precipitación, viento
    y temperatura estimada del agua desde Open-Meteo.
    """
    svc = ClimaService()
    try:
        datos = svc.obtener_clima_actual()
        datos["temperatura_agua_estimada_c"] = svc.estimar_temperatura_agua()
        return datos
    except ClimaAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/", summary="Registrar lectura en un estanque de mi finca")
def registrar_lectura(
    body:         LecturaCreate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(get_current_active_user),
):
    _verificar_estanque(db, body.estanque_id, current_user)
    svc = LecturaService(db)
    lectura = svc.registrar(
        estanque_id=body.estanque_id,
        usuario_id=current_user.id,
        temperatura=body.temperatura,
        ph=body.ph,
        oxigeno=body.oxigeno,
        observacion=body.observacion,
    )
    return lectura.to_dict()


@router.get("/estanque/{estanque_id}", summary="Historial de lecturas de un estanque")
def listar_lecturas_estanque(
    estanque_id:  int,
    limite:       int     = 50,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    _verificar_estanque(db, estanque_id, current_user)
    svc = LecturaService(db)
    lecturas = svc.listar_por_estanque(estanque_id, limite=limite)
    return [l.to_dict() for l in lecturas]


@router.get("/estanque/{estanque_id}/resumen", summary="Resumen estadístico de un estanque")
def resumen_estanque(
    estanque_id:  int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    _verificar_estanque(db, estanque_id, current_user)
    svc = LecturaService(db)
    return svc.resumen_estanque(estanque_id)


@router.get("/alertas", summary="Alertas activas de mi finca")
def alertas_activas(
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    """
    Devuelve lecturas con alerta=True, filtradas por la finca del usuario.
    SUPERADMIN ve todas las alertas de todas las fincas.
    """
    q = (
        db.query(Lectura)
        .join(Estanque, Lectura.estanque_id == Estanque.id)
        .filter(Lectura.alerta.is_(True))
    )
    if not current_user.es_superadmin:
        q = q.filter(Estanque.finca_id == current_user.finca_id)
    alertas = q.order_by(Lectura.registrado_en.desc()).limit(100).all()
    return [a.to_dict() for a in alertas]


@router.get("/{lectura_id}", summary="Ver lectura")
def obtener_lectura(
    lectura_id:   int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
):
    svc     = LecturaService(db)
    lectura = svc.obtener(lectura_id)
    if not lectura:
        raise HTTPException(404, "Lectura no encontrada")
    _verificar_estanque(db, lectura.estanque_id, current_user)
    return lectura.to_dict()


@router.delete("/{lectura_id}", summary="Eliminar lectura (ADMIN)")
def eliminar_lectura(
    lectura_id:   int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    svc     = LecturaService(db)
    lectura = svc.obtener(lectura_id)
    if not lectura:
        raise HTTPException(404, "Lectura no encontrada")
    _verificar_estanque(db, lectura.estanque_id, current_user)
    svc.eliminar(lectura_id)
    return {"ok": True}