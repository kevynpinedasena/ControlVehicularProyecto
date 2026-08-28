"""Endpoints de gestión de usuarios. Restringido al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.application.dto.usuario_dto import ActualizarUsuarioDTO, CrearUsuarioDTO
from app.application.use_cases.usuario_use_cases import (
    ActualizarUsuarioUseCase,
    CambiarEstadoUsuarioUseCase,
    CrearUsuarioUseCase,
    ListarUsuariosUseCase,
    ObtenerUsuarioUseCase,
)
from app.domain.entities.usuario import Usuario
from app.presentation.dependencies.autenticacion import UnidadNegocioActual, requerir_super_admin
from app.presentation.dependencies.casos_uso import (
    caso_uso_actualizar_usuario,
    caso_uso_cambiar_estado_usuario,
    caso_uso_crear_usuario,
    caso_uso_listar_usuarios,
    caso_uso_obtener_usuario,
)
from app.presentation.schemas.usuario_schemas import (
    ActualizarUsuarioRequest,
    CambiarEstadoUsuarioRequest,
    CrearUsuarioRequest,
    UsuarioResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"],
    dependencies=[Depends(requerir_super_admin)],
)


def _a_response(usuario: Usuario) -> UsuarioResponse:
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


@router.get("", response_model=list[UsuarioResponse])
async def listar_usuarios(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ListarUsuariosUseCase, Depends(caso_uso_listar_usuarios)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[UsuarioResponse]:
    usuarios = await caso_uso.ejecutar(unidad_negocio_id, skip=skip, limit=limit)
    return [_a_response(u) for u in usuarios]


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos: CrearUsuarioRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CrearUsuarioUseCase, Depends(caso_uso_crear_usuario)],
) -> UsuarioResponse:
    usuario = await caso_uso.ejecutar(
        unidad_negocio_id,
        CrearUsuarioDTO(nombre=datos.nombre, correo=datos.correo, password=datos.password, rol=datos.rol),
    )
    return _a_response(usuario)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ObtenerUsuarioUseCase, Depends(caso_uso_obtener_usuario)],
) -> UsuarioResponse:
    return _a_response(await caso_uso.ejecutar(unidad_negocio_id, usuario_id))


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    datos: ActualizarUsuarioRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ActualizarUsuarioUseCase, Depends(caso_uso_actualizar_usuario)],
) -> UsuarioResponse:
    usuario = await caso_uso.ejecutar(
        unidad_negocio_id,
        usuario_id,
        ActualizarUsuarioDTO(nombre=datos.nombre, correo=datos.correo, rol=datos.rol, password=datos.password),
    )
    return _a_response(usuario)


@router.patch("/{usuario_id}/status", response_model=UsuarioResponse)
async def cambiar_estado_usuario(
    usuario_id: int,
    datos: CambiarEstadoUsuarioRequest,
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[CambiarEstadoUsuarioUseCase, Depends(caso_uso_cambiar_estado_usuario)],
) -> UsuarioResponse:
    usuario = await caso_uso.ejecutar(unidad_negocio_id, usuario_id, datos.activo)
    return _a_response(usuario)
