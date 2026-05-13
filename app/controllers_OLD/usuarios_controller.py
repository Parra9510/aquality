"""
app/controllers/usuarios_controller.py
Endpoints REST para el módulo de usuarios (registro, login, CRUD).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.usuario import Usuario
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.usuario import RolUsuario
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ── Schemas Pydantic ─────────────────────────────────────────────────────────
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


# ── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/usuarios")
def registrar_usuario(
    datos: UsuarioCrear,
    db: Session = Depends(get_db)
):

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        password=datos.password,
        rol=datos.rol
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return nuevo_usuario

@router.post("/login")
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    """Autentica credenciales y retorna datos del usuario."""
    svc = UsuarioService(db)
    usuario = svc.autenticar(datos.email, datos.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    return {"mensaje": "Autenticación exitosa.", "usuario": usuario.to_dict()}


@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos los usuarios registrados."""
    svc = UsuarioService(db)
    return [u.to_dict() for u in svc.listar()]


@router.get("/{usuario_id}")
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por su ID."""
    svc = UsuarioService(db)
    usuario = svc.obtener(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return usuario.to_dict()


@router.patch("/{usuario_id}/rol")
def actualizar_rol(usuario_id: int, datos: UsuarioRolActualizar,
                   db: Session = Depends(get_db)):
    """Actualiza el rol de un usuario."""
    svc = UsuarioService(db)
    try:
        usuario = svc.actualizar_rol(usuario_id, datos.rol)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"mensaje": "Rol actualizado.", "usuario": usuario.to_dict()}


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Elimina un usuario del sistema."""
    svc = UsuarioService(db)
    eliminado = svc.eliminar(usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"mensaje": f"Usuario id={usuario_id} eliminado."}
