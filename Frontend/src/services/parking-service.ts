import { apiClient } from "@/services/api-client";
import type { Bloque, Parqueadero } from "@/types";

export const blockService = {
  listar: async () => {
    const { data } = await apiClient.get<Bloque[]>("/parking-blocks");
    return data;
  },
  crear: async (payload: { nombre: string; codigo: string }) => {
    const { data } = await apiClient.post<Bloque>("/parking-blocks", payload);
    return data;
  },
  actualizar: async (id: number, payload: { nombre: string; codigo: string }) => {
    const { data } = await apiClient.put<Bloque>(`/parking-blocks/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/parking-blocks/${id}`);
  },
};

export interface ParkingSpotPayload {
  bloque_id: number;
  numero: string;
  tipo_espacio: "COMUNAL" | "PRIVADO";
  tipo_vehiculo_id: number;
  capacidad: number;
  propietario_residente_id?: number | null;
}

export interface ActualizarParkingSpotPayload extends ParkingSpotPayload {
  activo: boolean;
}

export const parkingSpotService = {
  listar: async (bloqueId?: number) => {
    const { data } = await apiClient.get<Parqueadero[]>("/parking-spots", {
      params: { bloque_id: bloqueId },
    });
    return data;
  },
  crear: async (payload: ParkingSpotPayload) => {
    const { data } = await apiClient.post<Parqueadero>("/parking-spots", payload);
    return data;
  },
  actualizar: async (id: number, payload: ActualizarParkingSpotPayload) => {
    const { data } = await apiClient.put<Parqueadero>(`/parking-spots/${id}`, payload);
    return data;
  },
  eliminar: async (id: number) => {
    await apiClient.delete(`/parking-spots/${id}`);
  },
};