"""Implementación concreta del repositorio de usuarios usando SQLAlchemy."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.enums import NombreRol
from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.database.models import RolModel, UsuarioModel


def _a_entidad(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.id,
        nombre=modelo.nombre,
        correo=modelo.correo,
        password_hash=modelo.password_hash,
        rol=modelo.rol.nombre,
        unidad_negocio_id=modelo.unidad_negocio_id,
        activo=modelo.activo,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
    )


class UsuarioRepository(IUsuarioRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        resultado = await self._sesion.execute(
            select(UsuarioModel)
            .where(UsuarioModel.id == usuario_id)
            .options(selectinload(UsuarioModel.rol))
        )
        modelo = resultado.scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    async def obtener_por_correo(self, correo: str) -> Usuario | None:
        resultado = await self._sesion.execute(
            select(UsuarioModel)
            .where(UsuarioModel.correo == correo)
            .options(selectinload(UsuarioModel.rol))
        )
        modelo = resultado.scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    async def listar(
        self, unidad_negocio_id: int | None = None, skip: int = 0, limit: int = 50
    ) -> list[Usuario]:
        consulta = select(UsuarioModel).options(selectinload(UsuarioModel.rol))
        if unidad_negocio_id is not None:
            consulta = consulta.where(UsuarioModel.unidad_negocio_id == unidad_negocio_id)
        consulta = consulta.offset(skip).limit(limit).order_by(UsuarioModel.id)
        resultado = await self._sesion.execute(consulta)
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, usuario: Usuario) -> Usuario:
        rol_resultado = await self._sesion.execute(
            select(RolModel).where(RolModel.nombre == usuario.rol)
        )
        rol_modelo = rol_resultado.scalar_one()

        modelo = UsuarioModel(
            nombre=usuario.nombre,
            correo=usuario.correo,
            password_hash=usuario.password_hash,
            rol_id=rol_modelo.id,
            unidad_negocio_id=usuario.unidad_negocio_id,
            activo=usuario.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["rol"])
        return _a_entidad(modelo)

    async def actualizar(self, usuario: Usuario) -> Usuario:
        resultado = await self._sesion.execute(
            select(UsuarioModel)
            .where(UsuarioModel.id == usuario.id)
            .options(selectinload(UsuarioModel.rol))
        )
        modelo = resultado.scalar_one_or_none()
        if modelo is None:
            raise ValueError("Usuario no encontrado para actualizar")

        if usuario.rol != modelo.rol.nombre:
            rol_resultado = await self._sesion.execute(
                select(RolModel).where(RolModel.nombre == usuario.rol)
            )
            modelo.rol_id = rol_resultado.scalar_one().id

        modelo.nombre = usuario.nombre
        modelo.correo = usuario.correo
        modelo.password_hash = usuario.password_hash
        modelo.activo = usuario.activo

        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        await self._sesion.refresh(modelo, attribute_names=["rol"])
        return _a_entidad(modelo)

    async def existe_correo(self, correo: str, excluir_id: int | None = None) -> bool:
        consulta = select(UsuarioModel.id).where(UsuarioModel.correo == correo)
        if excluir_id is not None:
            consulta = consulta.where(UsuarioModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None


async def obtener_o_crear_rol(sesion: AsyncSession, nombre: NombreRol) -> RolModel:
    resultado = await sesion.execute(select(RolModel).where(RolModel.nombre == nombre))
    rol = resultado.scalar_one_or_none()
    if rol is None:
        rol = RolModel(nombre=nombre)
        sesion.add(rol)
        await sesion.commit()
    return rol
