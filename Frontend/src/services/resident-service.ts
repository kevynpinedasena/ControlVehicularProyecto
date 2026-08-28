import { apiClient } from "@/services/api-client";
import type { Residente } from "@/types";

export interface CrearResidentePayload {
  nombre: string;
  documento: string;
  tipo_residente_id: number;
  apartamento_id: number;
  telefono_1?: string | null;
  telefono_2?: string | null;
}

export interface ActualizarResidentePayload extends CrearResidentePayload {
  activo: boolean;
}

export interface ListarOpciones {
  busqueda?: string;
  skip?: number;
  limit?: number;
}

export const residentService = {
  listar: async (opciones: ListarOpciones = {}) => {
    const { data } = await apiClient.get<Residente[]>("/residents", { params: opciones });
    return data;
  },
  obtener: async (id: number) => {
    const { data } = await apiClient.get<Residente>(`/residents/${id}`);
    return data;
  },
  crear: async (payload: CrearResidentePayload) => {
    const { data } = await apiClient.post<Residente>("/residents", payload);
    return data;
  },
  actualizar: async (id: number, payload: ActualizarResidentePayload) => {
    const { data } = await apiClient.put<Residente>(`/residents/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/residents/${id}`);
  },
};
