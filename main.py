"""
main.py
Punto de entrada de AQUALITY – Sistema Integral para la Optimización Acuícola.
Ejecutar con: uvicorn main:app --reload
"""
from fastapi import FastAPI
from app.models.database import init_db
from app.controllers.usuarios_controller   import router as usuarios_router
from app.controllers.lecturas_controller   import router as lecturas_router
from app.controllers.inventario_controller import router as inventario_router
from app.controllers.personal_controller   import router as personal_router
from config.settings import APP_TITLE, APP_VERSION

# ── Inicialización ────────────────────────────────────────────────────────────
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=(
        "Plataforma de gestión integral para unidades piscícolas de trucha arcoíris. "
        "Módulos: monitoreo hídrico, inventario, personal y usuarios."
    ),
)

# ── Registro de routers (controladores) ──────────────────────────────────────
app.include_router(usuarios_router)
app.include_router(lecturas_router)
app.include_router(inventario_router)
app.include_router(personal_router)


# ── Evento de inicio: crear tablas si no existen ─────────────────────────────
@app.on_event("startup")
def startup_event() -> None:
    init_db()
    print(f"[AQUALITY] Base de datos inicializada. Versión {APP_VERSION}")


# ── Endpoint raíz ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def raiz():
    return {
        "sistema":  APP_TITLE,
        "version":  APP_VERSION,
        "estado":   "operativo",
        "docs":     "/docs",
        "modulos": [
            "Usuarios        → /usuarios",
            "Monitoreo hídrico → /lecturas",
            "Inventario      → /inventario",
            "Personal        → /personal",
        ],
    }
