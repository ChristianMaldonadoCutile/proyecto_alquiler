from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from config.base_datos import motor, Base

# Importar modelos para que SQLAlchemy los registre
from modelos import Propietario, Inquilino, Habitacion, Contrato, Pago

# Importar rutas API
from rutas.propietario import enrutador as ruta_propietario
from rutas.inquilino import enrutador as ruta_inquilino
from rutas.habitacion import enrutador as ruta_habitacion
from rutas.contrato import enrutador as ruta_contrato
from rutas.pago import enrutador as ruta_pago
from rutas.reporte import enrutador as ruta_reporte

# Importar rutas de vistas
from rutas.vistas import enrutador as ruta_vistas

# Importar scheduler
from servicios.servicio_notificacion import iniciar_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=motor)
    scheduler = iniciar_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Sistema de Cobros de Alquiler",
    description="API para gestión de habitaciones, inquilinos y pagos de alquiler",
    version="4.0.0",
    lifespan=lifespan
)

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Registrar rutas API
app.include_router(ruta_propietario)
app.include_router(ruta_inquilino)
app.include_router(ruta_habitacion)
app.include_router(ruta_contrato)
app.include_router(ruta_pago)
app.include_router(ruta_reporte)

# Registrar rutas de vistas
app.include_router(ruta_vistas)


@app.get("/")
async def inicio():
    return RedirectResponse(url="/vistas/login")