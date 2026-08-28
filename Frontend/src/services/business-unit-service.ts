import { apiClient } from "@/services/api-client";
import type { UnidadNegocio, UnidadNegocioPublica, Usuario } from "@/types";

export interface RestablecerPasswordResultado {
  usuario_id: number;
  correo: string;
  nueva_password: string;
}

export interface CrearUnidadNegocioPayload {
  nombre: string;
  slug: string;
  admin_nombre: string;
  admin_correo: string;
  admin_password: string;
  color_primario: string;
  color_secundario: string;
  logo?: File | null;
}

export interface ActualizarUnidadNegocioPayload {
  nombre: string;
  slug: string;
  color_primario: string;
  color_secundario: string;
  activo: boolean;
}

export const businessUnitService = {
  obtenerPublica: async (slug: string) => {
    const { data } = await apiClient.get<UnidadNegocioPublica>(`/business-units/public/${slug}`);
    return data;
  },
  listar: async () => {
    const { data } = await apiClient.get<UnidadNegocio[]>("/business-units");
    return data;
  },
  crear: async (payload: CrearUnidadNegocioPayload) => {
    const formData = new FormData();
    formData.append("nombre", payload.nombre);
    formData.append("slug", payload.slug);
    formData.append("admin_nombre", payload.admin_nombre);
    formData.append("admin_correo", payload.admin_correo);
    formData.append("admin_password", payload.admin_password);
    formData.append("color_primario", payload.color_primario);
    formData.append("color_secundario", payload.color_secundario);
    if (payload.logo) formData.append("logo", payload.logo);

    const { data } = await apiClient.post<UnidadNegocio>("/business-units", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
  actualizar: async (id: number, payload: ActualizarUnidadNegocioPayload) => {
    const { data } = await apiClient.put<UnidadNegocio>(`/business-units/${id}`, payload);
    return data;
  },
  subirLogo: async (id: number, logo: File) => {
    const formData = new FormData();
    formData.append("logo", logo);
    const { data } = await apiClient.post<UnidadNegocio>(`/business-units/${id}/logo`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
  listarUsuarios: async (unidadId: number) => {
    const { data } = await apiClient.get<Usuario[]>(`/business-units/${unidadId}/users`);
    return data;
  },
  restablecerPassword: async (unidadId: number, usuarioId: number, nuevaPassword?: string) => {
    const { data } = await apiClient.post<RestablecerPasswordResultado>(
      `/business-units/${unidadId}/users/${usuarioId}/reset-password`,
      { nueva_password: nuevaPassword ?? null },
    );
    return data;
  },
};
