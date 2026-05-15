"""
app/core/database.py
Configuración de SQLAlchemy para PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL

# Si no hay DATABASE_URL configurada, lanzar error claro en lugar de crashear
if not db_url:
    raise RuntimeError(
        "DATABASE_URL no está configurada. "
        "Agregála en Vercel → Settings → Environment Variables."
    )

# Corregir prefijo para Render/Railway que usa "postgres://"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# SQLite solo en desarrollo local
_connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas si no existen."""
    from app.domain import usuario, lectura, inventario, personal, estanque  # noqa: F401
    Base.metadata.create_all(bind=engine)