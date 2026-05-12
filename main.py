from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.models.database import init_db
from app.controllers.usuarios_controller   import router as usuarios_router
from app.controllers.lecturas_controller   import router as lecturas_router
from app.controllers.inventario_controller import router as inventario_router
from app.controllers.personal_controller   import router as personal_router
from config.settings import APP_TITLE, APP_VERSION
import os


app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# 1. MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ## 2. EVENTOS
# @app.on_event("startup")
# def startup_event():
#     init_db()

# 3. RUTAS DE LA API (Deben ir ANTES que el HTML)
app.include_router(usuarios_router)
app.include_router(lecturas_router)
app.include_router(inventario_router)
app.include_router(personal_router)

# Ruta de estado
@app.get("/status", tags=["Root"])
def status():
    return {"sistema": APP_TITLE, "version": APP_VERSION, "estado": "operativo"}

# 4. RUTA PRINCIPAL (DASHBOARD)
@app.get("/")
async def read_index():
    # Carga el archivo dashboard.html que está en la raíz de tu carpeta aquality
    return FileResponse('dashboard.html')

# 5. ARCHIVOS ESTÁTICOS
# Esta línea permite que el navegador encuentre manifest.json, sw.js y aquality_final.png
# Tal como lo tenías originalmente para que carguen desde la raíz (.)
app.mount("/", StaticFiles(directory="."), name="static")