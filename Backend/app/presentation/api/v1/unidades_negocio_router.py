"""Endpoints de administración de unidades de negocio (plataforma) y su consulta pública."""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.application.dto.unidad_negocio_dto import (
    ActualizarUnidadNegocioDTO,
    CrearUnidadNegocioDTO,
)
from app.application.use_cases.unidad_negocio_use_cases import (
    ActualizarLogoUnidadNegocioUseCase,
    ActualizarUnidadNegocioUseCase,
    CrearUnidadNegocioUseCase,
    ListarUnidadesNegocioUseCase,
    ObtenerUnidadNegocioPublicaUseCase,
)
from app.application.use_cases.usuario_use_cases import (
    ListarUsuariosDeUnidadUseCase,
    RestablecerPasswordUsuarioUseCase,
)
from app.domain.entities.unidad_negocio import UnidadNegocio
from app.domain.entities.usuario import Usuario
from app.infrastructure.storage.almacenamiento_logos import guardar_logo
from app.presentation.dependencies.autenticacion import requerir_admin_plataforma
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_logo_unidad_negocio,
    caso_uso_actualizar_unidad_negocio,
    caso_uso_crear_unidad_negocio,
    caso_uso_listar_unidades_negocio,
    caso_uso_listar_usuarios_de_unidad,
    caso_uso_obtener_unidad_negocio_publica,
    caso_uso_restablecer_password_usuario,
)
from app.presentation.schemas.unidad_negocio_schemas import (
    ActualizarUnidadNegocioRequest,
    RestablecerPasswordRequest,
    RestablecerPasswordResponse,
    UnidadNegocioPublicaResponse,
    UnidadNegocioResponse,
)
from app.presentation.schemas.usuario_schemas import UsuarioResponse

router = APIRouter(
    prefix="/business-units",
    tags=["Unidades de negocio"],
    dependencies=[Depends(requerir_admin_plataforma)],
)

router_publico = APIRouter(prefix="/business-units", tags=["Unidades de negocio (público)"])


def _a_response(unidad: UnidadNegocio) -> UnidadNegocioResponse:
    return UnidadNegocioResponse(
        id=unidad.id,
        nombre=unidad.nombre,
        slug=unidad.slug,
        logo_url=unidad.logo_url,
        color_primario=unidad.color_primario,
        color_secundario=unidad.color_secundario,
        activo=unidad.activo,
        created_at=unidad.created_at,
    )


@router.get("", response_model=list[UnidadNegocioResponse])
async def listar_unidades_negocio(
    caso_uso: Annotated[ListarUnidadesNegocioUseCase, Depends(caso_uso_listar_unidades_negocio)],
) -> list[UnidadNegocioResponse]:
    return [_a_response(u) for u in await caso_uso.ejecutar()]


@router.post("", response_model=UnidadNegocioResponse, status_code=status.HTTP_201_CREATED)
async def crear_unidad_negocio(
    caso_uso: Annotated[CrearUnidadNegocioUseCase, Depends(caso_uso_crear_unidad_negocio)],
    nombre: Annotated[str, Form()],
    slug: Annotated[str, Form()],
    admin_nombre: Annotated[str, Form()],
    admin_correo: Annotated[str, Form()],
    admin_password: Annotated[str, Form(min_length=8)],
    color_primario: Annotated[str, Form()] = "#2563eb",
    color_secundario: Annotated[str, Form()] = "#1e293b",
    logo: Annotated[UploadFile | None, File()] = None,
) -> UnidadNegocioResponse:
    logo_url = await guardar_logo(logo) if logo and logo.filename else None

    unidad = await caso_uso.ejecutar(
        CrearUnidadNegocioDTO(
            nombre=nombre,
            slug=slug,
            color_primario=color_primario,
            color_secundario=color_secundario,
            admin_nombre=admin_nombre,
            admin_correo=admin_correo,
            admin_password=admin_password,
            logo_url=logo_url,
        )
    )
    return _a_response(unidad)


@router.put("/{unidad_id}", response_model=UnidadNegocioResponse)
async def actualizar_unidad_negocio(
    unidad_id: int,
    datos: ActualizarUnidadNegocioRequest,
    caso_uso: Annotated[ActualizarUnidadNegocioUseCase, Depends(caso_uso_actualizar_unidad_negocio)],
) -> UnidadNegocioResponse:
    unidad = await caso_uso.ejecutar(
        unidad_id,
        ActualizarUnidadNegocioDTO(
            nombre=datos.nombre,
            slug=datos.slug,
            color_primario=datos.color_primario,
            color_secundario=datos.color_secundario,
            activo=datos.activo,
        ),
    )
    return _a_response(unidad)


@router.post("/{unidad_id}/logo", response_model=UnidadNegocioResponse)
async def subir_logo_unidad_negocio(
    unidad_id: int,
    caso_uso: Annotated[ActualizarLogoUnidadNegocioUseCase, Depends(caso_uso_actualizar_logo_unidad_negocio)],
    logo: Annotated[UploadFile, File()],
) -> UnidadNegocioResponse:
    logo_url = await guardar_logo(logo)
    unidad = await caso_uso.ejecutar(unidad_id, logo_url)
    return _a_response(unidad)


def _usuario_a_response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        nombre=usuario.nombre,
        correo=usuario.correo,
        rol=usuario.rol,
        unidad_negocio_id=usuario.unidad_negocio_id,
        activo=usuario.activo,
        created_at=usuario.created_at,
        updated_at=usuario.updated_at,
    )


@router.get("/{unidad_id}/users", response_model=list[UsuarioResponse])
async def listar_usuarios_de_unidad(
    unidad_id: int,
    caso_uso: Annotated[ListarUsuariosDeUnidadUseCase, Depends(caso_uso_listar_usuarios_de_unidad)],
) -> list[UsuarioResponse]:
    return [_usuario_a_response(u) for u in await caso_uso.ejecutar(unidad_id)]


@router.post("/{unidad_id}/users/{usuario_id}/reset-password", response_model=RestablecerPasswordResponse)
async def restablecer_password_usuario(
    unidad_id: int,
    usuario_id: int,
    caso_uso: Annotated[
        RestablecerPasswordUsuarioUseCase, Depends(caso_uso_restablecer_password_usuario)
    ],
    datos: RestablecerPasswordRequest | None = None,
) -> RestablecerPasswordResponse:
    resultado = await caso_uso.ejecutar(
        unidad_id, usuario_id, datos.nueva_password if datos else None
    )
    return RestablecerPasswordResponse(
        usuario_id=resultado.usuario_id,
        correo=resultado.correo,
        nueva_password=resultado.nueva_password,
    )


@router_publico.get("/public/{slug}", response_model=UnidadNegocioPublicaResponse)
async def obtener_unidad_negocio_publica(
    slug: str,
    caso_uso: Annotated[
        ObtenerUnidadNegocioPublicaUseCase, Depends(caso_uso_obtener_unidad_negocio_publica)
    ],
) -> UnidadNegocioPublicaResponse:
    unidad = await caso_uso.ejecutar(slug)
    return UnidadNegocioPublicaResponse(
        nombre=unidad.nombre,
        slug=unidad.slug,
        logo_url=unidad.logo_url,
        color_primario=unidad.color_primario,
        color_secundario=unidad.color_secundario,
        activo=unidad.activo,
    )
