"""
app/controllers/personal_controller.py
Endpoints REST para administración de personal.
"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.personal import Personal
from app.utils.validaciones import validar_cedula, sanitizar_texto

router = APIRouter(prefix="/personal", tags=["Personal"])


class PersonalCrear(BaseModel):
    cedula:        str
    nombre:        str
    cargo:         str
    fecha_ingreso: date
    telefono:      str | None = None


class PersonalActualizar(BaseModel):
    cargo:    str | None = None
    telefono: str | None = None
    activo:   bool | None = None


def _get_svc(db):
    """No hay servicio separado; operamos directamente (simplificación pedagógica)."""
    return db


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_personal(datos: PersonalCrear, db: Session = Depends(get_db)):
    if not validar_cedula(datos.cedula):
        raise HTTPException(status_code=400, detail="Cédula inválida (6-10 dígitos).")
    existente = db.query(Personal).filter(Personal.cedula == datos.cedula).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un colaborador con esa cédula.")
    persona = Personal(
        cedula=datos.cedula,
        nombre=sanitizar_texto(datos.nombre),
        cargo=sanitizar_texto(datos.cargo),
        fecha_ingreso=datos.fecha_ingreso,
        telefono=datos.telefono,
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)
    return {"mensaje": "Colaborador registrado.", "personal": persona.to_dict()}


@router.get("/")
def listar_personal(db: Session = Depends(get_db)):
    personas = db.query(Personal).order_by(Personal.nombre).all()
    return [p.to_dict() for p in personas]


@router.get("/{persona_id}")
def obtener_personal(persona_id: int, db: Session = Depends(get_db)):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado.")
    return persona.to_dict()


@router.patch("/{persona_id}")
def actualizar_personal(persona_id: int, datos: PersonalActualizar,
                         db: Session = Depends(get_db)):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado.")
    if datos.cargo   is not None: persona.cargo   = sanitizar_texto(datos.cargo)
    if datos.telefono is not None: persona.telefono = datos.telefono
    if datos.activo  is not None: persona.activo  = datos.activo
    db.commit()
    db.refresh(persona)
    return {"mensaje": "Colaborador actualizado.", "personal": persona.to_dict()}


@router.delete("/{persona_id}")
def desactivar_personal(persona_id: int, db: Session = Depends(get_db)):
    persona = db.get(Personal, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado.")
    persona.desactivar()
    db.commit()
    return {"mensaje": f"Colaborador id={persona_id} desactivado."}
