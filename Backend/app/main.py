"""Punto de entrada de la aplicación FastAPI."""
import asyncio
from collections.abc import AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import obtener_configuracion
from app.presentation.api.v1.router import router_v1
from app.shared.exceptions.manejador_excepciones import registrar_manejadores_excepciones
from app.shared.logging.logger import configurar_logging

configuracion = obtener_configuracion()
configurar_logging()


@asynccontextmanager
async def _ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
    """Amplía el thread pool de asyncio al tamaño configurado (ver Settings.tamano_pool_hilos),
    para que una ráfaga grande de logins simultáneos (bcrypt, vía asyncio.to_thread) no se quede
    esperando turno en el pool por defecto, mucho más pequeño."""
    asyncio.get_running_loop().set_default_executor(
        ThreadPoolExecutor(max_workers=configuracion.tamano_pool_hilos)
    )
    yield


app = FastAPI(
    title="Sistema de Control de Vehículos - Plataforma Multi-Conjunto",
    description=(
        "API multi-tenant para el registro de residentes, vehículos y la consulta rápida "
        "de placas por parte del personal de vigilancia de cada unidad de negocio."
    ),
    version="2.0.0",
    lifespan=_ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracion.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

registrar_manejadores_excepciones(app)

app.include_router(router_v1)


@app.get("/health", tags=["Salud"])
async def verificar_salud() -> dict[str, str]:
    """Endpoint de verificación de disponibilidad del servicio."""
    return {"estado": "operativo"}
