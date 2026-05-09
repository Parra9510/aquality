# AQUALITY – Sistema Integral para la Optimización Acuícola

> Plataforma de gestión para unidades piscícolas de trucha arcoíris (*Oncorhynchus mykiss*) en Colombia.  
> Proyecto de Grado – Ingeniería de Software · C.I.A.F. Pereira, 2026  
> **Autores:** Cristian David Gutiérrez · Víctor Manuel Parra

---

## Descripción

AQUALITY es una aplicación backend desarrollada en Python con FastAPI que integra:

- **Monitoreo hídrico** (temperatura, pH, oxígeno disuelto) con alertas automáticas.
- **Gestión de inventario** de insumos y alimentos con control de stock mínimo.
- **Administración de personal** de la piscifactoría.
- **Registro de usuarios** con roles diferenciados (administrador, supervisor, operario).
- **Consumo de API externa** Open-Meteo para datos climáticos ambientales.

---

## Requisitos

- Python 3.11+
- pip / venv

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/aquality/aquality-backend.git
cd aquality-backend

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.  
Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`

---

## Estructura del Proyecto

```
aquality/
├── app/
│   ├── models/
│   │   ├── database.py        # Configuración SQLAlchemy
│   │   ├── usuario.py         # Modelo Usuario (POO)
│   │   ├── estanque.py        # Modelo Estanque
│   │   ├── lectura.py         # Modelo LecturaHidrica (polimorfismo)
│   │   ├── inventario.py      # Modelos Insumo y MovimientoStock
│   │   └── personal.py        # Modelo Personal
│   ├── services/
│   │   ├── usuario_service.py
│   │   ├── lectura_service.py
│   │   ├── inventario_service.py
│   │   └── clima_service.py   # Consumo API externa Open-Meteo
│   ├── controllers/
│   │   ├── usuarios_controller.py
│   │   ├── lecturas_controller.py
│   │   ├── inventario_controller.py
│   │   └── personal_controller.py
│   └── utils/
│       └── validaciones.py
├── config/
│   └── settings.py
├── tests/
│   └── test_modelos.py        # Suite de pruebas unitarias (pytest)
├── main.py
├── requirements.txt
└── README.md
```

---

## Endpoints Principales

| Módulo | Método | Ruta | Descripción |
|--------|--------|------|-------------|
| Usuarios | POST | `/usuarios/` | Registrar usuario |
| Usuarios | POST | `/usuarios/login` | Autenticar |
| Usuarios | GET | `/usuarios/` | Listar usuarios |
| Lecturas | POST | `/lecturas/` | Registrar lectura hídrica |
| Lecturas | GET | `/lecturas/estanque/{id}` | Lecturas por estanque |
| Lecturas | GET | `/lecturas/alertas` | Parámetros fuera de rango |
| Lecturas | GET | `/lecturas/resumen/{id}` | Informe estadístico |
| Lecturas | GET | `/lecturas/clima/actual` | Datos climáticos (API externa) |
| Inventario | POST | `/inventario/insumos` | Crear insumo |
| Inventario | POST | `/inventario/movimientos` | Registrar movimiento de stock |
| Inventario | GET | `/inventario/alertas/bajo-stock` | Insumos bajo mínimo |
| Personal | POST | `/personal/` | Registrar colaborador |
| Personal | GET | `/personal/` | Listar personal |

---

## Pruebas

```bash
pytest tests/ -v
```

La suite incluye **más de 35 pruebas unitarias** que cubren:
- Modelos ORM (Usuario, Estanque, LecturaHidrica, Insumo, Personal)
- Lógica de negocio (evaluación de parámetros, alertas, stock)
- Utilidades de validación
- Servicio de API externa (con mock de `requests`)

---

## Conceptos de POO Implementados

| Concepto | Dónde se aplica |
|----------|-----------------|
| Clases y objetos | Todos los modelos (`Usuario`, `Estanque`, etc.) |
| Encapsulamiento | `Usuario._password_hash` + `set/verificar_password()` |
| Herencia | `LecturaHidrica(Base, LecturaBase)`, todos los modelos heredan de `Base` |
| Polimorfismo | `LecturaHidrica.evaluar()` redefine `LecturaBase.evaluar()` |
| `__init__` | Todos los modelos |
| `__str__` / `__repr__` | Todos los modelos |

---

## API Externa Consumida

**Open-Meteo** (`https://api.open-meteo.com`)  
- Sin autenticación requerida (API pública).  
- Se usa para correlacionar temperatura ambiente con temperatura del agua en estanques.
- Endpoint: `GET /lecturas/clima/actual?lat=4.8133&lon=-75.6189`

---

## Control de Versiones

```
main        ← producción estable
develop     ← integración continua
feature/*   ← funcionalidades en desarrollo
```

Convención de commits: `tipo(alcance): descripción corta`  
Ejemplos: `feat(lecturas): agregar endpoint de alertas`, `fix(inventario): corregir validación de stock`

---

## Base de Datos

Motor por defecto: **SQLite** (`aquality.db`)  
ORM: **SQLAlchemy 2.x**  
Para producción se recomienda PostgreSQL (cambiar `DATABASE_URL` en `.env`).

---

## Licencia

Proyecto académico – C.I.A.F. 2026. Todos los derechos reservados.
