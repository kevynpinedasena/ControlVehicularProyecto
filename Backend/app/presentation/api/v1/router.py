"""Agregador de todos los routers de la versión 1 de la API."""
from fastapi import APIRouter

from app.presentation.api.v1.apartamentos_router import router as apartamentos_router
from app.presentation.api.v1.auth_router import router as auth_router
from app.presentation.api.v1.bloques_router import router as bloques_router
from app.presentation.api.v1.consulta_placa_router import router as consulta_placa_router
from app.presentation.api.v1.importacion_router import router as importacion_router
from app.presentation.api.v1.parqueaderos_router import router as parqueaderos_router
from app.presentation.api.v1.residentes_router import router as residentes_router
from app.presentation.api.v1.tipos_residente_router import router as tipos_residente_router
from app.presentation.api.v1.tipos_vehiculo_router import router as tipos_vehiculo_router
from app.presentation.api.v1.torres_router import router as torres_router
from app.presentation.api.v1.unidades_negocio_router import router as unidades_negocio_router
from app.presentation.api.v1.unidades_negocio_router import router_publico as unidades_negocio_router_publico
from app.presentation.api.v1.usuarios_router import router as usuarios_router
from app.presentation.api.v1.vehiculos_router import router as vehiculos_router

router_v1 = APIRouter(prefix="/api/v1")

router_v1.include_router(auth_router)
router_v1.include_router(usuarios_router)
router_v1.include_router(residentes_router)
router_v1.include_router(consulta_placa_router)
router_v1.include_router(vehiculos_router)
router_v1.include_router(torres_router)
router_v1.include_router(apartamentos_router)
router_v1.include_router(importacion_router)
router_v1.include_router(tipos_vehiculo_router)
router_v1.include_router(tipos_residente_router)
router_v1.include_router(bloques_router)
router_v1.include_router(parqueaderos_router)
router_v1.include_router(unidades_negocio_router_publico)
router_v1.include_router(unidades_negocio_router)
