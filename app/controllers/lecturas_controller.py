"""
app/controllers/lecturas_controller.py
Endpoints REST para el módulo de monitoreo hídrico.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.services.lectura_service import LecturaService
from app.services.clima_service import ClimaService, ClimaAPIError

router = APIRouter(prefix="/lecturas", tags=["Monitoreo Hídrico"])


class LecturaCrear(BaseModel):
    estanque_id: int
    usuario_id:  int
    temperatura: float
    ph:          float
    oxigeno:     float
    observacion: str | None = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_lectura(datos: LecturaCrear, db: Session = Depends(get_db)):
    """Registra una nueva lectura de calidad hídrica."""
    svc = LecturaService(db)
    try:
        lectura = svc.registrar(
            estanque_id=datos.estanque_id,
            usuario_id=datos.usuario_id,
            temperatura=datos.temperatura,
            ph=datos.ph,
            oxigeno=datos.oxigeno,
            observacion=datos.observacion,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Lectura registrada.", "lectura": lectura.to_dict()}


@router.get("/estanque/{estanque_id}")
def listar_por_estanque(estanque_id: int, limite: int = 50,
                         db: Session = Depends(get_db)):
    """Lista las últimas lecturas de un estanque."""
    svc = LecturaService(db)
    lecturas = svc.listar_por_estanque(estanque_id, limite)
    return [l.to_dict() for l in lecturas]


@router.get("/alertas")
def alertas_activas(db: Session = Depends(get_db)):
    """Retorna lecturas con parámetros fuera del rango seguro."""
    svc = LecturaService(db)
    return [l.to_dict() for l in svc.alertas_activas()]


@router.get("/resumen/{estanque_id}")
def resumen_estanque(estanque_id: int, db: Session = Depends(get_db)):
    """Informe estadístico de las últimas 50 lecturas de un estanque."""
    svc = LecturaService(db)
    return svc.resumen_estanque(estanque_id)


@router.delete("/{lectura_id}")
def eliminar_lectura(lectura_id: int, db: Session = Depends(get_db)):
    """Elimina una lectura por ID."""
    svc = LecturaService(db)
    eliminado = svc.eliminar(lectura_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Lectura no encontrada.")
    return {"mensaje": f"Lectura id={lectura_id} eliminada."}


@router.get("/clima/actual")
def clima_actual(lat: float = 4.8133, lon: float = -75.6189):
    """
    Consulta temperatura ambiente desde API externa Open-Meteo.
    Útil para correlacionar con temperatura del agua en estanques.
    """
    svc = ClimaService()
    try:
        clima = svc.obtener_clima_actual(latitud=lat, longitud=lon)
        clima["temperatura_agua_estimada_c"] = svc.estimar_temperatura_agua(lat, lon)
        return clima
    except ClimaAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
