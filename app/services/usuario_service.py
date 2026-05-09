"""
app/services/usuario_service.py
Lógica de negocio para registro y consulta de usuarios.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.usuario import Usuario, RolUsuario
from app.utils.validaciones import validar_email, sanitizar_texto


class UsuarioService:
    """Servicio de dominio para gestión de usuarios del sistema."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def registrar(self, nombre: str, email: str, password: str,
                  rol: str = RolUsuario.OPERARIO) -> Usuario:
        """CRUD – CREATE. Registra un nuevo usuario con validaciones."""
        nombre = sanitizar_texto(nombre, max_len=100)
        email  = email.strip().lower()

        if not validar_email(email):
            raise ValueError(f"El correo '{email}' no tiene un formato válido.")
        if rol not in RolUsuario.TODOS:
            raise ValueError(f"Rol '{rol}' no permitido. Opciones: {RolUsuario.TODOS}")

        existente = self._db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            raise ValueError(f"Ya existe un usuario registrado con el email '{email}'.")

        try:
            usuario = Usuario(nombre=nombre, email=email, password=password, rol=rol)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        self._db.add(usuario)
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    def autenticar(self, email: str, password: str) -> Usuario | None:
        """Verifica credenciales y retorna el usuario o None."""
        usuario = self._db.query(Usuario).filter(
            Usuario.email == email.strip().lower()
        ).first()
        if usuario and usuario.verificar_password(password):
            return usuario
        return None

    def listar(self) -> list[Usuario]:
        """CRUD – READ todos los usuarios."""
        return self._db.query(Usuario).order_by(Usuario.nombre).all()

    def obtener(self, usuario_id: int) -> Usuario | None:
        """CRUD – READ por id."""
        return self._db.get(Usuario, usuario_id)

    def actualizar_rol(self, usuario_id: int, nuevo_rol: str) -> Usuario:
        """CRUD – UPDATE del rol de un usuario."""
        if nuevo_rol not in RolUsuario.TODOS:
            raise ValueError(f"Rol inválido: {nuevo_rol}")
        usuario = self._db.get(Usuario, usuario_id)
        if not usuario:
            raise ValueError(f"Usuario id={usuario_id} no encontrado.")
        usuario.rol = nuevo_rol
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    def eliminar(self, usuario_id: int) -> bool:
        """CRUD – DELETE."""
        usuario = self._db.get(Usuario, usuario_id)
        if not usuario:
            return False
        self._db.delete(usuario)
        self._db.commit()
        return True
