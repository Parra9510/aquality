"""
app/routers/usuarios.py
Endpoints REST para el módulo de usuarios.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.domain.usuario import RolUsuario
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


class UsuarioRolActualizar(BaseModel):
    rol: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: UsuarioCrear, db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    try:
        usuario = svc.registrar(
            nombre=datos.nombre,
            email=datos.email,
            password=datos.password,
            rol=datos.rol,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(exc)}")
    return {"mensaje": "Usuario registrado correctamente.", "usuario": usuario.to_dict()}


@router.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    usuario = svc.autenticar(datos.email, datos.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    return {"mensaje": "Autenticación exitosa.", "usuario": usuario.to_dict()}


@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    return [u.to_dict() for u in svc.listar()]


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    usuario = svc.obtener(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario.to_dict()


@router.patch("/{usuario_id}/rol")
def actualizar_rol(usuario_id: int, datos: UsuarioRolActualizar,
                   db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    try:
        usuario = svc.actualizar_rol(usuario_id, datos.rol)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Rol actualizado.", "usuario": usuario.to_dict()}


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    svc = UsuarioService(db)
    if not svc.eliminar(usuario_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"mensaje": f"Usuario id={usuario_id} eliminado."}