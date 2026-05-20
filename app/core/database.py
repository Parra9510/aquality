"""
app/core/database.py
Configuración de SQLAlchemy para PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
_connect_args = {"check_same_thread": False} if db_url and db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=_connect_args,
    pool_pre_ping=True,   # detecta conexiones caídas antes de usarlas
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
    # Importar en orden: Finca primero (tabla padre de todo)
    from app.domain import finca, usuario, lectura, inventario, personal, estanque  # noqa: F401
    Base.metadata.create_all(bind=engine)
