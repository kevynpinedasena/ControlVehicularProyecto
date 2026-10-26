"""Endpoints de autenticación: login, refresh y usuario actual."""
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.application.dto.auth_dto import CredencialesLoginDTO
from app.application.use_cases.auth_use_cases import (
    AutenticarUsuarioUseCase,
    ObtenerUsuarioActualUseCase,
    RefrescarTokenUseCase,
)
from app.presentation.dependencies.autenticacion import UsuarioAutenticado
from app.presentation.dependencies.casos_uso import (
    caso_uso_autenticar,
    caso_uso_refrescar_token,
    caso_uso_usuario_actual,
)
from app.presentation.dependencies.limitador_tasa import limitar_intentos_login
from app.presentation.schemas.auth_schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokensResponse,
    UsuarioActualResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokensResponse)
async def iniciar_sesion(
    request: Request,
    datos: LoginRequest,
    caso_uso: Annotated[AutenticarUsuarioUseCase, Depends(caso_uso_autenticar)],
) -> TokensResponse:
    limitar_intentos_login(request, datos.correo)
    tokens = await caso_uso.ejecutar(
        CredencialesLoginDTO(
            correo=datos.correo,
            password=datos.password,
            slug_unidad_negocio=datos.slug_unidad_negocio,
        )
    )
    return TokensResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/refresh", response_model=TokensResponse)
async def refrescar_token(
    datos: RefreshTokenRequest,
    caso_uso: Annotated[RefrescarTokenUseCase, Depends(caso_uso_refrescar_token)],
) -> TokensResponse:
    tokens = await caso_uso.ejecutar(datos.refresh_token)
    return TokensResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.get("/me", response_model=UsuarioActualResponse)
async def obtener_usuario_actual(
    usuario: UsuarioAutenticado,
    caso_uso: Annotated[ObtenerUsuarioActualUseCase, Depends(caso_uso_usuario_actual)],
) -> UsuarioActualResponse:
    datos = await caso_uso.ejecutar(usuario.id)
    return UsuarioActualResponse(
        id=datos.id,
        nombre=datos.nombre,
        correo=datos.correo,
        rol=datos.rol,
        unidad_negocio_id=datos.unidad_negocio_id,
    )
