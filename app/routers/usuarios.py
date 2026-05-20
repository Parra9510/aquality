"""
app/routers/usuarios.py
Registro, login y gestión de usuarios con aislamiento por finca.

Flujo de registro:
  - Usuario nuevo → se crea una Finca con el nombre que indique → se le asigna como ADMIN de esa finca.
  - El SUPERADMIN puede asignar usuarios a fincas existentes.
  - vm.parra10@ciaf.edu.co siempre tiene rol SUPERADMIN automáticamente.
"""
from __future__ import annotations
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token,
    get_current_active_user, require_admin,
    assert_same_finca,
)
from app.core.config  import settings
from app.domain.finca   import Finca
from app.domain.usuario import Usuario, RolUsuario, SUPERADMIN_EMAIL

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class RegistroRequest(BaseModel):
    email:        EmailStr
    nombre:       str
    password:     str
    nombre_finca: Optional[str] = None   # Si no envía, se usa nombre del usuario como finca


class LoginResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    usuario_id:   int
    nombre:       str
    rol:          str
    finca_id:     Optional[int]


class UsuarioUpdate(BaseModel):
    nombre:   Optional[str] = None
    activo:   Optional[bool] = None
    rol:      Optional[RolUsuario] = None
    finca_id: Optional[int] = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/registro", summary="Registrar nuevo usuario + crear su finca")
def registrar(body: RegistroRequest, db: Session = Depends(get_db)):
    """
    Cualquier persona puede registrarse. Al hacerlo:
    1. Se crea una Finca exclusiva para él (o con el nombre que provea).
    2. El usuario queda como ADMIN de esa finca.
    Excepción: si el email es el del SUPERADMIN, se asigna rol SUPERADMIN sin finca.
    """
    # Verificar email único
    if db.query(Usuario).filter(Usuario.email == body.email).first():
        raise HTTPException(400, "El email ya está registrado")

    es_superadmin = body.email.lower() == SUPERADMIN_EMAIL.lower()

    finca = None
    if not es_superadmin:
        # Crear finca exclusiva
        nombre_finca = body.nombre_finca or f"Finca de {body.nombre}"
        finca = Finca(nombre=nombre_finca)
        db.add(finca)
        db.flush()  # Obtener ID sin hacer commit

    nuevo = Usuario(
        email      = body.email.lower(),
        nombre     = body.nombre,
        hashed_pwd = hash_password(body.password),
        rol        = RolUsuario.SUPERADMIN if es_superadmin else RolUsuario.ADMIN,
        finca_id   = finca.id if finca else None,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "ok":      True,
        "mensaje": "Usuario registrado correctamente",
        "usuario": nuevo.to_dict(),
        "finca":   finca.to_dict() if finca else None,
    }


@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   Session = Depends(get_db),
):
    user = db.query(Usuario).filter(Usuario.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.hashed_pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.activo:
        raise HTTPException(400, "Cuenta desactivada. Contacta al administrador.")

    # Garantizar SUPERADMIN si es el email especial
    if user.email == SUPERADMIN_EMAIL and user.rol != RolUsuario.SUPERADMIN:
        user.rol = RolUsuario.SUPERADMIN
        db.commit()

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return LoginResponse(
        access_token=token,
        usuario_id=user.id,
        nombre=user.nombre,
        rol=user.rol,
        finca_id=user.finca_id,
    )


@router.get("/me", summary="Perfil del usuario autenticado")
def mi_perfil(current_user: Usuario = Depends(get_current_active_user)):
    data = current_user.to_dict()
    if current_user.finca:
        data["finca"] = current_user.finca.to_dict()
    return data


@router.get("/", summary="Listar usuarios de mi finca (ADMIN) o todos (SUPERADMIN)")
def listar_usuarios(
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    if current_user.es_superadmin:
        usuarios = db.query(Usuario).order_by(Usuario.id).all()
    else:
        usuarios = (
            db.query(Usuario)
            .filter(Usuario.finca_id == current_user.finca_id)
            .order_by(Usuario.id)
            .all()
        )
    return [u.to_dict() for u in usuarios]


@router.put("/{usuario_id}", summary="Actualizar usuario")
def actualizar_usuario(
    usuario_id:   int,
    body:         UsuarioUpdate,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")

    # Verificar que pertenece a la misma finca (salvo SUPERADMIN)
    assert_same_finca(current_user, usuario.finca_id)

    # Proteger al SUPERADMIN de cambios de rol
    if usuario.email == SUPERADMIN_EMAIL and body.rol and body.rol != RolUsuario.SUPERADMIN:
        raise HTTPException(403, "No se puede cambiar el rol del SUPERADMIN")

    if body.nombre   is not None: usuario.nombre   = body.nombre
    if body.activo   is not None: usuario.activo   = body.activo
    if body.rol      is not None and current_user.es_superadmin:
        usuario.rol = body.rol
    if body.finca_id is not None and current_user.es_superadmin:
        finca = db.get(Finca, body.finca_id)
        if not finca:
            raise HTTPException(404, "Finca no encontrada")
        usuario.finca_id = body.finca_id

    db.commit()
    db.refresh(usuario)
    return usuario.to_dict()


@router.delete("/{usuario_id}", summary="Eliminar usuario (ADMIN de finca o SUPERADMIN)")
def eliminar_usuario(
    usuario_id:   int,
    db:           Session  = Depends(get_db),
    current_user: Usuario  = Depends(require_admin),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    if usuario.email == SUPERADMIN_EMAIL:
        raise HTTPException(403, "No se puede eliminar al SUPERADMIN")
    assert_same_finca(current_user, usuario.finca_id)
    db.delete(usuario)
    db.commit()
    return {"ok": True}
