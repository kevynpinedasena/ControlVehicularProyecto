import { apiClient } from "@/services/api-client";
import type { TipoResidente, TipoVehiculo } from "@/types";

export const vehicleTypeService = {
  listar: async () => {
    const { data } = await apiClient.get<TipoVehiculo[]>("/vehicle-types");
    return data;
  },
};

export const residentTypeService = {
  listar: async () => {
    const { data } = await apiClient.get<TipoResidente[]>("/resident-types");
    return data;
  },
};