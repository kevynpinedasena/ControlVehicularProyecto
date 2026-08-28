"""Punto de entrada de la aplicación FastAPI."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import obtener_configuracion
from app.presentation.api.v1.router import router_v1
from app.shared.exceptions.manejador_excepciones import registrar_manejadores_excepciones
from app.shared.logging.logger import configurar_logging

configuracion = obtener_configuracion()
configurar_logging()

app = FastAPI(
    title="Sistema de Control de Vehículos - Plataforma Multi-Conjunto",
    description=(
        "API multi-tenant para el registro de residentes, vehículos y la consulta rápida "
        "de placas por parte del personal de vigilancia de cada unidad de negocio."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracion.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_manejadores_excepciones(app)

Path("uploads/logos").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(router_v1)


@app.get("/health", tags=["Salud"])
async def verificar_salud() -> dict[str, str]:
    """Endpoint de verificación de disponibilidad del servicio."""
    return {"estado": "operativo"}
