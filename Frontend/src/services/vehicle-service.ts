import { apiClient } from "@/services/api-client";
import type { ConsultaPlacaResultado, Vehiculo } from "@/types";

export interface CrearVehiculoPayload {
  placa: string;
  tipo_vehiculo_id: number;
  residente_id: number;
}

export interface ActualizarVehiculoPayload {
  placa: string;
  tipo_vehiculo_id: number;
  activo: boolean;
}

export interface ListarOpciones {
  busqueda?: string;
  skip?: number;
  limit?: number;
  parqueaderoId?: number;
}

export const vehicleService = {
  listar: async (opciones: ListarOpciones = {}) => {
    const { data } = await apiClient.get<Vehiculo[]>("/vehicles", {
      params: {
        busqueda: opciones.busqueda,
        skip: opciones.skip,
        limit: opciones.limit,
        parqueadero_id: opciones.parqueaderoId,
      },
    });
    return data;
  },
  crear: async (payload: CrearVehiculoPayload) => {
    const { data } = await apiClient.post<Vehiculo>("/vehicles", payload);
    return data;
  },
  actualizar: async (id: number, payload: ActualizarVehiculoPayload) => {
    const { data } = await apiClient.put<Vehiculo>(`/vehicles/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/vehicles/${id}`);
  },
  asignarParqueadero: async (vehiculoId: number, parqueaderoId: number | null) => {
    const { data } = await apiClient.put<Vehiculo>(`/vehicles/${vehiculoId}/parking-spot`, {
      parqueadero_id: parqueaderoId,
    });
    return data;
  },
  consultarPlaca: async (placa: string) => {
    const { data } = await apiClient.get<ConsultaPlacaResultado>(
      `/vehicles/plate/${encodeURIComponent(placa)}`,
    );
    return data;
  },
};
