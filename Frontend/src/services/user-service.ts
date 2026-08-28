import { apiClient } from "@/services/api-client";
import type { NombreRol, Usuario } from "@/types";

export interface CrearUsuarioPayload {
  nombre: string;
  correo: string;
  password: string;
  rol: NombreRol;
}

export interface ListarOpciones {
  skip?: number;
  limit?: number;
}

export const userService = {
  listar: async (opciones: ListarOpciones = {}) => {
    const { data } = await apiClient.get<Usuario[]>("/users", { params: opciones });
    return data;
  },
  crear: async (payload: CrearUsuarioPayload) => {
    const { data } = await apiClient.post<Usuario>("/users", payload);
    return data;
  },
  cambiarEstado: async (id: number, activo: boolean) => {
    const { data } = await apiClient.patch<Usuario>(`/users/${id}/status`, { activo });
    return data;
  },
};
