from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import init_db
from app.controllers.usuarios_controller   import router as usuarios_router
from app.controllers.lecturas_controller   import router as lecturas_router
from app.controllers.inventario_controller import router as inventario_router
from app.controllers.personal_controller   import router as personal_router
from config.settings import APP_TITLE, APP_VERSION

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(lecturas_router)
app.include_router(inventario_router)
app.include_router(personal_router)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", tags=["Root"])
def raiz():
    return {"sistema": APP_TITLE, "version": APP_VERSION, "estado": "operativo"}