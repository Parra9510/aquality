from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import init_db

from app.routers.usuarios  import router as usuarios_router
from app.routers.lecturas   import router as lecturas_router
from app.routers.inventario import router as inventario_router
from app.routers.personal   import router as personal_router
from app.routers.estanques  import router as estanques_router

# Ruta absoluta a la raíz del proyecto (carpeta "aquality/")
# api/main.py → api/ → aquality/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"[AQUALITY] Warning DB: {e}")

# Routers de la API
app.include_router(usuarios_router)
app.include_router(lecturas_router)
app.include_router(inventario_router)
app.include_router(personal_router)
app.include_router(estanques_router)

@app.get("/status", tags=["Root"])
def status():
    return {"sistema": settings.APP_TITLE, "version": settings.APP_VERSION, "estado": "operativo"}

@app.get("/health", tags=["Root"])
def health():
    return {"ok": True}

# Servir el dashboard HTML usando ruta absoluta
@app.get("/", include_in_schema=False)
async def read_index():
    html_path = os.path.join(BASE_DIR, "dashboard.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("<h1>AQUALITY API</h1><p>Docs: <a href='/docs'>/docs</a></p>")

# Archivos estáticos usando ruta absoluta
if os.path.isdir(BASE_DIR):
    app.mount("/", StaticFiles(directory=BASE_DIR), name="static")
