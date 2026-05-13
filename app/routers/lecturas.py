"""
app/routers/lecturas.py
Endpoints REST – Monitoreo hídrico y clima.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

# --- IMPORTS CORREGIDOS ---
from app.core.database import get_db
from app.services.lectura_service import LecturaService
from app.services.clima_service import ClimaService, ClimaAPIError

router = APIRouter(prefix="/lecturas", tags=["Monitoreo Hídrico"])


class LecturaCrear(BaseModel):
    estanque_id: int
    usuario_id:  int
    temperatura: float
    ph:          float
    oxigeno:     float
    observacion: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar(datos: LecturaCrear, db: Session = Depends(get_db)):
    try:
        # Usamos model_dump() para Pydantic v2
        l = LecturaService(db).registrar(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"mensaje": "Lectura registrada.", "lectura": l.to_dict()}


@router.get("/estanque/{estanque_id}")
def por_estanque(estanque_id: int, limite: int = 50, db: Session = Depends(get_db)):
    return [l.to_dict() for l in LecturaService(db).listar_por_estanque(estanque_id, limite)]


@router.get("/alertas")
def alertas(db: Session = Depends(get_db)):
    return [l.to_dict() for l in LecturaService(db).alertas_activas()]


@router.get("/resumen/{estanque_id}")
def resumen(estanque_id: int, db: Session = Depends(get_db)):
    return LecturaService(db).resumen_estanque(estanque_id)


@router.delete("/{lectura_id}")
def eliminar(lectura_id: int, db: Session = Depends(get_db)):
    if not LecturaService(db).eliminar(lectura_id):
        raise HTTPException(404, "Lectura no encontrada.")
    return {"mensaje": f"Lectura id={lectura_id} eliminada."}


@router.get("/clima/actual")
def clima(lat: float = 4.8133, lon: float = -75.6189):
    svc = ClimaService()
    try:
        datos = svc.obtener_clima_actual(lat, lon)
        datos["temperatura_agua_estimada_c"] = svc.estimar_temperatura_agua(lat, lon)
        return datos
    except ClimaAPIError as e:
        raise HTTPException(502, str(e))