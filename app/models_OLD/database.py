"""
api/models/database.py
Configuración de SQLAlchemy.
Soporta PostgreSQL (producción) y SQLite (desarrollo local).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config.settings import DATABASE_URL

# SQLite necesita check_same_thread=False; PostgreSQL no lo acepta
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass


def get_db():
    """Generador de sesión para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas si no existen (útil para desarrollo/test)."""
    # Importar modelos para que SQLAlchemy los registre antes de create_all
    from app.models import usuario, estanque, lectura, inventario, personal  # noqa: F401
    Base.metadata.create_all(bind=engine)