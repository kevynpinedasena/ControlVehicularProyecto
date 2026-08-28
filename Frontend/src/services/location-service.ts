import { apiClient } from "@/services/api-client";
import type { Apartamento, Torre } from "@/types";

export interface ListarTorresOpciones {
  skip?: number;
  limit?: number;
}

export interface ListarApartamentosOpciones {
  torreId?: number;
  skip?: number;
  limit?: number;
}

export const towerService = {
  listar: async (opciones: ListarTorresOpciones = {}) => {
    const { data } = await apiClient.get<Torre[]>("/towers", {
      params: { skip: opciones.skip, limit: opciones.limit },
    });
    return data;
  },
  crear: async (payload: { nombre: string; codigo: string }) => {
    const { data } = await apiClient.post<Torre>("/towers", payload);
    return data;
  },
  actualizar: async (id: number, payload: { nombre: string; codigo: string }) => {
    const { data } = await apiClient.put<Torre>(`/towers/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/towers/${id}`);
  },
};

export const apartmentService = {
  listar: async (opciones: ListarApartamentosOpciones = {}) => {
    const { data } = await apiClient.get<Apartamento[]>("/apartments", {
      params: { torre_id: opciones.torreId, skip: opciones.skip, limit: opciones.limit },
    });
    return data;
  },
  crear: async (payload: { torre_id: number; numero: string }) => {
    const { data } = await apiClient.post<Apartamento>("/apartments", payload);
    return data;
  },
  actualizar: async (id: number, payload: { torre_id: number; numero: string; activo: boolean }) => {
    const { data } = await apiClient.put<Apartamento>(`/apartments/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/apartments/${id}`);
  },
};
