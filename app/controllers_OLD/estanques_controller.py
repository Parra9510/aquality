"""
app/controllers/usuarios_controller.py
Endpoints REST – Usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.usuario import RolUsuario
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class UsuarioCrear(BaseModel):
    nombre:   str
    email:    EmailStr
    password: str
    rol:      str = RolUsuario.OPERARIO


class UsuarioLogin(BaseModel):
    email:    EmailStr
    password: str


class RolActualizar(BaseModel):
    rol: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioCrear, db: Session = Depends(get_db)):
    try:
        u = UsuarioService(db).registrar(**datos.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"mensaje": "Usuario registrado.", "usuario": u.to_dict()}


@router.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    u = UsuarioService(db).autenticar(datos.email, datos.password)
    if not u:
        raise HTTPException(401, "Credenciales incorrectas.")
    return {"mensaje": "Autenticación exitosa.", "usuario": u.to_dict()}


@router.get("/")
def listar(db: Session = Depends(get_db)):
    return [u.to_dict() for u in UsuarioService(db).listar()]


@router.get("/{usuario_id}")
def obtener(usuario_id: int, db: Session = Depends(get_db)):
    u = UsuarioService(db).obtener(usuario_id)
    if not u:
        raise HTTPException(404, "Usuario no encontrado.")
    return u.to_dict()


@router.patch("/{usuario_id}/rol")
def actualizar_rol(usuario_id: int, datos: RolActualizar, db: Session = Depends(get_db)):
    try:
        u = UsuarioService(db).actualizar_rol(usuario_id, datos.rol)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"mensaje": "Rol actualizado.", "usuario": u.to_dict()}


@router.delete("/{usuario_id}")
def eliminar(usuario_id: int, db: Session = Depends(get_db)):
    if not UsuarioService(db).eliminar(usuario_id):
        raise HTTPException(404, "Usuario no encontrado.")
    return {"mensaje": f"Usuario id={usuario_id} eliminado."}