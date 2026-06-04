"""
app/core/security.py
JWT, hashing de contraseñas y dependencias de autenticación con soporte multi-tenant.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.domain.usuario import Usuario, RolUsuario

SUPERADMIN_EMAIL = "vm.parra10@ciaf.edu.co"

oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/usuarios/login")
ALGORITHM      = "HS256"

# Contexto de hashing — bcrypt gestionado por passlib (compatible con Vercel)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Contraseñas ────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


# ─── JWT ────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Dependencias ───────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    payload = decode_token(token)
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token sin sujeto")
    user = db.get(Usuario, int(user_id))
    if not user or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


def require_admin(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    if not current_user.es_admin:
        raise HTTPException(status_code=403, detail="Se requiere rol ADMIN o superior")
    return current_user


def require_superadmin(
    current_user: Usuario = Depends(get_current_active_user),
) -> Usuario:
    if not current_user.es_superadmin:
        raise HTTPException(status_code=403, detail="Acceso exclusivo para SUPERADMIN")
    return current_user


# ─── Helpers de aislamiento ─────────────────────────────────────────────────

def get_finca_id_or_raise(user: Usuario) -> int:
    if user.es_superadmin and user.finca_id:
        return user.finca_id
    if user.finca_id is None:
        raise HTTPException(
            status_code=400,
            detail="Tu cuenta no tiene una finca asignada. Contacta al administrador.",
        )
    return user.finca_id


def assert_same_finca(user: Usuario, finca_id: int) -> None:
    if user.es_superadmin:
        return
    if user.finca_id != finca_id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para acceder a recursos de otra finca",
        )