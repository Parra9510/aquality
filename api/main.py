from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# 1. IMPORTS DE CONFIGURACIÓN Y BASE DE DATOS
from app.core.config import settings
from app.core.database import init_db

# 2. IMPORTS DE LOS ROUTERS (LAS RUTAS)
# Importamos los routers con los alias que ya usas en el código
from app.routers.usuarios import router as usuarios_router
from app.routers.lecturas import router as lecturas_router
from app.routers.inventario import router as inventario_router
from app.routers.personal import router as personal_router
from app.routers.estanques import router as estanques_router


# 3. INICIALIZACIÓN DE LA APP
# Usamos settings. para acceder al título y versión
app = FastAPI(
    title=settings.APP_TITLE, 
    version=settings.APP_VERSION
)

# 4. MIDDLEWARE (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. EVENTO DE ARRANQUE (Crea las tablas si no existen)
@app.on_event("startup")
def startup_event():
    init_db()

# 6. INCLUSIÓN DE RUTAS (API)
app.include_router(usuarios_router)
app.include_router(lecturas_router)
app.include_router(inventario_router)
app.include_router(personal_router)
app.include_router(estanques_router)

# Ruta de estado
@app.get("/status", tags=["Root"])
def status():
    return {
        "sistema": settings.APP_TITLE, 
        "version": settings.APP_VERSION, 
        "estado": "operativo"
    }

# 7. RUTA PRINCIPAL (DASHBOARD)
@app.get("/")
async def read_index():
    return FileResponse('dashboard.html')

# 8. ARCHIVOS ESTÁTICOS
# Importante: Como main.py está en /api, el directorio "." es la raíz del proyecto
app.mount("/", StaticFiles(directory="."), name="static")