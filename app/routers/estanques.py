"""
app/routers/estanques.py
Endpoints REST para gestión de estanques y monitoreo.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- IMPORTS CORREGIDOS (Asegúrate de que estas rutas existan) ---
from app.core.database import get_db
from app.services.estanques_service import EstanquesService # Necesitarás crear este servicio

# ESTA ES LA LÍNEA QUE TE DABA EL ERROR:
router = APIRouter(prefix="/estanques", tags=["Estanques"])

# ── Schemas Pydantic ─────────────────────────────────────────────────────────
class EstanqueCrear(BaseModel):
    nombre: str
    capacidad_litros: float
    ubicacion: str | None = None

class EstanqueActualizar(BaseModel):
    nombre: str | None = None
    capacidad_litros: float | None = None
    estado: str | None = None # Ejemplo: Activo, En mantenimiento

# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/")
def listar_estanques(db: Session = Depends(get_db)):
    svc = EstanquesService(db)
    # Suponiendo que tu servicio tiene un método listar_todos
    return [e.to_dict() for e in svc.listar_todos()]

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_estanque(datos: EstanqueCrear, db: Session = Depends(get_db)):
    svc = EstanquesService(db)
    try:
        nuevo_estanque = svc.crear_estanque(**datos.model_dump())
        return {"mensaje": "Estanque creado con éxito", "estanque": nuevo_estanque.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{estanque_id}")
def obtener_estanque(estanque_id: int, db: Session = Depends(get_db)):
    svc = EstanquesService(db)
    estanque = svc.obtener_por_id(estanque_id)
    if not estanque:
        raise HTTPException(status_code=404, detail="Estanque no encontrado")
    return estanque.to_dict()